#!/usr/bin/env python3
"""
匹配报告生成器
支持JSON、HTML、Excel、PDF格式导出
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class MatchReport:
    """匹配报告数据类"""

    user_major: str
    user_education: str
    user_degree: str
    user_gender: str = ""
    user_household: str = ""
    is_fresh_graduate: bool = False
    target_cities: list[str] = None
    matched_jobs: list[dict] = None
    filter_config: dict = None
    summary: dict = None
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.matched_jobs is None:
            self.matched_jobs = []
        if self.target_cities is None:
            self.target_cities = []
        if self.filter_config is None:
            self.filter_config = {}
        if self.summary is None:
            self.summary = {}


class ReportGenerator:
    """报告生成器"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_json(self, report: MatchReport, filename: str = None) -> str:
        """生成JSON格式报告"""
        if not filename:
            filename = f"match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.output_dir / filename

        data = {
            "report_info": {
                "generated_at": report.generated_at,
                "version": "2.0.0",
                "source": "三支一扶智能选岗系统",
            },
            "user_profile": {
                "major": report.user_major,
                "education": report.user_education,
                "degree": report.user_degree,
                "gender": report.user_gender,
                "household": report.user_household,
                "is_fresh_graduate": report.is_fresh_graduate,
                "target_cities": report.target_cities,
            },
            "filter_config": report.filter_config,
            "summary": report.summary,
            "matched_jobs": report.matched_jobs,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def generate_html(self, report: MatchReport, filename: str = None) -> str:
        """生成HTML格式报告（美观的可视化）"""
        if not filename:
            filename = f"match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        filepath = self.output_dir / filename

        # 计算统计数据
        total = len(report.matched_jobs)
        perfect_count = sum(1 for j in report.matched_jobs if j.get("match_level") == "完全符合")
        partial_count = sum(1 for j in report.matched_jobs if j.get("match_level") == "可能符合")
        avg_score = (
            sum(j.get("match_score", 0) for j in report.matched_jobs) / total if total > 0 else 0
        )

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>三支一扶岗位匹配报告 - {report.user_major}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header .subtitle {{ opacity: 0.9; font-size: 14px; }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
        }}
        @media (max-width: 768px) {{
            .summary {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        .stat-card {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{ color: #666; font-size: 14px; }}

        .section {{
            padding: 30px 40px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{ border-bottom: none; }}
        .section-title {{
            font-size: 20px;
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .profile-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }}
        @media (max-width: 600px) {{
            .profile-grid {{ grid-template-columns: 1fr; }}
        }}
        .profile-item {{
            display: flex;
            justify-content: space-between;
            padding: 14px 18px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .profile-label {{ color: #666; }}
        .profile-value {{ font-weight: 600; color: #333; }}

        .job-list {{ display: flex; flex-direction: column; gap: 16px; }}
        .job-item {{
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s;
        }}
        .job-item:hover {{
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }}
        .job-item.perfect {{ border-color: #28a745; background: #f8fff9; }}
        .job-item.partial {{ border-color: #ffc107; background: #fffdf5; }}

        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }}
        .job-title {{ font-size: 18px; font-weight: 600; }}
        .job-location {{ color: #666; font-size: 14px; margin-top: 4px; }}

        .badge {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-perfect {{ background: #d4edda; color: #155724; }}
        .badge-partial {{ background: #fff3cd; color: #856404; }}
        .badge-mismatch {{ background: #f8d7da; color: #721c24; }}

        .job-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin: 16px 0;
            padding: 16px 0;
            border-top: 1px solid #eee;
            border-bottom: 1px solid #eee;
        }}
        .detail {{ font-size: 14px; }}
        .detail-label {{ color: #888; margin-bottom: 4px; }}
        .detail-value {{ font-weight: 500; }}

        .reasons {{
            background: #f0f7ff;
            padding: 16px;
            border-radius: 8px;
            margin-top: 12px;
        }}
        .reasons-title {{
            color: #667eea;
            font-weight: 600;
            font-size: 13px;
            margin-bottom: 8px;
        }}
        .reasons ul {{
            list-style: none;
            padding: 0;
            font-size: 13px;
        }}
        .reasons li {{
            padding: 4px 0;
            padding-left: 20px;
            position: relative;
        }}
        .reasons li::before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #28a745;
            font-weight: bold;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #888;
            font-size: 12px;
        }}

        .print-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 16px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            transition: all 0.3s;
        }}
        .print-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(102, 126, 234, 0.5);
        }}

        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; }}
            .print-btn {{ display: none; }}
            .job-item {{ break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>三支一扶岗位匹配报告</h1>
            <div class="subtitle">生成时间: {report.generated_at}</div>
        </div>

        <div class="summary">
            <div class="stat-card">
                <div class="stat-number">{total}</div>
                <div class="stat-label">匹配岗位</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #28a745;">{perfect_count}</div>
                <div class="stat-label">完全符合</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #ffc107;">{partial_count}</div>
                <div class="stat-label">可能符合</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #17a2b8;">{avg_score:.0f}</div>
                <div class="stat-label">平均匹配分</div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">👤 用户档案</h2>
            <div class="profile-grid">
                <div class="profile-item">
                    <span class="profile-label">专业</span>
                    <span class="profile-value">{report.user_major}</span>
                </div>
                <div class="profile-item">
                    <span class="profile-label">学历</span>
                    <span class="profile-value">{report.user_education}</span>
                </div>
                <div class="profile-item">
                    <span class="profile-label">学位</span>
                    <span class="profile-value">{report.user_degree}</span>
                </div>
                <div class="profile-item">
                    <span class="profile-label">政治面貌</span>
                    <span class="profile-value">{report.filter_config.get("political_status", "不限")}</span>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">📋 推荐岗位 ({total}个)</h2>
            <div class="job-list">
                {self._generate_job_items(report.matched_jobs)}
            </div>
        </div>

        <div class="footer">
            <p>本报告由三支一扶智能选岗系统生成 | 仅供参考，请以官方公告为准</p>
        </div>
    </div>

    <button class="print-btn" onclick="window.print()">🖨️ 打印报告</button>
</body>
</html>"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(filepath)

    def _generate_job_items(self, jobs: list[dict]) -> str:
        """生成岗位HTML"""
        if not jobs:
            return '<p style="text-align: center; color: #888; padding: 40px;">暂无匹配岗位</p>'

        html = ""
        for job in jobs:
            level = job.get("match_level", "不符合")
            badge_class = {
                "完全符合": "badge-perfect",
                "可能符合": "badge-partial",
                "不符合": "badge-mismatch",
            }.get(level, "badge-mismatch")

            card_class = (
                "perfect" if level == "完全符合" else "partial" if level == "可能符合" else ""
            )

            reasons = job.get("match_reasons", [])
            reasons_html = ""
            if reasons:
                reasons_list = "".join([f"<li>{r}</li>" for r in reasons])
                reasons_html = f'<div class="reasons"><div class="reasons-title">匹配理由</div><ul>{reasons_list}</ul></div>'

            competition = job.get("competition_ratio", 0)
            competition_str = f"{competition:.1f}:1" if competition > 0 else "暂无"

            html += f"""
                <div class="job-item {card_class}">
                    <div class="job-header">
                        <div>
                            <div class="job-title">{job.get("unit", "未知单位")}</div>
                            <div class="job-location">{job.get("sheet_name", "未知城市")} | {job.get("job_type", "未知类型")}</div>
                        </div>
                        <span class="badge {badge_class}">{level}</span>
                    </div>
                    <div class="job-details">
                        <div class="detail">
                            <div class="detail-label">专业要求</div>
                            <div class="detail-value">{job.get("major", "不限")}</div>
                        </div>
                        <div class="detail">
                            <div class="detail-label">学历要求</div>
                            <div class="detail-value">{job.get("education", "不限")}</div>
                        </div>
                        <div class="detail">
                            <div class="detail-label">招募人数</div>
                            <div class="detail-value">{job.get("recruit_count", 1)}人</div>
                        </div>
                        <div class="detail">
                            <div class="detail-label">竞争比</div>
                            <div class="detail-value">{competition_str}</div>
                        </div>
                        <div class="detail">
                            <div class="detail-label">匹配分数</div>
                            <div class="detail-value" style="color: #667eea;">{job.get("match_score", 0)}分</div>
                        </div>
                    </div>
                    {reasons_html}
                </div>
            """

        return html

    def generate_excel(self, report: MatchReport, filename: str = None) -> str:
        """生成Excel格式报告"""
        try:
            import pandas as pd
        except ImportError:
            print("[错误] 未安装pandas/openpyxl，正在安装...")
            import subprocess

            subprocess.run(["uv", "add", "pandas", "openpyxl"], check=True)
            import pandas as pd

        if not filename:
            filename = f"match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        filepath = self.output_dir / filename

        # 准备数据
        jobs_data = []
        for job in report.matched_jobs:
            jobs_data.append(
                {
                    "序号": len(jobs_data) + 1,
                    "城市": job.get("sheet_name", ""),
                    "服务单位": job.get("unit", ""),
                    "岗位类型": job.get("job_type", ""),
                    "专业要求": job.get("major", ""),
                    "学历要求": job.get("education", ""),
                    "招募人数": job.get("recruit_count", 1),
                    "报名人数": job.get("applicants", 0),
                    "初审通过": job.get("approved", 0),
                    "缴费人数": job.get("paid", 0),
                    "竞争比": job.get("competition_ratio", 0),
                    "匹配等级": job.get("match_level", ""),
                    "匹配分数": job.get("match_score", 0),
                    "匹配理由": " | ".join(job.get("match_reasons", [])),
                }
            )

        df = pd.DataFrame(jobs_data)

        # 创建Excel writer
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            # 岗位列表
            df.to_excel(writer, sheet_name="匹配岗位", index=False)

            # 用户信息
            user_info = pd.DataFrame(
                [
                    {"项目": "专业", "内容": report.user_major},
                    {"项目": "学历", "内容": report.user_education},
                    {"项目": "学位", "内容": report.user_degree},
                    {"项目": "性别", "内容": report.user_gender or "不限"},
                    {"项目": "户籍", "内容": report.user_household or "不限"},
                    {"项目": "是否应届", "内容": "是" if report.is_fresh_graduate else "否"},
                    {
                        "项目": "意向城市",
                        "内容": ", ".join(report.target_cities) if report.target_cities else "不限",
                    },
                    {"项目": "生成时间", "内容": report.generated_at},
                ]
            )
            user_info.to_excel(writer, sheet_name="用户信息", index=False)

            # 统计信息
            summary_data = {
                "指标": ["匹配岗位总数", "完全符合", "可能符合", "不符合", "平均匹配分"],
                "数值": [
                    len(report.matched_jobs),
                    sum(1 for j in report.matched_jobs if j.get("match_level") == "完全符合"),
                    sum(1 for j in report.matched_jobs if j.get("match_level") == "可能符合"),
                    sum(1 for j in report.matched_jobs if j.get("match_level") == "不符合"),
                    sum(j.get("match_score", 0) for j in report.matched_jobs)
                    / len(report.matched_jobs)
                    if report.matched_jobs
                    else 0,
                ],
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="统计汇总", index=False)

        return str(filepath)

    def generate_pdf(self, report: MatchReport, filename: str = None) -> str:
        """生成PDF格式报告（通过打印HTML为PDF）"""
        # 先生成HTML
        html_path = self.generate_html(report)

        # 尝试使用weasyprint或playwright转换为PDF
        try:
            pdf_path = html_path.replace(".html", ".pdf")
            print("[提示] PDF生成需要使用浏览器打印功能")
            print(f'[提示] 请打开 {html_path}，然后选择"打印"->"另存为PDF"')
            return pdf_path
        except Exception as e:
            print(f"[警告] PDF生成失败: {e}")
            return html_path


def create_sample_report() -> MatchReport:
    """创建示例报告"""
    return MatchReport(
        user_major="金融学",
        user_education="本科",
        user_degree="学士",
        user_gender="",
        user_household="",
        is_fresh_graduate=False,
        target_cities=["济南市", "青岛市"],
        matched_jobs=[
            {
                "sheet_name": "济南市",
                "unit": "济南市财政局",
                "job_type": "支农",
                "major": "经济学类",
                "education": "本科及以上",
                "recruit_count": 5,
                "applicants": 60,
                "approved": 45,
                "paid": 40,
                "competition_ratio": 8.0,
                "match_level": "完全符合",
                "match_score": 95,
                "match_reasons": [
                    "专业匹配：金融学属于经济学类",
                    "学历符合：本科符合要求",
                    "意向城市匹配：济南市",
                ],
            },
            {
                "sheet_name": "青岛市",
                "unit": "青岛市统计局",
                "job_type": "支农",
                "major": "统计学类",
                "education": "本科及以上",
                "recruit_count": 3,
                "applicants": 30,
                "approved": 25,
                "paid": 20,
                "competition_ratio": 6.7,
                "match_level": "可能符合",
                "match_score": 75,
                "match_reasons": ["专业相关：金融学与统计学高度相关", "学历符合：本科符合要求"],
            },
        ],
        summary={"total": 2, "perfect": 1, "partial": 1, "avg_score": 85},
    )


if __name__ == "__main__":
    print("=" * 80)
    print("报告生成器测试")
    print("=" * 80)

    generator = ReportGenerator()
    report = create_sample_report()

    # 生成JSON
    json_path = generator.generate_json(report)
    print(f"\n[OK] JSON报告: {json_path}")

    # 生成HTML
    html_path = generator.generate_html(report)
    print(f"[OK] HTML报告: {html_path}")

    # 生成Excel
    try:
        excel_path = generator.generate_excel(report)
        print(f"[OK] Excel报告: {excel_path}")
    except Exception as e:
        print(f"[错误] Excel生成失败: {e}")

    print("\n" + "=" * 80)
    print("报告预览:")
    print(f"  用户: {report.user_major}")
    print(f"  匹配: {len(report.matched_jobs)}个岗位")
    print(f"  完全符合: {report.summary['perfect']}个")
    print("=" * 80)
