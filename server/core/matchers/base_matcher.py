#!/usr/bin/env python3
"""
匹配器基类
"""

from abc import ABC, abstractmethod
from typing import Tuple


class BaseMatcher(ABC):
    """
    匹配器基类

    所有匹配器必须实现 match 方法
    """

    @abstractmethod
    def match(self, job_requirement: str, user_profile_value) -> Tuple[bool, str]:
        """
        匹配方法

        Args:
            job_requirement: 岗位要求（如"本科及以上"）
            user_profile_value: 用户档案中的值

        Returns:
            (是否匹配, 原因说明)
        """
        pass

    def _is_empty(self, value) -> bool:
        """判断值是否为空"""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (list, tuple)) and len(value) == 0:
            return True
        return False


# 导出
__all__ = ["BaseMatcher"]