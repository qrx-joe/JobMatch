#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Excel读取器 - 更可靠
"""
import pandas as pd
import glob
import os
from typing import List, Dict, Optional
from job_matcher import Job


class SimpleJobReader:
    """简化岗位读取器"""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_all(self) -> List[Job]:
        """读取所有岗位"""
        jobs = []

        xl = pd.ExcelFile(self.file_path)
        for sheet_name in xl.sheet_names:
            if sheet_name == '省林草局':
                continue

            sheet_jobs = self._read_sheet(sheet_name)
            jobs.extend(sheet_jobs)
            print(f"  {sheet_name}: {len(sheet_jobs)} 个岗位")

        return jobs

    def _read_sheet(self, sheet_name: str) -> List[Job]:
        """读取单个Sheet"""
        jobs = []

        try:
            # 读取原始数据找表头
            df_raw = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)

            # 找表头行
            header_row = None
            for idx in range(min(10, len(df_raw))):
                row_text = ' '.join([str(v) for v in df_raw.iloc[idx].values if pd.notna(v)])
                if '序号' in row_text and '服务' in row_text:
                    header_row = idx
                    break

            if header_row is None:
                return []

            # 用找到的表头读取
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, header=header_row)

            # 遍历每一行
            for _, row in df.iterrows():
                job = self._parse_row(row, sheet_name)
                if job and job.unit and len(job.unit) > 3:
                    jobs.append(job)

        except Exception as e:
            print(f"  {sheet_name} 错误: {e}")

        return jobs

    def _parse_row(self, row: pd.Series, sheet_name: str) -> Optional[Job]:
        """解析一行"""
        try:
            # 获取第一列（序号）
            idx_val = row.iloc[0]
            if pd.isna(idx_val):
                return None

            # 检查是否是数字
            try:
                int(float(idx_val))
            except:
                return None

            job = Job()
            job.sheet_name = sheet_name
            job.index = int(float(idx_val))

            # 获取列名并清理
            cols = list(row.index)

            # 按位置或名称查找字段
            job.unit = self._find_value(row, cols, ['服务单位', '服务单位名称'])
            if not job.unit or len(job.unit) < 3:
                return None

            job.job_type = self._find_value(row, cols, ['岗位类型', '岗位名称'])
            job.service_category = self._find_value(row, cols, ['服务类别', '服务类型'])
            job.recruit_count = self._parse_int(self._find_value(row, cols, ['招募人数']))
            job.phone = self._find_value(row, cols, ['联系电话', '电话'])
            job.contact = self._find_value(row, cols, ['联系人'])

            # 直接读取各列（处理Unnamed列）
            job.education = self._find_value(row, cols, ['服务岗位要求'])
            job.degree = self._find_value(row, cols, ['Unnamed: 6'])
            job.major = self._find_value(row, cols, ['Unnamed: 7'])
            job.qualifications = self._find_value(row, cols, ['Unnamed: 8'])
            job.other = self._find_value(row, cols, ['Unnamed: 9'])

            # 清理可能包含的表头文字
            if job.education == '学历':
                job.education = ''
            if job.degree == '学位':
                job.degree = ''
            if job.major == '专业':
                job.major = ''
            if job.qualifications == '相关资格':
                job.qualifications = ''
            if job.other == '其他':
                job.other = ''

            return job

        except Exception as e:
            return None

    def _parse_requirements(self, requirements: str) -> dict:
        """
        从服务岗位要求中解析出各个字段
        格式示例：本科及以上，学士及以上，经济学类（0201）、统计学类（0712）
        """
        result = {
            'education': '',
            'degree': '',
            'major': '',
            'qualifications': '',
            'other': ''
        }

        if not requirements:
            return result

        req = str(requirements).strip()

        # 提取学历（如：本科及以上，大专及以上，研究生）
        edu_patterns = ['研究生及以上', '研究生', '本科及以上', '本科', '大专及以上', '大专', '专科及以上', '专科']
        for pattern in edu_patterns:
            if pattern in req:
                result['education'] = pattern
                break

        # 提取学位（如：学士及以上，硕士及以上）
        degree_patterns = ['博士及以上', '博士', '硕士及以上', '硕士', '学士及以上', '学士']
        for pattern in degree_patterns:
            if pattern in req:
                result['degree'] = pattern
                break

        # 提取专业：通常在"学历/学位"之后，或包含"类"、"专业"、数字代码
        # 尝试找到专业部分
        major = ''

        # 尝试匹配"本科及以上，学士及以上，专业名称"这种格式
        parts = req.split('，')
        if len(parts) >= 3:
            # 最后一部分可能是专业
            major = parts[-1]
        elif len(parts) == 2:
            # 可能只有学历和专业
            if '及以上' in parts[0] or '本科' in parts[0] or '大专' in parts[0]:
                major = parts[1]
        elif len(parts) == 1:
            # 只有一项，判断是否是专业
            if '类' in parts[0] or any(c.isdigit() for c in parts[0]):
                major = parts[0]

        # 如果还没找到，尝试用正则匹配专业代码格式（如：0201）
        if not major:
            import re
            # 匹配包含数字代码的部分
            match = re.search(r'[（(](\d{4})[）)]', req)
            if match:
                # 找到代码，提取从代码往前到学历/学位的部分
                idx = match.start()
                # 向前找逗号或空格
                start = max(0, req.rfind('，', 0, idx))
                if start == 0:
                    start = max(0, req.rfind(' ', 0, idx))
                major = req[start:].strip('，')

        # 清理专业字段
        if major:
            # 移除学历相关文字
            for edu in edu_patterns:
                major = major.replace(edu, '')
            # 移除学位相关文字
            for deg in degree_patterns:
                major = major.replace(deg, '')
            # 清理多余字符
            major = major.strip('，,、 ')
            result['major'] = major

        # 提取相关资格（如：教师资格证、法律职业资格等）
        qual_patterns = ['教师资格证', '法律职业资格', '医师资格证', '护士资格证', '会计证', '注册会计师']
        for pattern in qual_patterns:
            if pattern in req:
                result['qualifications'] = pattern
                break

        # 其他要求（性别、户籍等）暂不归入other，由其他列处理

        return result

    def _find_value(self, row: pd.Series, cols: list, possible_names: list, default='') -> str:
        """查找字段值"""
        # 先按列名查找
        for name in possible_names:
            name_clean = str(name).replace('\n', '').replace(' ', '')
            for col in cols:
                col_str = str(col).replace('\n', '').replace(' ', '')
                if name_clean in col_str or col_str in name_clean:
                    val = row[col]
                    if pd.notna(val):
                        return str(val).strip()

        # 如果没找到，按列位置估计
        # 服务单位通常在第2列（索引1）
        if '服务单位' in possible_names and len(row) > 1:
            val = row.iloc[1]
            if pd.notna(val):
                return str(val).strip()

        return default

    def _parse_int(self, val: str, default: int = 1) -> int:
        """解析整数"""
        try:
            return int(float(val))
        except:
            return default


class StatsReader:
    """统计表读取器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.stats = {}

    def read(self) -> dict:
        """读取统计表"""
        try:
            df = pd.read_excel(self.file_path, header=1)

            for _, row in df.iterrows():
                try:
                    unit = str(row.get('服务单位', '')).strip()
                    job_type = str(row.get('岗位类型', '')).strip()
                    paid = int(row.get('缴费人数', 0)) if pd.notna(row.get('缴费人数')) else 0

                    if unit and job_type:
                        key = (unit, job_type)
                        self.stats[key] = {
                            'applicants': int(row.get('填报信息人数', 0)) if pd.notna(row.get('填报信息人数')) else 0,
                            'approved': int(row.get('初审通过人数', 0)) if pd.notna(row.get('初审通过人数')) else 0,
                            'paid': paid,
                        }
                except:
                    continue

        except Exception as e:
            print(f"统计表读取错误: {e}")

        return self.stats

    def match_job(self, job: Job) -> Optional[dict]:
        """匹配岗位统计"""
        # 精确匹配
        key = (f"{job.sheet_name}-{job.unit}", job.job_type)
        if key in self.stats:
            return self.stats[key]

        # 模糊匹配
        for (stats_unit, stats_type), stats in self.stats.items():
            if stats_type == job.job_type:
                if job.unit in stats_unit or stats_unit in job.unit:
                    return stats

        return None
