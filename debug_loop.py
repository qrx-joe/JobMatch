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

print("=== 测试循环 ===")

df = pd.read_excel(file_path, sheet_name='太原市', header=1)
print(f"总行数: {len(df)}")
print(f"\n遍历每一行:")

count = 0
for idx, row in df.iterrows():
    print(f"\n索引 {idx}:")
    print(f"  第一列值: {row.iloc[0]} (类型: {type(row.iloc[0])})")
    print(f"  isna: {pd.isna(row.iloc[0])}")

    if pd.isna(row.iloc[0]):
        print(f"  -> 跳过 (NaN)")
        continue

    first_val = str(row.iloc[0]).strip()
    print(f"  字符串值: '{first_val}'")

    if not first_val or first_val in ['序号', 'nan', '']:
        print(f"  -> 跳过 (无效值)")
        continue

    try:
        num = int(float(first_val))
        print(f"  转换为数字: {num}")
        count += 1
        if count >= 3:
            break
    except Exception as e:
        print(f"  转换失败: {e}")
        continue

print(f"\n成功解析 {count} 行")
