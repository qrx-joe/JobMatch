#!/usr/bin/env python3
import glob

import pandas as pd

files = glob.glob("*.xlsx")
files = [f for f in files if "岗位汇总表" in f and not f.startswith("~$")]
file_path = files[0]

# 读取太原市
df_raw = pd.read_excel(file_path, sheet_name="太原市", header=None)

# 找表头行
header_row = None
for idx in range(min(10, len(df_raw))):
    row_text = " ".join([str(v) for v in df_raw.iloc[idx].values if pd.notna(v)])
    if "序号" in row_text and "服务" in row_text:
        header_row = idx
        break

print(f"表头行: {header_row}")

# 读取
df = pd.read_excel(file_path, sheet_name="太原市", header=header_row)
print(f"\n列名: {df.columns.tolist()}")

# 检查第一行数据
print("\n=== 第一行数据 ===")
row = df.iloc[1]  # 第二行（第一行是NaN）
for col in df.columns[:10]:
    val = row[col]
    print(f"  {col}: {val}")

# 特别检查专业和学历字段
print("\n=== 关键字段 ===")
for col in df.columns:
    col_str = str(col).replace("\n", "").replace(" ", "")
    if "专业" in col_str or "学历" in col_str or "学位" in col_str:
        val = row[col]
        print(f"  {col} -> {val}")
