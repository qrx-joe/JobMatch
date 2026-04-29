#!/usr/bin/env python3
"""
历史数据分析器

分析岗位历年分数线和竞争趋势
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..models.job import Job
from ..models.historical_stats import HistoricalStats, HistoricalTrend


class HistoricalAnalyzer:
    """
    历史数据分析器

    功能：
    1. 分析历年竞争比变化趋势
    2. 预测明年竞争比
    3. 分析分数线变化
    4. 预测进面分数
    """

    def __init__(self, historical_data: Optional[Dict[int, HistoricalStats]] = None):
        """
        初始化分析器

        Args:
            historical_data: 历史数据，格式 {年份: HistoricalStats}
        """
        self.data = historical_data or {}

    def analyze_trend(self, unit_name: str) -> Optional[HistoricalTrend]:
        """
        分析历史趋势

        Args:
            unit_name: 单位名称

        Returns:
            HistoricalTrend: 趋势分析结果
        """
        if not self.data:
            return None

        trend = HistoricalTrend(unit_name=unit_name)

        # 按年份排序
        sorted_stats = sorted(self.data.values(), key=lambda x: x.year)
        trend.yearly_stats = sorted_stats

        if not sorted_stats:
            return None

        # 计算平均/最高/最低竞争比
        ratios = [s.competition_ratio for s in sorted_stats if s.competition_ratio > 0]
        if ratios:
            trend.avg_competition_ratio = sum(ratios) / len(ratios)
            trend.max_competition_ratio = max(ratios)
            trend.min_competition_ratio = min(ratios)

        # 计算平均进面分
        scores = [s.passing_score for s in sorted_stats if s.passing_score > 0]
        if scores:
            trend.avg_passing_score = sum(scores) / len(scores)

        # 判断分数趋势
        if len(scores) >= 2:
            recent = scores[-1]
            previous = scores[-2]
            if recent > previous * 1.05:
                trend.score_trend = "上升"
            elif recent < previous * 0.95:
                trend.score_trend = "下降"
            else:
                trend.score_trend = "稳定"

        # 预测明年
        trend.predicted_next_year_ratio = self._predict_next_ratio()
        trend.predicted_next_year_score = self._predict_next_score()

        return trend

    def _predict_next_ratio(self) -> float:
        """预测明年竞争比（基于线性回归）"""
        data_list = sorted(self.data.values(), key=lambda x: x.year)
        if len(data_list) < 2:
            # 数据不足，返回平均值
            ratios = [s.competition_ratio for s in data_list if s.competition_ratio > 0]
            return sum(ratios) / len(ratios) if ratios else 0.0

        # 简单线性回归
        n = len(data_list)
        years = [s.year for s in data_list]
        ratios = [s.competition_ratio for s in data_list]

        # 计算斜率
        sum_x = sum(years)
        sum_y = sum(ratios)
        sum_xy = sum(x * y for x, y in zip(years, ratios))
        sum_x2 = sum(x**2 for x in years)

        if n * sum_x2 - sum_x**2 == 0:
            return ratios[-1]

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        intercept = (sum_y - slope * sum_x) / n

        # 预测下一年
        next_year = data_list[-1].year + 1
        predicted = slope * next_year + intercept

        # 不能为负
        return max(0, predicted)

    def _predict_next_score(self) -> float:
        """预测明年进面分数"""
        data_list = sorted(self.data.values(), key=lambda x: x.year)
        scores = [s.passing_score for s in data_list if s.passing_score > 0]

        if not scores:
            return 0.0

        if len(scores) < 2:
            return scores[-1]

        # 简单移动平均
        recent_scores = scores[-3:]  # 最近3年
        return sum(recent_scores) / len(recent_scores)

    def add_historical_data(self, stats: HistoricalStats) -> None:
        """添加历史数据"""
        if stats.year not in self.data:
            self.data[stats.year] = stats

    @classmethod
    def from_job(cls, job: Job) -> "HistoricalAnalyzer":
        """
        从Job创建分析器

        Args:
            job: 岗位（包含历史数据）

        Returns:
            HistoricalAnalyzer: 分析器实例
        """
        return cls(job.historical_stats)


class TrendDetector:
    """
    趋势检测器

    检测竞争比和分数的变化趋势
    """

    @staticmethod
    def detect_ratio_trend(ratios: List[float]) -> Tuple[str, float]:
        """
        检测竞争比趋势

        Args:
            ratios: 历年竞争比列表（从早到晚）

        Returns:
            (趋势描述, 变化率)
        """
        if len(ratios) < 2:
            return "稳定", 0.0

        # 计算变化率
        recent = ratios[-1]
        oldest = ratios[0]

        if oldest == 0:
            change_rate = 0.0
        else:
            change_rate = (recent - oldest) / oldest

        # 判断趋势
        if change_rate > 0.2:
            trend = "大幅上升"
        elif change_rate > 0.05:
            trend = "小幅上升"
        elif change_rate < -0.2:
            trend = "大幅下降"
        elif change_rate < -0.05:
            trend = "小幅下降"
        else:
            trend = "稳定"

        return trend, change_rate

    @staticmethod
    def detect_score_trend(scores: List[float]) -> Tuple[str, float]:
        """
        检测分数趋势

        Args:
            scores: 历年进面分列表（从早到晚）

        Returns:
            (趋势描述, 变化值)
        """
        if len(scores) < 2:
            return "稳定", 0.0

        recent = scores[-1]
        oldest = scores[0]

        diff = recent - oldest

        if diff > 5:
            trend = "明显上升"
        elif diff > 0:
            trend = "小幅上升"
        elif diff < -5:
            trend = "明显下降"
        elif diff < 0:
            trend = "小幅下降"
        else:
            trend = "稳定"

        return trend, diff


# 导出
__all__ = ["HistoricalAnalyzer", "TrendDetector"]