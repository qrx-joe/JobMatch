#!/usr/bin/env python3
"""
通用Excel解析器 - 自动解析任意格式的考公考编岗位表
支持三支一扶、公务员、事业单位、教师等不同平台

设计目标：不依赖硬编码列名，自动识别任意格式的Excel表头
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import pandas as pd

from .column_mapper import ColumnMapper, RowMapper


class MatchLevel(Enum):
    PERFECT = "完全符合"
    PARTIAL = "可能符合"
    MISMATCH = "不符合"


@dataclass
class Job:
    """岗位数据模型（扩展版）"""

    # 基本信息
    id: int = 0
    platform: str = ""  # 平台类型（三支一扶/公务员等）
    city: str = ""  # 地市
    unit: str = ""  # 服务单位
    job_type: str = ""  # 岗位类型
    service_category: str = ""  # 服务类别
    recruit_count: int = 1  # 招募人数

    # 要求（扩展）
    education: str = ""  # 学历要求
    degree: str = ""  # 学位要求
    major: str = ""  # 专业要求
    qualifications: str = ""  # 资格证书要求
    other: str = ""  # 其他要求

    # 新增字段
    age_limit: str = ""  # 年龄要求 "30岁以下"
    political_requirement: str = ""  # 政治面貌要求 "中共党员"
    grassroots_experience: str = ""  # 基层工作经验要求
    directional_recruit: str = ""  # 定向招录

    # 竞争数据
    applicants: int = 0  # 报名人数
    approved: int = 0  # 初审通过人数
    paid: int = 0  # 缴费人数
    competition_ratio: float = 0.0  # 竞争比

    # 原始数据
    raw_data: dict = field(default_factory=dict)  # 原始行数据JSON

    # 匹配结果（解析时不填充，由匹配器填充）
    match_level: Optional[MatchLevel] = None
    match_score: int = 0
    match_reasons: list[str] = field(default_factory=list)
    mismatch_reasons: list[str] = field(default_factory=list)

    # 推荐相关
    recommendation_tier: str = ""  # "冲刺" / "稳妥" / "保底"
    predicted_score: float = 0.0  # 预测进面分数
    pass_probability: float = 0.0  # 上岸概率


@dataclass
class UserProfile:
    """用户画像模型"""

    id: int = 0
    openid: str = ""  # 微信openid

    # 基本信息
    major: str = ""  # 所学专业
    education: str = ""  # 学历
    degree: str = ""  # 学位
    gender: str = ""  # 性别
    age: int = 0  # 年龄

    # 户籍与政治面貌
    household: str = ""  # 户籍所在地
    party_status: str = ""  # 政治面貌

    # 附加条件
    is_fresh_graduate: bool = False  # 是否应届生
    grassroots_exp: int = 0  # 基层工作年限
    qualifications: list[str] = field(default_factory=list)  # 持有资格证书
    estimated_score: float = 0.0  # 预估考试成绩

    # 偏好设置
    target_cities: list[str] = field(default_factory=list)  # 意向城市
    target_platforms: list[str] = field(default_factory=list)  # 意向平台类型

    # 收藏
    favorite_jobs: list[int] = field(default_factory=list)  # 收藏的岗位ID列表


class UniversalParser:
    """
    通用Excel解析器

    支持多种格式的岗位表，自动识别列名

    使用方法:
        parser = UniversalParser()
        jobs = parser.parse("岗位表.xlsx")
        for job in jobs:
            print(f"{job.unit} - {job.major}")
    """

    def __init__(self, platform: str = "sanzhiyifu"):
        """
        初始化解析器

        Args:
            platform: 平台类型，支持 sanzhiyifu/gongwuyuan/shiyedan/jiaoshi
        """
        self.platform = platform
        self.column_mapper = ColumnMapper()
        self._job_counter = 0

    def parse(self, file_path: str, sheet_names: Optional[list[str]] = None) -> list[Job]:
        """
        解析Excel文件

        Args:
            file_path: Excel文件路径
            sheet_names: 要解析的Sheet名列表，None表示全部

        Returns:
            Job列表
        """
        self._job_counter = 0
        jobs = []

        xl = pd.ExcelFile(file_path)

        # 确定要解析的Sheet
        if sheet_names is None:
            sheet_names = xl.sheet_names

        for sheet_name in sheet_names:
            # 跳过明显不是岗位表的Sheet
            if self._should_skip_sheet(sheet_name):
                continue

            sheet_jobs = self._parse_sheet(file_path, sheet_name)
            jobs.extend(sheet_jobs)

        return jobs

    def _should_skip_sheet(self, sheet_name: str) -> bool:
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

    def _parse_sheet(self, file_path: str, sheet_name: str) -> list[Job]:
        """解析单个Sheet"""
        jobs = []

        try:
            # 读取原始数据（不指定header）找表头
            df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

            # 找表头行
            header_row = self._find_header_row(df_raw)
            if header_row is None:
                return []

            # 用找到的表头读取
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

            # 构建列名映射
            col_map = self.column_mapper.detect_columns(df, header_row=0)

            if not col_map:
                # 尝试多行表头
                col_map = self._detect_multirow_header(df_raw, header_row)

            # 构建行映射器
            row_mapper = RowMapper(df, col_map)

            # 遍历数据行
            for row_idx in range(1, len(df)):
                job = self._parse_row(row_mapper, row_idx, sheet_name)
                if job and self._is_valid_job(job):
                    jobs.append(job)

        except Exception as e:
            print(f"解析Sheet[{sheet_name}]错误: {e}")

        return jobs

    def _find_header_row(self, df_raw: pd.DataFrame) -> Optional[int]:
        """查找表头行"""
        for idx in range(min(10, len(df_raw))):
            row_text = " ".join([str(v) for v in df_raw.iloc[idx].values if pd.notna(v)])
            # 典型的表头特征
            if "序号" in row_text or ("服务" in row_text and "单位" in row_text):
                return idx
        return None

    def _detect_multirow_header(self, df_raw: pd.DataFrame, header_row: int) -> dict:
        """检测多行表头，返回合并后的列映射"""
        col_map = {}

        if header_row + 1 >= len(df_raw):
            return col_map

        main_headers = df_raw.iloc[header_row].tolist()
        sub_headers = df_raw.iloc[header_row + 1].tolist()

        for i, (main, sub) in enumerate(zip(main_headers, sub_headers, strict=False)):
            main_str = str(main).strip() if pd.notna(main) else ""
            sub_str = str(sub).strip() if pd.notna(sub) else ""

            # 优先使用子表头
            if sub_str and sub_str not in ["nan", ""]:
                col_map[sub_str] = i
            elif main_str and not main_str.startswith("Unnamed"):
                col_map[main_str] = i

        return col_map

    def _parse_row(
        self, row_mapper: RowMapper, row_idx: int, sheet_name: str
    ) -> Optional[Job]:
        """解析单行数据"""
        try:
            # 获取序号，检查是否是有效数据行
            idx_val = row_mapper.get(row_idx, "序号", "")
            if not idx_val:
                return None

            # 检查是否是数字序号
            try:
                int(float(idx_val))
            except:
                return None

            job = Job()
            job.platform = self.platform
            job.city = sheet_name

            # 基本信息
            job.unit = row_mapper.get(row_idx, "服务单位", "")
            job.job_type = row_mapper.get(row_idx, "岗位类型", "")
            job.service_category = row_mapper.get(row_idx, "服务类别", "")

            # 招募人数
            job.recruit_count = row_mapper.get_int(row_idx, "招募人数", 1)

            # 学历与专业
            job.education = row_mapper.get(row_idx, "学历", "")
            job.degree = row_mapper.get(row_idx, "学位", "")
            job.major = row_mapper.get(row_idx, "专业", "")

            # 扩展字段
            job.age_limit = row_mapper.get(row_idx, "年龄", "")
            job.political_requirement = row_mapper.get(row_idx, "政治面貌", "")
            job.grassroots_experience = row_mapper.get(row_idx, "基层经验", "")
            job.directional_recruit = row_mapper.get(row_idx, "定向招录", "")

            # 资格证书
            job.qualifications = row_mapper.get(row_idx, "资格证书", "")

            # 其他要求
            job.other = row_mapper.get(row_idx, "其他", "")

            # 竞争数据
            job.applicants = row_mapper.get_int(row_idx, "报名人数", 0)
            job.approved = row_mapper.get_int(row_idx, "初审通过", 0)
            job.paid = row_mapper.get_int(row_idx, "缴费人数", 0)

            # 计算竞争比
            if job.recruit_count > 0 and job.paid > 0:
                job.competition_ratio = job.paid / job.recruit_count

            # 清理表头残留
            self._clean_job_fields(job)

            return job

        except Exception as e:
            return None

    def _clean_job_fields(self, job: Job) -> None:
        """清理Job字段中的无效值"""
        header_values = ["学历", "学位", "专业", "相关资格", "其他", "序号"]

        for field_name in ["education", "degree", "major", "qualifications", "other"]:
            val = getattr(job, field_name, "")
            if val in header_values:
                setattr(job, field_name, "")

        # 专业可能包含在学历字段中，需要解析
        if job.education and not job.major:
            parsed = self._parse_requirements(job.education)
            if parsed.get("major"):
                job.major = parsed["major"]

    def _parse_requirements(self, requirements: str) -> dict:
        """
        从服务岗位要求中解析出各个字段
        格式示例：本科及以上，学士及以上，经济学类（0201）、统计学类（0712）
        """
        result = {"education": "", "degree": "", "major": "", "qualifications": ""}

        if not requirements:
            return result

        req = str(requirements).strip()

        # 提取学历
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
                result["education"] = pattern
                break

        # 提取学位
        degree_patterns = ["博士及以上", "博士", "硕士及以上", "硕士", "学士及以上", "学士"]
        for pattern in degree_patterns:
            if pattern in req:
                result["degree"] = pattern
                break

        # 提取专业
        major = ""
        parts = req.split("，")
        if len(parts) >= 3:
            major = parts[-1]
        elif len(parts) == 2:
            if "及以上" in parts[0] or "本科" in parts[0] or "大专" in parts[0]:
                major = parts[1]

        if not major and "类" in req:
            match = re.search(r"[（(](\d{4})[）)]", req)
            if match:
                idx = match.start()
                start = max(0, req.rfind("，", 0, idx))
                major = req[start:].strip("，")

        if major:
            for edu in edu_patterns:
                major = major.replace(edu, "")
            for deg in degree_patterns:
                major = major.replace(deg, "")
            major = major.strip("，,、 ")
            result["major"] = major

        return result

    def _is_valid_job(self, job: Job) -> bool:
        """验证Job是否是有效的岗位"""
        # 必须有服务单位
        if not job.unit or len(job.unit) < 2:
            return False

        # 序号必须是数字
        try:
            int(float(job.unit[0])) if job.unit else None
        except:
            pass

        return True


# 导出
__all__ = ["UniversalParser", "Job", "UserProfile", "MatchLevel"]