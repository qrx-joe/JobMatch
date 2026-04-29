#!/usr/bin/env python3
"""
匹配结果模型
"""

from dataclasses import dataclass, field
from typing import Optional

from .job import MatchLevel


@dataclass
class MatchResult:
    """
    匹配结果模型

    记录用户与岗位的匹配详情
    """

    job_id: int = 0
    user_id: int = 0

    # 各维度匹配结果
    major_match: tuple[bool, str] = (False, "")  # (是否匹配, 原因)
    education_match: tuple[bool, str] = (False, "")
    degree_match: tuple[bool, str] = (False, "")
    political_match: tuple[bool, str] = (False, "")
    age_match: tuple[bool, str] = (False, "")
    grassroots_match: tuple[bool, str] = (False, "")
    qualifications_match: tuple[bool, str] = (False, "")
    household_match: tuple[bool, str] = (False, "")
    gender_match: tuple[bool, str] = (False, "")

    # 综合评分
    total_score: int = 0  # 总分 0-100
    match_level: Optional[MatchLevel] = None  # 匹配等级

    # 推荐
    recommendation_tier: str = ""  # 冲/稳/保

    # 竞争分析
    competition_ratio: float = 0.0  # 当前竞争比
    historical_avg_ratio: float = 0.0  # 历史平均竞争比

    # 匹配原因
    match_reasons: list[str] = field(default_factory=list)
    mismatch_reasons: list[str] = field(default_factory=list)

    # 上岸概率
    pass_probability: float = 0.0

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "job_id": self.job_id,
            "major_match": self.major_match[1] if self.major_match else "",
            "education_match": self.education_match[1] if self.education_match else "",
            "political_match": self.political_match[1] if self.political_match else "",
            "age_match": self.age_match[1] if self.age_match else "",
            "total_score": self.total_score,
            "match_level": self.match_level.value if self.match_level else None,
            "recommendation_tier": self.recommendation_tier,
            "pass_probability": round(self.pass_probability, 2),
            "match_reasons": self.match_reasons,
            "mismatch_reasons": self.mismatch_reasons,
        }


# 导出
__all__ = ["MatchResult"]