import pandas as pd
import plotly.graph_objects as go

from hexbin_ploty import create_pedastrain_intensity
from toilet_scatter import create_restroom_map

DATA_PATH = "./data/"

path_pedastrain = DATA_PATH + "Pedestrian_Mobility_Plan_Pedestrian_Demand_20250425.csv"
path_toilet = DATA_PATH + "Public_Restrooms.csv"

fig1 = create_pedastrain_intensity(path_pedastrain)
fig2 = create_restroom_map(path_toilet)

# 创建叠加图层
fig = go.Figure()

# 添加一个虚拟的trace用于控制行人强度图层
fig.add_trace(go.Scatter(
    x=[40.7128],  # 使用地图中心点的坐标
    y=[-74.0060],
    mode='markers',
    marker=dict(size=1, color='rgba(0,0,0,0)'),  # 完全透明
    name="Show <b>Pedastra intensity</b>",
    legendgroup="pedestrian",
    showlegend=True
))

# 添加fig1的所有trace到新图层(行人强度)
for trace in fig1.data:
    trace.name = "行人强度"  # 为图例添加名称
    trace.legendgroup = "pedestrian"  # 分组
    trace.showlegend = False  # 不在图例中显示
    fig.add_trace(trace)

# 添加fig2的所有trace到新图层(公共厕所)
for trace in fig2.data:
    fig.add_trace(trace)

# 更新布局，显示图例在左上角
fig.update_layout(
    mapbox=dict(
        center=dict(lat=40.7128, lon=-74.0060),  # NYC中心
        zoom=10,
        style="carto-positron"
    ),
    coloraxis=dict(
        colorscale='Viridis_r',
        showscale=False,  # 显示颜色条
        colorbar=dict(
            title="行人强度",
            x=0.01,  # 水平位置，靠左
            y=0.5,   # 垂直位置，中间
            xanchor="left",
            thickness=20,
            len=0.5   # 颜色条长度为图高的一半
        )
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    autosize=True,
    hovermode='closest',
    dragmode='zoom',
    showlegend=True,  # 显示图例
    legend=dict(
        x=0.01,  # 水平位置，靠左
        y=0.99,  # 垂直位置，靠上
        xanchor="left",  # 左对齐
        yanchor="top",   # 顶部对齐
        bgcolor="rgba(252, 245, 237, 0.5)",  # 半透明白色背景
        bordercolor="rgba(0, 0, 0, 0.5)",    # 边框颜色
        font=dict(
            family=" Georgia, Palatino, serif",
            size=12,
            color='rgba(147, 61, 63, 1)',  # 使用相同的颜色值
            weight="normal"
        ),
    ),
    # 明确隐藏x和y轴
    xaxis=dict(visible=False),
    yaxis=dict(visible=False)
)

fig.update_layout(
    hoverlabel=dict(
        font_family="Georgia, Palatino, serif",
        font_size=12,
    )
)

# 保存时确保启用滚轮缩放
fig.write_html(
    "nyc_scatter_hexbin.html",
    config={
        'scrollZoom': True,
        'displayModeBar': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'responsive': True
    },
    include_plotlyjs='cdn'
)

# 显示图层
# fig.show()