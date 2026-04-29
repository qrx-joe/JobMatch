#!/usr/bin/env python3
import glob
import io
import sys

import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

files = glob.glob("*.xlsx")
files = [f for f in files if "岗位汇总表" in f and not f.startswith("~$")]
file_path = files[0]

print("=== 检查所有列的内容 ===")

# 读取太原市
df = pd.read_excel(file_path, sheet_name="太原市", header=1)

print(f"总行数: {len(df)}")
print(f"\n列名: {list(df.columns)}")

# 显示前3行的所有列数据
print("\n=== 前3行完整数据 ===")
for i in range(min(3, len(df))):
    print(f"\n--- 行{i + 1} ---")
    for col in df.columns:
        val = df.iloc[i][col]
        if pd.notna(val) and str(val).strip():
            print(f"  {col}: {val}")

# 特别检查Unnamed列
print("\n=== 检查Unnamed列 ===")
unnamed_cols = [c for c in df.columns if "Unnamed" in str(c)]
print(f"Unnamed列: {unnamed_cols}")

for col in unnamed_cols:
    print(f"\n列 {col}:")
    values = df[col].dropna().unique()
    print(f"  唯一值({len(values)}个): {list(values[:5])}")  # 只显示前5个
