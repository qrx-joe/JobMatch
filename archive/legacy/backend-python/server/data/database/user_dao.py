#!/usr/bin/env python3
"""
用户DAO - 数据访问对象
"""

from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from .connection import UserModel, FavoriteModel, get_db_session


class UserDAO:
    """用户数据访问对象"""

    @staticmethod
    def create(user_data: dict) -> int:
        """创建用户"""
        with get_db_session() as session:
            user = UserModel(**user_data)
            session.add(user)
            session.flush()
            user_id = user.id
        return user_id

    @staticmethod
    def get_by_id(user_id: int) -> Optional[UserModel]:
        """根据ID获取用户"""
        with get_db_session() as session:
            return session.query(UserModel).filter(UserModel.id == user_id).first()

    @staticmethod
    def get_by_openid(openid: str) -> Optional[UserModel]:
        """根据openid获取用户"""
        with get_db_session() as session:
            return session.query(UserModel).filter(UserModel.openid == openid).first()

    @staticmethod
    def update(user_id: int, update_data: dict) -> bool:
        """更新用户"""
        with get_db_session() as session:
            user = session.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                return False

            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            session.flush()
            return True

    @staticmethod
    def delete(user_id: int) -> bool:
        """删除用户"""
        with get_db_session() as session:
            user = session.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                return False

            session.delete(user)
            session.flush()
            return True


class FavoriteDAO:
    """收藏数据访问对象"""

    @staticmethod
    def add(user_id: int, job_id: int) -> bool:
        """添加收藏"""
        with get_db_session() as session:
            # 检查是否已存在
            existing = (
                session.query(FavoriteModel)
                .filter(and_(FavoriteModel.user_id == user_id, FavoriteModel.job_id == job_id))
                .first()
            )
            if existing:
                return True  # 已经收藏

            favorite = FavoriteModel(user_id=user_id, job_id=job_id)
            session.add(favorite)
            session.flush()
            return True

    @staticmethod
    def remove(user_id: int, job_id: int) -> bool:
        """取消收藏"""
        with get_db_session() as session:
            favorite = (
                session.query(FavoriteModel)
                .filter(and_(FavoriteModel.user_id == user_id, FavoriteModel.job_id == job_id))
                .first()
            )
            if not favorite:
                return False

            session.delete(favorite)
            session.flush()
            return True

    @staticmethod
    def get_user_favorites(user_id: int) -> List[int]:
        """获取用户的所有收藏岗位ID"""
        with get_db_session() as session:
            favorites = (
                session.query(FavoriteModel.job_id)
                .filter(FavoriteModel.user_id == user_id)
                .all()
            )
            return [fav[0] for fav in favorites]

    @staticmethod
    def is_favorited(user_id: int, job_id: int) -> bool:
        """检查是否已收藏"""
        with get_db_session() as session:
            favorite = (
                session.query(FavoriteModel)
                .filter(and_(FavoriteModel.user_id == user_id, FavoriteModel.job_id == job_id))
                .first()
            )
            return favorite is not None


# 导出
__all__ = ["UserDAO", "FavoriteDAO"]