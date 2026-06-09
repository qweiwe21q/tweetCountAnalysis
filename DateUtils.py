from datetime import datetime
import pytz  # 如果需要指定时区
def get_remaining_time(end_date_str: str, tz=pytz.timezone('Asia/Shanghai')) -> str:
    """
    计算距离结束日期剩余时间
    输入: "2026-06-09"
    输出格式: "8-3-45" （天-小时-分钟）
    """
    try:
        # 当前时间（上海时区）
        now = datetime.now(tz)

        # 目标结束时间（默认当天 23:59:59）
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        end = tz.localize(end_date.replace(hour=23, minute=59, second=59))

        # 计算剩余时间
        remaining = end - now

        if remaining.total_seconds() <= 0:
            return "0-0-0"  # 已结束

        # 转换为 天、小时、分钟
        total_seconds = remaining.total_seconds()
        days = int(total_seconds // (24 * 3600))
        hours = int((total_seconds % (24 * 3600)) // 3600)
        minutes = int((total_seconds % 3600) // 60)

        return f"{days}-{hours}-{minutes}"

    except Exception as e:
        print(f"日期解析错误: {e}")
        return "0-0-0"