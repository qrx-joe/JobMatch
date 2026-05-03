#!/usr/bin/env python3
"""
冲/稳/保 推荐器

基于用户画像和岗位竞争比进行分层推荐
"""

from typing import Dict, List, Optional

from ..models.job import Job, MatchLevel, RecommendationTier
from ..models.user_profile import UserProfile
from ..models.match_result import MatchResult


class TierRecommender:
    """
    冲/稳/保 推荐逻辑

    分类标准：
    - 冲刺: 专业完全匹配 + 竞争比<30 + 历史分数接近用户预估
    - 稳妥: 专业匹配 + 竞争比30-80 + 难度稳定
    - 保底: 专业部分匹配/不限 + 竞争比<20
    """

    # 竞争比阈值
    STRETCH_RATIO_THRESHOLD = 30.0  # 冲刺门槛
    SAFE_RATIO_MIN = 30.0  # 稳妥下限
    SAFE_RATIO_MAX = 80.0  # 稳妥上限
    BOTTOM_RATIO_THRESHOLD = 20.0  # 保底门槛

    def __init__(self, user_profile: UserProfile):
        """
        初始化推荐器

        Args:
            user_profile: 用户画像
        """
        self.profile = user_profile

    def recommend(self, jobs: List[Job], match_results: List[MatchResult]) -> Dict[str, List[Job]]:
        """
        对岗位进行分层推荐

        Args:
            jobs: 岗位列表
            match_results: 匹配结果列表

        Returns:
            dict: {"冲刺": [...], "稳妥": [...], "保底": [...]}
        """
        # 构建 job_id -> match_result 映射
        result_map = {r.job_id: r for r in match_results}

        stretch = []
        safe = []
        bottom = []

        for job in jobs:
            result = result_map.get(job.id)
            if not result:
                continue

            tier = self._classify(job, result)
            job.recommendation_tier = tier

            # 计算上岸概率
            job.pass_probability = self._calc_probability(job, result)

            if tier == RecommendationTier.STRETCH:
                stretch.append(job)
            elif tier == RecommendationTier.SAFE:
                safe.append(job)
            else:
                bottom.append(job)

        return {
            "冲刺": stretch,
            "稳妥": safe,
            "保底": bottom,
        }

    def _classify(self, job: Job, result: MatchResult) -> RecommendationTier:
        """
        分类岗位到 冲/稳/保

        Args:
            job: 岗位
            result: 匹配结果

        Returns:
            RecommendationTier: 推荐层级
        """
        ratio = job.competition_ratio

        # 1. 先看专业匹配情况
        major_ok = result.major_match[0] if result.major_match else False

        # 专业完全匹配
        if major_ok:
            # 竞争比很低，值得冲刺
            if ratio < self.STRETCH_RATIO_THRESHOLD:
                # 加上其他条件判断
                if self._is_stretch_candidate(job, result):
                    return RecommendationTier.STRETCH

            # 竞争比中等，稳妥
            if self.SAFE_RATIO_MIN <= ratio <= self.SAFE_RATIO_MAX:
                return RecommendationTier.SAFE

            # 竞争比很高
            if ratio > self.SAFE_RATIO_MAX:
                # 但分数够高，可以冲刺
                if self._should_stretch_high_ratio(job, result):
                    return RecommendationTier.STRETCH
                return RecommendationTier.SAFE

        # 专业部分匹配或不限
        else:
            # 竞争比很低，可以保底
            if ratio < self.BOTTOM_RATIO_THRESHOLD:
                return RecommendationTier.BOTTOM

            # 竞争比中等，看其他条件
            if ratio < self.STRETCH_RATIO_THRESHOLD:
                return RecommendationTier.SAFE

        # 默许稳妥
        return RecommendationTier.SAFE

    def _is_stretch_candidate(self, job: Job, result: MatchResult) -> bool:
        """判断是否适合冲刺"""
        # 条件：专业完全匹配 + 竞争比低 + 用户预估分数够高
        if result.total_score >= 80:
            return True

        # 有历史数据且历史分数趋势下降
        if job.historical_stats:
            latest = max(job.historical_stats.values(), key=lambda x: x.year)
            if latest.passing_score > 0 and self.profile.estimated_score >= latest.passing_score:
                return True

        return False

    def _should_stretch_high_ratio(self, job: Job, result: MatchResult) -> bool:
        """竞争比高但仍然可以冲刺"""
        # 用户预估分数远高于历史进面分
        if job.historical_stats and self.profile.estimated_score > 0:
            latest = max(job.historical_stats.values(), key=lambda x: x.year)
            if latest.passing_score > 0:
                score_diff = self.profile.estimated_score - latest.passing_score
                if score_diff >= 10:  # 预估分比进面分高10分以上
                    return True

        return False

    def _calc_probability(self, job: Job, result: MatchResult) -> float:
        """
        计算上岸概率

        基于竞争比和分数预测的贝叶斯模型

        Args:
            job: 岗位
            result: 匹配结果

        Returns:
            float: 上岸概率 (0.0 - 0.95)
        """
        # 基础概率 = 1/(1+竞争比)
        if job.competition_ratio > 0:
            base_prob = 1.0 / (1.0 + job.competition_ratio)
        else:
            base_prob = 0.5  # 没有竞争数据，假设50%

        # 根据匹配分数调整
        score_factor = result.total_score / 100.0  # 0-1

        # 根据预估分数调整
        score_diff_factor = 1.0
        if job.historical_stats and self.profile.estimated_score > 0:
            latest = max(job.historical_stats.values(), key=lambda x: x.year)
            if latest.passing_score > 0:
                diff = self.profile.estimated_score - latest.passing_score
                # 每高1分，概率提高2%
                score_diff_factor = 1.0 + diff * 0.02

        # 综合计算
        prob = base_prob * (0.4 + 0.4 * score_factor) * min(max(score_diff_factor, 0.5), 1.5)

        # 限制在 0.01 - 0.95 之间
        return min(max(prob, 0.01), 0.95)


# 导出
__all__ = ["TierRecommender"]