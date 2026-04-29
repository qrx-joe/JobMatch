#!/usr/bin/env python3
"""
智能推荐器 - 基于多维度进行智能排序和推荐
"""

from typing import Dict, List, Optional, Callable

from ..models.job import Job, MatchLevel, RecommendationTier
from ..models.user_profile import UserProfile
from ..models.match_result import MatchResult


class SmartRecommender:
    """
    智能推荐器

    综合考虑以下因素进行推荐：
    1. 匹配度（匹配分数）
    2. 竞争比（越低越好）
    3. 上岸概率
    4. 用户偏好（意向城市等）
    5. 历史数据分析
    """

    def __init__(self, user_profile: UserProfile):
        """
        初始化智能推荐器

        Args:
            user_profile: 用户画像
        """
        self.profile = user_profile

    def recommend(
        self,
        jobs: List[Job],
        match_results: List[MatchResult],
        limit: int = 20,
        sort_by: str = "score",
    ) -> List[Job]:
        """
        智能推荐

        Args:
            jobs: 岗位列表
            match_results: 匹配结果
            limit: 返回数量限制
            sort_by: 排序方式
                - "score": 按匹配分数
                - "ratio": 按竞争比（低到高）
                - "probability": 按上岸概率
                - "comprehensive": 综合评分

        Returns:
            List[Job]: 推荐岗位列表
        """
        # 构建映射
        result_map = {r.job_id: r for r in match_results}

        # 计算综合评分
        scored_jobs = []
        for job in jobs:
            result = result_map.get(job.id)
            if not result:
                continue

            # 计算综合评分
            score = self._calc_comprehensive_score(job, result)
            scored_jobs.append((score, job))

        # 排序
        if sort_by == "score":
            scored_jobs.sort(key=lambda x: x[1].match_score, reverse=True)
        elif sort_by == "ratio":
            scored_jobs.sort(key=lambda x: x[1].competition_ratio)
        elif sort_by == "probability":
            scored_jobs.sort(key=lambda x: x[1].pass_probability, reverse=True)
        else:  # comprehensive
            scored_jobs.sort(key=lambda x: x[0], reverse=True)

        return [job for _, job in scored_jobs[:limit]]

    def _calc_comprehensive_score(self, job: Job, result: MatchResult) -> float:
        """
        计算综合评分

        综合评分 = 匹配分数权重 * 匹配分 + 竞争比权重 * (100 - 竞争比) + 偏好权重 * 偏好分

        Args:
            job: 岗位
            result: 匹配结果

        Returns:
            float: 综合评分 (0-100)
        """
        # 1. 匹配分数 (50%权重)
        match_score = result.total_score * 0.5

        # 2. 竞争比 (30%权重) - 竞争比越低越好，转换为 100 - ratio
        if job.competition_ratio > 0:
            ratio_score = max(0, 100 - job.competition_ratio) * 0.3
        else:
            ratio_score = 50 * 0.3  # 没有数据给50分

        # 3. 城市偏好 (20%权重)
        preference_score = 0.0
        if self.profile.target_cities and job.city in self.profile.target_cities:
            preference_score = 100 * 0.2
        elif self.profile.target_cities:
            preference_score = 0  # 非意向城市0分

        return match_score + ratio_score + preference_score

    def get_top_by_tier(
        self,
        jobs: List[Job],
        match_results: List[MatchResult],
        tier: str,
        limit: int = 10,
    ) -> List[Job]:
        """
        获取特定层级的最优岗位

        Args:
            jobs: 岗位列表
            match_results: 匹配结果
            tier: "冲刺" / "稳妥" / "保底"
            limit: 返回数量

        Returns:
            List[Job]: 该层级的推荐岗位
        """
        tier_mapping = {
            "冲刺": RecommendationTier.STRETCH,
            "稳妥": RecommendationTier.SAFE,
            "保底": RecommendationTier.BOTTOM,
        }

        target_tier = tier_mapping.get(tier)
        if not target_tier:
            return []

        # 过滤出该层级的岗位
        tier_jobs = [j for j in jobs if j.recommendation_tier == target_tier]

        # 重新排序
        result_map = {r.job_id: r for r in match_results}
        scored = []
        for job in tier_jobs:
            result = result_map.get(job.id)
            if result:
                score = self._calc_comprehensive_score(job, result)
                scored.append((score, job))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [job for _, job in scored[:limit]]

    def explain_recommendation(self, job: Job, result: MatchResult) -> Dict[str, any]:
        """
        解释推荐理由

        Args:
            job: 岗位
            result: 匹配结果

        Returns:
            Dict: 推荐理由解释
        """
        reasons = []

        # 专业匹配说明
        if result.major_match:
            reasons.append(result.major_match[1])

        # 学历匹配说明
        if result.education_match:
            reasons.append(result.education_match[1])

        # 竞争比说明
        if job.competition_ratio > 0:
            if job.competition_ratio < 20:
                reasons.append(f"竞争比较低({job.competition_ratio:.1f}:1)，成功概率较高")
            elif job.competition_ratio < 50:
                reasons.append(f"竞争比中等({job.competition_ratio:.1f}:1)")
            else:
                reasons.append(f"竞争比较激烈({job.competition_ratio:.1f}:1)")

        # 推荐层级说明
        if job.recommendation_tier:
            tier_desc = {
                RecommendationTier.STRETCH: "冲刺型岗位：专业要求严格匹配，竞争比相对较低",
                RecommendationTier.SAFE: "稳妥型岗位：整体匹配度较好，成功概率较高",
                RecommendationTier.BOTTOM: "保底型岗位：要求相对宽松，适合求稳",
            }
            reasons.append(tier_desc.get(job.recommendation_tier, ""))

        return {
            "job_id": job.id,
            "unit": job.unit,
            "city": job.city,
            "tier": job.recommendation_tier.value if job.recommendation_tier else None,
            "pass_probability": round(job.pass_probability * 100, 1),
            "reasons": reasons,
            "match_score": result.total_score,
            "competition_ratio": round(job.competition_ratio, 2),
        }


# 导出
__all__ = ["SmartRecommender"]