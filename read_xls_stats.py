#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import warnings
import sys
import io
warnings.filterwarnings('ignore')

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取.xls统计数据文件
stats_file = r'D:\EdgeDownload\QQ音乐\three-zhi-one-fu\P020260410598205300172.xls'

# 读取所有sheet
xl = pd.ExcelFile(stats_file)
print(f"统计文件包含的sheet: {xl.sheet_names}")

# 读取数据
df = pd.read_excel(stats_file, sheet_name='sheet1', header=None)
print(f"\n行数: {len(df)}, 列数: {len(df.columns)}")

# 查看前几行
print("\n前5行数据:")
for i in range(min(5, len(df))):
    print(f"第{i}行: {df.iloc[i].tolist()}")

# 表头在第1行（索引1）
print("\n表头行:")
headers = df.iloc[1].tolist()
print(headers)

# 数据从第2行开始
print("\n前10条数据记录:")
data_rows = []
for i in range(2, min(12, len(df))):
    row = df.iloc[i].tolist()
    print(f"{i}: {row}")
    data_rows.append(row)
