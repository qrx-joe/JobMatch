#!/usr/bin/env python3
"""
三支一扶平台适配器
"""

import re
from typing import Dict, List, Optional

import pandas as pd

from .base_platform import PlatformAdapter
from ..core.models.job import Job


class SanzhiyifuAdapter(PlatformAdapter):
    """
    三支一扶适配器

    三支一扶是面向高校毕业生的基层服务项目，
    包括支教、支农、支医和扶贫
    """

    PLATFORM_NAME = "三支一扶"
    PLATFORM_DESC = "三支一扶计划 - 支教、支农、支医、扶贫"

    def get_column_mapping(self) -> Dict[str, List[str]]:
        """获取三支一扶的列名映射"""
        return {
            "服务单位": ["服务单位", "服务单位名称", "用人单位"],
            "岗位类型": ["岗位类型", "岗位名称", "服务类别", "服务类型"],
            "招募人数": ["招募人数", "招录人数", "计划人数", "人数", "名额"],
            "学历": ["学历要求", "学历", "服务岗位要求"],
            "学位": ["学位要求", "学位"],
            "专业": ["专业要求", "专业", "所学专业", "Unnamed: 7"],
            "年龄": ["年龄要求", "年龄限制", "年龄", "岁"],
            "政治面貌": ["政治面貌要求", "政治面貌", "政治面目"],
            "户籍": ["户籍要求", "户籍", "生源地", "户口所在地"],
            "其他": ["其他要求", "其他", "备注", "附加条件"],
            "联系电话": ["联系电话", "咨询电话", "电话", "联系方式"],
            "联系人": ["联系人", "咨询人", "负责人员"],
        }

    def detect_header_row(self, df_raw: pd.DataFrame) -> Optional[int]:
        """检测表头行"""
        for idx in range(min(10, len(df_raw))):
            row_text = " ".join([str(v) for v in df_raw.iloc[idx].values if pd.notna(v)])
            # 三支一扶典型表头
            if "序号" in row_text and "服务" in row_text:
                return idx
        return None

    def parse_job(self, row: pd.Series, city: str, row_mapper) -> Optional[Job]:
        """解析单行数据"""
        try:
            # 检查序号
            idx_val = row_mapper.get(0, "序号", "")
            if not idx_val:
                return None
            try:
                int(float(idx_val))
            except:
                return None

            job = Job()
            job.city = city

            # 基本信息
            job.unit = row_mapper.get(0, "服务单位", "")
            if not job.unit or len(job.unit) < 2:
                return None

            job.job_type = row_mapper.get(0, "岗位类型", "")
            job.recruit_count = row_mapper.get_int(0, "招募人数", 1)

            # 学历与专业
            raw_edu = row_mapper.get(0, "学历", "")
            job.education, job.degree, job.major = self._parse_education_major(raw_edu)

            # 其他字段
            job.age_limit = row_mapper.get(0, "年龄", "")
            job.political_requirement = row_mapper.get(0, "政治面貌", "")
            job.other = row_mapper.get(0, "其他", "")
            job.phone = row_mapper.get(0, "联系电话", "")

            return job

        except Exception:
            return None

    def _parse_education_major(self, requirement: str) -> tuple:
        """
        解析学历和专业

        格式示例：本科及以上，学士及以上，经济学类（0201）、统计学类（0712）
        """
        education = ""
        degree = ""
        major = ""

        if not requirement:
            return education, degree, major

        req = str(requirement).strip()

        # 学历模式
        edu_patterns = [
            "研究生及以上",
            "研究生",
            "本科及以上",
            "本科",
            "大专及以上",
            "大专",
            "专科及以上",
            "专科",
        ]
        for pattern in edu_patterns:
            if pattern in req:
                education = pattern
                break

        # 学位模式
        degree_patterns = [
            "博士及以上",
            "博士",
            "硕士及以上",
            "硕士",
            "学士及以上",
            "学士",
        ]
        for pattern in degree_patterns:
            if pattern in req:
                degree = pattern
                break

        # 专业：通常在最后，或者包含代码
        parts = req.split("，")
        if len(parts) >= 2:
            # 最后一部分是专业
            potential_major = parts[-1]
            # 清理学历学位
            for p in edu_patterns + degree_patterns:
                potential_major = potential_major.replace(p, "")
            potential_major = potential_major.strip("，,、 ")
            if potential_major:
                major = potential_major

        # 尝试用代码定位专业
        if not major:
            match = re.search(r"[（(](\d{4})[）)]", req)
            if match:
                idx = match.start()
                start = max(0, req.rfind("，", 0, idx))
                if start == 0:
                    start = max(0, req.rfind("，", 0, idx))
                major = req[start:].strip("，")
                for p in edu_patterns + degree_patterns:
                    major = major.replace(p, "")
                major = major.strip("，,、 ")

        return education, degree, major

    def validate_file(self, file_path: str) -> bool:
        """验证文件格式"""
        try:
            xl = pd.ExcelFile(file_path)
            # 应该有多个Sheet（各地市）
            if len(xl.sheet_names) < 2:
                return False

            # 检查第一个Sheet是否有典型的三支一扶表头
            df_raw = pd.read_excel(file_path, sheet_name=0, header=None)
            row_text = " ".join([str(v) for v in df_raw.iloc[0].values if pd.notna(v)])
            return "序号" in row_text and "服务" in row_text

        except Exception:
            return False


# 导出
__all__ = ["SanzhiyifuAdapter"]