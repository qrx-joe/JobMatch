#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
import glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from excel_reader_v2 import SimpleJobReader

files = glob.glob('*.xlsx')
files = [f for f in files if '岗位汇总表' in f and not f.startswith('~$')]
file_path = files[0]

print(f"读取文件: {file_path}")

reader = SimpleJobReader(file_path)
all_jobs = reader.read_all()

print(f"\n总共读取 {len(all_jobs)} 个岗位")

# 统计专业分布
major_stats = {}
for job in all_jobs:
    major = job.major if job.major else '空'
    major_stats[major] = major_stats.get(major, 0) + 1

print(f"\n=== 专业分布（前15）===")
sorted_majors = sorted(major_stats.items(), key=lambda x: -x[1])
for major, count in sorted_majors[:15]:
    print(f"  {major}: {count}个")

# 找出一些非"不限"的岗位示例
print(f"\n=== 有具体专业要求的岗位示例 ===")
count = 0
for job in all_jobs:
    if job.major and job.major != '不限' and count < 10:
        print(f"\n{count+1}. {job.sheet_name} - {job.unit}")
        print(f"   岗位: {job.job_type}")
        print(f"   专业: {job.major}")
        print(f"   学历: {job.education}")
        print(f"   学位: {job.degree}")
        count += 1
