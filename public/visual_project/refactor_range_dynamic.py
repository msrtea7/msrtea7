import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import re

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

def meters_to_pixels_for_plotly(lat, radius_meters):
    """
    计算在Plotly地图上，给定纬度和半径(米)对应的像素大小
    
    Args:
        lat (float): 纬度
        radius_meters (float): 半径(米)
    
    Returns:
        float: Plotly标记大小
    """
    # 纬度调整因子 - 纬度越高，经度方向的缩放越大
    lat_factor = 1 / np.cos(np.radians(abs(lat)))
    
    # 将米转换为Plotly的marker.size
    # 这里使用经验比例因子，可以根据视觉效果调整
    scale_factor = 20
    
    # 应用纬度调整和比例转换
    marker_size = (radius_meters / scale_factor) * np.sqrt(lat_factor)
    
    return marker_size

def create_restroom_map_with_coverage(data_path, initial_radius=500, min_radius=300, max_radius=1000, radius_step=100, center_lat=40.7128, center_lon=-74.0060, zoom=10, height=600):
    """
    创建公共厕所地图可视化，包括数据加载、分析和覆盖半径
    
    Args:
        data_path (str): CSV文件路径
        initial_radius (int): 初始覆盖半径(米)
        min_radius (int): 最小覆盖半径值(米)
        max_radius (int): 最大覆盖半径值(米)
        radius_step (int): 半径滑块的步长(米)
        center_lat (float): 地图中心纬度
        center_lon (float): 地图中心经度
        zoom (int): 地图缩放级别
        height (int): 地图高度
    
    Returns:
        plotly.graph_objects.Figure: 创建的地图图表
    """
    # 加载数据
    df = load_restroom_data(data_path)
    
    # 创建基础地图 - 首先只包含厕所点位
    fig = px.scatter_mapbox(
        df, 
        lat="Latitude", 
        lon="Longitude",
        hover_name="Facility Name",
        hover_data={
            "Location Type": True,
            "Status": True,
            "Hours of Operation": False,
            "Accessibility": True,
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
        # height=height
    )
    
    # 设置地图风格
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},  # 修改顶部和底部间距以容纳滑块
    )
    
    # 设置点的大小
    fig.update_traces(marker=dict(size=5))
    
    # 计算平均纬度，用于半径转换
    avg_lat = df["Latitude"].mean()
    
    # 计算覆盖半径对应的标记大小
    marker_size = meters_to_pixels_for_plotly(avg_lat, initial_radius)
    
    # 添加半透明圆形覆盖区域作为新的图层
    fig.add_trace(
        go.Scattermapbox(
            lat=df["Latitude"],
            lon=df["Longitude"],
            mode="markers",
            marker=dict(
                size=marker_size,  # 使用计算出的半径大小
                color="rgba(92, 30, 25, 0.5)",  
                opacity=0.5,
            ),
            name=f"覆盖范围 ({initial_radius}米)",
            showlegend=False,
            hoverinfo="none",  # 禁用悬停显示以避免与原始点重复
        )
    )
    
    # 创建滑块范围的数值列表
    radius_values = list(range(min_radius, max_radius + 1, radius_step))
    
    # 这个是用于显示的
    label_radius_values = [300, 500, 700, 900]
    # 创建适用于静态HTML的滑块
    sliders = [dict(
        active=radius_values.index(initial_radius) if initial_radius in radius_values else 0,  # 默认滑块位置
        currentvalue={"prefix": "Range: ", "suffix": " meters", "visible": True, "font": {"size": 12, "color": "#933D3F"},},
        pad={"t": 5, "l": 5},  # 减少顶部填充，增加左侧填充
        len=0.2,  # 滑块长度，0-1之间，1为全宽
        x=0.01,   # 滑块左侧位置，0-1之间
        y=0.98,   # 滑块顶部位置，0-1之间
        yanchor="top",  # 顶部对齐
        xanchor="left", # 左侧对齐

        font={ "family": "Georgia, Palatino, serif", "color": "#933D3F", "size": 10},
        bordercolor="#933D3F",
        activebgcolor="#933D3F",

        steps=[
            dict(
                method="restyle",
                args=[
                    {"marker.size": meters_to_pixels_for_plotly(avg_lat, radius)},
                    [4]  # 只更新第二个轨迹(覆盖圆)的marker.size
                ],
                # label=str(radius) if radius in label_radius_values else "",
                label=f"{radius}m",
                value=radius,
            ) for radius in radius_values
        ]
    )]
    
    # 更新布局以包含滑块
    fig.update_layout(
        sliders=sliders,
        # title=f"NYC公共厕所分布图 (覆盖半径: {initial_radius}米)",
        autosize=True,
        hovermode='closest',
        clickmode='event+select',
        dragmode='pan',
        showlegend=False,
    )
    
    return fig

def save_map_to_html(fig, output_file="nyc_coverage.html", initial_zoom=10, initial_radius=500):
    """
    将地图保存为HTML文件，并添加缩放调整脚本
    
    Args:
        fig (plotly.graph_objects.Figure): 地图图表
        output_file (str): 输出HTML文件名
        initial_zoom (int): 初始缩放级别
        initial_radius (int): 初始覆盖半径(米)
    """
    # 生成基本HTML
    html_string = fig.to_html(
        config={
            'scrollZoom': True,
            'displayModeBar': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'responsive': True
        },
        include_plotlyjs='cdn'
    )
    
    # 注入缩放调整脚本
    zoom_adjust_script = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var myPlot = document.getElementById('CHART_ID');
        var initialZoom = INITIAL_ZOOM; // 初始缩放级别
        var initialRadius = INITIAL_RADIUS; // 初始半径(米)
        var currentRadius = initialRadius; // 当前半径
        var currentZoom = initialZoom; // 当前缩放级别
        
        // 添加说明标签
        var infoDiv = document.createElement('div');
        infoDiv.style.position = 'absolute';
        // infoDiv.style.top = '80px';
        infoDiv.style.right = '10px';
        infoDiv.style.backgroundColor = 'transparent';
        infoDiv.style.padding = '5px';
        infoDiv.style.borderRadius = '5px';
        infoDiv.style.zIndex = '1000';
        infoDiv.style.maxWidth = '200px';

        infoDiv.style.fontFamily = 'Georgia, Palatino, serif'; // 设置字体
        infoDiv.style.fontSize = '12px';               // 字体大小
        // infoDiv.style.fontWeight = 'bold';             // 加粗文字
        infoDiv.style.color = '#933D3F';               // 文字颜色

        infoDiv.style.top = '20.5%'; 
        infoDiv.style.left = '2%';

        infoDiv.innerHTML = 'Current Radius: ' + initialRadius + 'meters<br>Zoom Lebel: 10';
        document.body.appendChild(infoDiv);
        
        // 辅助函数：计算地图缩放级别下的实际像素尺寸
        function calculateMarkerSize(radiusMeters, zoom) {
            // 基于NYC的平均纬度计算
            var avgLat = 40.7128;
            var latFactor = 1 / Math.cos(avgLat * Math.PI / 180);
            
            // 不同缩放级别下的缩放比例
            var zoomFactor = Math.pow(2, zoom - initialZoom);
            
            // 基础缩放因子
            var scaleFactor = 20;
            
            // 计算最终大小
            return (radiusMeters / scaleFactor) * Math.sqrt(latFactor) * zoomFactor;
        }
        
        // 辅助函数：计算地图缩放级别下的实际像素尺寸
        function calculateMarkerSize(radiusMeters, zoom) {
            // 基于NYC的平均纬度计算
            var avgLat = 40.7128;
            var latFactor = 1 / Math.cos(avgLat * Math.PI / 180);
            
            // 不同缩放级别下的缩放比例
            var zoomFactor = Math.pow(2, zoom - initialZoom);
            
            // 基础缩放因子
            var scaleFactor = 20;
            
            // 计算最终大小
            return (radiusMeters / scaleFactor) * Math.sqrt(latFactor) * zoomFactor;
        }
        
        // 监听地图缩放和移动事件
        if (myPlot) {
            myPlot.on('plotly_relayout', function(eventData) {
                // 检查是否发生了缩放
                if (eventData['mapbox.zoom'] !== undefined) {
                    var newZoom = eventData['mapbox.zoom'];
                    
                    // 计算新的marker大小
                    var newSize = calculateMarkerSize(currentRadius, newZoom);
                    
                    // 更新覆盖圆的大小
                    Plotly.restyle(myPlot, {'marker.size': newSize}, [4]);
                    
                    // 更新当前缩放级别
                    currentZoom = newZoom;
                    
                    // 更新信息框
                    infoDiv.innerHTML = 'Current Radius: ' + currentRadius + ' meters<br>Zoom Level: ' + newZoom.toFixed(1);
                }
            });
            
            // 监听滑块变化，更新当前半径
            myPlot.on('plotly_sliderchange', function(e) {
                // 直接从事件获取滑块值
                if (e && e.step !== undefined && e.step.value !== undefined) {
                    currentRadius = parseInt(e.step.value);
                    
                    // 更新信息框
                    infoDiv.innerHTML = 'Current Radius: ' + currentRadius + ' meters<br>Zoom Level: ' + currentZoom.toFixed(1);
                    
                    // 可选：根据新半径和当前缩放级别更新marker大小
                    var newSize = calculateMarkerSize(currentRadius, currentZoom);
                    Plotly.restyle(myPlot, {'marker.size': newSize}, [4]);
                }
            });
        }
    });
    </script>
    """
    
    
    # 替换图表ID和初始值
    div_id = re.search(r'id="([^"]*)"', html_string).group(1)
    zoom_adjust_script = zoom_adjust_script.replace('CHART_ID', div_id)
    zoom_adjust_script = zoom_adjust_script.replace('INITIAL_ZOOM', str(initial_zoom))
    zoom_adjust_script = zoom_adjust_script.replace('INITIAL_RADIUS', str(initial_radius))
    
    # 在</body>前插入脚本
    html_string = html_string.replace('</body>', zoom_adjust_script + '</body>')
    
    # 写入文件
    with open(output_file, 'w') as f:
        f.write(
            html_string,
        )

def main(data_path='./data/Public_Restrooms.csv'):
    """
    主函数
    
    Args:
        data_path (str): 数据文件路径
    """
    # 设置初始参数
    initial_radius = 300  # 初始半径为500米
    initial_zoom = 10     # 初始缩放级别
    
    # 创建带覆盖半径的地图
    fig = create_restroom_map_with_coverage(
        data_path,
        initial_radius=initial_radius,
        min_radius=300,       # 最小半径为300米
        max_radius=900,      # 最大半径为900米
        radius_step=50,      # 滑块步长为200米
        zoom=initial_zoom     # 设置初始缩放级别
    )
    
    # 显示地图
    fig.show()
    
    # 保存地图，并传入初始缩放级别和半径值用于JavaScript
    save_map_to_html(fig, initial_zoom=initial_zoom, initial_radius=initial_radius)

# 如果作为主程序运行
if __name__ == "__main__":
    DATA_PATH = './data/Public_Restrooms.csv'
    main(DATA_PATH)