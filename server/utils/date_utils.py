#!/usr/bin/env python3
"""
日期工具函数
"""

from datetime import datetime, timedelta
from typing import Optional


def get_current_year() -> int:
    """获取当前年份"""
    return datetime.now().year


def get_exam_countdown(deadline: str) -> dict:
    """
    计算考试倒计时

    Args:
        deadline: 截止日期，格式如 "2026-05-15" 或 "2026/05/15"

    Returns:
        dict: {"days": 天数, "hours": 小时数, "message": 提示信息}
    """
    try:
        # 解析日期
        if "/" in deadline:
            exam_date = datetime.strptime(deadline, "%Y/%m/%d")
        else:
            exam_date = datetime.strptime(deadline, "%Y-%m-%d")

        now = datetime.now()
        diff = exam_date - now

        if diff.total_seconds() < 0:
            return {
                "days": 0,
                "hours": 0,
                "message": "报名已截止",
                "expired": True,
            }

        days = diff.days
        hours = int(diff.seconds / 3600)

        if days == 0:
            message = f"距报名截止还有 {hours} 小时"
        elif days == 1:
            message = "距报名截止还有 1 天"
        elif days < 7:
            message = f"距报名截止还有 {days} 天"
        elif days < 30:
            weeks = days // 7
            message = f"距报名截止还有 {weeks} 周"
        else:
            message = f"距报名截止还有 {days} 天"

        return {
            "days": days,
            "hours": hours,
            "message": message,
            "expired": False,
        }

    except Exception as e:
        return {
            "days": 0,
            "hours": 0,
            "message": "日期解析错误",
            "expired": False,
            "error": str(e),
        }


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    格式化日期

    Args:
        date: datetime对象
        format_str: 格式字符串

    Returns:
        str: 格式化后的日期
    """
    if date is None:
        return ""
    return date.strftime(format_str)


def parse_date(date_str: str) -> Optional[datetime]:
    """
    解析日期字符串

    支持格式：
    - 2026-05-15
    - 2026/05/15
    - 2026年5月15日
    - 2026.05.15

    Args:
        date_str: 日期字符串

    Returns:
        datetime或None
    """
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y年%m月%d日",
        "%Y.%m.%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def calculate_age(birth_year: int, birth_month: int = 1, birth_day: int = 1) -> int:
    """
    计算年龄（周岁）

    Args:
        birth_year: 出生年份
        birth_month: 出生月份
        birth_day: 出生日期

    Returns:
        int: 年龄
    """
    now = datetime.now()
    birth_date = datetime(birth_year, birth_month, birth_day)

    age = now.year - birth_year
    # 如果今年还没过生日，减1
    if (now.month, now.day) < (birth_month, birth_day):
        age -= 1

    return age


def get_week_start_end(date: Optional[datetime] = None) -> tuple:
    """
    获取本周的开始和结束日期

    Args:
        date: 参照日期，None表示今天

    Returns:
        (周一, 周日)
    """
    if date is None:
        date = datetime.now()

    # 周一
    week_start = date - timedelta(days=date.weekday())
    # 周日
    week_end = week_start + timedelta(days=6)

    return week_start, week_end


def get_month_start_end(date: Optional[datetime] = None) -> tuple:
    """
    获取本月的开始和结束日期

    Args:
        date: 参照日期，None表示今天

    Returns:
        (月初, 月末)
    """
    if date is None:
        date = datetime.now()

    # 月初
    month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # 月末
    if date.month == 12:
        month_end = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = date.replace(month=date.month + 1, day=1) - timedelta(days=1)

    return month_start, month_end


# 导出
__all__ = [
    "get_current_year",
    "get_exam_countdown",
    "format_date",
    "parse_date",
    "calculate_age",
    "get_week_start_end",
    "get_month_start_end",
]