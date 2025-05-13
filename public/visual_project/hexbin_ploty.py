import pandas as pd
import geopandas as gpd
from shapely import wkt
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
from shapely.geometry import Point, LineString, MultiLineString, Polygon
import h3
import json
from shapely.ops import transform
import pyproj
from functools import partial


def load_data(file_path):
    """加载CSV数据并处理地理信息"""
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 将WKT格式转换为Shapely几何对象
    df['geometry'] = df['the_geom'].apply(wkt.loads)
    
    # 创建GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    
    # 计算每条街道的长度(米)
    gdf['length_m'] = gdf.to_crs(epsg=3857).geometry.length
    
    return gdf


def extract_points_from_linestrings(gdf):
    """
    从线数据中提取点，用于生成Hexbin地图
    每段线按长度比例提取点，确保长线段贡献更多点
    
    Args:
        gdf: 包含线数据的GeoDataFrame
        
    Returns:
        DataFrame: 包含提取的点及其对应的强度值
    """
    points = []
    
    for idx, row in gdf.iterrows():
        # 反转Rank值，使较小的Rank对应较高的强度
        intensity = 6 - row['Rank']  # 将0-5的范围转换为6-1
        
        geom = row.geometry
        # 根据长度确定从这条线上提取的点数
        # 长度越长，提取的点越多，增加其权重
        n_points = max(3, int(row['length_m'] / 50))  # 每50米提取一个点，最少3个点
        
        if isinstance(geom, MultiLineString):
            for line in geom.geoms:
                # 从线上均匀采样点
                for i in range(n_points):
                    point = line.interpolate(i / (n_points - 1), normalized=True)
                    points.append({
                        'lon': point.x,
                        'lat': point.y,
                        'intensity': intensity,
                        'street_id': row['segmentid']
                    })
        else:
            # 从线上均匀采样点
            for i in range(n_points):
                point = geom.interpolate(i / (n_points - 1), normalized=True)
                points.append({
                    'lon': point.x,
                    'lat': point.y,
                    'intensity': intensity,
                    'street_id': row['segmentid']
                })
    
    return pd.DataFrame(points)


def create_hexbin_mapbox(points_df, center=None, zoom=10, hex_size=45, 
                         mapbox_token=None, style='carto-positron'):
    """
    创建交互式Plotly Hexbin地图
    
    Args:
        points_df: 包含点数据的DataFrame (必须包含'lat', 'lon', 'intensity'列)
        center: 地图中心点 [lat, lon]
        zoom: 初始缩放级别
        hex_size: 六边形大小
        mapbox_token: Mapbox访问令牌(可选)
        style: 地图样式
        
    Returns:
        plotly.graph_objects.Figure: Plotly图形对象
    """
    if center is None:
        # 默认以数据中心为地图中心
        center = {
            'lat': points_df['lat'].mean(),
            'lon': points_df['lon'].mean()
        }
    
    # 创建六边形分箱地图
    fig = ff.create_hexbin_mapbox(
        data_frame=points_df, 
        lat='lat', 
        lon='lon',
        color='intensity',
        nx_hexagon=hex_size,
        opacity=0.2,
        labels={'color': 'Intensity'},  # Changed from '行人强度' to 'Intensity'
        color_continuous_scale='Viridis_r',  # 'Plasma', 'Inferno', 'Magma', 'Cividis'
        mapbox_style=style,
        min_count=1,  # 最少需要1个点才显示六边形
        show_original_data=False,  # 不显示原始点
        original_data_marker=dict(opacity=0.1, size=2, color='black'),
        center=center,
        zoom=zoom,
    )

    # 设置图布局
    fig.update_layout(
        # title='NYC 人行道强度地图',
        autosize=True,
        height=800,
        margin=dict(t=50, b=0, l=0, r=0),
        mapbox=dict(
            accesstoken=mapbox_token,
            style=style
        ),
        showlegend=True,
        hoverlabel=dict(
            font_family="Georgia, Palatino, serif"  # Added custom font for hover tooltip
        )
    )
    fig.update_layout(
        hoverlabel=dict(
            font_family="Georgia, Palatino, serif",  # 已添加的字体设置
            bgcolor="white",     # 设置背景颜色
            bordercolor="black", # 设置边框颜色
            font_color="black"   # 设置文本颜色
        )
    )

    # 添加悬停提示 - 注意这里保留了原本的格式但应用了自定义字体
    fig.update_traces(
        hovertemplate='<b>Intensity</b>: %{z:.2f}<br><extra></extra>'
    )

    return fig


def create_h3_hexbin(gdf, resolution=9):
    """
    使用H3索引系统创建高精度六边形地图
    
    Args:
        gdf: 包含街道数据的GeoDataFrame
        resolution: H3索引的分辨率(7-10)
        
    Returns:
        GeoDataFrame: 包含六边形及其强度值的GeoDataFrame
    """
    # 提取所有点
    points_df = extract_points_from_linestrings(gdf)
    
    # 为每个点创建H3索引
    points_df['h3_index'] = points_df.apply(
        lambda row: h3.geo_to_h3(row['lat'], row['lon'], resolution), 
        axis=1
    )
    
    # 按H3索引分组并计算平均强度
    hex_data = points_df.groupby('h3_index').agg({
        'intensity': 'mean',
        'street_id': 'count',
        'lat': 'mean',
        'lon': 'mean'
    }).reset_index()
    
    hex_data.rename(columns={'street_id': 'point_count'}, inplace=True)
    
    # 将H3索引转换为六边形几何
    hex_data['geometry'] = hex_data['h3_index'].apply(
        lambda h: Polygon(h3.h3_to_geo_boundary(h, geo_json=True))
    )
    
    # 创建GeoDataFrame
    hex_gdf = gpd.GeoDataFrame(hex_data, geometry='geometry', crs='EPSG:4326')
    
    return hex_gdf


def create_pedastrain_intensity(file_path, resolution=9, hex_size=30):
    """
    主函数：加载数据并生成交互式地图
    
    Args:
        file_path: CSV文件路径
        resolution: H3分辨率 (可选)
        hex_size: Plotly六边形大小 (可选)
        
    Returns:
        plotly.graph_objects.Figure: 交互式地图
    """
    # 加载数据
    print("正在加载数据...")
    gdf = load_data(file_path)
    print(f"加载了 {len(gdf)} 条街道记录")
    
    # 提取点
    print("处理几何数据...")
    points_df = extract_points_from_linestrings(gdf)
    print(f"从线段中提取了 {len(points_df)} 个点")
    
    # 创建Hexbin地图
    print("创建交互式地图...")
    fig = create_hexbin_mapbox(
        points_df,
        center={'lat': 40.7128, 'lon': -74.0060},  # NYC中心
        zoom=10,
        hex_size=hex_size
    )

    fig.update_traces(marker=dict(line=dict(width=0)))
    fig.update_layout(coloraxis_showscale=False)

    
    return fig


def save_and_show_map(fig, output_file='nyc_sidewalk_intensity_hexbin.html'):
    """保存并显示地图"""
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
    print(f"地图已保存到 {output_file}")
    return fig

# 保存时确保启用滚轮缩放

if __name__ == "__main__":
    # 替换为你的数据文件路径
    DATA_PATH = "./data/"
    file_path = DATA_PATH + "Pedestrian_Mobility_Plan_Pedestrian_Demand_20250425.csv"
    
    # 创建地图
    fig = create_pedastrain_intensity(file_path, hex_size=45)
    
    # 保存并显示地图
    save_and_show_map(fig)
    
    print("NYC人行道强度Hexbin地图已成功创建！")