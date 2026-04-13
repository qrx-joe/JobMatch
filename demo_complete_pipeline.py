#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整流程演示 - 从Excel到匹配结果
展示端到端的岗位筛选流程
"""
import pandas as pd
import os
from typing import List, Dict
from dataclasses import asdict

# 导入所有模块
from excel_reader_v2 import SimpleJobReader as ExcelReader
from job_matcher_v3 import JobMatcherV3, Job, MatchLevel
from report_generator import ReportGenerator, MatchReport
from historical_analyzer import enrich_jobs_with_historical_data, HistoricalAnalyzer
import yaml


def load_jobs_from_excel(excel_path: str, stats_path: str = None) -> List[Job]:
    """
    从Excel加载岗位数据

    Args:
        excel_path: 岗位表Excel路径
        stats_path: 报名人数统计表路径（可选）

    Returns:
        List[Job]: 岗位列表
    """
    print(f"[1/4] 读取岗位表: {excel_path}")

    jobs = []

    try:
        # 读取岗位表
        reader = ExcelReader(excel_path)
        sheets_data = reader.read_all_sheets()

        print(f"      发现 {len(sheets_data)} 个地市数据")

        # 读取统计数据（如果提供）
        stats_data = {}
        if stats_path and os.path.exists(stats_path):
            print(f"[2/4] 读取报名人数统计: {stats_path}")
            stats_df = pd.read_excel(stats_path)
            # 假设统计表包含：单位名称、报名人数、初审通过、缴费人数
            for _, row in stats_df.iterrows():
                unit = str(row.get('单位名称', '')).strip()
                if unit:
                    stats_data[unit] = {
                        'applicants': int(row.get('填报信息人数', 0) or 0),
                        'approved': int(row.get('初审通过人数', 0) or 0),
                        'paid': int(row.get('缴费人数', 0) or 0)
                    }
            print(f"      加载了 {len(stats_data)} 条统计数据")

        # 转换数据为Job对象
        for sheet_name, df in sheets_data.items():
            print(f"      处理 [{sheet_name}] - {len(df)} 条记录")

            for idx, row in df.iterrows():
                try:
                    # 智能字段映射
                    job = Job(
                        sheet_name=sheet_name,
                        index=idx + 1,
                        unit=_get_field(row, ['服务单位', '单位名称', '用人单位', '单位']),
                        job_type=_get_field(row, ['岗位类型', '职位类型', '类别']),
                        service_category=_get_field(row, ['服务类别', '服务类型']),
                        recruit_count=_parse_int(_get_field(row, ['招募人数', '招录人数', '人数', '计划']), 1),
                        education=_get_field(row, ['学历要求', '学历', '文化程度']),
                        degree=_get_field(row, ['学位要求', '学位']),
                        major=_get_field(row, ['专业要求', '专业', '所需专业']),
                        qualifications=_get_field(row, ['相关资格', '资格证书', '职业资格']),
                        other=_get_field(row, ['其他要求', '备注', '其他条件', '备注说明']),
                        phone=_get_field(row, ['联系电话', '电话', '联系方式']),
                        contact=_get_field(row, ['联系人', '负责人'])
                    )

                    # 关联统计数据
                    unit = job.unit
                    if unit in stats_data:
                        job.applicants = stats_data[unit]['applicants']
                        job.approved = stats_data[unit]['approved']
                        job.paid = stats_data[unit]['paid']
                        # 计算竞争比
                        if job.recruit_count > 0:
                            job.competition_ratio = job.paid / job.recruit_count

                    jobs.append(job)

                except Exception as e:
                    print(f"        警告: 第{idx+1}行解析失败 - {e}")
                    continue

        print(f"[OK] 成功加载 {len(jobs)} 个岗位")
        return jobs

    except Exception as e:
        print(f"[错误] 读取Excel失败: {e}")
        return []


def _get_field(row, possible_names: List[str]) -> str:
    """智能获取字段值"""
    for name in possible_names:
        if name in row.index:
            value = row[name]
            if pd.notna(value):
                return str(value).strip()
    return ""


def _parse_int(value, default: int = 0) -> int:
    """安全解析整数"""
    if pd.isna(value):
        return default
    try:
        return int(float(str(value).strip()))
    except:
        return default


def filter_and_match_jobs(
    jobs: List[Job],
    config_path: str = "config_full.yaml",
    min_match_score: int = 50,
    max_competition_ratio: float = 100.0
) -> List[Job]:
    """
    筛选并匹配岗位

    Args:
        jobs: 岗位列表
        config_path: 配置文件路径
        min_match_score: 最低匹配分数
        max_competition_ratio: 最大竞争比

    Returns:
        List[Job]: 匹配结果
    """
    print(f"[3/4] 开始匹配岗位...")

    # 创建匹配器
    matcher = JobMatcherV3(config_path)

    print(f"      用户档案:")
    print(f"        专业: {matcher.profile.major}")
    print(f"        学历: {matcher.profile.education}")
    print(f"        户籍: {matcher.profile.household or '不限'}")
    print(f"        意向城市: {', '.join(matcher.profile.target_cities) or '不限'}")

    matched_jobs = []

    for job in jobs:
        # 执行匹配
        result = matcher.match(job)

        # 过滤条件
        if result.match_score < min_match_score:
            continue

        if result.competition_ratio > max_competition_ratio:
            continue

        # 只保留符合和可能符合的
        if result.match_level in [MatchLevel.PERFECT, MatchLevel.PARTIAL]:
            matched_jobs.append(result)

    # 按匹配分数排序
    matched_jobs.sort(key=lambda x: x.match_score, reverse=True)

    print(f"[OK] 匹配完成: {len(matched_jobs)} 个符合条件的岗位")
    return matched_jobs


def analyze_competition(jobs: List[Job]) -> Dict:
    """分析竞争情况"""
    if not jobs:
        return {}

    total_jobs = len(jobs)

    # 竞争比分布
    low_competition = [j for j in jobs if j.competition_ratio < 10]  # 低竞争
    mid_competition = [j for j in jobs if 10 <= j.competition_ratio < 30]  # 中等
    high_competition = [j for j in jobs if j.competition_ratio >= 30]  # 高竞争

    # 最容易的岗位
    easiest = sorted([j for j in jobs if j.competition_ratio > 0],
                    key=lambda x: x.competition_ratio)[:5]

    return {
        "total": total_jobs,
        "low_competition": len(low_competition),
        "mid_competition": len(mid_competition),
        "high_competition": len(high_competition),
        "avg_ratio": sum(j.competition_ratio for j in jobs) / total_jobs if jobs else 0,
        "easiest_jobs": easiest
    }


def display_results(jobs: List[Job], show_top: int = 10):
    """显示匹配结果"""
    print(f"\n{'='*80}")
    print(f"匹配结果 (前{min(show_top, len(jobs))}个)")
    print(f"{'='*80}")

    for i, job in enumerate(jobs[:show_top], 1):
        # 竞争比显示
        ratio_str = f"{job.competition_ratio:.1f}:1" if job.competition_ratio > 0 else "暂无"

        # 难度评级
        if job.competition_ratio < 10:
            difficulty = "[容易]"
        elif job.competition_ratio < 30:
            difficulty = "[中等]"
        else:
            difficulty = "[困难]"

        # 报名数据
        stats = f"报名{job.applicants}/初审{job.approved}/缴费{job.paid}" if job.paid > 0 else "暂无报名数据"

        print(f"\n[{i}] {job.unit}")
        print(f"    [地区] {job.sheet_name} | {job.job_type}")
        print(f"    [专业] {job.major} | 学历: {job.education}")
        print(f"    [人数] 招募: {job.recruit_count}人 | 竞争比: {ratio_str} {difficulty}")
        print(f"    [统计] {stats}")
        print(f"    [匹配] {job.match_level.value} | 分数: {job.match_score}")

        if job.match_reasons:
            print(f"    [原因]")
            for reason in job.match_reasons[:3]:
                print(f"       - {reason}")


def export_results(jobs: List[Job], profile: dict, output_dir: str = "reports", config: dict = None):
    """导出结果（支持历史数据）"""
    print(f"\n[导出报告]")

    # 准备数据
    jobs_data = []
    for job in jobs:
        job_dict = {
            'sheet_name': job.sheet_name,
            'unit': job.unit,
            'job_type': job.job_type,
            'major': job.major,
            'education': job.education,
            'recruit_count': job.recruit_count,
            'applicants': job.applicants,
            'approved': job.approved,
            'paid': job.paid,
            'competition_ratio': job.competition_ratio,
            'match_level': job.match_level.value,
            'match_score': job.match_score,
            'match_reasons': job.match_reasons,
            # 历史数据字段
            'historical_stats': job.historical_stats,
            'predicted_score': job.predicted_score,
            'difficulty_trend': job.difficulty_trend,
            'pass_probability': job.pass_probability
        }
        jobs_data.append(job_dict)

    # 创建报告
    report = MatchReport(
        user_major=profile.get('major', ''),
        user_education=profile.get('education', ''),
        user_degree=profile.get('degree', ''),
        matched_jobs=jobs_data,
        summary={
            'total': len(jobs),
            'perfect': sum(1 for j in jobs if j.match_level == MatchLevel.PERFECT),
            'partial': sum(1 for j in jobs if j.match_level == MatchLevel.PARTIAL),
            'avg_score': sum(j.match_score for j in jobs) / len(jobs) if jobs else 0,
            'avg_competition': sum(j.competition_ratio for j in jobs) / len(jobs) if jobs else 0,
            # 历史数据统计
            'with_historical': sum(1 for j in jobs if j.historical_stats),
            'avg_predicted_score': (sum(j.predicted_score for j in jobs if j.predicted_score > 0) /
                                   sum(1 for j in jobs if j.predicted_score > 0))
                                   if sum(1 for j in jobs if j.predicted_score > 0) > 0 else 0
        }
    )

    generator = ReportGenerator(output_dir)

    # 生成各种格式
    json_path = generator.generate_json(report)
    print(f"  JSON: {json_path}")

    html_path = generator.generate_html(report)
    print(f"  HTML: {html_path}")

    try:
        excel_path = generator.generate_excel(report)
        print(f"  Excel: {excel_path}")
    except Exception as e:
        print(f"  Excel生成失败: {e}")

    return {
        'json': json_path,
        'html': html_path,
        'excel': excel_path if 'excel_path' in locals() else None
    }

    return {
        'json': json_path,
        'html': html_path
    }


def demo_with_mock_data():
    """使用模拟数据演示完整流程"""
    print("="*80)
    print("完整流程演示 - 三支一扶智能选岗系统")
    print("="*80)
    print()

    # 创建模拟岗位数据
    mock_jobs = [
        Job(
            sheet_name="济南市",
            unit="济南市财政局",
            job_type="支农",
            major="经济学类",
            education="本科及以上",
            recruit_count=5,
            applicants=60,
            approved=45,
            paid=40,
            competition_ratio=8.0  # 40/5=8
        ),
        Job(
            sheet_name="济南市",
            unit="济南市统计局",
            job_type="支农",
            major="统计学类",
            education="本科及以上",
            recruit_count=3,
            applicants=90,
            approved=75,
            paid=60,
            competition_ratio=20.0  # 60/3=20
        ),
        Job(
            sheet_name="青岛市",
            unit="青岛市教育局",
            job_type="支教",
            major="教育学类",
            education="本科及以上",
            recruit_count=10,
            applicants=500,
            approved=400,
            paid=350,
            competition_ratio=35.0  # 350/10=35
        ),
        Job(
            sheet_name="青岛市",
            unit="青岛市卫健委",
            job_type="支医",
            major="医学类",
            education="本科及以上",
            recruit_count=8,
            applicants=80,
            approved=60,
            paid=48,
            competition_ratio=6.0  # 48/8=6
        ),
        Job(
            sheet_name="烟台市",
            unit="烟台市人社局",
            job_type="支农",
            major="经济学类",
            education="硕士及以上",
            recruit_count=2,
            applicants=100,
            approved=80,
            paid=70,
            competition_ratio=35.0  # 70/2=35
        )
    ]

    print(f"[模拟数据] 创建了 {len(mock_jobs)} 个岗位")

    # 执行匹配
    matched_jobs = filter_and_match_jobs(mock_jobs, max_competition_ratio=50)

    # 显示结果
    display_results(matched_jobs)

    # 竞争分析
    analysis = analyze_competition(matched_jobs)
    print(f"\n{'='*80}")
    print("竞争分析")
    print(f"{'='*80}")
    print(f"  总岗位数: {analysis['total']}")
    print(f"  低竞争(<10:1): {analysis['low_competition']}个")
    print(f"  中竞争(10-30:1): {analysis['mid_competition']}个")
    print(f"  高竞争(>30:1): {analysis['high_competition']}个")
    print(f"  平均竞争比: {analysis['avg_ratio']:.1f}:1")

    if analysis['easiest_jobs']:
        print(f"\n  最容易的岗位:")
        for job in analysis['easiest_jobs']:
            print(f"    - {job.unit} - 竞争比 {job.competition_ratio:.1f}:1")

    # 导出报告
    profile = {'major': '金融学', 'education': '本科', 'degree': '学士'}
    export_paths = export_results(matched_jobs, profile)

    print(f"\n{'='*80}")
    print("演示完成！")
    print(f"{'='*80}")
    print(f"报告已生成:")
    for format_type, path in export_paths.items():
        print(f"  {format_type.upper()}: {path}")


def load_config(config_path: str = "config_full.yaml") -> dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"警告: 读取配置文件失败: {e}")
        return {}


def run_with_config(config_path: str = "config_full.yaml"):
    """
    使用配置文件的完整流程

    Args:
        config_path: 配置文件路径
    """
    print("=" * 80)
    print("三支一扶智能选岗系统 - 历史数据分析版")
    print("=" * 80)

    # 1. 加载配置
    config = load_config(config_path)
    print(f"\n[配置] 已加载: {config_path}")

    # 2. 获取岗位表路径（从配置或命令行）
    jobs_file = config.get('data', {}).get('jobs_file', '岗位表.xlsx')

    if not os.path.exists(jobs_file):
        print(f"错误: 岗位表不存在: {jobs_file}")
        print("使用模拟数据演示...")
        demo_with_mock_data()
        return

    # 3. 加载岗位数据
    jobs = load_jobs_from_excel(jobs_file)

    if not jobs:
        print("错误: 未能加载岗位数据")
        return

    # 4. 历史数据分析（新增）
    historical_config = config.get('historical_data', {})
    if historical_config.get('启用', False):
        jobs = enrich_jobs_with_historical_data(jobs, historical_config)

    # 5. 匹配筛选
    matched_jobs = filter_and_match_jobs(jobs, config_path)

    # 6. 显示结果（增强版）
    display_results_with_history(matched_jobs, show_top=20)

    # 7. 导出报告
    profile = config.get('profile', {})
    export_results(matched_jobs, profile, config=config)

    print(f"\n{'=' * 80}")
    print("分析完成！")
    print(f"{'=' * 80}")


def display_results_with_history(jobs: List[Job], show_top: int = 10):
    """显示带历史数据的匹配结果"""
    print(f"\n{'=' * 80}")
    print(f"匹配结果 - 含历史数据分析 (前{min(show_top, len(jobs))}个)")
    print(f"{'=' * 80}")

    for i, job in enumerate(jobs[:show_top], 1):
        # 竞争比显示
        ratio_str = f"{job.competition_ratio:.1f}:1" if job.competition_ratio > 0 else "暂无"

        # 难度评级
        if job.competition_ratio < 10:
            difficulty = "[容易]"
        elif job.competition_ratio < 30:
            difficulty = "[中等]"
        else:
            difficulty = "[困难]"

        # 报名数据
        stats = f"报名{job.applicants}/初审{job.approved}/缴费{job.paid}" if job.paid > 0 else "暂无报名数据"

        print(f"\n[{i}] {job.unit}")
        print(f"    [地区] {job.sheet_name} | {job.job_type}")
        print(f"    [专业] {job.major} | 学历: {job.education}")
        print(f"    [人数] 招募: {job.recruit_count}人 | 竞争比: {ratio_str} {difficulty}")
        print(f"    [统计] {stats}")
        print(f"    [匹配] {job.match_level.value} | 分数: {job.match_score}")

        # 显示历史数据分析（新增）
        if job.historical_stats:
            print(f"    [历史] ", end="")
            years = sorted(job.historical_stats.keys())
            for year in years:
                stats = job.historical_stats[year]
                ratio = stats.get('competition_ratio', 0)
                score = stats.get('pass_score', 0)
                print(f"{year}年(竞比{ratio:.1f}:1/分数{score}) ", end="")
            print()

            if job.predicted_score > 0:
                print(f"    [预测] 今年预测上岸分: {job.predicted_score:.1f}分 | 趋势: {job.difficulty_trend}")
                print(f"    [概率] 你的上岸概率: {job.pass_probability:.0f}%")

        if job.match_reasons:
            print(f"    [原因]")
            for reason in job.match_reasons[:3]:
                print(f"       - {reason}")


def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1:
        # 检查是否是配置文件模式
        if sys.argv[1].endswith('.yaml') or sys.argv[1].endswith('.yml'):
            # 配置文件模式: python demo.py config.yaml
            run_with_config(sys.argv[1])
        else:
            # 传统模式: python demo.py 岗位表.xlsx [统计表.xlsx]
            excel_path = sys.argv[1]
            stats_path = sys.argv[2] if len(sys.argv) > 2 else None

            print(f"从Excel加载: {excel_path}")
            jobs = load_jobs_from_excel(excel_path, stats_path)

            if jobs:
                matched_jobs = filter_and_match_jobs(jobs)
                display_results(matched_jobs, show_top=20)
                export_results(matched_jobs, {'major': '金融学', 'education': '本科'})
    else:
        # 检查是否存在默认配置文件
        if os.path.exists('config_full.yaml'):
            run_with_config('config_full.yaml')
        else:
            # 使用模拟数据演示
            demo_with_mock_data()


if __name__ == "__main__":
    main()
