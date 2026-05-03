#!/usr/bin/env python3
"""
历史统计数据模型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HistoricalStats:
    """
    历史统计数据模型

    记录岗位历年的报名和录取情况
    """

    # 唯一标识
    id: int = 0
    job_id: int = 0  # 关联岗位ID
    year: int = 0  # 年份

    # 招录数据
    recruitment_count: int = 0  # 招录人数
    applicants: int = 0  # 报名人数
    approved: int = 0  # 初审通过人数
    paid: int = 0  # 缴费人数

    # 竞争比
    competition_ratio: float = 0.0  # 竞争比 = 缴费人数 / 招录人数

    # 分数数据
    passing_score: float = 0.0  # 进面最低分
    avg_score: float = 0.0  # 平均分
    highest_score: float = 0.0  # 最高分

    # 附加信息
    notes: str = ""  # 备注
    source: str = ""  # 数据来源

    def calculate_ratio(self) -> float:
        """计算竞争比"""
        if self.recruitment_count > 0 and self.paid > 0:
            self.competition_ratio = self.paid / self.recruitment_count
        return self.competition_ratio

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "year": self.year,
            "recruitment_count": self.recruitment_count,
            "applicants": self.applicants,
            "paid": self.paid,
            "competition_ratio": round(self.competition_ratio, 2),
            "passing_score": self.passing_score,
            "avg_score": round(self.avg_score, 1),
            "highest_score": self.highest_score,
        }


@dataclass
class HistoricalTrend:
    """
    历史趋势分析

    基于历年数据的趋势分析结果
    """

    job_id: int = 0
    unit_name: str = ""

    # 历年数据
    yearly_stats: list[HistoricalStats] = field(default_factory=list)

    # 趋势分析
    avg_competition_ratio: float = 0.0  # 平均竞争比
    max_competition_ratio: float = 0.0  # 最高竞争比
    min_competition_ratio: float = 0.0  # 最低竞争比

    # 分数趋势
    avg_passing_score: float = 0.0  # 平均进面分
    score_trend: str = ""  # 分数趋势：上升/下降/稳定

    # 预测
    predicted_next_year_ratio: float = 0.0  # 预测明年竞争比
    predicted_next_year_score: float = 0.0  # 预测明年进面分

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "unit_name": self.unit_name,
            "avg_competition_ratio": round(self.avg_competition_ratio, 2),
            "max_competition_ratio": round(self.max_competition_ratio, 2),
            "min_competition_ratio": round(self.min_competition_ratio, 2),
            "avg_passing_score": round(self.avg_passing_score, 1),
            "score_trend": self.score_trend,
            "predicted_next_year_ratio": round(self.predicted_next_year_ratio, 2),
            "predicted_next_year_score": round(self.predicted_next_year_score, 1),
            "yearly_stats": [s.to_dict() for s in self.yearly_stats],
        }


# 导出
__all__ = ["HistoricalStats", "HistoricalTrend"]