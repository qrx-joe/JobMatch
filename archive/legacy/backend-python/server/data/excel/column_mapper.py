#!/usr/bin/env python3
"""
通用列名映射器 - 自动识别Excel列名
支持多种考公考编岗位表格式

设计目标：不依赖硬编码列名，自动识别任意格式的Excel表头
"""

import re
from typing import Optional

import pandas as pd


# 列名同义词映射表
COLUMN_SYNONYMS: dict[str, list[str]] = {
    # 基本信息
    "服务单位": ["用人单位", "招录机关", "单位名称", "工作单位", "服务单位名称"],
    "岗位类型": ["岗位名称", "职位", "职务", "职级", "服务类别", "服务类型", "岗位类别"],
    "招募人数": ["招录人数", "计划人数", "人数", "名额", "录用人数"],
    "联系电话": ["咨询电话", "电话", "联系方式", "咨询方式"],
    "联系人": ["咨询人", "负责人员"],
    "序号": ["编号", "排序"],

    # 学历与学位
    "学历": ["学历要求", "文化程度", "文化水平", "学历条件", "受教育程度"],
    "学位": ["学位要求", "是否要求学位", "学位条件", "是否要求学士"],

    # 专业
    "专业": ["所学专业", "报考专业", "专业要求", "专业条件", "招录专业", "招录岗位专业"],

    # 户籍与生源地
    "户籍": ["户籍要求", "生源地", "户口所在地", "户籍所在地", "户口", "招生来源"],
    "生源地": ["来源地", "生源", "籍贯"],

    # 年龄
    "年龄": ["年龄要求", "年龄限制", "年龄条件", "岁", "周岁"],

    # 政治面貌
    "政治面貌": ["政治面貌要求", "政治面目", "党团员", "政治立场"],

    # 性别
    "性别": ["男", "女", "性别要求"],

    # 基层工作经验
    "基层经验": ["基层工作经验", "基层工作年限", "基层经历", "工作年限", "工作经历"],
    "基层服务": ["基层服务项目", "基层服务经历", "三支一扶", "西部计划"],

    # 定向招录
    "定向招录": ["定向招聘", "定向", "专项招聘", "专项计划"],
    "退役士兵": ["退役", "退伍", "军转"],

    # 资格证书
    "资格证书": ["相关资格", "资质要求", "证书要求", "资格条件", "执业资格"],

    # 其他要求
    "其他": ["其他要求", "备注", "附加条件", "其他条件", "其他资格条件"],

    # 竞争数据
    "报名人数": ["填报信息人数", "报名", "报名人数统计"],
    "初审通过": ["初审通过人数", "通过初审", "资格审核通过"],
    "缴费人数": ["确认人数", "缴费确认", "已缴费人数", "交费人数"],

    # 考试信息
    "笔试科目": ["考试科目", "笔试内容", "笔试类型"],
    "考试时间": ["笔试时间", "报名时间", "截止时间", "考试日期"],
}


class ColumnMapper:
    """
    列名映射器 - 自动检测Excel列名对应关系

    使用方法:
        mapper = ColumnMapper()
        mapping = mapper.detect_columns(df)  # df是pandas DataFrame
        # 返回: {"专业": 2, "学历": 3, "服务单位": 1, ...}
    """

    def __init__(self, synonyms: Optional[dict[str, list[str]]] = None):
        """
        初始化列名映射器

        Args:
            synonyms: 自定义同义词映射，默认使用 COLUMN_SYNONYMS
        """
        self.synonyms = synonyms or COLUMN_SYNONYMS
        # 构建反向映射：同义词 -> 标准名
        self._reverse_map: dict[str, str] = {}
        for std_name, syns in self.synonyms.items():
            for syn in syns:
                self._reverse_map[syn] = std_name
            self._reverse_map[std_name] = std_name  # 标准名也加入

    def detect_columns(self, df, header_row: int = 0, max_rows: int = 10) -> dict[str, int]:
        """
        自动检测列名对应关系

        Args:
            df: pandas DataFrame
            header_row: 表头所在行索引（默认0）
            max_rows: 用于验证的行数

        Returns:
            dict[str, int]: 标准列名到列索引的映射，如 {"专业": 2, "学历": 3}
        """
        result: dict[str, int] = {}
        used_cols: set[int] = set()

        # 获取表头行
        if header_row >= len(df):
            return result

        header = df.iloc[header_row]
        columns = list(df.columns)

        # 遍历每一列
        for col_idx, col_name in enumerate(columns):
            if pd.isna(col_name):
                continue

            col_str = str(col_name).strip()
            if not col_str or col_str.startswith("Unnamed"):
                continue

            # 尝试匹配标准列名
            matched_std = self._match_column(col_str)
            if matched_std and matched_std not in result:
                # 验证这一列确实有数据
                if self._validate_column(df, col_idx, matched_std, max_rows):
                    result[matched_std] = col_idx
                    used_cols.add(col_idx)

        return result

    def _match_column(self, col_name: str) -> Optional[str]:
        """
        匹配列名到标准名称

        Args:
            col_name: 列名

        Returns:
            标准列名或None
        """
        col_clean = col_name.replace("\n", "").replace(" ", "").replace("\t", "")

        # 精确匹配（考虑清理后的）
        if col_clean in self._reverse_map:
            return self._reverse_map[col_clean]

        # 模糊匹配：检查是否包含某个同义词
        best_match: tuple[str, int] = ("", 0)  # (标准名, 匹配分数)

        for std_name, syns in self.synonyms.items():
            for syn in syns:
                syn_clean = syn.replace("\n", "").replace(" ", "").replace("\t", "")
                # 计算相似度
                score = self._calculate_similarity(col_clean, syn_clean)
                if score > best_match[1] and score > 0.6:
                    best_match = (std_name, score)

                # 子串匹配
                if syn_clean in col_clean or col_clean in syn_clean:
                    if score > best_match[1]:
                        best_match = (std_name, max(score, 0.8))

        return best_match[0] if best_match[1] > 0.6 else None

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """
        计算两个字符串的相似度（简单实现）

        Returns:
            0.0 - 1.0 之间的相似度
        """
        if not s1 or not s2:
            return 0.0

        # 相同
        if s1 == s2:
            return 1.0

        # 包含关系
        if s1 in s2 or s2 in s1:
            return 0.7

        # 编辑距离（简化版）
        len1, len2 = len(s1), len(s2)
        if len1 > 0 and len2 > 0:
            # 公共子串长度 / 最长长度
            common = sum(1 for c1, c2 in zip(s1, s2) if c1 == c2)
            return common / max(len1, len2)

        return 0.0

    def _validate_column(
        self, df: pd.DataFrame, col_idx: int, std_name: str, max_rows: int
    ) -> bool:
        """
        验证列是否有真实数据

        Args:
            df: DataFrame
            col_idx: 列索引
            std_name: 标准列名（用于特殊验证）
            max_rows: 验证行数

        Returns:
            True如果列有有效数据
        """
        actual_col = df.columns[col_idx]

        for i in range(1, min(max_rows + 1, len(df))):
            if i >= len(df):
                break
            val = df.iloc[i][actual_col]
            if pd.notna(val):
                val_str = str(val).strip()
                # 排除明显是表头或空的
                if val_str and val_str not in [std_name, "nan", "", "None"]:
                    return True

        return False

    def build_row_mapper(self, df, header_row: int = 0) -> "RowMapper":
        """
        构建行映射器，方便后续按标准列名取值

        Args:
            df: DataFrame
            header_row: 表头行

        Returns:
            RowMapper实例
        """
        col_map = self.detect_columns(df, header_row)
        return RowMapper(df, col_map)


class RowMapper:
    """
    行映射器 - 方便按标准列名取值

    使用方法:
        mapper = ColumnMapper().build_row_mapper(df)
        value = mapper.get(row, "专业")  # 获取某行的"专业"列值
        value = mapper.get(row, "学历", default="本科")  # 带默认值
    """

    def __init__(self, df: pd.DataFrame, col_map: dict[str, int]):
        self.df = df
        self.col_map = col_map

    def get(self, row_idx: int, field: str, default: str = "") -> str:
        """
        获取指定行指定字段的值

        Args:
            row_idx: 行索引
            field: 标准字段名
            default: 默认值

        Returns:
            字段值或默认值
        """
        if field not in self.col_map:
            return default

        col_idx = self.col_map[field]
        if col_idx >= len(self.df.columns):
            return default

        col = self.df.columns[col_idx]
        val = self.df.iloc[row_idx][col]

        if pd.isna(val):
            return default

        result = str(val).strip()
        if result == field:  # 表头行
            return default
        return result

    def get_int(self, row_idx: int, field: str, default: int = 0) -> int:
        """获取整数"""
        val = self.get(row_idx, field, "")
        try:
            return int(float(val))
        except:
            return default

    def get_float(self, row_idx: int, field: str, default: float = 0.0) -> float:
        """获取浮点数"""
        val = self.get(row_idx, field, "")
        try:
            return float(val)
        except:
            return default


# 导出常用类和函数
__all__ = ["ColumnMapper", "RowMapper", "COLUMN_SYNONYMS"]


# 方便直接调用的函数
def detect_columns(df, header_row: int = 0) -> dict[str, int]:
    """快捷函数：检测列名映射"""
    return ColumnMapper().detect_columns(df, header_row)


def build_row_mapper(df, header_row: int = 0) -> RowMapper:
    """快捷函数：构建行映射器"""
    return ColumnMapper().build_row_mapper(df, header_row)