#!/usr/bin/env python3
"""
调试Sheet读取
"""

import glob
import io
import os
import sys

import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 找到文件
files = glob.glob("*岗位汇总表*.xlsx")
files = [f for f in files if not os.path.basename(f).startswith("~$")]

if not files:
    print("未找到岗位表文件")
    exit(1)

file_path = files[0]
print(f"分析文件: {file_path}")
print("=" * 80)

# 读取所有sheet
xl = pd.ExcelFile(file_path)
print(f"\n共有 {len(xl.sheet_names)} 个Sheet:")
for i, name in enumerate(xl.sheet_names, 1):
    print(f"  {i}. {name}")

print("\n" + "=" * 80)

# 逐个检查每个sheet的前几行
for sheet_name in xl.sheet_names:
    print(f"\n【Sheet: {sheet_name}】")
    print("-" * 80)

    try:
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        print(f"总行数: {len(df_raw)}")

        # 显示前8行
        for idx in range(min(8, len(df_raw))):
            row = df_raw.iloc[idx]
            row_values = [str(v)[:40] if pd.notna(v) else "" for v in row.values]
            print(f"  行{idx}: {row_values}")

        # 找表头
        print("\n  查找表头...")
        header_row_idx = None
        for idx in range(min(10, len(df_raw))):
            row_text = " ".join([str(v) for v in df_raw.iloc[idx].values if pd.notna(v)])
            if "序号" in row_text and ("服务单位" in row_text or "单位" in row_text):
                # 检查是否有岗位相关字段
                has_job_field = any(
                    kw in row_text for kw in ["岗位", "岗位类型", "岗位名称", "学历", "专业"]
                )
                if has_job_field:
                    header_row_idx = idx
                    print(f"    -> 表头在第 {idx} 行")
                    break

        if header_row_idx is None:
            print("    -> 未找到表头行！")

    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "=" * 80)
