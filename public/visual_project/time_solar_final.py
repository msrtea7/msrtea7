import pandas as pd
import numpy as np
import re
import json
from collections import defaultdict

# 颜色映射
COLOR_MAP = {
    'NYC Parks': '#8BC34A',           # 绿色
    'NYPL': '#64B5F6',                # 蓝色
    'NYC Parks Concessionaire': '#FFB74D',  # 橙色
    'QPL': '#BA68C8',                 # 紫色
    'BPL': '#EF9A9A',                 # 红色
    'Others': '#90A4AE'               # 灰色
}

# 主要运营商列表
MAIN_OPERATORS = ['NYC Parks', 'NYPL', 'NYC Parks Concessionaire', 'QPL', 'BPL', 'Others']

# 星期列表
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def load_data(csv_file):
    """加载CSV数据"""
    return pd.read_csv(csv_file)

def parse_time_ranges(time_str):
    """解析时间范围字符串为小时列表"""
    if pd.isna(time_str) or time_str == 'CLOSED':
        return []
    
    if time_str == '24 HOURS':
        return list(range(24))
    
    hours = []
    time_ranges = time_str.split(',')
    
    for time_range in time_ranges:
        match = re.match(r'(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})', time_range.strip())
        if match:
            start_hour, start_min, end_hour, end_min = map(int, match.groups())
            
            # 转换为24小时制
            if 'PM' in time_range and start_hour < 12:
                start_hour += 12
            if 'PM' in time_range and end_hour < 12:
                end_hour += 12
            
            # 添加所有小时段
            current_hour = start_hour
            while current_hour != end_hour:
                hours.append(current_hour)
                current_hour = (current_hour + 1) % 24
    
    return hours

def categorize_operator(operator):
    """将运营商分类为主要类别或'Others'"""
    return operator if operator in MAIN_OPERATORS[:-1] else 'Others'

def calculate_hourly_counts(df, day):
    """计算指定日期每小时每个运营商的设施数量"""
    hourly_counts = {hour: defaultdict(list) for hour in range(24)}
    
    for _, row in df.iterrows():
        if pd.isna(row[day]) or row[day] == '':
            continue
            
        hours = parse_time_ranges(row[day])
        operator = categorize_operator(row['Operator'])
        
        for hour in hours:
            hourly_counts[hour][operator].append(row['Facility Name'])
    
    return hourly_counts

def calculate_global_max_count(df):
    """计算所有日期的全局最大计数"""
    global_max = 0
    
    for day in DAYS_OF_WEEK:
        hourly_counts = calculate_hourly_counts(df, day)
        
        # 计算AM和PM的最大值，然后取全局最大值
        am_max = max(sum(len(hourly_counts[h][op]) for op in hourly_counts[h]) for h in range(12))
        pm_max = max(sum(len(hourly_counts[h][op]) for op in hourly_counts[h]) for h in range(12, 24))
        day_max = max(am_max, pm_max)
        
        global_max = max(global_max, day_max)
    
    return global_max

def generate_all_days_data(df):
    """生成所有日期的数据（用于客户端渲染）"""
    global_max_count = calculate_global_max_count(df)
    all_data = {"global_max_count": global_max_count}
    
    for day in DAYS_OF_WEEK:
        hourly_counts = calculate_hourly_counts(df, day)
        
        day_data = {
            "day": day,
            "hourly_data": {}
        }
        
        for hour in range(24):
            operators_data = {}
            for operator, facilities in hourly_counts[hour].items():
                operators_data[operator] = {
                    "count": len(facilities),
                    "facilities": facilities
                }
            day_data["hourly_data"][hour] = operators_data
            
        all_data[day] = day_data
    
    return all_data

def create_nyc_bathroom_visualization(csv_file='./data/Public_Restrooms_time.csv'):
    """主函数，创建NYC浴室可视化"""
    # 加载数据
    df = load_data(csv_file)
    
    # 生成所有日期的数据
    all_data = generate_all_days_data(df)
    all_data_json = json.dumps(all_data)
    
    # 生成HTML内容
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NYC Public Bathroom Hours</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: "Georgia, Palatino, serif";
                margin: 0;
                background-color: transparent;
            }}
            .container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                max-width: 1200px;
                background-color: #FCF5ED;
            }}
            h1 {{
                color: #333;
                text-align: center;
                margin-bottom: 20px;
            }}
            .subtitle {{
                text-align: center;
                color: #666;
                margin-top: -10px;
                margin-bottom: 20px;
            }}
            .day-selector {{
                margin: 20px 0;
                text-align: center;
                width: 100%;
            }}
            select {{
                padding: 10px 15px;
                font-size: 12px;
                font-family: "Georgia, Palatino, serif";
                border-radius: 4px;
                border: 1px solid #ccc;
                background-color: white;
                cursor: pointer;
                min-width: 100px;
            }}
            select:focus {{
                outline: none;
                border-color: #4a90e2;
                box-shadow: 0 0 5px rgba(74,144,226,0.5);
            }}
            label[for="day-select"] {{
                font-family: "Georgia, Palatino, serif";
                font-size: 14px;
                font-weight: 500;
                color: #333;
                margin-right: 10px;
            }}
            #chart-container {{
                width: 100%;
                position: relative;
                height: 600px;
            }}
            .subplot-title {{
                font-family: "Georgia, Palatino, serif";
                font-size: 16px;
                font-weight: 600;
                text-align: center;
                color: #333;
                margin-bottom: 5px;
                position: absolute;
                width: 100%;
                top: 10px;
                z-index: 10;
            }}
            .am-title {{
                left: 0;
                width: 50%;
            }}
            .pm-title {{
                right: 0;
                width: 50%;
            }}
            .legend-note {{
                margin-top: 20px;
                text-align: center;
                font-size: 14px;
                color: #666;
            }}
            #chart {{
                width: 100%;
                height: 100%;
            }}
            
            
        </style>
    </head>
    <body>
        <div class="container">
            <div id="chart-container">
                <div id="chart"></div>
            </div>
            
            <div class="day-selector">
                <label for="day-select">Select Day: </label>
                <select id="day-select">
                    {"".join([f'<option value="{day}">{day}</option>' for day in DAYS_OF_WEEK])}
                </select>
            </div>
        </div>
        
        <script>
            // 存储所有图表数据
            const allData = {all_data_json};
            
            // 运营商颜色
            const operatorColors = {json.dumps(COLOR_MAP)};
            
            // 主要运营商
            const mainOperators = {json.dumps(MAIN_OPERATORS)};
            
            // 获取DOM元素
            const daySelect = document.getElementById('day-select');
            const chartDiv = document.getElementById('chart');
            
            // 检查设备是否为移动设备
            function isMobile() {{
                return window.innerWidth <= 768;
            }}
            
            // 获取极坐标图配置
            function getPolarConfig(period, globalMaxCount) {{
                return {{
                    hole: 0.05,
                    radialaxis: {{
                        showticklabels: false,
                        visible: false,
                        range: [0, globalMaxCount * 1.1],
                        showline: false,
                        showgrid: false,
                    }},
                    angularaxis: {{
                        showline: false,
                        showgrid: false,
                        ticks: "",
                        ticklen: 5,
                        direction: "clockwise",
                        period: 12,
                        tickmode: "array",
                        tickvals: [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
                        ticktext: period === 'AM' ? 
                                 ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'] : 
                                 ['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23'],
                        tickfont: {{ size: 18,  family: "Georgia, Palatino, serif", }}
                    }},
                    bgcolor: "rgba(0,0,0,0)",
                }};
            }}
            
            // 根据屏幕尺寸更新布局
            function updateResponsiveLayout(layout) {{
                const mobile = isMobile();
                
                if (mobile) {{
                    // 移动设备布局 - 上下排列
                    layout.grid = {{
                        rows: 2,
                        columns: 1,
                        pattern: 'independent',
                        roworder: 'top to bottom'
                    }};
                    layout.height = 900;
                    
                    // 更新极坐标域
                    layout.polar.domain = {{
                        x: [0.1, 0.9],
                        y: [0.55, 0.95]
                    }};
                    layout.polar2.domain = {{
                        x: [0.55, 1],
                        y: [0, 1]
                    }};
                }} else {{
                    // 桌面布局 - 左右排列
                    layout.grid = {{
                        rows: 1,
                        columns: 2,
                        pattern: 'independent'
                    }};
                    layout.height = 600;
                    
                    // 更新极坐标域
                    layout.polar.domain = {{
                        x: [0, 0.43],
                        y: [0, 1]
                    }};
                    layout.polar2.domain = {{
                        x: [0.57, 1],
                        y: [0, 1]
                    }};
                }}
                
                return layout;
            }}
            
            // 根据数据创建图表
            function createChart(dayData) {{
                const day = dayData.day;
                const hourlyData = dayData.hourly_data;
                
                // AM和PM小时
                const amHours = Array.from({{length: 12}}, (_, i) => i);
                const pmHours = Array.from({{length: 12}}, (_, i) => i + 12);
                
                // 使用全局最大计数进行缩放
                const globalMaxCount = allData.global_max_count;
                
                // 准备图表数据结构
                const traces = [];
                
                // 为每个时段（AM/PM）为每个运营商创建堆叠数据
                ['AM', 'PM'].forEach((period, periodIdx) => {{
                    const hours = period === 'AM' ? amHours : pmHours;
                    const subplot = period === 'AM' ? 'polar' : 'polar2';
                    
                    // 调整角度以匹配时钟布局
                    const theta = hours.map(hour => 
                        ((period === 'AM' ? hour : hour - 12) * 30) + 15
                    );
                    
                    // 准备堆叠数据
                    const cumulativeR = {{}};
                    hours.forEach(hour => {{ cumulativeR[hour] = 0; }});
                    
                    // 为每个运营商创建一个trace
                    mainOperators.forEach(operator => {{
                        const rValues = [];
                        const textValues = [];
                        
                        hours.forEach(hour => {{
                            const operatorData = (hourlyData[hour] || {{}})[operator] || {{ count: 0, facilities: [] }};
                            const count = operatorData.count;
                            const facilities = operatorData.facilities;
                            
                            rValues.push(count);
                            
                            // 准备悬浮文本
                            let facilityNames = facilities.slice(0, 5).join('<br>');
                            if (facilities.length > 5) {{
                                facilityNames += `<br>...and ${{facilities.length - 5}} more`;
                            }}
                            
                            let text = `Hour: ${{hour}}:00-${{(hour+1) % 24}}:00<br>Operator: ${{operator}}<br>Count: ${{count}}`;
                            if (count < 0) {{
                                text += `<br><br>Facilities:<br>${{facilityNames}}`;
                            }}
                            textValues.push(text);
                        }});
                        
                        // 创建基础值用于堆叠
                        const baseValues = hours.map(hour => cumulativeR[hour]);
                        
                        // 添加trace
                        traces.push({{
                            width: 30,
                            type: 'barpolar',
                            r: rValues,
                            theta: theta,
                            base: baseValues,
                            name: operator,
                            marker: {{color: operatorColors[operator]}},
                            hoverinfo: 'text',
                            hovertext: textValues,
                            showlegend: periodIdx === 0, // 只在第一个时段显示图例
                            subplot: subplot,
                            legendgroup: operator // 在图例中链接AM和PM的trace
                        }});
                        
                        // 更新累积高度
                        hours.forEach((hour, i) => {{
                            cumulativeR[hour] += rValues[i];
                        }});
                    }});
                }});
                
                // 创建布局
                const layout = {{
                    font: {{
                        family: "Georgia, Palatino, serif",
                    }},
                    hoverlabel:{{
                        font: {{
                            family: "Georgia, Palatino, serif",
                        }},
                    }},
                    polar: getPolarConfig('AM', globalMaxCount),
                    polar2: getPolarConfig('PM', globalMaxCount),
                    showlegend: true,
                    paper_bgcolor: "rgba(0,0,0,0)",
                    plot_bgcolor: "rgba(0,0,0,0)",
                    // 添加悬浮标签样式
                    legend: {{
                        orientation: "h",
                        yanchor: "top",
                        y: -0.15,
                        xanchor: "center",
                        x: 0.5,
                        font: {{
                            family: "Georgia, Palatino, serif",
                            size: 12,
                        }},
                    }},
                    margin: {{t: 45, b: 50}},
                    height: 600,
                    uirevision: 'true' // 维持图例状态
                }};
                
                // 应用响应式布局
                const updatedLayout = updateResponsiveLayout(layout);
                
                // 清除旧图表并创建新图表
                Plotly.react(chartDiv, traces, updatedLayout, {{
                    displayModeBar: false, // 隐藏模式栏以获得更简洁的外观
                    responsive: false,
                    autosize: true,
                }});
            }}
            
            // 响应日期选择变化的处理函数
            function updateChart() {{
                const selectedDay = daySelect.value;
                const dayData = allData[selectedDay];
                
                if (dayData) {{
                    createChart(dayData);
                }}
            }}
            
            // 页面加载时设置事件监听器
            document.addEventListener('DOMContentLoaded', function() {{
                // 添加日期选择器事件监听器
                daySelect.addEventListener('change', updateChart);
                
                // 添加窗口大小变化监听器
                window.addEventListener('resize', function() {{
                    const selectedDay = daySelect.value;
                    const dayData = allData[selectedDay];
                    if (dayData) {{
                        createChart(dayData);
                    }}
                }});
                
                // 初始化图表 - 使用当前选中的日期
                const selectedDay = daySelect.value;
                const dayData = allData[selectedDay];
                if (dayData) {{
                    createChart(dayData);
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # 保存为HTML文件
    with open('nyc_clock.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Visualization saved as 'nyc_clock.html'")
    return html_content

# 运行代码
if __name__ == "__main__":
    create_nyc_bathroom_visualization()