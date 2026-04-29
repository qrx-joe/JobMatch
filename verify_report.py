#!/usr/bin/env python3
"""
报告验证工具 - 验证JSON报告编码和内容
"""

import json
from pathlib import Path


def verify_latest_report():
    """验证最新的报告文件"""
    reports_dir = Path("reports")

    # 找到最新的JSON报告
    json_files = sorted(reports_dir.glob("*.json"))
    if not json_files:
        print("未找到JSON报告文件")
        return

    latest = json_files[-1]
    print(f"验证报告: {latest.name}")
    print("=" * 60)

    # 验证编码
    with open(latest, "rb") as f:
        raw = f.read()

    # 检查编码
    try:
        content = raw.decode("utf-8")
        print("[OK] 文件编码: UTF-8 (正确)")
    except UnicodeDecodeError:
        print("[ERROR] 文件编码错误: 不是有效的UTF-8")
        return

    # 解析JSON
    try:
        data = json.loads(content)
        print("[OK] JSON格式: 有效")
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON解析错误: {e}")
        return

    # 验证内容
    print("\n报告内容:")
    print(f"  生成时间: {data.get('report_info', {}).get('generated_at', 'N/A')}")
    print(f"  系统版本: {data.get('report_info', {}).get('version', 'N/A')}")
    print(f"  系统名称: {data.get('report_info', {}).get('source', 'N/A')}")

    print("\n用户信息:")
    profile = data.get("user_profile", {})
    print(f"  专业: {profile.get('major', 'N/A')}")
    print(f"  学历: {profile.get('education', 'N/A')}")
    print(f"  意向城市: {', '.join(profile.get('target_cities', []))}")

    print("\n匹配结果:")
    jobs = data.get("matched_jobs", [])
    summary = data.get("summary", {})
    print(f"  总岗位数: {summary.get('total', 0)}")
    print(f"  完全符合: {summary.get('perfect', 0)}")
    print(f"  可能符合: {summary.get('partial', 0)}")
    print(f"  平均匹配分: {summary.get('avg_score', 0):.1f}")

    if summary.get("with_historical") is not None:
        print(f"  含历史数据: {summary.get('with_historical', 0)}")

    print("\n前3个匹配岗位:")
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n  [{i}] {job.get('unit', 'N/A')}")
        print(f"      地区: {job.get('sheet_name', 'N/A')}")
        print(f"      专业: {job.get('major', 'N/A')}")
        print(f"      竞争比: {job.get('competition_ratio', 0):.1f}:1")
        print(f"      匹配度: {job.get('match_level', 'N/A')} ({job.get('match_score', 0)}分)")

        # 显示历史数据
        hist = job.get("historical_stats", {})
        if hist:
            print(f"      历史数据: {len(hist)} 年")
            for year in sorted(hist.keys()):
                stats = hist[year]
                print(
                    f"        {year}: 竞比{stats.get('competition_ratio', 0):.1f}:1 "
                    f"/ 分数{stats.get('pass_score', 0)}"
                )

        if job.get("predicted_score"):
            print(f"      预测分数: {job.get('predicted_score', 0):.1f}")
            print(f"      上岸概率: {job.get('pass_probability', 0):.0f}%")

    print("\n" + "=" * 60)
    print("[OK] 报告验证完成，编码和内容均正常")

    # 同时输出到文件（确保编码正确）
    output_file = reports_dir / "verification_result.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"报告文件: {latest.name}\n")
        f.write("=" * 60 + "\n")
        f.write("[OK] 文件编码: UTF-8 (正确)\n")
        f.write("[OK] JSON格式: 有效\n\n")
        f.write(f"系统名称: {data.get('report_info', {}).get('source', 'N/A')}\n")
        f.write(f"匹配岗位数: {len(jobs)}\n")
    print(f"\n验证结果已保存到: {output_file}")


if __name__ == "__main__":
    verify_latest_report()
