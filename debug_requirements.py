#!/usr/bin/env python3
import glob
import io
import sys

import pandas as pd

# 强制UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

files = glob.glob("*.xlsx")
files = [f for f in files if "岗位汇总表" in f and not f.startswith("~$")]
file_path = files[0]

print("=== 调试服务岗位要求列 ===")

# 读取太原市
header_row = None
for idx in range(10):
    df_test = pd.read_excel(file_path, sheet_name="太原市", header=None, nrows=10)
    row_text = " ".join([str(v) for v in df_test.iloc[idx].values if pd.notna(v)])
    if "序号" in row_text and "服务" in row_text:
        header_row = idx
        break

if header_row is None:
    print("未找到表头行")
else:
    df = pd.read_excel(file_path, sheet_name="太原市", header=header_row)
    print(f"表头行: {header_row}")
    print(f"总行数: {len(df)}")
    print(f"\n列名: {list(df.columns)}")

    # 找到服务岗位要求列
    req_col = None
    for col in df.columns:
        if "服务岗位要求" in str(col):
            req_col = col
            break

    if req_col:
        print(f"\n服务岗位要求列名: {req_col}")
        print("\n前10行数据:")
        for i in range(min(10, len(df))):
            val = df.iloc[i][req_col]
            unit_col = "服务单位" if "服务单位" in df.columns else df.columns[1]
            unit = df.iloc[i][unit_col] if unit_col in df.columns else "N/A"
            print(f"\n行{i + 1}:")
            print(f"  单位: {unit}")
            print(f"  要求: {val}")
    else:
        print("未找到服务岗位要求列")
