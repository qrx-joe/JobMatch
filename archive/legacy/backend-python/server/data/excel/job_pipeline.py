#!/usr/bin/env python3
"""
Excel → 数据库 数据管道

将解析后的岗位数据批量存入数据库
"""

import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.data.excel.universal_parser import Job, UniversalParser
from server.data.database.connection import get_db_session, JobModel


class JobPipeline:
    """
    岗位数据管道

    将Excel解析的Job对象批量存入数据库
    """

    def __init__(self):
        self.parser = UniversalParser()

    def parse_and_save(self, excel_path: str, platform: str = "三支一扶") -> dict:
        """
        解析Excel并保存到数据库

        Args:
            excel_path: Excel文件路径
            platform: 平台类型

        Returns:
            dict: 处理结果统计
        """
        print(f"开始解析: {excel_path}")

        # 解析Excel
        self.parser.platform = platform
        jobs = self.parser.parse(excel_path)
        print(f"解析完成，共 {len(jobs)} 个岗位")

        # 保存到数据库
        return self.save_jobs(jobs)

    def save_jobs(self, jobs: List[Job]) -> dict:
        """
        将Job列表保存到数据库

        Args:
            jobs: Job对象列表

        Returns:
            dict: 保存结果统计
        """
        success_count = 0
        error_count = 0
        duplicate_count = 0

        with get_db_session() as session:
            for job in jobs:
                try:
                    # 检查是否已存在（根据平台+城市+单位+岗位类型）
                    existing = (
                        session.query(JobModel)
                        .filter(
                            JobModel.platform == job.platform,
                            JobModel.city == job.city,
                            JobModel.unit == job.unit,
                            JobModel.job_type == job.job_type,
                        )
                        .first()
                    )

                    if existing:
                        # 更新现有记录
                        self._update_job_model(existing, job)
                        duplicate_count += 1
                    else:
                        # 创建新记录
                        job_model = self._job_to_model(job)
                        session.add(job_model)

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    print(f"保存岗位失败: {job.unit} - {e}")

            # session.commit() 由 context manager 自动处理

        return {
            "total": len(jobs),
            "success": success_count,
            "updated": duplicate_count,
            "errors": error_count,
        }

    def _job_to_model(self, job: Job) -> JobModel:
        """将Job对象转换为JobModel"""
        return JobModel(
            platform=job.platform,
            city=job.city,
            unit=job.unit,
            job_type=job.job_type,
            service_category=job.service_category,
            recruit_count=job.recruit_count,
            education=job.education,
            degree=job.degree,
            major=job.major,
            age_limit=job.age_limit,
            political_requirement=job.political_requirement,
            grassroots_experience=job.grassroots_experience,
            directional_recruit=job.directional_recruit,
            qualifications=job.qualifications,
            other=job.other,
            phone=job.phone,
            contact=job.contact,
            applicants=job.applicants,
            approved=job.approved,
            paid=job.paid,
            competition_ratio=job.competition_ratio,
            raw_data=job.raw_data,
        )

    def _update_job_model(self, model: JobModel, job: Job) -> None:
        """更新已存在的JobModel"""
        model.education = job.education
        model.degree = job.degree
        model.major = job.major
        model.age_limit = job.age_limit
        model.political_requirement = job.political_requirement
        model.qualifications = job.qualifications
        model.recruit_count = job.recruit_count
        model.applicants = job.applicants
        model.approved = job.approved
        model.paid = job.paid
        model.competition_ratio = job.competition_ratio


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Excel → 数据库导入工具")
    parser.add_argument("excel", help="Excel文件路径")
    parser.add_argument("--platform", "-p", default="三支一扶", help="平台类型")
    args = parser.parse_args()

    pipeline = JobPipeline()
    result = pipeline.parse_and_save(args.excel, args.platform)

    print("\n导入结果:")
    print(f"  总数: {result['total']}")
    print(f"  成功: {result['success']}")
    print(f"  更新: {result['updated']}")
    print(f"  错误: {result['errors']}")


if __name__ == "__main__":
    main()