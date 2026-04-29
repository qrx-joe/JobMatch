#!/usr/bin/env python3
"""
JobMatch 完整流程演示脚本

演示从 Excel 解析 -> 智能匹配 -> 冲/稳/保推荐的全流程
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.data.excel.universal_parser import UniversalParser
from server.core.models.job import Job
from server.core.models.user_profile import UserProfile
from server.core.matchers.composite_matcher import CompositeMatcher
from server.core.recommenders.tier_recommender import TierRecommender
from server.core.recommenders.smart_recommender import SmartRecommender
from server.core.analyzers.historical_analyzer import HistoricalAnalyzer


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_job(job: Job, index: int = 1):
    """打印岗位信息"""
    print(f"\n【岗位 {index}】{job.unit}")
    print(f"  地市: {job.city}")
    print(f"  岗位类型: {job.job_type}")
    print(f"  招募人数: {job.recruit_count}")
    print(f"  学历要求: {job.education}")
    print(f"  专业要求: {job.major}")
    if job.age_limit:
        print(f"  年龄要求: {job.age_limit}")
    if job.political_requirement:
        print(f"  政治面貌: {job.political_requirement}")
    if job.competition_ratio > 0:
        print(f"  竞争比: {job.competition_ratio:.1f}:1")


def print_profile(profile: UserProfile):
    """打印用户画像"""
    print("\n【用户画像】")
    print(f"  专业: {profile.major}")
    print(f"  学历: {profile.education}")
    print(f"  性别: {profile.gender}")
    print(f"  年龄: {profile.age}")
    print(f"  户籍: {profile.household}")
    print(f"  政治面貌: {profile.party_status}")
    if profile.target_cities:
        print(f"  意向城市: {', '.join(profile.target_cities)}")
    if profile.estimated_score > 0:
        print(f"  预估分数: {profile.estimated_score}")


def print_match_result(result):
    """打印匹配结果"""
    print("\n【匹配结果】")
    print(f"  总分: {result.total_score}/100")
    print(f"  匹配等级: {result.match_level.value if result.match_level else '未知'}")

    if result.match_reasons:
        print("  匹配理由:")
        for reason in result.match_reasons:
            print(f"    ✓ {reason}")

    if result.mismatch_reasons:
        print("  不匹配理由:")
        for reason in result.mismatch_reasons:
            print(f"    ✗ {reason}")


def demo_with_excel(excel_path: str):
    """使用真实Excel文件的演示"""
    print_header("JobMatch 智能选岗平台 - 完整流程演示")

    # 步骤1: 解析Excel
    print_header("步骤1: Excel 解析")
    print(f"正在解析文件: {excel_path}")

    parser = UniversalParser(platform="sanzhiyifu")
    jobs = parser.parse(excel_path)

    print(f"\n成功解析 {len(jobs)} 个岗位")

    # 显示前3个岗位
    for i, job in enumerate(jobs[:3], 1):
        print_job(job, i)

    if len(jobs) > 3:
        print(f"\n... 还有 {len(jobs) - 3} 个岗位")

    return jobs


def demo_with_mock_data():
    """使用模拟数据的演示"""
    print_header("JobMatch 智能选岗平台 - 模拟数据演示")

    # 创建模拟岗位数据
    jobs = [
        Job(
            id=1,
            platform="三支一扶",
            city="太原市",
            unit="太原市小店区教育局",
            job_type="支教",
            recruit_count=2,
            education="本科及以上",
            major="教育学类",
            age_limit="30岁以下",
            competition_ratio=8.5,
            applicants=120,
            paid=17
        ),
        Job(
            id=2,
            platform="三支一扶",
            city="吕梁市",
            unit="吕梁市离石区农业农村局",
            job_type="支农",
            recruit_count=3,
            education="本科",
            major="农学类",
            age_limit="30岁以下",
            competition_ratio=15.2,
            applicants=280,
            paid=46
        ),
        Job(
            id=3,
            platform="三支一扶",
            city="运城市",
            unit="运城市中心医院",
            job_type="支医",
            recruit_count=5,
            education="本科及以上",
            major="临床医学",
            age_limit="35岁以下",
            competition_ratio=25.0,
            applicants=580,
            paid=125
        ),
        Job(
            id=4,
            platform="三支一扶",
            city="大同市",
            unit="大同市人社局",
            job_type="扶贫",
            recruit_count=4,
            education="大专及以上",
            major="不限",
            age_limit="28岁以下",
            competition_ratio=32.5,
            applicants=680,
            paid=130
        ),
        Job(
            id=5,
            platform="三支一扶",
            city="临汾市",
            unit="临汾市尧都区卫健局",
            job_type="支医",
            recruit_count=2,
            education="本科",
            major="护理学",
            age_limit="30岁以下",
            competition_ratio=5.8,
            applicants=68,
            paid=12
        ),
    ]

    print(f"\n创建了 {len(jobs)} 个模拟岗位")
    for i, job in enumerate(jobs, 1):
        print_job(job, i)

    return jobs


def demo_matching(jobs: list, profile: UserProfile):
    """演示匹配流程"""
    print_header("步骤2: 智能匹配")

    matcher = CompositeMatcher()
    match_results = []

    print(f"\n正在匹配 {len(jobs)} 个岗位...")

    for job in jobs:
        result = matcher.match(job, profile)
        match_results.append(result)

        # 只显示前3个的详情
        if job.id <= 3:
            print(f"\n--- 岗位: {job.unit} ---")
            print(f"  专业匹配: {result.major_match[1]}")
            print(f"  学历匹配: {result.education_match[1]}")
            print(f"  政治面貌匹配: {result.political_match[1]}")
            print(f"  年龄匹配: {result.age_match[1]}")
            print(f"  总分: {result.total_score}")

    # 统计匹配情况
    perfect = sum(1 for r in match_results if r.match_level and r.match_level.value == "完全符合")
    partial = sum(1 for r in match_results if r.match_level and r.match_level.value == "可能符合")
    mismatch = sum(1 for r in match_results if r.match_level and r.match_level.value == "不符合")

    print(f"\n【匹配统计】")
    print(f"  完全符合: {perfect} 个")
    print(f"  可能符合: {partial} 个")
    print(f"  不符合: {mismatch} 个")

    return match_results


def demo_recommendation(jobs: list, match_results: list, profile: UserProfile):
    """演示推荐流程"""
    print_header("步骤3: 冲/稳/保 推荐")

    # 1. 分层推荐
    recommender = TierRecommender(profile)
    tier_result = recommender.recommend(jobs, match_results)

    print("\n【分层推荐结果】")
    print(f"  冲刺: {len(tier_result['冲刺'])} 个岗位")
    print(f"  稳妥: {len(tier_result['稳妥'])} 个岗位")
    print(f"  保底: {len(tier_result['保底'])} 个岗位")

    # 显示各层级岗位
    for tier_name, tier_jobs in tier_result.items():
        if tier_jobs:
            print(f"\n  --- {tier_name}级岗位 ---")
            for job in tier_jobs[:3]:  # 最多显示3个
                prob = job.pass_probability * 100
                print(f"    {job.unit} | 竞争比 {job.competition_ratio:.1f}:1 | 上岸概率 {prob:.0f}%")

    # 2. 智能排序推荐
    smart_rec = SmartRecommender(profile)
    top_jobs = smart_rec.recommend(jobs, match_results, limit=5, sort_by="comprehensive")

    print("\n【综合排序TOP5】")
    for i, job in enumerate(top_jobs, 1):
        result = next((r for r in match_results if r.job_id == job.id), None)
        print(f"  {i}. {job.unit} | {job.city} | 匹配分 {result.total_score if result else 0}")

    return tier_result


def demo_historical_analysis():
    """演示历史分析"""
    print_header("步骤4: 历史数据分析")

    # 模拟历年数据
    from server.core.models.historical_stats import HistoricalStats

    historical_data = {
        2024: HistoricalStats(year=2024, recruitment_count=2, paid=17, competition_ratio=8.5, passing_score=58),
        2023: HistoricalStats(year=2023, recruitment_count=2, paid=15, competition_ratio=7.5, passing_score=55),
        2022: HistoricalStats(year=2022, recruitment_count=3, paid=12, competition_ratio=4.0, passing_score=52),
    }

    analyzer = HistoricalAnalyzer(historical_data)
    trend = analyzer.analyze_trend("太原市某区教育局")

    if trend:
        print("\n【历年趋势分析】")
        print(f"  单位: {trend.unit_name}")
        print(f"  平均竞争比: {trend.avg_competition_ratio:.1f}:1")
        print(f"  最高竞争比: {trend.max_competition_ratio:.1f}:1")
        print(f"  最低竞争比: {trend.min_competition_ratio:.1f}:1")
        print(f"  平均进面分: {trend.avg_passing_score:.1f}")
        print(f"  分数趋势: {trend.score_trend}")
        print(f"\n  预测明年竞争比: {trend.predicted_next_year_ratio:.1f}:1")
        print(f"  预测明年进面分: {trend.predicted_next_year_score:.1f}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="JobMatch 智能选岗演示")
    parser.add_argument("--excel", "-e", help="Excel文件路径")
    parser.add_argument("--profile", "-p", type=str, default="经济学,本科,女,25,山西,中共党员",
                        help="用户画像: 专业,学历,性别,年龄,户籍,政治面貌")
    args = parser.parse_args()

    # 解析用户画像
    profile_parts = args.profile.split(",")
    profile = UserProfile(
        major=profile_parts[0] if len(profile_parts) > 0 else "经济学",
        education=profile_parts[1] if len(profile_parts) > 1 else "本科",
        gender=profile_parts[2] if len(profile_parts) > 2 else "女",
        age=int(profile_parts[3]) if len(profile_parts) > 3 else 25,
        household=profile_parts[4] if len(profile_parts) > 4 else "山西",
        party_status=profile_parts[5] if len(profile_parts) > 5 else "中共党员",
        target_cities=["太原市", "吕梁市"],
        estimated_score=65.0
    )

    print_profile(profile)

    # 获取岗位数据
    if args.excel and os.path.exists(args.excel):
        jobs = demo_with_excel(args.excel)
    else:
        jobs = demo_with_mock_data()

    if not jobs:
        print("\n没有找到岗位数据，退出")
        return

    # 匹配
    match_results = demo_matching(jobs, profile)

    # 推荐
    demo_recommendation(jobs, match_results, profile)

    # 历史分析
    demo_historical_analysis()

    print_header("演示完成")
    print("\n如需查看完整功能，请启动后端服务:")
    print("  uv run python server/app.py")
    print("\n然后在微信开发者工具中导入 miniprogram 目录")


if __name__ == "__main__":
    main()