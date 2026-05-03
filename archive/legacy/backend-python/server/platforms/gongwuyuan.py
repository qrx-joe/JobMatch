#!/usr/bin/env python3
"""
公务员平台适配器
"""

import re
from typing import Dict, List, Optional

import pandas as pd

from .base_platform import PlatformAdapter
from ..core.models.job import Job


class GongwuyuanAdapter(PlatformAdapter):
    """
    公务员适配器

    支持国考和省考的岗位表格式
    """

    PLATFORM_NAME = "公务员"
    PLATFORM_DESC = "公务员考试 - 国考/省考"

    def get_column_mapping(self) -> Dict[str, List[str]]:
        """获取公务员的列名映射"""
        return {
            "招录机关": ["招录机关", "用人单位", "单位名称", "工作部门"],
            "职位名称": ["职位名称", "职位", "岗位名称", "职位类别"],
            "招录人数": ["招录人数", "录用人数", "计划人数", "人数"],
            "学历": ["学历", "学历要求", "文化程度"],
            "学位": ["学位", "学位要求"],
            "专业": ["专业", "所学专业", "专业要求"],
            "年龄": ["年龄", "年龄要求", "年龄限制"],
            "政治面貌": ["政治面貌", "政治面貌要求"],
            "户籍": ["户籍要求", "户籍", "生源地"],
            "基层工作经历": ["基层工作经历", "基层经历", "基层工作经验"],
            "其他": ["其他条件", "备注", "其他"],
            "咨询电话": ["咨询电话", "联系电话"],
        }

    def detect_header_row(self, df_raw: pd.DataFrame) -> Optional[int]:
        """检测表头行"""
        for idx in range(min(10, len(df_raw))):
            row_text = " ".join([str(v) for v in df_raw.iloc[idx].values if pd.notna(v)])
            # 公务员典型表头
            if "招录机关" in row_text or "职位名称" in row_text:
                return idx
        return None

    def parse_job(self, row: pd.Series, city: str, row_mapper) -> Optional[Job]:
        """解析单行数据"""
        try:
            # 检查招录机关
            unit = row_mapper.get(0, "招录机关", "")
            if not unit or len(unit) < 2:
                return None

            job = Job()
            job.city = city
            job.unit = unit
            job.job_type = row_mapper.get(0, "职位名称", "")
            job.recruit_count = row_mapper.get_int(0, "招录人数", 1)
            job.education = row_mapper.get(0, "学历", "")
            job.degree = row_mapper.get(0, "学位", "")
            job.major = row_mapper.get(0, "专业", "")
            job.age_limit = row_mapper.get(0, "年龄", "")
            job.political_requirement = row_mapper.get(0, "政治面貌", "")
            job.grassroots_experience = row_mapper.get(0, "基层工作经历", "")
            job.other = row_mapper.get(0, "其他", "")
            job.phone = row_mapper.get(0, "咨询电话", "")

            return job

        except Exception:
            return None

    def validate_file(self, file_path: str) -> bool:
        """验证文件格式"""
        try:
            xl = pd.ExcelFile(file_path)
            df_raw = pd.read_excel(file_path, sheet_name=0, header=None)
            row_text = " ".join([str(v) for v in df_raw.iloc[0].values if pd.notna(v)])
            return "招录机关" in row_text or "职位" in row_text
        except Exception:
            return False


# 导出
__all__ = ["GongwuyuanAdapter"]