import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def load_restroom_data(file_path):
    """
    加载公共厕所数据
    
    Args:
        file_path (str): CSV文件路径
    
    Returns:
        pandas.DataFrame: 加载的数据
    """
    df = pd.read_csv(file_path)
    return df

def create_restroom_map(data_path, center_lat=40.7128, center_lon=-74.0060, zoom=10, height=600):
    """
    创建公共厕所地图可视化，包括数据加载和分析
    
    Args:
        data_path (str): CSV文件路径
        center_lat (float): 地图中心纬度
        center_lon (float): 地图中心经度
        zoom (int): 地图缩放级别
        height (int): 地图高度
    
    Returns:
        plotly.graph_objects.Figure: 创建的地图图表
    """
    # 加载数据
    df = load_restroom_data(data_path)
    
    # 创建地图
    fig = px.scatter_mapbox(
        df, 
        lat="Latitude", 
        lon="Longitude",
        hover_name="Facility Name",
        hover_data={
            "Location Type": True,
            "Status": True,
            "Hours of Operation": False,
            "Accessibility": False,
            "Latitude": False,
            "Longitude": False
        },
        color="Status",
        color_discrete_map={
            "Operational": "#41b349",
            "Not Operational": "#f03752",
            "Closed":"#2d0c13",
            "Closed for Construction":"#fbc82f",
        },
        zoom=zoom,
        center={"lat": center_lat, "lon": center_lon},
        height=height
    )
    
    # 设置地图风格
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        # legend_title_text="厕所状态",
    )

    fig.update_layout(
        hoverlabel=dict(
            font_family="Georgia, Palatino, serif",
            font_size=12,
            # font_color= "#AE3737",
            # # bgcolor="white",
            # bordercolor="gray"
        )
    )

    
    # 添加响应式布局和交互控件
    fig.update_layout(
        autosize=True,
        hovermode='closest',
        # clickmode='event+select',
        dragmode='pan',
        showlegend=True,
    )

    fig.update_traces(marker=dict(size=5))  # 设置所有点大小为12像素
    
    return fig

def save_map_to_html(fig, output_file="nyc_public_restrooms_map.html"):
    """
    将地图保存为HTML文件
    """
    fig.write_html(
        output_file,         
        config={
            'scrollZoom': True,
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'responsive': True
        },
        include_plotlyjs='cdn'
    )
    

def main(data_path='./data/Public_Restrooms.csv'):
    """
    主函数，只调用创建地图和保存地图两个函数
    
    Args:
        data_path (str): 数据文件路径
    """
    # 创建地图
    fig = create_restroom_map(data_path)
    
    # 显示地图
    fig.show()
    
    # 保存地图
    save_map_to_html(fig)

# 如果作为主程序运行
if __name__ == "__main__":
    DATA_PATH = './data/Public_Restrooms.csv'
    main(DATA_PATH)