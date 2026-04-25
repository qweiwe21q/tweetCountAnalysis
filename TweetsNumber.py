from datetime import timedelta
from typing import Dict


def estimate_tweets_in_7days(day:int,remaining_str: str, tweets_number: int) -> Dict:
    """
    根据剩余时间和已发推特数量，估算7天内总共会发多少推特

    参数:
        remaining_str: str - 剩余时间，格式 "天-小时-分钟"，例如 "3-7-50"
        tweets_number: int - 当前已经发的推特数量

    返回: dict 包含详细计算结果
    """
    # 1. 解析剩余时间
    try:
        days, hours, minutes = map(int, remaining_str.split('-'))
        remaining = timedelta(days=days, hours=hours, minutes=minutes)
    except:
        raise ValueError("剩余时间格式错误！正确格式示例: '3-7-50'")

    # 2. 总时长 = 7天
    total_duration = timedelta(days=day)

    # 3. 计算已经过去的时间
    elapsed = total_duration - remaining

    # 4. 计算发推速率（每分钟发多少条）
    if elapsed.total_seconds() <= 0:
        return {
            "error": "剩余时间不能大于或等于7天"
        }

    elapsed_minutes = elapsed.total_seconds() / 60
    rate_per_minute = tweets_number / elapsed_minutes  # 每分钟发多少条

    # 5. 计算7天总分钟数
    total_minutes_7days = day * 24 * 60

    # 6. 预计7天总推特数
    estimated_total = round(rate_per_minute * total_minutes_7days)
    rate_per_day = round(rate_per_minute * 1440, 1)  # 每天平均发多少条

    return {
        "remaining_time": str(remaining),
        "elapsed_time": str(elapsed),
        "elapsed_days": round(elapsed.total_seconds() / 86400, 2),
        "tweets_so_far": tweets_number,
        "rate_per_day": rate_per_day,
        "estimated_total_in_7days": estimated_total,
        "message": f"按照当前速度，{timedelta}天预计总共会发约 {estimated_total} 条推特（每天平均约 {rate_per_day} 条）"
    }


# ====================== 使用示例 ======================

if __name__ == "__main__":
    result = estimate_tweets_in_7days(7,"3-15-0", 86)
    # result = estimate_tweets_in_7days(2,"0-2-0", 53)
    print(result["message"])
    print(f"已用时间: {result['elapsed_time']}")
    print(f"每天平均发推: {result['rate_per_day']} 条")
    print(f"7天预计总数: {result['estimated_total_in_7days']} 条")