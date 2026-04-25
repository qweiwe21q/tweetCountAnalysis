import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime, timedelta

# file_name = "WhiteHouse-White_House___posts_April_21___April_28__2026_-tweets.csv"
# file_name = "WhiteHouse-White_House___posts_April_17___April_24__2026_-tweets.csv"
file_name = "elonmusk-Elon_Musk___tweets_April_21___April_28__2026_-tweets.csv"

# ^ 表示从字符串开头开始匹配
# ([^-]+) 表示匹配直到遇到第一个连字符 - 为止的所有字符
match = re.search(r'^([^-]+)', file_name)

if match:
    # 设置网页标题
    user_name = match.group(1)
    st.set_page_config(page_title=f"{user_name}推文数据分析", layout="wide")
    st.title(f"🏛️ {user_name} 社交媒体监控大屏")

# 加载数据
@st.cache_data
def load_data():
    df = pd.read_csv(file_name)
    df['Posted At (EST)'] = pd.to_datetime(df['Posted At (EST)'])

    df['full_time_str'] = df['Posted Date'].astype(str) + ' ' + df['Posted At (EST)'].astype(str)
    df['dt'] = pd.to_datetime(df['full_time_str'], errors='coerce')

    # df['dt'] = pd.to_datetime(df['Posted At (EST)'])
    # 提取日期字符串（用于行索引）
    df['Date'] = df['Posted At (EST)'].dt.date

    # 提取小时（用于列索引）


    df['Date_line'] = df['dt'].dt.strftime('%Y-%m-%d')

    df['Hour'] = df['dt'].dt.hour
    return df

df = load_data()

def get_range_from_filename(name):
    # 正则表达式匹配类似 April_17 和 April_24 的字段
    dates = re.findall(r'([A-Z][a-z]+_\d{1,2})', name)
    if len(dates) >= 2:
        # 将字符串转为日期对象（假设年份为 2026）
        start_dt = datetime.strptime(f"{dates[0]}_2026", "%B_%d_%Y").date()
        end_dt = datetime.strptime(f"{dates[1]}_2026", "%B_%d_%Y").date()
        return start_dt, end_dt
    return None, None

start_date, end_date = get_range_from_filename(file_name)

# --- 2. 构建完整的日期占位列表 ---
if start_date and end_date:
    # 计算总天数（包含结束当天）
    total_days = (end_date - start_date).days + 1
    fixed_dates = [start_date + timedelta(days=i) for i in range(total_days)]
    full_range_df = pd.DataFrame({'Date': fixed_dates})
else:
    st.error("文件名格式不对，无法提取日期")
    st.stop()


# --- 第一排：核心指标 ---
col1, col3 = st.columns(2)
col1.metric("总推文数", len(df))
col3.metric("统计周期", f"{start_date} - {end_date}")


# 统计实际发帖
daily_stats = df.groupby('Date').size().reset_index(name='Tweet_Count')

# 合并：确保文件名里的每一天在图表里都有位置
final_df = pd.merge(full_range_df, daily_stats, on='Date', how='left').fillna(0)

# --- 4. 绘图展示 ---
fig = px.bar(
    final_df,
    x='Date',
    y='Tweet_Count',
    title=f"Activity Monitor: {start_date} to {end_date}",
    text_auto=True,
    color='Tweet_Count', # 根据数量深浅变色
    color_continuous_scale='Blues',  # 使用蓝色系
)


# 强制 X 轴按顺序显示所有日期标签
fig.update_xaxes(type='category', tickformat='%b %d',
                 )
fig.update_layout(
    xaxis=dict(fixedrange=True),      # 锁定横轴，禁止鼠标拖动或缩放
    yaxis=dict(fixedrange=True),      # 锁定纵轴，禁止鼠标拖动或缩放
    dragmode=False                    # 彻底关闭拖拽模式
)
st.plotly_chart(fig, width="stretch",
                config={'displayModeBar': False})



# ==========================================

# 第二部分

# --- 3. 7x24 矩阵逻辑补充 ---
def get_heatmap_data(df, start_date, end_date):
    # 构建完整的时间轴范围
    total_days = (end_date - start_date).days + 1
    all_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(total_days)]

    # 基础统计
    stats = df.groupby(['Date_line', 'Hour']).size().unstack(fill_value=0)

    # 补充缺失的日期行
    stats = stats.reindex(all_dates, fill_value=0)

    # 补充缺失的小时列 (0-23)
    for h in range(24):
        if h not in stats.columns:
            stats[h] = 0

    # 排序：行按日期，列按 0-23 小时
    stats = stats.reindex(columns=sorted(stats.columns))
    return stats


heatmap_df = get_heatmap_data(df, start_date, end_date)

# --- 1. 计算边际总量 ---
# 计算每一天的总和 (放在最右侧)
heatmap_df['Total'] = heatmap_df.sum(axis=1)

# 计算每个小时的总和 (准备放在最下面或最上面)
hourly_total = heatmap_df.iloc[:, :-1].sum(axis=0) # 排除刚加的 Total 列
hourly_total_row = pd.DataFrame(hourly_total).T
hourly_total_row.index = ['TOTAL']
hourly_total_row['Total'] = hourly_total.sum() # 总计的总计

# 将总量行拼接到矩阵下方 (可选，如果你想让它像 Excel 一样显示)
heatmap_with_total = pd.concat([heatmap_df, hourly_total_row])

# A. 顶部：小时总活跃度 (柱状图占位)
st.subheader("🔥 每小时发帖总强度 (All Week)")
fig_top = px.bar(
    x=[f"{h}:00" for h in range(24)],
    y=hourly_total.values,
    text_auto=True,
    color_discrete_sequence=['#1e293b']
)

fig_top.update_layout(height=150, margin=dict(l=0, r=50, t=10, b=0), xaxis_title=None, yaxis_title=None)
st.plotly_chart(fig_top, use_container_width=True, config={'displayModeBar': False})


# B. 中间：热力图矩阵 (右侧自带 Total 列)
st.subheader("🗓️ 7x24 活跃分布 (带日总量)")

# 为了让 Total 列看起来更显眼，我们可以给最后一列换个色标或者加个特殊标注
fig_heat = px.imshow(
    heatmap_df,
    labels=dict(x="Hour & Daily Total", y="Date", color="Posts"),
    x=[f"{h}:00" for h in range(24)] + ["【TOTAL】"], # X轴增加一列
    y=heatmap_df.index,
    color_continuous_scale='Blues',
    text_auto=True,
    aspect="auto"
)

# 锁定缩放并隐藏工具栏
fig_heat.update_layout(
    xaxis=dict(fixedrange=True),
    yaxis=dict(fixedrange=True),
    dragmode=False,
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})



