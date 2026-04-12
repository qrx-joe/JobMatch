#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
岗位筛选主程序
"""
import os
import sys

# 修复Windows终端编码问题
if sys.platform == 'win32':
    import io
    # 强制使用UTF-8编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import glob
import argparse
from typing import List
from job_matcher import JobMatcher, Job, MatchLevel
from excel_reader_v2 import SimpleJobReader as JobExcelReader, StatsReader as StatsExcelReader
from excel_exporter import ExcelExporter
import yaml


def find_files() -> tuple:
    """查找岗位表和统计表文件"""
    # 岗位表
    job_files = glob.glob('*岗位汇总表*.xlsx') + glob.glob('*岗位汇总表*.xls')
    job_files = [f for f in job_files if not os.path.basename(f).startswith('~$')]

    # 统计表
    stats_files = glob.glob('P0*.xls') + glob.glob('*统计*.xls') + glob.glob('*统计*.xlsx')
    stats_files = [f for f in stats_files if not os.path.basename(f).startswith('~$')]

    return job_files, stats_files


def filter_jobs(jobs: List[Job], matcher: JobMatcher) -> List[Job]:
    """对所有岗位进行匹配"""
    print("\n开始匹配岗位...")

    for i, job in enumerate(jobs):
        matcher.match(job)
        if (i + 1) % 50 == 0:
            print(f"  已处理 {i + 1}/{len(jobs)} 个岗位")

    print(f"  完成！共处理 {len(jobs)} 个岗位")

    return jobs


def associate_stats(jobs: List[Job], stats_reader: StatsExcelReader) -> List[Job]:
    """关联竞争数据"""
    print("\n关联竞争数据...")

    matched = 0
    for job in jobs:
        stats = stats_reader.match_job(job)
        if stats:
            job.applicants = stats['applicants']
            job.approved = stats['approved']
            job.paid = stats['paid']
            matched += 1

    print(f"  成功关联 {matched}/{len(jobs)} 个岗位的竞争数据")

    return jobs


def print_summary(jobs: List[Job]):
    """打印汇总信息"""
    print("\n" + "=" * 80)
    print("筛选结果汇总")
    print("=" * 80)

    # 按匹配等级统计
    perfect = [j for j in jobs if j.match_level == MatchLevel.PERFECT]
    partial = [j for j in jobs if j.match_level == MatchLevel.PARTIAL]
    mismatch = [j for j in jobs if j.match_level == MatchLevel.MISMATCH]

    print(f"\n匹配统计:")
    print(f"  完全符合: {len(perfect)} 个岗位")
    print(f"  可能符合: {len(partial)} 个岗位")
    print(f"  不符合:   {len(mismatch)} 个岗位")

    # 按城市统计
    print(f"\n按地市统计（完全符合）:")
    city_counts = {}
    for job in perfect:
        city_counts[job.sheet_name] = city_counts.get(job.sheet_name, 0) + 1

    for city, count in sorted(city_counts.items(), key=lambda x: -x[1]):
        print(f"  {city}: {count} 个")

    # 竞争比分析
    print(f"\n竞争比分析（完全符合且有数据的岗位）:")
    jobs_with_data = [j for j in perfect if j.paid > 0]
    if jobs_with_data:
        ratios = [j.competition_ratio for j in jobs_with_data]
        avg_ratio = sum(ratios) / len(ratios)
        min_ratio = min(ratios)
        max_ratio = max(ratios)

        print(f"  平均竞争比: {avg_ratio:.1f}:1")
        print(f"  最低竞争比: {min_ratio:.1f}:1")
        print(f"  最高竞争比: {max_ratio:.1f}:1")

        # 竞争比分布
        low = len([r for r in ratios if r < 30])
        mid = len([r for r in ratios if 30 <= r < 100])
        high = len([r for r in ratios if r >= 100])

        print(f"\n  竞争比分布:")
        print(f"    低竞争(<30:1):  {low} 个")
        print(f"    中竞争(30-100): {mid} 个")
        print(f"    高竞争(>100):   {high} 个")

    # 显示前10个最匹配的岗位
    print(f"\n前10个最匹配的岗位（按竞争比升序）:")
    sorted_jobs = sorted(jobs_with_data, key=lambda j: j.competition_ratio)

    for i, job in enumerate(sorted_jobs[:10], 1):
        ratio_str = f"{job.competition_ratio:.1f}:1" if job.paid > 0 else "暂无数据"
        print(f"\n  [{i}] {job.sheet_name} - {job.unit}")
        print(f"      岗位: {job.job_type} | 专业: {job.major}")
        print(f"      竞争比: {ratio_str} (招{job.recruit_count}人，{job.paid}人缴费)")


def main():
    parser = argparse.ArgumentParser(description='三支一扶岗位筛选工具')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径')
    parser.add_argument('--output', '-o', default='筛选结果.xlsx', help='输出文件路径')
    parser.add_argument('--mode', '-m', default='full', choices=['full', 'match_only'],
                       help='输出模式: full=全量标记, match_only=仅匹配的')
    args = parser.parse_args()

    print("=" * 80)
    print("三支一扶岗位筛选工具")
    print("=" * 80)

    # 1. 加载配置
    print("\n[1/5] 加载配置...")
    if not os.path.exists(args.config):
        print(f"错误: 配置文件不存在: {args.config}")
        sys.exit(1)

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    print(f"  配置文件: {args.config}")
    print(f"  专业: {config['profile']['专业']}")
    print(f"  学历: {config['profile']['学历']}")
    print(f"  性别: {config['profile']['性别']}")
    print(f"  户籍: {config['profile']['户籍']}")
    print(f"  意向城市: {config['preference']['意向城市']}")

    # 2. 查找文件
    print("\n[2/5] 查找数据文件...")
    job_files, stats_files = find_files()

    if not job_files:
        print("错误: 未找到岗位表文件")
        sys.exit(1)

    job_file = job_files[0]
    print(f"  岗位表: {job_file}")

    if stats_files:
        stats_file = stats_files[0]
        print(f"  统计表: {stats_file}")
    else:
        stats_file = None
        print("  警告: 未找到统计表，将不包含竞争数据")

    # 3. 读取岗位表
    print("\n[3/5] 读取岗位表...")
    job_reader = JobExcelReader(job_file)
    jobs = job_reader.read_all()

    if not jobs:
        print("错误: 未读取到任何岗位数据")
        sys.exit(1)

    print(f"  共读取 {len(jobs)} 个岗位")

    # 4. 读取统计表并关联数据
    if stats_file:
        print("\n[4/5] 读取统计表...")
        stats_reader = StatsExcelReader(stats_file)
        stats_reader.read()
        jobs = associate_stats(jobs, stats_reader)
    else:
        print("\n[4/5] 跳过统计表...")

    # 5. 匹配岗位
    print("\n[5/5] 匹配岗位...")
    matcher = JobMatcher(args.config)
    jobs = filter_jobs(jobs, matcher)

    # 6. 打印汇总
    print_summary(jobs)

    # 7. 导出Excel
    print(f"\n导出Excel文件: {args.output}")
    exporter = ExcelExporter(args.config)
    exporter.export(jobs, args.output)

    print(f"\n[OK] 完成！结果已保存到: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()
