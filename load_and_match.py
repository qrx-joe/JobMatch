#!/usr/bin/env python3
"""
从数据库加载岗位数据并进行匹配

完整流程演示：
1. 从Excel导入数据到数据库
2. 从数据库查询岗位
3. 进行智能匹配
4. 输出推荐结果
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.data.database.connection import get_db_session, JobModel, init_db
from server.data.excel.job_pipeline import JobPipeline
from server.core.models.job import Job
from server.core.models.user_profile import UserProfile
from server.core.matchers.composite_matcher import CompositeMatcher
from server.core.recommenders.tier_recommender import TierRecommender


def load_excel_to_db(excel_path: str, platform: str = "三支一扶") -> int:
    """加载Excel到数据库"""
    print("=" * 60)
    print("  步骤1: Excel → 数据库")
    print("=" * 60)

    init_db()
    pipeline = JobPipeline()
    result = pipeline.parse_and_save(excel_path, platform)

    print(f"\n导入完成: {result['success']} 个岗位")
    return result['success']


def query_jobs_from_db(
    city: str = None,
    major: str = None,
    education: str = None,
    max_competition_ratio: float = None,
    limit: int = 100
) -> list:
    """从数据库查询岗位"""
    print("\n" + "=" * 60)
    print("  步骤2: 从数据库查询岗位")
    print("=" * 60)

    with get_db_session() as session:
        query = session.query(JobModel)

        if city:
            query = query.filter(JobModel.city == city)
        if major:
            query = query.filter(JobModel.major.like(f"%{major}%"))
        if education:
            query = query.filter(JobModel.education.like(f"%{education}%"))
        if max_competition_ratio:
            query = query.filter(JobModel.competition_ratio <= max_competition_ratio)

        query = query.limit(limit)

        models = query.all()
        print(f"查询到 {len(models)} 个岗位")

        # 转换为 Job 对象
        jobs = []
        for m in models:
            job = Job(
                id=m.id,
                platform=m.platform,
                city=m.city,
                unit=m.unit,
                job_type=m.job_type,
                service_category=m.service_category,
                recruit_count=m.recruit_count,
                education=m.education,
                degree=m.degree,
                major=m.major,
                age_limit=m.age_limit,
                political_requirement=m.political_requirement,
                qualifications=m.qualifications,
                other=m.other,
                applicants=m.applicants,
                approved=m.approved,
                paid=m.paid,
                competition_ratio=m.competition_ratio,
            )
            jobs.append(job)

        return jobs


def match_and_recommend(jobs: list, profile: UserProfile) -> dict:
    """匹配并推荐"""
    print("\n" + "=" * 60)
    print("  步骤3: 智能匹配")
    print("=" * 60)

    matcher = CompositeMatcher()
    recommender = TierRecommender(profile)

    match_results = []
    for job in jobs:
        result = matcher.match(job, profile)
        match_results.append(result)

    # 统计
    perfect = sum(1 for r in match_results if r.match_level and r.match_level.value == "完全符合")
    partial = sum(1 for r in match_results if r.match_level and r.match_level.value == "可能符合")
    print(f"匹配统计: 完全符合 {perfect}, 可能符合 {partial}")

    # 推荐
    tier_result = recommender.recommend(jobs, match_results)
    print(f"\n推荐结果:")
    print(f"  冲刺: {len(tier_result['冲刺'])} 个岗位")
    print(f"  稳妥: {len(tier_result['稳妥'])} 个岗位")
    print(f"  保底: {len(tier_result['保底'])} 个岗位")

    return tier_result


def display_results(tier_result: dict, limit: int = 5):
    """展示推荐结果"""
    print("\n" + "=" * 60)
    print("  推荐岗位详情")
    print("=" * 60)

    for tier_name, tier_jobs in tier_result.items():
        if not tier_jobs:
            continue

        print(f"\n【{tier_name}级岗位】")
        for i, job in enumerate(tier_jobs[:limit], 1):
            prob = job.pass_probability * 100
            print(f"  {i}. {job.unit}")
            print(f"     城市: {job.city} | 竞争比: {job.competition_ratio:.1f}:1 | 上岸概率: {prob:.0f}%")
            print(f"     专业: {job.major} | 学历: {job.education}")


def main():
    parser = argparse.ArgumentParser(description="Excel → 数据库 → 匹配 → 推荐")
    parser.add_argument("--excel", "-e", help="Excel文件路径（可选，不传则从数据库查询）")
    parser.add_argument("--platform", "-p", default="三支一扶", help="平台类型")
    parser.add_argument("--city", "-c", help="筛选城市")
    parser.add_argument("--major", "-m", help="筛选专业")
    parser.add_argument("--limit", "-l", type=int, default=50, help="查询数量限制")

    # 用户画像参数
    parser.add_argument("--user-major", default="经济学", help="用户专业")
    parser.add_argument("--user-edu", default="本科", help="用户学历")
    parser.add_argument("--user-gender", default="女", help="用户性别")
    parser.add_argument("--user-age", type=int, default=25, help="用户年龄")
    parser.add_argument("--user-household", default="山西", help="用户户籍")
    parser.add_argument("--user-party", default="群众", help="用户政治面貌")

    args = parser.parse_args()

    # 1. 可选：从Excel导入
    if args.excel and os.path.exists(args.excel):
        load_excel_to_db(args.excel, args.platform)
    else:
        init_db()
        print("\n跳过Excel导入（未指定或文件不存在）")

    # 2. 查询岗位
    jobs = query_jobs_from_db(
        city=args.city,
        major=args.major,
        limit=args.limit
    )

    if not jobs:
        print("\n没有找到匹配的岗位！")
        return

    # 3. 构建用户画像
    profile = UserProfile(
        major=args.user_major,
        education=args.user_edu,
        gender=args.user_gender,
        age=args.user_age,
        household=args.user_household,
        party_status=args.user_party,
        target_cities=[],
        estimated_score=65.0
    )

    print(f"\n用户画像: {profile.major} | {profile.education} | {profile.age}岁 | {profile.party_status}")

    # 4. 匹配推荐
    tier_result = match_and_recommend(jobs, profile)

    # 5. 展示结果
    display_results(tier_result)

    print("\n" + "=" * 60)
    print("  完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()