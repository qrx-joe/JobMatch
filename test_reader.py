#!/usr/bin/env python3
import glob
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 导入读取器
from excel_reader_v2 import SimpleJobReader

# 找到文件
files = glob.glob("*.xlsx")
files = [f for f in files if "岗位汇总表" in f and not f.startswith("~$")]

if not files:
    print("未找到岗位表文件")
    sys.exit(1)

file_path = files[0]
print(f"读取文件: {file_path}")
print(f"文件存在: {os.path.exists(file_path)}")

# 创建读取器
reader = SimpleJobReader(file_path)

# 测试读取单个sheet
print("\n=== 测试读取太原市 ===")
jobs = reader._read_sheet("太原市")
print(f"读取到 {len(jobs)} 个岗位")

if jobs:
    for i, job in enumerate(jobs[:3]):
        print(f"\n岗位 {i + 1}:")
        print(f"  单位: {job.unit}")
        print(f"  岗位: {job.job_type}")
        print(f"  专业: {job.major}")
else:
    print("没有读取到岗位，让我调试...")

# 测试读取所有
print("\n=== 测试读取全部 ===")
all_jobs = reader.read_all()
print(f"总共读取 {len(all_jobs)} 个岗位")
