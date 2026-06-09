import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime, timedelta
import DateUtils,TweetsNumber

# file_name = "elonmusk-Elon_Musk___tweets_May_19___May_26__2026_-tweets.csv"
# file_name = "elonmusk-Elon_Musk___tweets_May_22___May_29__2026_-tweets.csv"
file_name = "elonmusk-Elon_Musk___tweets_June_2___June_9__2026_-tweets.csv"
# file_name = "WhiteHouse-White_House___posts_June_2___June_9__2026_-tweets.csv"

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

    # ==================== 这里修改时间（核心） ====================
    df['dt'] = df['dt'] - pd.Timedelta(hours=12)
    df['Date'] = df['Posted At (EST)'].dt.date


    df['Date_line'] = df['dt'].dt.strftime('%Y-%m-%d')

    df['Hour'] = df['dt'].dt.hour
    return df

df = load_data()


# 设置开始时间和结束时间
def extract_dates_as_datetime(filename):
    pattern = r"(?:posts|tweets)_(\w+)_(\d+)_+_(\w+)_(\d+)_+(\d{4})"
    match = re.search(pattern, filename)

    if not match:
        return None, None

    start_month = match.group(1)
    start_day = int(match.group(2))
    end_month = match.group(3)
    end_day = int(match.group(4))
    year = int(match.group(5))

    # 转换为 datetime 对象
    start_date = datetime.strptime(f"{start_month} {start_day} {year}", "%B %d %Y")
    end_date = datetime.strptime(f"{end_month} {end_day} {year}", "%B %d %Y")

    return start_date.date(), end_date.date()

start_date, end_date = extract_dates_as_datetime(file_name)

# --- 2. 构建完整的日期占位列表 ---
if start_date and end_date:
    # 计算总天数（包含结束当天）
    total_days = (end_date - start_date).days
    fixed_dates = [start_date + timedelta(days=i) for i in range(total_days)]
    full_range_df = pd.DataFrame({'Date': fixed_dates})
else:
    st.error("文件名格式不对，无法提取日期")
    st.stop()


reatinTime = DateUtils.get_remaining_time(str(end_date))
tweetNumber = TweetsNumber.estimate_tweets_in_7days(7,reatinTime,len(df))

# --- 第一排：核心指标 ---
col1,col2, col3 = st.columns(3)
col1.metric("总推文数", len(df))
col3.metric("统计周期", f"{start_date} - {end_date}")

col2.metric("推测",tweetNumber['estimated_total_in_7days'])


# ==========================================

# 第二部分

# --- 3. 7x24 矩阵逻辑补充 ---
def get_heatmap_data(df, start_date, end_date):
    # 构建完整的时间轴范围
    total_days = (end_date - start_date).days
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


# 7*24样式设置
# 为了让 Total 列看起来更显眼，我们可以给最后一列换个色标或者加个特殊标注
fig_heat = px.imshow(
    heatmap_df,
    labels=dict(x="Hour & Daily Total", y="Date", color="Posts"),
    x=[f"{h}:00" for h in range(24)] + ["【TOTAL】"], # X轴增加一列
    y=heatmap_df.index,
    color_continuous_scale='pubugn',  #底部颜色
    text_auto=True,
    aspect="auto"
)
def get_current_hour():
    """返回当前小时（24小时制），并使用你之前的时间偏移"""
    # 和你 load_data 里保持一致的偏移（-12小时）
    now = datetime.now()
    return now.hour

# 手动添加你想改颜色的那个
fig_heat.add_annotation(
    x=get_current_hour(),                    # ← 这里改：0=0:00, 5=5:00, 15=15:00 ...
    y=-0.09,
    text=f"{get_current_hour()}:00",            # 要显示的文字
    showarrow=False,
    bgcolor="pink",                           # ← 背景颜色
    font=dict(color="blue", size=13),
    xref="x",
    yref="paper",
    xanchor="center"
)

fig_heat.update_yaxes(autorange="reversed")

# 锁定缩放并隐藏工具栏
fig_heat.update_layout(
    xaxis=dict(fixedrange=True),
    yaxis=dict(fixedrange=True),
    dragmode=False,
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})



