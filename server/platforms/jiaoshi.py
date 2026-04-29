#!/usr/bin/env python3
"""
教师招聘平台适配器
"""

import re
from typing import Dict, List, Optional

import pandas as pd

from .base_platform import PlatformAdapter
from ..core.models.job import Job


class JiaoshiAdapter(PlatformAdapter):
    """
    教师招聘适配器

    支持编制教师、特岗教师招聘
    """

    PLATFORM_NAME = "教师"
    PLATFORM_DESC = "教师招聘 - 编制教师/特岗教师"

    def get_column_mapping(self) -> Dict[str, List[str]]:
        """获取教师招聘的列名映射"""
        return {
            "招聘学校": ["招聘学校", "用人单位", "单位名称", "学校名称"],
            "招聘岗位": ["招聘岗位", "岗位名称", "科目", "学科"],
            "招聘人数": ["招聘人数", "录用人数", "计划人数", "人数"],
            "学历": ["学历要求", "学历", "文化程度"],
            "学位": ["学位要求", "学位"],
            "专业": ["专业要求", "专业", "所学专业", "教师资格证学科"],
            "年龄": ["年龄要求", "年龄限制", "年龄"],
            "政治面貌": ["政治面貌要求", "政治面貌"],
            "教师资格": ["教师资格", "教师资格证", "资格要求"],
            "其他": ["其他条件", "备注", "其他要求"],
            "联系电话": ["联系电话", "咨询电话"],
        }

    def detect_header_row(self, df_raw: pd.DataFrame) -> Optional[int]:
        """检测表头行"""
        for idx in range(min(10, len(df_raw))):
            row_text = " ".join([str(v) for v in df_raw.iloc[idx].values if pd.notna(v)])
            if "教师" in row_text or "学校" in row_text or "招聘" in row_text:
                return idx
        return None

    def parse_job(self, row: pd.Series, city: str, row_mapper) -> Optional[Job]:
        """解析单行数据"""
        try:
            unit = row_mapper.get(0, "招聘学校", "")
            if not unit or len(unit) < 2:
                return None

            job = Job()
            job.city = city
            job.unit = unit
            job.job_type = row_mapper.get(0, "招聘岗位", "")
            job.recruit_count = row_mapper.get_int(0, "招聘人数", 1)
            job.education = row_mapper.get(0, "学历", "")
            job.degree = row_mapper.get(0, "学位", "")
            job.major = row_mapper.get(0, "专业", "")
            job.age_limit = row_mapper.get(0, "年龄", "")
            job.political_requirement = row_mapper.get(0, "政治面貌", "")
            job.qualifications = row_mapper.get(0, "教师资格", "")
            job.other = row_mapper.get(0, "其他", "")
            job.phone = row_mapper.get(0, "联系电话", "")

            return job

        except Exception:
            return None

    def validate_file(self, file_path: str) -> bool:
        """验证文件格式"""
        try:
            xl = pd.ExcelFile(file_path)
            df_raw = pd.read_excel(file_path, sheet_name=0, header=None)
            row_text = " ".join([str(v) for v in df_raw.iloc[0].values if pd.notna(v)])
            return "教师" in row_text or "学校" in row_text or "招聘" in row_text
        except Exception:
            return False


# 导出
__all__ = ["JiaoshiAdapter"]