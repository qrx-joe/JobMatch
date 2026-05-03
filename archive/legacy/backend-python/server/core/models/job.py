#!/usr/bin/env python3
"""
岗位数据模型 - 扩展版
支持政治面貌、年龄、基层经验等多种筛选维度
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MatchLevel(Enum):
    """匹配等级"""

    PERFECT = "完全符合"  # 绿色 - 所有条件都满足
    PARTIAL = "可能符合"  # 黄色 - 部分条件满足
    MISMATCH = "不符合"  # 红色 - 关键条件不满足


class RecommendationTier(Enum):
    """推荐层级"""

    STRETCH = "冲刺"  # 冲 - 竞争激烈但有希望
    SAFE = "稳妥"  # 稳 - 把握较大
    BOTTOM = "保底"  # 保 - 相对稳妥的保底选择


@dataclass
class HistoricalStats:
    """历年统计数据"""

    year: int = 0  # 年份
    recruitment_count: int = 0  # 招录人数
    applicants: int = 0  # 报名人数
    paid: int = 0  # 缴费人数
    competition_ratio: float = 0.0  # 竞争比
    passing_score: float = 0.0  # 进面分数（最低分）
    avg_score: float = 0.0  # 平均分


@dataclass
class Job:
    """
    岗位数据模型（扩展版）

    支持多种筛选维度：
    - 基本信息：平台类型、地市、服务单位、岗位类型
    - 学历要求：学历、学位
    - 专业要求：专业名称
    - 附加条件：年龄、政治面貌、基层经验、定向招录、资格证书
    - 竞争数据：报名人数、初审通过、缴费人数、竞争比
    - 历史数据：历年分数线
    - 匹配结果：匹配等级、分数、原因
    - 推荐结果：冲刺/稳妥/保底、上岸概率
    """

    # ID
    id: int = 0

    # 基本信息
    platform: str = ""  # 平台类型（三支一扶/公务员/事业编/教师）
    city: str = ""  # 地市
    unit: str = ""  # 服务单位
    job_type: str = ""  # 岗位类型
    service_category: str = ""  # 服务类别
    recruit_count: int = 1  # 招募人数

    # 学历与学位
    education: str = ""  # 学历要求
    degree: str = ""  # 学位要求

    # 专业
    major: str = ""  # 专业要求

    # 扩展条件
    age_limit: str = ""  # 年龄要求 "30岁以下"
    political_requirement: str = ""  # 政治面貌要求 "中共党员"
    grassroots_experience: str = ""  # 基层工作经验要求
    directional_recruit: str = ""  # 定向招录
    qualifications: str = ""  # 资格证书要求
    other: str = ""  # 其他要求

    # 联系方式
    phone: str = ""  # 联系电话
    contact: str = ""  # 联系人

    # 竞争数据
    applicants: int = 0  # 填报信息人数
    approved: int = 0  # 初审通过人数
    paid: int = 0  # 缴费人数
    competition_ratio: float = 0.0  # 竞争比 = 缴费人数 / 招募人数

    # 历史数据
    historical_stats: dict[int, HistoricalStats] = field(default_factory=dict)

    # 匹配结果
    match_level: Optional[MatchLevel] = None
    match_score: int = 0  # 匹配分数（用于排序）
    match_reasons: list[str] = field(default_factory=list)
    mismatch_reasons: list[str] = field(default_factory=list)

    # 推荐相关
    recommendation_tier: Optional[RecommendationTier] = None
    predicted_score: float = 0.0  # 预测进面分数
    pass_probability: float = 0.0  # 上岸概率

    # 原始数据（JSON格式存储）
    raw_data: dict = field(default_factory=dict)

    def calculate_competition_ratio(self) -> float:
        """计算竞争比"""
        if self.recruit_count > 0 and self.paid > 0:
            self.competition_ratio = self.paid / self.recruit_count
        return self.competition_ratio

    def to_dict(self) -> dict:
        """转换为字典（API响应用）"""
        return {
            "id": self.id,
            "platform": self.platform,
            "city": self.city,
            "unit": self.unit,
            "job_type": self.job_type,
            "service_category": self.service_category,
            "recruit_count": self.recruit_count,
            "education": self.education,
            "degree": self.degree,
            "major": self.major,
            "age_limit": self.age_limit,
            "political_requirement": self.political_requirement,
            "grassroots_experience": self.grassroots_experience,
            "qualifications": self.qualifications,
            "competition_ratio": round(self.competition_ratio, 2),
            "match_level": self.match_level.value if self.match_level else None,
            "match_score": self.match_score,
            "recommendation_tier": (
                self.recommendation_tier.value if self.recommendation_tier else None
            ),
            "pass_probability": round(self.pass_probability, 2),
        }


@dataclass
class JobFilter:
    """岗位筛选条件"""

    # 平台类型
    platform: Optional[str] = None
    platforms: list[str] = field(default_factory=list)

    # 地区
    city: Optional[str] = None
    cities: list[str] = field(default_factory=list)

    # 学历
    min_education: Optional[str] = None  # 最低学历要求

    # 专业
    major: Optional[str] = None  # 所学专业

    # 竞争比
    max_competition_ratio: Optional[float] = None

    # 招募人数
    min_recruit_count: int = 1

    # 其他
    political_required: Optional[str] = None  # 必须的政治面貌
    has_age_limit: bool = False
    has_grassroots_exp: bool = False


# 导出
__all__ = ["Job", "JobFilter", "MatchLevel", "RecommendationTier", "HistoricalStats"]