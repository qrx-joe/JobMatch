#!/usr/bin/env python3
"""
政治面貌匹配器
"""

import re
from typing import Tuple

from .base_matcher import BaseMatcher


class PoliticalMatcher(BaseMatcher):
    """
    政治面貌匹配器

    匹配规则：
    - 岗位要求"不限" -> 全部通过
    - 岗位要求"中共党员" -> 只有党员通过
    - 岗位要求"中共党员或共青团员" -> 党员或团员通过
    - 岗位要求"群众" -> 只有群众通过
    """

    # 政治面貌层级（层级高的可以兼容低的）
    POLITICAL_LEVELS = {
        "中共党员": 4,
        "党员": 4,
        "预备党员": 3,
        "共青团员": 2,
        "团员": 2,
        "群众": 1,
        "无": 0,
    }

    def __init__(self, user_party_status: str):
        """
        初始化政治面貌匹配器

        Args:
            user_party_status: 用户政治面貌
        """
        self.user_level = self._get_level(user_party_status)

    def _get_level(self, status: str) -> int:
        """获取政治面貌层级"""
        if not status:
            return 0

        status = str(status).strip()

        # 精确匹配
        for key, level in self.POLITICAL_LEVELS.items():
            if key in status:
                return level

        return 0

    def match(self, job_requirement: str, user_status: str = None) -> Tuple[bool, str]:
        """
        匹配政治面貌

        Args:
            job_requirement: 岗位的政治面貌要求
            user_status: 用户政治面貌（可选）

        Returns:
            (是否匹配, 原因说明)
        """
        if user_status is None:
            user_level = self.user_level
            user_status = str(user_status) if user_status else ""
        else:
            user_level = self._get_level(user_status)

        job_req = str(job_requirement).strip()

        # 空值检查
        if not job_req or job_req in ["无", "nan", "", "None", "不限", "政治面貌不限"]:
            return True, "政治面貌不限"

        # 检查岗位是否限定了政治面貌
        # 模式：限党员/限共青团员/限群众

        # 1. 要求中共党员（含预备党员）
        if "党员" in job_req and "共青团员" not in job_req and "团员" not in job_req:
            if user_level >= 3:  # 党员或预备党员
                return True, f"政治面貌符合：要求{job_req}"
            else:
                status_str = self._level_to_str(user_level)
                return False, f"政治面貌不符合：要求{job_req}，你是{status_str}"

        # 2. 要求中共党员或共青团员
        if ("党员" in job_req and "共青团员" in job_req) or "党团员" in job_req:
            if user_level >= 2:  # 党员或团员
                return True, f"政治面貌符合：要求{job_req}"
            else:
                status_str = self._level_to_str(user_level)
                return False, f"政治面貌不符合：要求{job_req}，你是{status_str}"

        # 3. 要求共青团员
        if "共青团员" in job_req or "团员" in job_req:
            if user_level >= 2:
                return True, f"政治面貌符合：要求{job_req}"
            else:
                status_str = self._level_to_str(user_level)
                return False, f"政治面貌不符合：要求{job_req}，你是{status_str}"

        # 4. 要求群众
        if "群众" in job_req:
            if user_level == 1:
                return True, f"政治面貌符合：要求{job_req}"
            else:
                status_str = self._level_to_str(user_level)
                return False, f"政治面貌不符合：要求{job_req}，你是{status_str}"

        # 5. 其他情况视为不限
        return True, "政治面貌不限"

    def _level_to_str(self, level: int) -> str:
        """层级转字符串"""
        mapping = {
            4: "中共党员",
            3: "预备党员",
            2: "共青团员",
            1: "群众",
            0: "未知",
        }
        return mapping.get(level, "未知")


# 导出
__all__ = ["PoliticalMatcher"]