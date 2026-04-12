#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import glob
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

files = glob.glob('*.xlsx')
files = [f for f in files if '岗位汇总表' in f and not f.startswith('~$')]
file_path = files[0]

print("=== 测试_find_value逻辑 ===")

# 读取太原市
df = pd.read_excel(file_path, sheet_name='太原市', header=1)

# 取第一行有效数据（跳过头行"学历"等）
row = df.iloc[1]  # 第二行数据
cols = list(row.index)

print(f"列名: {cols}")
print(f"\nRow index类型: {type(row.index)}")
print(f"Row index: {row.index.tolist()}")

# 测试直接访问
print("\n=== 直接访问测试 ===")
print(f"row['Unnamed: 7']: {row['Unnamed: 7']}")
print(f"row.loc['Unnamed: 7']: {row.loc['Unnamed: 7']}")

# 模拟_find_value
def find_value(row, cols, possible_names, default=''):
    """查找字段值"""
    # 先按列名查找
    for name in possible_names:
        for col in cols:
            col_str = str(col).replace('\n', '').replace(' ', '')
            if name in col_str or col_str in name:
                val = row[col]
                if pd.notna(val):
                    return str(val).strip()
    return default

print("\n=== _find_value测试结果 ===")
print(f"查找专业('Unnamed: 7'): '{find_value(row, cols, ['Unnamed: 7'])}'")
print(f"查找学历('服务岗位要求'): '{find_value(row, cols, ['服务岗位要求'])}'")

# 显示整行数据
print("\n=== 整行数据 ===")
for col in cols:
    val = row[col]
    if pd.notna(val):
        print(f"  {col}: {val}")
