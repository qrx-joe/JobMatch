#!/usr/bin/env python3
"""
历史数据分析模块 - 支持历年数据对比、趋势预测
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class YearlyStats:
    """单年度统计数据"""

    year: int
    applicants: int = 0  # 报名人数
    approved: int = 0  # 初审通过
    paid: int = 0  # 缴费人数
    pass_score: float = 0.0  # 上岸分数线
    avg_competition: float = 0.0  # 平均竞争比


class HistoricalAnalyzer:
    """历史数据分析器"""

    def __init__(self, historical_config: dict):
        """
        初始化历史数据分析器

        Args:
            historical_config: 配置中的 historical_data 部分
        """
        self.config = historical_config
        self.current_year = historical_config.get("当前年份", 2025)
        self.yearly_data: dict[int, YearlyStats] = {}
        self.user_score = historical_config.get("分析选项", {}).get("预估分数", 0)

    def load_historical_data(self) -> dict[int, pd.DataFrame]:
        """
        加载所有历年统计数据

        Returns:
            Dict[int, pd.DataFrame]: {年份: 统计表DataFrame}
        """
        historical_files = self.config.get("历年统计", {})
        loaded_data = {}

        for year, file_config in historical_files.items():
            year = int(year)
            file_path = file_config.get("文件路径", "")

            if not file_path or not Path(file_path).exists():
                print(f"  警告: {year}年统计文件不存在: {file_path}")
                continue

            try:
                df = pd.read_excel(file_path)
                loaded_data[year] = df
                print(f"  加载 {year}年统计数据: {len(df)} 条记录")
            except Exception as e:
                print(f"  错误: 读取{year}年统计失败: {e}")

        return loaded_data

    def analyze_job_historical(
        self, unit_name: str, historical_dfs: dict[int, pd.DataFrame]
    ) -> dict[int, dict]:
        """
        分析单个岗位的历年数据

        Args:
            unit_name: 单位名称
            historical_dfs: 历年统计数据 {年份: DataFrame}

        Returns:
            Dict[int, dict]: {年份: {applicants, paid, score, competition_ratio}}
        """
        stats = {}

        for year, df in historical_dfs.items():
            # 尝试匹配单位名称（支持模糊匹配）
            year_stats = self._match_unit_in_df(unit_name, df, year)
            if year_stats:
                stats[year] = year_stats

        return stats

    def _match_unit_in_df(self, unit_name: str, df: pd.DataFrame, year: int) -> dict | None:
        """
        在DataFrame中匹配单位名称

        Args:
            unit_name: 要匹配的单位名称
            df: 统计数据DataFrame
            year: 年份（用于获取分数线）

        Returns:
            Optional[dict]: 匹配到的统计数据
        """
        if df.empty:
            return None

        # 可能的列名
        unit_columns = ["单位名称", "服务单位", "用人单位", "单位"]
        unit_col = None

        for col in unit_columns:
            if col in df.columns:
                unit_col = col
                break

        if not unit_col:
            return None

        # 精确匹配
        matches = df[df[unit_col].astype(str).str.strip() == unit_name.strip()]

        # 如果没有精确匹配，尝试包含匹配
        if matches.empty:
            matches = df[df[unit_col].astype(str).str.contains(unit_name[:6], na=False)]

        if matches.empty:
            return None

        # 取第一条匹配记录
        row = matches.iloc[0]

        # 获取该年分数线配置
        year_config = self.config.get("历年统计", {}).get(str(year), {})
        pass_score = year_config.get("上岸分数线", 0)

        # 获取统计数据字段
        def get_field(row, possible_names, default=0):
            for name in possible_names:
                if name in row.index:
                    val = row[name]
                    if pd.notna(val):
                        try:
                            return int(float(str(val).strip()))
                        except:
                            return default
            return default

        applicants = get_field(row, ["填报信息人数", "报名人数", "报名", "applicants"])
        paid = get_field(row, ["缴费人数", "缴费", "paid"])
        recruit_count = get_field(row, ["招募人数", "招录人数", "人数", "recruit_count"], 1)

        competition_ratio = paid / recruit_count if recruit_count > 0 else 0

        return {
            "applicants": applicants,
            "paid": paid,
            "recruit_count": recruit_count,
            "competition_ratio": competition_ratio,
            "pass_score": pass_score,
        }

    def predict_score(self, historical_stats: dict[int, dict]) -> tuple[float, str]:
        """
        基于历史数据预测今年上岸分数

        Args:
            historical_stats: 历年统计数据

        Returns:
            (预测分数, 预测方法说明)
        """
        if not historical_stats:
            return 0.0, "无历史数据"

        years = sorted(historical_stats.keys())
        scores = [
            historical_stats[y].get("pass_score", 0)
            for y in years
            if historical_stats[y].get("pass_score")
        ]

        if len(scores) < 2:
            return scores[0] if scores else 0.0, "单年数据"

        # 简单线性回归预测
        x = np.array(years)
        y = np.array(scores)

        # 计算趋势线
        z = np.polyfit(x, y, 1)
        predicted = np.polyval(z, self.current_year)

        # 根据趋势给出说明
        trend = "上升" if z[0] > 0.5 else "下降" if z[0] < -0.5 else "稳定"

        return round(predicted, 1), f"基于{years[0]}-{years[-1]}年趋势预测({trend})"

    def calculate_pass_probability(self, predicted_score: float) -> float:
        """
        计算上岸概率

        Args:
            predicted_score: 预测上岸分数

        Returns:
            上岸概率 (0-100%)
        """
        if not self.user_score or not predicted_score:
            return 0.0

        # 分差
        diff = self.user_score - predicted_score

        # 简单概率模型
        if diff >= 10:
            return 95.0
        elif diff >= 5:
            return 85.0
        elif diff >= 0:
            return 70.0
        elif diff >= -5:
            return 50.0
        elif diff >= -10:
            return 30.0
        else:
            return 10.0

    def analyze_trend(self, historical_stats: dict[int, dict]) -> str:
        """
        分析竞争趋势

        Args:
            historical_stats: 历年统计数据

        Returns:
            趋势描述: 上升/下降/稳定/未知
        """
        if not historical_stats or len(historical_stats) < 2:
            return "未知"

        years = sorted(historical_stats.keys())
        ratios = [historical_stats[y].get("competition_ratio", 0) for y in years]

        if len(ratios) < 2:
            return "未知"

        # 计算变化率
        first_ratio = ratios[0]
        last_ratio = ratios[-1]

        if first_ratio == 0:
            return "未知"

        change_pct = (last_ratio - first_ratio) / first_ratio * 100

        if change_pct > 20:
            return "上升"
        elif change_pct < -20:
            return "下降"
        else:
            return "稳定"

    def get_strategy_advice(self, pass_probability: float, trend: str) -> str:
        """
        获取报考策略建议

        Args:
            pass_probability: 上岸概率
            trend: 竞争趋势

        Returns:
            策略建议
        """
        strategy_mode = self.config.get("分析选项", {}).get("报考策略", "conservative")

        if strategy_mode == "conservative":
            if pass_probability >= 80:
                return "【稳妥】上岸概率高，推荐报考"
            elif pass_probability >= 60:
                return "【可冲】有一定把握，可以考虑"
            else:
                return "【谨慎】风险较高，建议备选"

        elif strategy_mode == "aggressive":
            if pass_probability >= 50:
                return "【推荐】值得一试"
            else:
                return "【捡漏】风险高但可能有机会"

        else:  # normal
            if pass_probability >= 70:
                return "【推荐】把握较大"
            elif pass_probability >= 50:
                return "【考虑】中等风险"
            else:
                return "【观望】建议关注其他岗位"


def enrich_jobs_with_historical_data(jobs: list, historical_config: dict) -> list:
    """
    为岗位列表添加历史数据分析

    Args:
        jobs: 岗位列表
        historical_config: 历史数据配置

    Returns:
        添加历史数据后的岗位列表
    """
    if not historical_config.get("启用", False):
        return jobs

    print("\n[历史数据分析]")

    analyzer = HistoricalAnalyzer(historical_config)

    # 加载所有历年数据
    historical_dfs = analyzer.load_historical_data()

    if not historical_dfs:
        print("  未找到历史数据，跳过分析")
        return jobs

    enriched_count = 0

    for job in jobs:
        # 分析该岗位的历年数据
        historical_stats = analyzer.analyze_job_historical(job.unit, historical_dfs)

        if historical_stats:
            job.historical_stats = historical_stats

            # 预测分数
            predicted_score, method = analyzer.predict_score(historical_stats)
            job.predicted_score = predicted_score

            # 计算上岸概率
            job.pass_probability = analyzer.calculate_pass_probability(predicted_score)

            # 分析趋势
            job.difficulty_trend = analyzer.analyze_trend(historical_stats)

            enriched_count += 1

    print(f"  已为 {enriched_count}/{len(jobs)} 个岗位添加历史数据分析")

    return jobs


if __name__ == "__main__":
    # 测试代码
    test_config = {
        "启用": True,
        "当前年份": 2025,
        "历年统计": {
            2023: {"文件路径": "test_2023.xlsx", "上岸分数线": 65.5},
            2024: {"文件路径": "test_2024.xlsx", "上岸分数线": 68.0},
        },
        "分析选项": {"预测分数": True, "预估分数": 70.0, "报考策略": "conservative"},
    }

    analyzer = HistoricalAnalyzer(test_config)
    print("历史数据分析模块测试完成")
