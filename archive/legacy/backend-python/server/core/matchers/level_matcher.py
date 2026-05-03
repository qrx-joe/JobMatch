#!/usr/bin/env python3
"""
计算机/英语等级匹配器
"""

from typing import Tuple

from .base_matcher import BaseMatcher


class ComputerLevelMatcher(BaseMatcher):
    """
    计算机等级匹配器

    匹配规则：
    - 岗位无要求 -> 通过
    - 岗位要求计算机等级，用户有对应等级 -> 通过
    """

    LEVEL_KEYWORDS = {
        "一级": ["计算机一级", "一级计算机", "一级"],
        "二级": ["计算机二级", "二级计算机", "二级"],
        "三级": ["计算机三级", "三级计算机", "三级"],
        "四级": ["计算机四级", "四级计算机", "四级"],
    }

    def __init__(self, user_computer_level: str = ""):
        self.user_level = user_computer_level.strip()

    def match(self, job_requirement: str, user_level: str = None) -> Tuple[bool, str]:
        if user_level is None:
            user_level = self.user_level

        job_req = str(job_requirement).strip()
        if not job_req:
            return True, "计算机等级不限"

        # 检查岗位是否要求计算机等级
        required_level = None
        for level_name, keywords in self.LEVEL_KEYWORDS.items():
            for kw in keywords:
                if kw in job_req:
                    required_level = level_name
                    break
            if required_level:
                break

        if not required_level:
            return True, "计算机等级不限"

        # 用户有等级
        if user_level:
            for kw in self.LEVEL_KEYWORDS.get(required_level, []):
                if kw in user_level:
                    return True, f"计算机等级符合：要求{required_level}，你有{user_level}"
            # 不满足要求但宽松模式
            return True, f"计算机等级不符合：要求{required_level}，你有{user_level}（仍可报名）"

        # 用户无等级
        return True, f"计算机等级不符：要求{required_level}，你无计算机等级（仍可报名）"


class EnglishLevelMatcher(BaseMatcher):
    """
    英语等级匹配器

    匹配规则：
    - 岗位无要求 -> 通过
    - 岗位要求英语等级，用户有对应等级 -> 通过
    """

    LEVEL_KEYWORDS = {
        "四级": ["英语四级", "CET-4", "大学英语四级"],
        "六级": ["英语六级", "CET-6", "大学英语六级"],
        "八级": ["英语八级", "TEM-8"],
    }

    def __init__(self, user_english_level: str = ""):
        self.user_level = user_english_level.strip()

    def match(self, job_requirement: str, user_level: str = None) -> Tuple[bool, str]:
        if user_level is None:
            user_level = self.user_level

        job_req = str(job_requirement).strip()
        if not job_req:
            return True, "英语等级不限"

        # 检查岗位是否要求英语等级
        required_level = None
        for level_name, keywords in self.LEVEL_KEYWORDS.items():
            for kw in keywords:
                if kw in job_req:
                    required_level = level_name
                    break
            if required_level:
                break

        if not required_level:
            return True, "英语等级不限"

        # 用户有等级
        if user_level:
            for kw in self.LEVEL_KEYWORDS.get(required_level, []):
                if kw in user_level:
                    return True, f"英语等级符合：要求{required_level}，你有{user_level}"
            return True, f"英语等级不符合：要求{required_level}，你有{user_level}（仍可报名）"

        return True, f"英语等级不符：要求{required_level}，你无英语等级（仍可报名）"


# 导出
__all__ = ["ComputerLevelMatcher", "EnglishLevelMatcher"]