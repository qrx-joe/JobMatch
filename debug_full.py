#!/usr/bin/env python3
import glob
import io
import sys

import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

files = glob.glob("*.xlsx")
files = [f for f in files if "岗位汇总表" in f and not f.startswith("~$")]
file_path = files[0]

print("=== 完整测试解析 ===")

df = pd.read_excel(file_path, sheet_name="太原市", header=1)
print(f"总行数: {len(df)}")


# 清理列名
def clean_column_name(name):
    name = str(name).replace("\n", "").replace(" ", "").strip()
    if name.startswith("Unnamed:"):
        return ""
    return name


# 获取值
def get_value_fuzzy(row, col_map, possible_names, default=""):
    for name in possible_names:
        if name in col_map:
            col = col_map[name]
            val = row[col]
            if pd.notna(val):
                return str(val).strip()

        clean_name = clean_column_name(name)
        for col_clean, col_original in col_map.items():
            if clean_name in col_clean or col_clean in clean_name:
                val = row[col_original]
                if pd.notna(val):
                    return str(val).strip()
    return default


# 解析行
def parse_row(row, sheet_name):
    col_map = {clean_column_name(str(c)): c for c in row.index}

    unit = get_value_fuzzy(row, col_map, ["服务单位", "服务单位名称", "单位"], "")
    print(f"  单位: '{unit}'")

    if not unit or unit in ["服务单位", "nan", ""]:
        print("  -> 无效单位，返回None")
        return None

    return {"unit": unit}


# 测试前5行
for idx in range(1, 6):
    row = df.iloc[idx]
    print(f"\n索引 {idx}:")
    result = parse_row(row, "太原市")
    if result:
        print(f"  -> 成功: {result}")
    else:
        print("  -> 失败")
