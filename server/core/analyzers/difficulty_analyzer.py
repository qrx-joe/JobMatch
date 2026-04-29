#!/usr/bin/env python3
"""
难度分析器

分析岗位难度，提供选岗建议
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..models.job import Job
from ..models.user_profile import UserProfile
from ..models.match_result import MatchResult


class DifficultyAnalyzer:
    """
    难度分析器

    综合评估岗位难度，帮助用户做出选岗决策
    """

    # 竞争比难度等级
    RATIO_LEVELS = {
        "极低": (0, 10),
        "较低": (10, 30),
        "中等": (30, 50),
        "较高": (50, 100),
        "极高": (100, float("inf")),
    }

    # 分数难度等级
    SCORE_LEVELS = {
        "极低": (0, 50),
        "较低": (50, 60),
        "中等": (60, 70),
        "较高": (70, 80),
        "极高": (80, 100),
    }

    def __init__(self, job: Job, match_result: MatchResult, user_profile: UserProfile):
        """
        初始化难度分析器

        Args:
            job: 岗位
            match_result: 匹配结果
            user_profile: 用户画像
        """
        self.job = job
        self.result = match_result
        self.profile = user_profile

    def analyze(self) -> "DifficultyReport":
        """
        分析难度

        Returns:
            DifficultyReport: 难度报告
        """
        report = DifficultyReport()

        # 1. 竞争难度
        report.competition_level = self._analyze_competition()

        # 2. 分数难度
        report.score_level = self._analyze_score_difficulty()

        # 3. 匹配难度
        report.match_difficulty = self._analyze_match_difficulty()

        # 4. 综合难度
        report.overall_difficulty = self._calc_overall_difficulty()

        # 5. 建议
        report.suggestions = self._generate_suggestions()

        return report

    def _analyze_competition(self) -> str:
        """分析竞争难度"""
        ratio = self.job.competition_ratio

        for level, (min_val, max_val) in self.RATIO_LEVELS.items():
            if min_val <= ratio < max_val:
                return level

        return "未知"

    def _analyze_score_difficulty(self) -> str:
        """分析分数难度"""
        if not self.job.historical_stats:
            return "数据不足"

        latest = max(self.job.historical_stats.values(), key=lambda x: x.year)
        if latest.passing_score <= 0:
            return "数据不足"

        for level, (min_val, max_val) in self.SCORE_LEVELS.items():
            if min_val <= latest.passing_score < max_val:
                return level

        return "极高"

    def _analyze_match_difficulty(self) -> str:
        """分析匹配难度（岗位对用户而言的符合程度）"""
        score = self.result.total_score

        if score >= 90:
            return "极易"
        elif score >= 75:
            return "较易"
        elif score >= 60:
            return "中等"
        elif score >= 40:
            return "较难"
        else:
            return "极难"

    def _calc_overall_difficulty(self) -> str:
        """计算综合难度"""
        # 根据多个因素综合判断
        factors = {
            "competition": 0.4,
            "score": 0.3,
            "match": 0.3,
        }

        # 竞争难度转换为数值
        comp_map = {"极低": 1, "较低": 2, "中等": 3, "较高": 4, "极高": 5}
        comp_score = comp_map.get(self.result.competition_level, 3)

        # 分数难度转换为数值
        score_map = {"极低": 1, "较低": 2, "中等": 3, "较高": 4, "极高": 5}
        score_score = score_map.get(self.result.score_level, 3)

        # 匹配难度转换为数值
        match_map = {"极易": 1, "较易": 2, "中等": 3, "较难": 4, "极难": 5}
        match_score = match_map.get(self.result.match_difficulty, 3)

        # 加权平均
        weighted = (
            comp_score * factors["competition"]
            + score_score * factors["score"]
            + match_score * factors["match"]
        )

        # 转换为难度描述
        if weighted <= 1.5:
            return "极容易"
        elif weighted <= 2.5:
            return "较容易"
        elif weighted <= 3.5:
            return "中等"
        elif weighted <= 4.5:
            return "较难"
        else:
            return "极难"

    def _generate_suggestions(self) -> List[str]:
        """生成建议"""
        suggestions = []

        # 基于竞争比
        ratio = self.job.competition_ratio
        if ratio > 100:
            suggestions.append("竞争比极高，谨慎报考")
        elif ratio > 50:
            suggestions.append("竞争比较激烈，需充分准备")

        # 基于匹配度
        if self.result.total_score < 50:
            suggestions.append("岗位匹配度较低，建议优先选择匹配度更高的岗位")
        elif self.result.total_score >= 80:
            suggestions.append("岗位匹配度高，是优先推荐的选择")

        # 基于分数预测
        if self.job.historical_stats:
            latest = max(self.job.historical_stats.values(), key=lambda x: x.year)
            if latest.passing_score > 0 and self.profile.estimated_score > 0:
                diff = self.profile.estimated_score - latest.passing_score
                if diff >= 10:
                    suggestions.append("你的预估分数高于往年进面分，有一定优势")
                elif diff >= 0:
                    suggestions.append("预估分数接近往年进面分，需要认真备考")
                else:
                    suggestions.append("预估分数低于往年进面分，建议谨慎考虑")

        # 基于上岸概率
        if self.job.pass_probability >= 0.5:
            suggestions.append("上岸概率较高，可以考虑")
        elif self.job.pass_probability >= 0.2:
            suggestions.append("上岸概率中等，需要努力备考")
        else:
            suggestions.append("上岸概率较低，可以作为冲刺选项")

        return suggestions


@dataclass
class DifficultyReport:
    """难度报告"""

    competition_level: str = ""  # 竞争难度等级
    score_level: str = ""  # 分数难度等级
    match_difficulty: str = ""  # 匹配难度
    overall_difficulty: str = ""  # 综合难度
    suggestions: List[str] = None  # 建议

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "competition_level": self.competition_level,
            "score_level": self.score_level,
            "match_difficulty": self.match_difficulty,
            "overall_difficulty": self.overall_difficulty,
            "suggestions": self.suggestions,
        }


# 导出
__all__ = ["DifficultyAnalyzer", "DifficultyReport"]