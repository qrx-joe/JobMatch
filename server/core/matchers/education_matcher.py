#!/usr/bin/env python3
"""
学历匹配器 - 支持向下兼容
"""

import re
from typing import Tuple

from .base_matcher import BaseMatcher


class EducationMatcher(BaseMatcher):
    """
    学历匹配器

    匹配规则：用户学历 >= 岗位要求学历
    例如：本科可以报"大专及以上"，但大专不能报"本科及以上"
    """

    # 学历层级（数字越大级别越高）
    EDU_LEVELS = {
        "中专": 0,
        "中职": 0,
        "高中": 1,
        "高职": 2,
        "大专": 2,
        "专科": 2,
        "本科": 3,
        "大学": 3,
        "学士": 3,
        "研究生": 4,
        "硕士": 4,
        "博士": 5,
    }

    def __init__(self, user_education: str):
        """
        初始化学历匹配器

        Args:
            user_education: 用户学历
        """
        self.user_level = self._get_level(user_education)

    def _get_level(self, edu: str) -> int:
        """获取学历等级"""
        if not edu:
            return 0

        edu = str(edu).strip()
        for key, level in sorted(self.EDU_LEVELS.items(), key=lambda x: x[1], reverse=True):
            if key in edu:
                return level

        # 尝试正则匹配
        match = re.search(r"(中专|中职|高中|高职|大专|专科|本科|大学|学士|研究生|硕士|博士)", edu)
        if match:
            key = match.group(1)
            return self.EDU_LEVELS.get(key, 0)

        return 0

    def match(self, job_requirement: str, user_education: str = None) -> Tuple[bool, str]:
        """
        匹配学历

        Args:
            job_requirement: 岗位的学历要求
            user_education: 用户学历（可选，默认使用初始化时的学历）

        Returns:
            (是否匹配, 原因说明)
        """
        if user_education is None:
            user_level = self.user_level
        else:
            user_level = self._get_level(user_education)

        job_edu = str(job_requirement).strip()

        # 空值检查
        if not job_edu or job_edu in ["无", "nan", "", "None", "不限", "学历不限"]:
            return True, "学历不限"

        # 提取岗位要求的最低学历
        job_min_level = self._get_level(job_edu)

        if job_min_level == 0:
            return True, "学历不限"

        # 检查是否有"及以上"
        has_above = "及以上" in job_edu or "以上" in job_edu

        if has_above:
            # 用户学历 >= 岗位要求
            if user_level >= job_min_level:
                user_edu_str = self._level_to_str(user_level)
                return True, f"学历符合：{user_edu_str} >= {job_edu}"
            else:
                return (
                    False,
                    f"学历不够：要求{job_edu}，你是{self._level_to_str(user_level)}",
                )
        else:
            # 没有"及以上"，通常是精确匹配（如"本科"）
            # 但我们仍然支持向上兼容（用户本科可以报本科）
            if user_level >= job_min_level:
                user_edu_str = self._level_to_str(user_level)
                return True, f"学历符合：{user_edu_str} >= {job_edu}"
            else:
                return (
                    False,
                    f"学历不匹配：要求{job_edu}，你是{self._level_to_str(user_level)}",
                )

    def _level_to_str(self, level: int) -> str:
        """学历等级转字符串"""
        mapping = {0: "未知", 1: "高中", 2: "大专", 3: "本科", 4: "研究生", 5: "博士"}
        return mapping.get(level, "未知")


class DegreeMatcher(BaseMatcher):
    """
    学位匹配器

    匹配规则：用户学位 >= 岗位要求学位
    例如：学士可以报"学士及以上"
    """

    DEGREE_LEVELS = {
        "无学位": 0,
        "学士": 1,
        "硕士": 2,
        "博士": 3,
    }

    def __init__(self, user_degree: str):
        self.user_level = self._get_level(user_degree)

    def _get_level(self, degree: str) -> int:
        if not degree:
            return 0

        degree = str(degree).strip()
        for key, level in sorted(self.DEGREE_LEVELS.items(), key=lambda x: x[1], reverse=True):
            if key in degree:
                return level
        return 0

    def match(self, job_requirement: str, user_degree: str = None) -> Tuple[bool, str]:
        """匹配学位"""
        if user_degree is None:
            user_level = self.user_level
        else:
            user_level = self._get_level(user_degree)

        job_degree = str(job_requirement).strip()

        if not job_degree or job_degree in ["无", "nan", "", "None", "不限", "学位不限"]:
            return True, "学位不限"

        job_min_level = self._get_level(job_degree)

        if job_min_level == 0:
            return True, "学位不限"

        has_above = "及以上" in job_degree or "以上" in job_degree

        if has_above:
            if user_level >= job_min_level:
                return True, f"学位符合：{self._level_to_str(user_level)} >= {job_degree}"
            else:
                return (
                    False,
                    f"学位不够：要求{job_degree}，你是{self._level_to_str(user_level)}",
                )
        else:
            if user_level >= job_min_level:
                return True, f"学位符合：{self._level_to_str(user_level)}"
            else:
                return (
                    False,
                    f"学位不匹配：要求{job_degree}，你是{self._level_to_str(user_level)}",
                )

    def _level_to_str(self, level: int) -> str:
        mapping = {0: "无学位", 1: "学士", 2: "硕士", 3: "博士"}
        return mapping.get(level, "未知")


# 导出
__all__ = ["EducationMatcher", "DegreeMatcher"]