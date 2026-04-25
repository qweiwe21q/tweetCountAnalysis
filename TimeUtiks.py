from datetime import datetime
import zoneinfo


def convert_dual_time(time_str: str, year: int = 2026):
    """
    输入: "4-10-6"
    同时按两种情况解析：
    1. 输入是北京时间 → 输出对应的 UTC 时间
    2. 输入是 UTC 时间 → 输出对应的北京时间
    """
    try:
        month, day, hour = map(int, time_str.split('-'))

        # ==================== 情况1：输入是北京时间 ====================
        beijing_tz = zoneinfo.ZoneInfo("Asia/Shanghai")
        beijing_dt = datetime(year, month, day, hour, 0, 0, tzinfo=beijing_tz)
        utc_from_beijing = beijing_dt.astimezone(zoneinfo.ZoneInfo("UTC"))

        # ==================== 情况2：输入是 UTC 时间 ====================
        utc_dt = datetime(year, month, day, hour, 0, 0, tzinfo=zoneinfo.ZoneInfo("UTC"))
        beijing_from_utc = utc_dt.astimezone(beijing_tz)

        return {
            "input": f"{month}月{day}日 {hour}:00",
            # 如果输入是北京时间
            "beijing_input": beijing_dt.strftime("%Y-%m-%d %H:%00 北京时间"),
            "utc_from_beijing": utc_from_beijing.strftime("%Y-%m-%d %H:%00 UTC"),
            # 如果输入是 UTC 时间
            "utc_input": utc_dt.strftime("%Y-%m-%d %H:%00 UTC"),
            "beijing_from_utc": beijing_from_utc.strftime("%Y-%m-%d %H:%00 北京时间"),
        }

    except ValueError:
        return {"error": "格式错误！请使用 '月-日-时' 格式，例如 '4-10-6'"}


# ====================== 使用示例 ======================

if __name__ == "__main__":
    result = convert_dual_time("4-4-04")

    print("输入:", result["input"])
    print("=" * 50)
    print("【情况1】如果输入是北京时间:")
    print("   北京时间:", result["beijing_input"])
    print("   对应 UTC :", result["utc_from_beijing"])
    print("=" * 50)
    print("【情况2】如果输入是 UTC 时间:")
    print("   UTC 时间 :", result["utc_input"])
    print("   对应北京时间:", result["beijing_from_utc"])