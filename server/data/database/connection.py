#!/usr/bin/env python3
"""
数据库连接模块

使用 SQLAlchemy 进行数据库连接和会话管理
"""

from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# 数据库Schema定义
Base = declarative_base()


# 全局配置（可通过配置文件覆盖）
_DB_URL = "mysql+pymysql://root:password@localhost:3306/jobmatch?charset=utf8mb4"

# 全局引擎和会话工厂
_engine = None
_SessionLocal = None


def init_db(db_url: Optional[str] = None) -> None:
    """
    初始化数据库连接

    Args:
        db_url: 数据库URL，如果为None则使用默认配置
    """
    global _engine, _SessionLocal

    if db_url is None:
        db_url = _DB_URL

    _engine = create_engine(
        db_url,
        pool_pre_ping=True,  # 连接前ping一下
        pool_size=10,
        max_overflow=20,
        echo=False,  # 调试时可改为True
    )

    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_engine():
    """获取数据库引擎"""
    global _engine
    if _engine is None:
        init_db()
    return _engine


def get_session_factory():
    """获取会话工厂"""
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


@contextmanager
def get_db_session() -> Session:
    """
    获取数据库会话的上下文管理器

    使用方式:
        with get_db_session() as session:
            session.query(...)
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    """创建所有表"""
    Base.metadata.create_all(bind=get_engine())


def drop_tables():
    """删除所有表（谨慎使用）"""
    Base.metadata.drop_all(bind=get_engine())


# SQL表模型定义
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func


class JobModel(Base):
    """岗位表"""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False, index=True)  # 平台类型
    city = Column(String(50), index=True)  # 地市
    unit = Column(String(200), nullable=False)  # 服务单位
    job_type = Column(String(100))  # 岗位类型
    service_category = Column(String(50))  # 服务类别
    recruit_count = Column(Integer, default=1)  # 招募人数

    education = Column(String(50))  # 学历要求
    degree = Column(String(50))  # 学位要求
    major = Column(String(200))  # 专业要求
    age_limit = Column(String(50))  # 年龄要求
    political_requirement = Column(String(50))  # 政治面貌要求
    grassroots_experience = Column(String(100))  # 基层工作经验要求
    directional_recruit = Column(String(100))  # 定向招录
    qualifications = Column(String(100))  # 资格证书要求
    other = Column(Text)  # 其他要求

    phone = Column(String(50))  # 联系电话
    contact = Column(String(50))  # 联系人

    applicants = Column(Integer, default=0)  # 报名人数
    approved = Column(Integer, default=0)  # 初审通过人数
    paid = Column(Integer, default=0)  # 缴费人数
    competition_ratio = Column(Float, default=0.0)  # 竞争比

    raw_data = Column(JSON)  # 原始JSON数据

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserModel(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(100), unique=True, index=True)  # 微信openid

    major = Column(String(100))  # 专业
    education = Column(String(50))  # 学历
    degree = Column(String(50))  # 学位
    gender = Column(String(10))  # 性别
    age = Column(Integer, default=0)  # 年龄
    household = Column(String(100))  # 户籍
    party_status = Column(String(50))  # 政治面貌

    is_fresh_graduate = Column(Boolean, default=False)  # 是否应届生
    grassroots_exp = Column(Integer, default=0)  # 基层工作年限
    qualifications = Column(JSON)  # 持有资格证书
    estimated_score = Column(Float, default=0.0)  # 预估考试成绩

    target_cities = Column(JSON)  # 意向城市
    target_platforms = Column(JSON)  # 意向平台类型

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class FavoriteModel(Base):
    """收藏表"""

    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    job_id = Column(Integer, index=True)
    created_at = Column(DateTime, server_default=func.now())


class HistoricalStatsModel(Base):
    """历史统计数据表"""

    __tablename__ = "historical_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, index=True)
    year = Column(Integer, nullable=False)  # 年份

    recruitment_count = Column(Integer, default=0)  # 招录人数
    applicants = Column(Integer, default=0)  # 报名人数
    approved = Column(Integer, default=0)  # 初审通过人数
    paid = Column(Integer, default=0)  # 缴费人数
    competition_ratio = Column(Float, default=0.0)  # 竞争比

    passing_score = Column(Float, default=0.0)  # 进面最低分
    avg_score = Column(Float, default=0.0)  # 平均分
    highest_score = Column(Float, default=0.0)  # 最高分

    notes = Column(Text)  # 备注
    source = Column(String(200))  # 数据来源

    created_at = Column(DateTime, server_default=func.now())


# 导出
__all__ = [
    "Base",
    "init_db",
    "get_engine",
    "get_session_factory",
    "get_db_session",
    "create_tables",
    "drop_tables",
    "JobModel",
    "UserModel",
    "FavoriteModel",
    "HistoricalStatsModel",
]