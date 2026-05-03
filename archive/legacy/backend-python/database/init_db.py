#!/usr/bin/env python3
"""
数据库初始化脚本

创建数据库和表
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.data.database.connection import init_db, create_tables, drop_tables, get_db_url


def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("  JobMatch 数据库初始化")
    print("=" * 60)

    # 显示连接信息（密码隐藏）
    db_url = get_db_url()
    # 隐藏密码
    hidden_url = db_url.replace(os.environ.get("DB_PASSWORD", "password"), "***")
    print(f"\n数据库连接: {hidden_url}")

    try:
        # 初始化连接
        init_db()
        print("\n✓ 数据库连接成功")

        # 确认操作
        confirm = input("\n是否重建所有表？（会清空现有数据）[y/N]: ").strip().lower()
        if confirm == 'y':
            print("\n删除旧表...")
            drop_tables()
            print("✓ 旧表已删除")

        print("\n创建表结构...")
        create_tables()
        print("✓ 表结构创建成功")

        print("\n" + "=" * 60)
        print("  数据库初始化完成！")
        print("=" * 60)
        print("\n接下来可以运行:")
        print("  uv run python demo_full_pipeline.py  # 演示匹配功能")
        print("  uv run uvicorn server.app:app --reload  # 启动API服务")

    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        print("\n请检查:")
        print("  1. MySQL 服务是否启动")
        print("  2. .env 文件中的数据库配置是否正确")
        print("  3. 数据库用户权限是否足够")


if __name__ == "__main__":
    init_database()