#!/usr/bin/env python3
"""
平台适配器基类

为不同类型的考公考编岗位表提供统一的解析接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import pandas as pd

from ..data.excel.column_mapper import ColumnMapper
from ..core.models.job import Job


class PlatformAdapter(ABC):
    """
    岗位平台适配器基类

    不同平台（三支一扶、公务员、事业编等）的Excel格式不同，
    通过适配器提供统一的解析接口
    """

    # 平台名称
    PLATFORM_NAME: str = ""

    # 平台描述
    PLATFORM_DESC: str = ""

    def __init__(self):
        self.column_mapper = ColumnMapper()
        self._job_counter = 0

    @abstractmethod
    def get_column_mapping(self) -> Dict[str, List[str]]:
        """
        获取该平台的列名映射

        Returns:
            Dict[str, List[str]]: 标准列名到可能列名的映射
            例如: {"unit": ["服务单位", "用人单位"], "major": ["专业", "所学专业"]}
        """
        pass

    @abstractmethod
    def detect_header_row(self, df_raw: pd.DataFrame) -> Optional[int]:
        """
        检测表头行

        Args:
            df_raw: 原始DataFrame（无表头）

        Returns:
            表头行索引，或None
        """
        pass

    @abstractmethod
    def parse_job(self, row: pd.Series, city: str, row_mapper) -> Optional[Job]:
        """
        解析单行数据为Job

        Args:
            row: 原始行数据
            city: 地市名称
            row_mapper: 行映射器

        Returns:
            Job对象或None
        """
        pass

    @abstractmethod
    def validate_file(self, file_path: str) -> bool:
        """
        验证文件格式

        Args:
            file_path: 文件路径

        Returns:
            True如果文件格式正确
        """
        pass

    def get_platform_name(self) -> str:
        """获取平台名称"""
        return self.PLATFORM_NAME

    def get_platform_desc(self) -> str:
        """获取平台描述"""
        return self.PLATFORM_DESC

    def should_skip_sheet(self, sheet_name: str) -> bool:
        """判断是否跳过某个Sheet"""
        skip_patterns = [
            "统计",
            "说明",
            "备注",
            "注意事项",
            "目录",
            "封面",
            "首页",
            "Sheet",
        ]
        for pattern in skip_patterns:
            if pattern in sheet_name:
                return True
        return False

    def parse(
        self, file_path: str, sheet_names: Optional[List[str]] = None
    ) -> List[Job]:
        """
        解析Excel文件

        Args:
            file_path: Excel文件路径
            sheet_names: 要解析的Sheet列表，None表示全部

        Returns:
            List[Job]: 岗位列表
        """
        self._job_counter = 0
        jobs = []

        xl = pd.ExcelFile(file_path)

        if sheet_names is None:
            sheet_names = xl.sheet_names

        for sheet_name in sheet_names:
            if self.should_skip_sheet(sheet_name):
                continue

            sheet_jobs = self._parse_sheet(file_path, sheet_name)
            jobs.extend(sheet_jobs)

        return jobs

    def _parse_sheet(self, file_path: str, sheet_name: str) -> List[Job]:
        """解析单个Sheet"""
        jobs = []

        try:
            df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

            header_row = self.detect_header_row(df_raw)
            if header_row is None:
                return []

            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

            col_map = self.column_mapper.detect_columns(df, header_row=0)

            row_mapper = self.column_mapper.build_row_mapper(df, col_map)

            for row_idx in range(1, len(df)):
                job = self.parse_job(df.iloc[row_idx], sheet_name, row_mapper)
                if job and self._is_valid_job(job):
                    self._job_counter += 1
                    job.id = self._job_counter
                    job.platform = self.PLATFORM_NAME
                    jobs.append(job)

        except Exception as e:
            print(f"解析Sheet[{sheet_name}]错误: {e}")

        return jobs

    def _is_valid_job(self, job: Job) -> bool:
        """验证Job是否有效"""
        if not job.unit or len(job.unit) < 2:
            return False
        return True

    def get_stats_columns(self) -> List[str]:
        """获取统计表特有的列名"""
        return [
            "服务单位",
            "岗位类型",
            "填报信息人数",
            "初审通过人数",
            "缴费人数",
        ]


# 导出
__all__ = ["PlatformAdapter"]