#!/usr/bin/env python3
"""
岗位DAO - 数据访问对象
"""

from typing import List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from .connection import JobModel, get_db_session


class JobDAO:
    """岗位数据访问对象"""

    @staticmethod
    def create(job_data: dict) -> int:
        """
        创建岗位

        Args:
            job_data: 岗位数据

        Returns:
            int: 新岗位ID
        """
        with get_db_session() as session:
            job = JobModel(**job_data)
            session.add(job)
            session.flush()
            job_id = job.id
        return job_id

    @staticmethod
    def bulk_create(jobs_data: List[dict]) -> List[int]:
        """
        批量创建岗位

        Args:
            jobs_data: 岗位数据列表

        Returns:
            List[int]: 新岗位ID列表
        """
        with get_db_session() as session:
            jobs = [JobModel(**data) for data in jobs_data]
            session.add_all(jobs)
            session.flush()
            job_ids = [job.id for job in jobs]
        return job_ids

    @staticmethod
    def get_by_id(job_id: int) -> Optional[JobModel]:
        """根据ID获取岗位"""
        with get_db_session() as session:
            return session.query(JobModel).filter(JobModel.id == job_id).first()

    @staticmethod
    def get_by_platform(platform: str, limit: int = 100) -> List[JobModel]:
        """根据平台获取岗位"""
        with get_db_session() as session:
            return (
                session.query(JobModel)
                .filter(JobModel.platform == platform)
                .limit(limit)
                .all()
            )

    @staticmethod
    def search(
        platform: Optional[str] = None,
        city: Optional[str] = None,
        major: Optional[str] = None,
        education: Optional[str] = None,
        max_competition_ratio: Optional[float] = None,
        min_recruit_count: int = 1,
        limit: int = 100,
    ) -> List[JobModel]:
        """
        搜索岗位

        Args:
            platform: 平台类型
            city: 地市
            major: 专业
            education: 学历
            max_competition_ratio: 最大竞争比
            min_recruit_count: 最少招募人数
            limit: 返回数量限制

        Returns:
            List[JobModel]: 岗位列表
        """
        with get_db_session() as session:
            query = session.query(JobModel)

            filters = []

            if platform:
                filters.append(JobModel.platform == platform)

            if city:
                filters.append(JobModel.city == city)

            if major:
                filters.append(JobModel.major.like(f"%{major}%"))

            if education:
                filters.append(JobModel.education.like(f"%{education}%"))

            if max_competition_ratio is not None:
                filters.append(JobModel.competition_ratio <= max_competition_ratio)

            if min_recruit_count > 0:
                filters.append(JobModel.recruit_count >= min_recruit_count)

            if filters:
                query = query.filter(and_(*filters))

            return query.limit(limit).all()

    @staticmethod
    def update(job_id: int, update_data: dict) -> bool:
        """更新岗位"""
        with get_db_session() as session:
            job = session.query(JobModel).filter(JobModel.id == job_id).first()
            if not job:
                return False

            for key, value in update_data.items():
                if hasattr(job, key):
                    setattr(job, key, value)

            session.flush()
            return True

    @staticmethod
    def delete(job_id: int) -> bool:
        """删除岗位"""
        with get_db_session() as session:
            job = session.query(JobModel).filter(JobModel.id == job_id).first()
            if not job:
                return False

            session.delete(job)
            session.flush()
            return True

    @staticmethod
    def count(platform: Optional[str] = None) -> int:
        """统计岗位数量"""
        with get_db_session() as session:
            query = session.query(JobModel)
            if platform:
                query = query.filter(JobModel.platform == platform)
            return query.count()

    @staticmethod
    def get_cities(platform: Optional[str] = None) -> List[str]:
        """获取所有地市"""
        with get_db_session() as session:
            query = session.query(JobModel.city).distinct()
            if platform:
                query = query.filter(JobModel.platform == platform)
            return [city for city, in query.all() if city]


# 导出
__all__ = ["JobDAO"]