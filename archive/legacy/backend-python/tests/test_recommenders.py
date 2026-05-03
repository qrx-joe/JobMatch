#!/usr/bin/env python3
"""
测试推荐器
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.core.models.job import Job, RecommendationTier
from server.core.models.user_profile import UserProfile
from server.core.models.match_result import MatchResult
from server.core.recommenders.tier_recommender import TierRecommender


def test_tier_recommender():
    """测试冲/稳/保推荐器"""
    # 创建用户画像
    profile = UserProfile(
        major="经济学",
        education="本科",
        party_status="中共党员",
        estimated_score=65.0,
    )

    # 创建测试岗位
    jobs = [
        Job(id=1, unit="单位1", major="经济学", competition_ratio=10.0),
        Job(id=2, unit="单位2", major="经济学", competition_ratio=50.0),
        Job(id=3, unit="单位3", major="不限", competition_ratio=5.0),
    ]

    # 创建匹配结果
    match_results = [
        MatchResult(job_id=1, total_score=85, major_match=(True, "专业匹配")),
        MatchResult(job_id=2, total_score=80, major_match=(True, "专业匹配")),
        MatchResult(job_id=3, total_score=50, major_match=(True, "专业不限")),
    ]

    # 进行推荐
    recommender = TierRecommender(profile)
    result = recommender.recommend(jobs, match_results)

    print("推荐结果:")
    print(f"  冲刺: {len(result['冲刺'])} 个岗位")
    print(f"  稳妥: {len(result['稳妥'])} 个岗位")
    print(f"  保底: {len(result['保底'])} 个岗位")

    # 验证
    assert len(result["冲刺"]) > 0 or len(result["稳妥"]) > 0 or len(result["保底"]) > 0

    print("✓ 推荐器测试通过")


def test_probability_calculation():
    """测试概率计算"""
    profile = UserProfile(
        major="经济学",
        education="本科",
        estimated_score=70.0,
    )

    job = Job(id=1, unit="测试单位", major="经济学", competition_ratio=20.0)
    result = MatchResult(job_id=1, total_score=85, major_match=(True, "匹配"))

    recommender = TierRecommender(profile)
    prob = recommender._calc_probability(job, result)

    print(f"计算的上岸概率: {prob:.2%}")
    assert 0 < prob < 1, "概率应在0-1之间"

    print("✓ 概率计算测试通过")


if __name__ == "__main__":
    test_tier_recommender()
    test_probability_calculation()
    print("\n所有推荐器测试通过! ✓")