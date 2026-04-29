#!/usr/bin/env python3
import glob
import io
import os
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 使用glob获取文件
dir_path = r"D:\EdgeDownload\QQ音乐\three-zhi-one-fu"

# 获取第一个xlsx文件（排除临时文件）
xlsx_files = [
    f for f in glob.glob(dir_path + "\\*.xlsx") if not os.path.basename(f).startswith("~$")
]
print(f"找到的xlsx文件: {xlsx_files}")

if not xlsx_files:
    print("未找到xlsx文件")
    sys.exit(1)

file1 = xlsx_files[0]
print(f"\n处理文件: {file1}")

# 获取所有sheet名称
xl = pd.ExcelFile(file1)
print("=" * 80)
print(f"包含的sheet: {xl.sheet_names}")
print("=" * 80)

# 读取每个sheet的前几行
for sheet_name in xl.sheet_names:
    print(f"\n{'=' * 80}")
    print(f"Sheet: {sheet_name}")
    print("=" * 80)

    df = pd.read_excel(file1, sheet_name=sheet_name, header=None)
    print(f"行数: {len(df)}, 列数: {len(df.columns)}")
    print("\n前10行数据:")
    print(df.head(10).to_string())
