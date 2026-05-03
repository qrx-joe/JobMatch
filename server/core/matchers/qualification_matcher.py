#!/usr/bin/env python3
"""
资格证书匹配器
"""

from typing import Tuple

from .base_matcher import BaseMatcher


class QualificationMatcher(BaseMatcher):
    """
    资格证书匹配器

    检查用户是否持有岗位要求的资格证书
    """

    # 常见资格证书别名映射
    QUALIFICATION_ALIASES = {
        "教师资格证": ["教师资格证", "教师资格"],
        "法律职业资格": ["法律职业资格", "法律职业资格证", "法律职业资格证书", "律师资格"],
        "医师资格证": ["医师资格证", "执业医师"],
        "护士资格证": ["护士资格证", "护士执业证"],
        "会计证": ["会计证", "会计从业资格"],
        "注册会计师": ["注册会计师", "CPA"],
        "建造师证": ["建造师", "一级建造师", "二级建造师"],
    }

    def __init__(self, user_qualifications: list[str] = None):
        self.user_quals = [q.strip() for q in (user_qualifications or [])]

    def match(self, job_requirement: str, user_quals: list[str] = None) -> Tuple[bool, str]:
        if user_quals is None:
            user_quals = self.user_quals

        job_req = str(job_requirement).strip()

        # 无要求
        if not job_req or job_req in ["无", "不限", "nan", "", "无资格证书要求"]:
            return True, "无资格要求"

        # 提取岗位要求的资格类型
        required_types = self._extract_qualification_types(job_req)

        if not required_types:
            return True, "资格要求不明确"

        # 检查用户是否拥有
        for req_type in required_types:
            if not self._has_qualification(req_type, user_quals):
                return False, f"缺少资格：{req_type}"

        return True, f"拥有所需资格：{', '.join(required_types)}"

    def _extract_qualification_types(self, text: str) -> list[str]:
        """从文本中提取资格要求类型"""
        found = []
        text_lower = text.lower()

        for qual_name, aliases in self.QUALIFICATION_ALIASES.items():
            for alias in aliases:
                if alias in text:
                    found.append(qual_name)
                    break

        return found

    def _has_qualification(self, required: str, user_quals: list[str]) -> bool:
        """检查用户是否有某资格"""
        for user_qual in user_quals:
            # 精确匹配或包含匹配
            if required in user_qual or user_qual in required:
                return True
            # 检查别名
            if required in self.QUALIFICATION_ALIASES:
                for alias in self.QUALIFICATION_ALIASES[required]:
                    if alias in user_qual:
                        return True
        return False


# 导出
__all__ = ["QualificationMatcher"]