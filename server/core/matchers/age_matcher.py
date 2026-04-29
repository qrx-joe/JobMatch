#!/usr/bin/env python3
"""
年龄匹配器
"""

import re
from datetime import datetime
from typing import Tuple, Optional

from .base_matcher import BaseMatcher


class AgeMatcher(BaseMatcher):
    """
    年龄匹配器

    支持多种格式：
    - "30岁以下"
    - "35岁及以下"
    - "28-35周岁"
    - "1989年1月1日后出生"
    """

    def __init__(self, user_age: int, birth_year: Optional[int] = None):
        """
        初始化年龄匹配器

        Args:
            user_age: 用户年龄（周岁）
            birth_year: 出生年份（用于精确计算）
        """
        self.user_age = user_age
        self.birth_year = birth_year

    def match(self, job_requirement: str, user_age: int = None) -> Tuple[bool, str]:
        """
        匹配年龄

        Args:
            job_requirement: 岗位的年龄要求
            user_age: 用户年龄（可选）

        Returns:
            (是否匹配, 原因说明)
        """
        if user_age is None:
            age = self.user_age
        else:
            age = user_age

        job_req = str(job_requirement).strip()

        # 空值检查
        if not job_req or job_req in ["无", "nan", "", "None", "不限", "年龄不限"]:
            return True, "年龄不限"

        # 解析年龄要求
        parsed = self._parse_age_requirement(job_req)

        if parsed is None:
            # 无法解析，保守处理
            return True, f"年龄要求（无法解析）：{job_req}"

        min_age, max_age = parsed

        # 检查是否在范围内
        if min_age is not None and age < min_age:
            return False, f"年龄不符合：要求{min_age}岁以上，你是{age}岁"

        if max_age is not None and age > max_age:
            return False, f"年龄不符合：要求{max_age}岁以下，你是{age}岁"

        return True, f"年龄符合：要求{job_req}，你是{age}岁"

    def _parse_age_requirement(self, requirement: str) -> Optional[Tuple[Optional[int], Optional[int]]]:
        """
        解析年龄要求

        Returns:
            (最小年龄, 最大年龄) 或 None
        """
        requirement = requirement.strip()

        # 模式1: "30岁以下"
        match = re.match(r"(\d+)\s*岁以下", requirement)
        if match:
            max_age = int(match.group(1))
            return (None, max_age - 1)  # 30岁以下意味着 <= 29

        # 模式2: "35岁及以下"
        match = re.match(r"(\d+)\s*岁及以下", requirement)
        if match:
            max_age = int(match.group(1))
            return (None, max_age)

        # 模式3: "28-35周岁"
        match = re.match(r"(\d+)\s*[-~]\s*(\d+)\s*(?:周岁|岁)", requirement)
        if match:
            min_age = int(match.group(1))
            max_age = int(match.group(2))
            return (min_age, max_age)

        # 模式4: "30周岁以下"
        match = re.match(r"(\d+)\s*周岁以下", requirement)
        if match:
            max_age = int(match.group(1))
            return (None, max_age - 1)

        # 模式5: "30-35岁"
        match = re.match(r"(\d+)\s*[-~]\s*(\d+)\s*岁", requirement)
        if match:
            min_age = int(match.group(1))
            max_age = int(match.group(2))
            return (min_age, max_age)

        # 模式6: 仅最大年龄 "35岁以下"
        match = re.match(r"(\d+)\s*以下", requirement)
        if match:
            max_age = int(match.group(1))
            return (None, max_age - 1)

        # 模式7: "1989年1月1日后出生" - 用出生年份判断
        match = re.match(r"(\d{4})\s*年.*?后\s*出生", requirement)
        if match:
            birth_year_limit = int(match.group(1))
            current_year = datetime.now().year
            max_age = current_year - birth_year_limit
            return (None, max_age)

        return None

    def check_by_birth_year(self, job_requirement: str, birth_year: int) -> Tuple[bool, str]:
        """
        用出生年份检查年龄要求（更精确）

        Args:
            job_requirement: 年龄要求
            birth_year: 出生年份

        Returns:
            (是否匹配, 原因说明)
        """
        job_req = str(job_requirement).strip()

        if not job_req or job_req in ["无", "nan", "", "None", "不限"]:
            return True, "年龄不限"

        # 如果有出生年份限制
        match = re.match(r"(\d{4})\s*年.*?后\s*出生", job_req)
        if match:
            limit_year = int(match.group(1))
            if birth_year >= limit_year:
                return True, f"出生年份符合：要求{job_req}"
            else:
                return False, f"出生年份不符合：要求{job_req}，你的出生年份是{birth_year}"

        # 其他情况用年龄
        age = datetime.now().year - birth_year
        return self.match(job_req, age)


# 导出
__all__ = ["AgeMatcher"]