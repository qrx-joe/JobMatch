#!/usr/bin/env python3
"""
匹配报告导出器 - 支持PDF和Excel格式
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MatchReport:
    """匹配报告数据"""

    user_major: str
    user_education: str
    user_degree: str
    target_jobs: list[dict]
    filter_criteria: dict
    summary: dict
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ReportExporter:
    """报告导出器"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_json(self, report: MatchReport, filename: str = None) -> str:
        """导出为JSON格式"""
        if not filename:
            filename = f"match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join(self.output_dir, filename)

        data = {
            "generated_at": report.generated_at,
            "user_profile": {
                "major": report.user_major,
                "education": report.user_education,
                "degree": report.user_degree,
            },
            "filter_criteria": report.filter_criteria,
            "summary": report.summary,
            "target_jobs": report.target_jobs,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def export_html(self, report: MatchReport, filename: str = None) -> str:
        """导出为HTML报告"""
        if not filename:
            filename = f"match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        filepath = os.path.join(self.output_dir, filename)

        # 统计
        total = len(report.target_jobs)
        perfect = sum(1 for j in report.target_jobs if j.get("level") == "完全符合")
        partial = sum(1 for j in report.target_jobs if j.get("level") == "可能符合")

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>三支一扶岗位匹配报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header .meta {{ opacity: 0.9; font-size: 14px; }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .card .number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }}
        .card .label {{ color: #666; font-size: 14px; }}

        .section {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .section h2 {{
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}

        .profile-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
        }}
        .profile-item {{
            display: flex;
            justify-content: space-between;
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .profile-item .label {{ color: #666; }}
        .profile-item .value {{ font-weight: 500; }}

        .job-list {{ display: flex; flex-direction: column; gap: 16px; }}
        .job-item {{
            border: 1px solid #e8e8e8;
            border-radius: 10px;
            padding: 20px;
            transition: box-shadow 0.2s;
        }}
        .job-item:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .job-title {{ font-size: 18px; font-weight: 600; }}
        .job-location {{ color: #666; font-size: 14px; }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        .badge-perfect {{ background: #d4edda; color: #155724; }}
        .badge-partial {{ background: #fff3cd; color: #856404; }}
        .badge-mismatch {{ background: #f8d7da; color: #721c24; }}

        .job-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-top: 12px;
            font-size: 14px;
        }}
        .detail-item {{ display: flex; gap: 8px; }}
        .detail-item .label {{ color: #888; }}

        .reasons {{
            margin-top: 12px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 13px;
        }}
        .reasons .title {{ color: #667eea; font-weight: 500; margin-bottom: 6px; }}
        .reasons ul {{ padding-left: 18px; }}
        .reasons li {{ margin: 4px 0; }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: #888;
            font-size: 12px;
        }}

        @media print {{
            body {{ background: white; }}
            .section {{ box-shadow: none; border: 1px solid #ddd; }}
            .header {{ -webkit-print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>三支一扶岗位匹配报告</h1>
            <div class="meta">生成时间: {report.generated_at}</div>
        </div>

        <div class="summary-cards">
            <div class="card">
                <div class="number">{total}</div>
                <div class="label">匹配岗位总数</div>
            </div>
            <div class="card">
                <div class="number" style="color: #28a745;">{perfect}</div>
                <div class="label">完全符合</div>
            </div>
            <div class="card">
                <div class="number" style="color: #ffc107;">{partial}</div>
                <div class="label">可能符合</div>
            </div>
            <div class="card">
                <div class="number" style="color: #17a2b8;">{report.summary.get("avg_score", 0):.0f}</div>
                <div class="label">平均匹配分</div>
            </div>
        </div>

        <div class="section">
            <h2>用户档案</h2>
            <div class="profile-grid">
                <div class="profile-item">
                    <span class="label">专业</span>
                    <span class="value">{report.user_major}</span>
                </div>
                <div class="profile-item">
                    <span class="label">学历</span>
                    <span class="value">{report.user_education}</span>
                </div>
                <div class="profile-item">
                    <span class="label">学位</span>
                    <span class="value">{report.user_degree}</span>
                </div>
            </div>
        </div>
"""

        # 添加岗位列表
        html += """
        <div class="section">
            <h2>推荐岗位</h2>
            <div class="job-list">
"""

        for job in report.target_jobs:
            level = job.get("level", "不符合")
            badge_class = {
                "完全符合": "badge-perfect",
                "可能符合": "badge-partial",
                "不符合": "badge-mismatch",
            }.get(level, "badge-mismatch")

            match_reasons = job.get("match_reasons", [])
            reasons_html = ""
            if match_reasons:
                reasons_list = "".join([f"<li>{r}</li>" for r in match_reasons])
                reasons_html = f'<div class="reasons"><div class="title">匹配理由</div><ul>{reasons_list}</ul></div>'

            html += f"""
                <div class="job-item">
                    <div class="job-header">
                        <div>
                            <div class="job-title">{job.get("unit", "未知单位")}</div>
                            <div class="job-location">{job.get("city", "未知城市")} | {job.get("job_type", "未知类型")}</div>
                        </div>
                        <span class="badge {badge_class}">{level}</span>
                    </div>
                    <div class="job-details">
                        <div class="detail-item">
                            <span class="label">专业要求:</span>
                            <span>{job.get("major", "不限")}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">学历要求:</span>
                            <span>{job.get("education", "不限")}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">招募人数:</span>
                            <span>{job.get("recruit_count", 1)}人</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">竞争比:</span>
                            <span>{job.get("competition_ratio", "N/A")}</span>
                        </div>
                    </div>
                    {reasons_html}
                </div>
"""

        html += """
            </div>
        </div>

        <div class="footer">
            <p>本报告由AI智能选岗系统生成，仅供参考</p>
            <p>最终报考请以官方公告为准</p>
        </div>
    </div>
</body>
</html>
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        return filepath

    def create_sample_report(self) -> MatchReport:
        """创建示例报告"""
        return MatchReport(
            user_major="金融学",
            user_education="本科",
            user_degree="学士",
            target_jobs=[
                {
                    "unit": "某市财政局",
                    "city": "济南市",
                    "job_type": "支农",
                    "major": "经济学类",
                    "education": "本科及以上",
                    "recruit_count": 5,
                    "competition_ratio": "12:1",
                    "level": "完全符合",
                    "match_score": 95,
                    "match_reasons": [
                        "专业匹配：金融学属于经济学类",
                        "学历符合：本科符合要求",
                        "意向城市匹配",
                    ],
                },
                {
                    "unit": "某县统计局",
                    "city": "青岛市",
                    "job_type": "支农",
                    "major": "统计学类",
                    "education": "本科及以上",
                    "recruit_count": 3,
                    "competition_ratio": "8:1",
                    "level": "可能符合",
                    "match_score": 75,
                    "match_reasons": ["专业相关：金融学与统计学高度相关", "学历符合：本科符合要求"],
                },
                {
                    "unit": "某市教育局",
                    "city": "烟台市",
                    "job_type": "支教",
                    "major": "教育学类",
                    "education": "本科及以上",
                    "recruit_count": 10,
                    "competition_ratio": "25:1",
                    "level": "不符合",
                    "match_score": 30,
                    "match_reasons": ["专业不匹配：金融学与教育学类差异较大"],
                },
            ],
            filter_criteria={
                "意向城市": ["济南市", "青岛市"],
                "学历要求": "本科及以上",
                "最大竞争比": 50,
            },
            summary={
                "total_jobs": 150,
                "matched_jobs": 45,
                "perfect_match": 12,
                "partial_match": 33,
                "avg_score": 72.5,
            },
        )


if __name__ == "__main__":
    # 测试导出功能
    exporter = ReportExporter()

    # 创建示例报告
    report = exporter.create_sample_report()

    print("=" * 80)
    print("报告导出测试")
    print("=" * 80)

    # 导出JSON
    json_path = exporter.export_json(report)
    print(f"\nJSON报告已导出: {json_path}")

    # 导出HTML
    html_path = exporter.export_html(report)
    print(f"HTML报告已导出: {html_path}")

    print("\n" + "=" * 80)
    print("报告内容预览:")
    print("=" * 80)
    print(f"用户专业: {report.user_major}")
    print(f"匹配岗位数: {len(report.target_jobs)}")
    print(f"完全符合: {sum(1 for j in report.target_jobs if j.get('level') == '完全符合')}")
    print(f"可能符合: {sum(1 for j in report.target_jobs if j.get('level') == '可能符合')}")
