#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import glob
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 找到文件
files = glob.glob('*岗位汇总表*.xlsx')
files = [f for f in files if not os.path.basename(f).startswith('~$')]

file_path = files[0]

# 测试大同市
df_raw = pd.read_excel(file_path, sheet_name='大同市', header=None)
print("=== 大同市 Sheet ===")
print(f"总行数: {len(df_raw)}")

for idx in range(min(5, len(df_raw))):
    row = df_raw.iloc[idx]
    print(f"\n行{idx}:")
    print(f"  值: {row.tolist()}")
    row_text = ' '.join([str(v) for v in row.values if pd.notna(v)])
    print(f"  文本: {row_text[:100]}")

    # 检查表头条件
    has_xuhao = '序号' in row_text
    has_danwei = '服务' in row_text and '单位' in row_text
    has_gangwei = any(kw in row_text for kw in ['岗位', '岗位类型', '岗位名称'])

    print(f"  含'序号': {has_xuhao}, 含'服务单位': {has_danwei}, 含岗位相关: {has_gangwei}")

    if has_xuhao and has_danwei:
        print(f"  -> 这行可能是表头!")

# 重新读取
df = pd.read_excel(file_path, sheet_name='大同市', header=1)
print("\n=== 读取后的列名 ===")
print(df.columns.tolist())
print("\n=== 前3行数据 ===")
print(df.head(3))
