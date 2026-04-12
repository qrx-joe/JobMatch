#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文件读取器 V2 - 更健壮的读取逻辑
"""
import pandas as pd
import glob
import os
import re
from typing import List, Dict, Optional
from job_matcher import Job


class JobExcelReader:
    """岗位表Excel读取器"""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_all(self) -> List[Job]:
        """读取所有Sheet的岗位数据"""
        jobs = []

        xl = pd.ExcelFile(self.file_path)
        for sheet_name in xl.sheet_names:
            # 跳过省林草局
            if sheet_name == '省林草局':
                continue

            print(f"\n  正在读取: {sheet_name}...", end='')
            sheet_jobs = self._read_sheet(sheet_name)
            jobs.extend(sheet_jobs)
            print(f" {len(sheet_jobs)} 个岗位")

        return jobs

    def _read_sheet(self, sheet_name: str) -> List[Job]:
        """读取单个Sheet"""
        jobs = []

        try:
            # 读取原始数据（不指定header）
            df_raw = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)

            # 找到表头行
            header_row_idx = self._find_header_row(df_raw)
            if header_row_idx is None:
                print(f" [无法找到表头，跳过]", end='')
                return []

            # 重新读取，使用正确的header
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, header=header_row_idx)

            # 标准化列名（移除换行符和空格）
            df.columns = [self._clean_column_name(str(c)) for c in df.columns]

            # 提取岗位数据
            for idx, row in df.iterrows():
                # 跳过空行（第一行通常是子表头，全是NaN）
                if pd.isna(row.iloc[0]):
                    continue

                # 检查是否是有效数据行（序号应该是数字）
                first_val = str(row.iloc[0]).strip()
                if not first_val or first_val in ['序号', 'nan', '']:
                    continue

                try:
                    int(float(first_val))
                except:
                    continue

                job = self._parse_row(row, sheet_name)
                if job and job.unit and job.unit not in ['服务单位', 'nan', '']:
                    jobs.append(job)

        except Exception as e:
            print(f" [错误: {e}]", end='')

        return jobs

    def _find_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """找到表头所在行"""
        for idx in range(min(10, len(df))):
            row_values = df.iloc[idx].tolist()
            row_text = ' '.join([str(v) for v in row_values if pd.notna(v)])

            # 关键：必须有"序号"和"服务"+"单位"
            has_xuhao = '序号' in row_text
            has_danwei = '服务' in row_text and ('单位' in row_text or '单位名称' in row_text)

            if has_xuhao and has_danwei:
                return idx

        return None

    def _clean_column_name(self, name: str) -> str:
        """清理列名"""
        # 移除换行符和多余空格
        name = name.replace('\n', '').replace(' ', '').strip()
        # 移除Unnamed
        if name.startswith('Unnamed:'):
            return ''
        return name

    def _parse_row(self, row: pd.Series, sheet_name: str) -> Optional[Job]:
        """解析一行数据为Job对象"""
        try:
            job = Job()
            job.sheet_name = sheet_name

            # 获取列名映射
            col_map = {self._clean_column_name(str(c)): c for c in row.index}

            # 提取字段 - 使用模糊匹配
            job.index = self._get_value_fuzzy(row, col_map, ['序号'], 0)
            job.unit = self._get_value_fuzzy(row, col_map, ['服务单位', '服务单位名称', '单位'], '')
            job.job_type = self._get_value_fuzzy(row, col_map, ['岗位类型', '岗位名称', '岗位'], '')
            job.service_category = self._get_value_fuzzy(row, col_map, ['服务类别', '服务类型', '类别'], '')
            job.recruit_count = self._parse_int(self._get_value_fuzzy(row, col_map, ['招募人数', '招聘人数', '招录人数'], '1'))
            job.education = self._get_value_fuzzy(row, col_map, ['学历', '学历要求'], '')
            job.degree = self._get_value_fuzzy(row, col_map, ['学位', '学位要求'], '')
            job.major = self._get_value_fuzzy(row, col_map, ['专业', '专业要求'], '')
            job.qualifications = self._get_value_fuzzy(row, col_map, ['相关资格', '资格要求'], '')
            job.other = self._get_value_fuzzy(row, col_map, ['其他', '其他要求', '备注'], '')
            job.phone = self._get_value_fuzzy(row, col_map, ['联系电话', '电话', '单位联系电话'], '')
            job.contact = self._get_value_fuzzy(row, col_map, ['联系人'], '')
            job.description = self._get_value_fuzzy(row, col_map, ['岗位描述', '描述'], '')
            job.benefits = self._get_value_fuzzy(row, col_map, ['福利待遇', '待遇', '福利'], '')

            # 清理数据
            job.unit = str(job.unit).strip()
            job.major = str(job.major).strip()

            return job

        except Exception as e:
            return None

    def _get_value_fuzzy(self, row: pd.Series, col_map: Dict[str, str],
                         possible_names: List[str], default='') -> str:
        """模糊匹配获取值"""
        for name in possible_names:
            # 直接匹配
            if name in col_map:
                col = col_map[name]
                val = row[col]
                if pd.notna(val):
                    return str(val).strip()

            # 清理后匹配
            clean_name = self._clean_column_name(name)
            for col_clean, col_original in col_map.items():
                if clean_name in col_clean or col_clean in clean_name:
                    val = row[col_original]
                    if pd.notna(val):
                        return str(val).strip()

        return default

    def _parse_int(self, val: str, default: int = 0) -> int:
        """解析整数"""
        try:
            return int(float(str(val).strip()))
        except:
            return default


class StatsExcelReader:
    """统计表Excel读取器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.stats: Dict[tuple, dict] = {}

    def read(self) -> Dict[tuple, dict]:
        """读取统计数据"""
        try:
            df = pd.read_excel(self.file_path, header=1)
        except:
            # 尝试不同的header
            df = pd.read_excel(self.file_path)

        print(f"统计表: 共 {len(df)} 条记录")

        for _, row in df.iterrows():
            try:
                unit_full = str(row.get('服务单位', '')).strip()
                job_type = str(row.get('岗位类型', '')).strip()
                recruit = int(row.get('招募人数', 0)) if pd.notna(row.get('招募人数')) else 0
                applicants = int(row.get('填报信息人数', 0)) if pd.notna(row.get('填报信息人数')) else 0
                approved = int(row.get('初审通过人数', 0)) if pd.notna(row.get('初审通过人数')) else 0
                paid = int(row.get('缴费人数', 0)) if pd.notna(row.get('缴费人数')) else 0

                if not unit_full:
                    continue

                key = (unit_full, job_type)
                self.stats[key] = {
                    'recruit': recruit,
                    'applicants': applicants,
                    'approved': approved,
                    'paid': paid,
                }

            except Exception as e:
                continue

        print(f"统计表: 成功解析 {len(self.stats)} 条记录")
        return self.stats

    def match_job(self, job: Job) -> Optional[dict]:
        """为岗位匹配统计数据"""
        # 构建可能的单位名
        possible_units = [
            f"{job.sheet_name}-{job.unit}",
            job.unit,
        ]

        # 尝试精确匹配
        for unit in possible_units:
            key = (unit, job.job_type)
            if key in self.stats:
                return self.stats[key]

        # 尝试模糊匹配
        return self._fuzzy_match(job)

    def _fuzzy_match(self, job: Job) -> Optional[dict]:
        """模糊匹配统计数据"""
        best_score = 0
        best_match = None

        job_unit_clean = self._clean_unit_name(job.unit)

        for (stats_unit, stats_type), stats in self.stats.items():
            if stats_type != job.job_type:
                continue

            score = self._calc_similarity(job_unit_clean, stats_unit)

            if score > best_score and score >= 0.5:
                best_score = score
                best_match = stats

        return best_match

    def _clean_unit_name(self, name: str) -> str:
        """清理单位名"""
        name = str(name).strip()
        prefixes = ['太原市', '大同市', '朔州市', '忻州市', '吕梁市',
                   '晋中市', '阳泉市', '长治市', '晋城市', '临汾市', '运城市']
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        return name.strip()

    def _calc_similarity(self, job_unit: str, stats_unit: str) -> float:
        """计算单位名相似度"""
        if job_unit in stats_unit or stats_unit in job_unit:
            return 0.8

        job_chars = set(job_unit)
        stats_chars = set(stats_unit)

        if not job_chars or not stats_chars:
            return 0.0

        overlap = len(job_chars & stats_chars)
        return overlap / max(len(job_chars), len(stats_chars))
