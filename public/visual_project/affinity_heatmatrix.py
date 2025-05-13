import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, BasicTicker
from bokeh.palettes import Iridescent18
from bokeh.transform import transform  # 添加 transform 导入
from bokeh.layouts import column
from sklearn.metrics.pairwise import cosine_similarity

def load_and_process_data(poi_file, toilet_file):
    """
    Load and process POI and toilet datasets
    """
    # Load POI data
    poi_df = pd.read_csv(poi_file)
    
    # Extract latitude and longitude from the_geom
    poi_df['Longitude'] = poi_df['the_geom'].str.extract(r'POINT \(([-\d.]+)', expand=False).astype(float)
    poi_df['Latitude'] = poi_df['the_geom'].str.extract(r'POINT \([-\d.]+ ([-\d.]+)', expand=False).astype(float)
    
    # Filter out Residential type (FACILITY_T=1) and invalid data
    poi_df = poi_df[poi_df['FACILITY_T'] != 1]
    
    # Ensure valid latitude and longitude data
    poi_df = poi_df.dropna(subset=['Latitude', 'Longitude'])
    poi_df = poi_df[(poi_df['Latitude'] > 40.0) & (poi_df['Latitude'] < 41.0) &
                   (poi_df['Longitude'] > -75.0) & (poi_df['Longitude'] < -73.0)]
    
    # Load toilet data
    toilet_df = pd.read_csv(toilet_file)
    
    # Extract clean latitude and longitude data
    if 'Location' in toilet_df.columns:
        if toilet_df['Location'].dtype == object and toilet_df['Location'].str.contains('POINT').any():
            # If Location column contains POINT format, extract coordinates
            toilet_df['Longitude'] = toilet_df['Location'].str.extract(r'POINT \(([-\d.]+)', expand=False).astype(float)
            toilet_df['Latitude'] = toilet_df['Location'].str.extract(r'POINT \([-\d.]+ ([-\d.]+)', expand=False).astype(float)
    
    # Ensure required columns exist
    expected_cols = ['Latitude', 'Longitude']
    for col in expected_cols:
        if col not in toilet_df.columns:
            raise ValueError(f"Missing {col} column in toilet dataset")
    
    # Facility type name dictionary
    facility_types = {
        2: "Educational", 
        3: "Cultural", 
        4: "Recreational", 
        5: "Social Services",
        6: "Transportation", 
        7: "Commercial", 
        8: "Government", 
        9: "Religious", 
        10: "Health Services", 
        11: "Public Safety", 
        12: "Water Services", 
        13: "Miscellaneous"
    }
    
    # Add facility type names
    poi_df['FACILITY_NAME'] = poi_df['FACILITY_T'].map(facility_types)
    
    # Add type marker for toilet data
    toilet_df['FACILITY_T'] = 14  # Use a non-duplicate number
    toilet_df['FACILITY_NAME'] = "Public Restrooms"
    
    return poi_df, toilet_df

def create_spatial_density_grid(df, lat_min, lat_max, lon_min, lon_max, grid_size=0.01):
    """
    Create spatial density grid for each facility type
    """
    # Create grid
    lat_bins = np.arange(lat_min, lat_max + grid_size, grid_size)
    lon_bins = np.arange(lon_min, lon_max + grid_size, grid_size)
    
    # Initialize result dictionary
    density_map = {}
    
    # Get unique facility types
    facility_types = df['FACILITY_T'].unique()
    
    # Create density grid for each facility type
    for facility_type in facility_types:
        # Filter facilities of this type
        subset = df[df['FACILITY_T'] == facility_type]
        
        # Ensure sufficient data points
        if len(subset) < 2:
            print(f"Warning: Facility type {facility_type} has only {len(subset)} data points, cannot create valid density grid. Skipping.")
            continue
        
        try:
            # Create 2D histogram
            hist, _, _ = np.histogram2d(
                subset['Latitude'], 
                subset['Longitude'], 
                bins=[lat_bins, lon_bins]
            )
            
            # Normalize density to balance differences in facility counts
            if hist.sum() > 0:  # Avoid division by zero
                hist = hist / hist.sum()
                
            # Flatten histogram as feature vector
            density_map[facility_type] = hist.flatten()
        except Exception as e:
            print(f"Error processing facility type {facility_type}: {e}")
    
    return density_map

def compute_similarity_matrix(density_map):
    """
    Compute cosine similarity matrix between facility types
    """
    # Get all facility types
    facility_types = list(density_map.keys())
    
    # Create feature matrix, each row is a density vector for a facility type
    features = np.array([density_map[ft] for ft in facility_types])
    
    # Compute cosine similarity
    similarity_matrix = cosine_similarity(features)
    
    return similarity_matrix, facility_types




def create_heatmap(similarity_matrix, facility_names, output_file_path="nyc_spatial_similarity_heatmap.html"):
    """
    Create a Bokeh heatmap visualization of the similarity matrix
    """
    # Prepare data for bokeh
    facility_count = len(facility_names)
    
    # Create a DataFrame for the heatmap
    heatmap_data = {
        'facility1': [],
        'facility2': [],
        'x': [],
        'y': [],
        'similarity': []
    }
    
    # Fill the data - 保持完整矩阵以确保正确大小
    for i in range(facility_count):
        for j in range(facility_count):
            # 修改：不再限制仅对角线及以下部分，绘制完整矩阵
            heatmap_data['facility1'].append(facility_names[i])
            heatmap_data['facility2'].append(facility_names[j])
            heatmap_data['x'].append(facility_names[j])
            heatmap_data['y'].append(facility_names[i])  # 修改：不再反转y坐标
            heatmap_data['similarity'].append(similarity_matrix[i, j])
        
    source = ColumnDataSource(data=heatmap_data)
    
    # 修改: 使用 Iridescent18 调色板代替 Viridis256
    from bokeh.palettes import Iridescent18
    colors = list(Iridescent18)
    colors = colors[0:15]
    mapper = LinearColorMapper(
        palette=colors, 
        low=0, 
        high=1
    )
    # Create color mapper
    mapper = LinearColorMapper(
        palette=colors, 
        low=0, 
        high=1
    )
    
    # 设置交互工具
    # TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
    TOOLS = "hover,save,reset"

    
    # Set up figure - 修改x轴位置
    p = figure(
        width=700,
        height=700,
        x_range=facility_names,  # 不反转X轴顺序
        y_range=facility_names,  # 不反转Y轴顺序
        toolbar_location=None,
        x_axis_location="below",  # 修改：将x轴移到下方
        # tooltips=[('Facilities', '@facility1 - @facility2'), ('Similarity', '@similarity{0.000}')],
        background_fill_color=None,
        border_fill_color=None,
        outline_line_color=None,
        tools=TOOLS,
        sizing_mode='stretch_both', # 响应式
        tooltips="""
        <div style="font-family: Georgia, Palatino, serif; font-size: 8pt;">
            <div><span style="font-weight: bold;">Facilities:</span> @facility1 - @facility2</div>
            <div><span style="font-weight: bold;">Similarity:</span> @similarity{0.000}</div>
        </div>
        """,
    )
    
    # Add heatmap rectangles
    p.rect(
        x='x',
        y='y',
        width=1.0,
        height=1.0,
        source=source,
        fill_color={'field': 'similarity', 'transform': mapper},
        line_color=None,
        alpha=0.8
    )
    
    # 修改: 调整 ColorBar 样式
    color_bar = ColorBar(
        color_mapper=mapper,
        ticker=BasicTicker(desired_num_ticks=7),
        label_standoff=6,
        border_line_color=None,
        location=(0, 0),
        width=20,
        height=300,
        title="",
        background_fill_color=None,
        visible=False 
    )
    
    p.add_layout(color_bar, 'right')
    
    # Set axes style
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "10px"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = 0.9  # 保持X轴标签角度
    p.yaxis.major_label_orientation = 0  # 确保Y轴标签水平
    
    # Remove grid lines
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    p.axis.major_label_text_font = "Georgia, Palatino, serif"
    p.axis.major_label_text_font_style = "normal"  # 可以是 normal, italic, bold 等

    
    # Output to file
    output_file(output_file_path)
    save(p)
    
    print(f"Heatmap saved to {output_file_path}")
    return p

def main(poi_file, toilet_file, output_file="nyc_heatmatrix.html"):
    """
    Main function for the analysis
    """
    # 1. Load and process data
    poi_df, toilet_df = load_and_process_data(poi_file, toilet_file)
    
    # 2. Combine datasets
    combined_df = pd.concat([poi_df[['FACILITY_T', 'FACILITY_NAME', 'Latitude', 'Longitude']], 
                            toilet_df[['FACILITY_T', 'FACILITY_NAME', 'Latitude', 'Longitude']]])
    
    # 3. Set NYC boundaries
    nyc_bounds = {
        'lat_min': 40.5,
        'lat_max': 40.9,
        'lon_min': -74.1,
        'lon_max': -73.7
    }
    
    # 4. Create spatial density grid
    density_map = create_spatial_density_grid(
        combined_df, 
        nyc_bounds['lat_min'], 
        nyc_bounds['lat_max'], 
        nyc_bounds['lon_min'], 
        nyc_bounds['lon_max']
    )
    
    # 5. Compute similarity matrix
    similarity_matrix, facility_types = compute_similarity_matrix(density_map)
    
    # Get facility type names
    facility_names = []
    for ft in facility_types:
        if ft == 14:  # Toilet code
            facility_names.append("Public Restrooms")
        else:
            name = combined_df[combined_df['FACILITY_T'] == ft]['FACILITY_NAME'].iloc[0]
            facility_names.append(name)
    
    # 6. Create heatmap
    create_heatmap(similarity_matrix, facility_names, output_file)
    
    # 7. Analyze similarity with toilets
    toilet_index = facility_types.index(14)  # Index of toilets
    similarity_with_toilet = similarity_matrix[toilet_index]
    
    # Create similarity ranking
    similarity_ranking = [(name, sim) for name, sim in zip(facility_names, similarity_with_toilet)]
    similarity_ranking.sort(key=lambda x: x[1], reverse=True)
    
    # Return similarity ranking (excluding toilets themselves)
    return [(name, sim) for name, sim in similarity_ranking if name != "Public Restrooms"]

if __name__ == "__main__":
    # File path parameters
    poi_file = "./data/Points_of_Interest_20250425.csv"
    toilet_file = "./data/Public_Restrooms.csv"
    
    # Run analysis
    similarity_ranking = main(poi_file, toilet_file)
    
    # Print facility types with spatial distribution most similar to public restrooms
    print("Facility types with spatial distribution most similar to public restrooms:")
    for name, similarity in similarity_ranking:
        print(f"{name}: {similarity:.4f}")