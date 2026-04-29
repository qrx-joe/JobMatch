#!/usr/bin/env python3
"""
用户画像模型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UserProfile:
    """
    用户画像模型

    包含用户的所有信息，用于与岗位进行匹配
    """

    # ID
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
    target_job_types: list[str] = field(default_factory=list)  # 意向岗位类型

    # 收藏
    favorite_jobs: list[int] = field(default_factory=list)  # 收藏的岗位ID列表

    # 元数据
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "major": self.major,
            "education": self.education,
            "degree": self.degree,
            "gender": self.gender,
            "age": self.age,
            "household": self.household,
            "party_status": self.party_status,
            "is_fresh_graduate": self.is_fresh_graduate,
            "grassroots_exp": self.grassroots_exp,
            "qualifications": self.qualifications,
            "estimated_score": self.estimated_score,
            "target_cities": self.target_cities,
            "target_platforms": self.target_platforms,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """从字典创建"""
        profile = cls()
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        return profile


# 导出
__all__ = ["UserProfile"]