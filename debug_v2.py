#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 测试读取太原市
import glob
files = glob.glob('*.xlsx')
files = [f for f in files if '岗位汇总表' in f and not f.startswith('~$')]
file_path = files[0]

print("=== 测试读取太原市 ===")
df_raw = pd.read_excel(file_path, sheet_name='太原市', header=None)
print(f"总行数: {len(df_raw)}")

# 检查每一行
for idx in range(min(6, len(df_raw))):
    row = df_raw.iloc[idx]
    row_values = row.tolist()
    print(f"\n行{idx}: {row_values[:5]}...")  # 只显示前5列

    row_text = ' '.join([str(v) for v in row_values if pd.notna(v)])
    print(f"  文本: {row_text[:80]}")

    # 检查条件
    has_xuhao = '序号' in row_text
    has_danwei = '服务' in row_text and '单位' in row_text
    print(f"  含'序号': {has_xuhao}, 含'服务单位': {has_danwei}")

    if has_xuhao and has_danwei:
        print(f"  -> 这是表头行!")

# 使用header=1读取
print("\n=== 使用header=1读取 ===")
df = pd.read_excel(file_path, sheet_name='太原市', header=1)
print(f"列名: {df.columns.tolist()}")
print(f"\n前3行:")
print(df.head(3))
