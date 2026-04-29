#!/usr/bin/env python3
import glob
import io
import sys

import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 找到文件
files = glob.glob("*.xlsx")
files = [f for f in files if "岗位汇总表" in f and not f.startswith("~$")]
file_path = files[0]

print("=== 测试太原市解析 ===")

# 读取
df = pd.read_excel(file_path, sheet_name="太原市", header=1)
print(f"列名: {df.columns.tolist()}")
print(f"总行数: {len(df)}")

# 测试第一行数据
row = df.iloc[1]  # 第二行（第一行是NaN）
print("\n第一行数据:")
print(f"  序号: {row.iloc[0]}")
print(f"  类型: {type(row.iloc[0])}")

# 测试是否能转换为整数
try:
    val = int(float(row.iloc[0]))
    print(f"  转换成功: {val}")
except Exception as e:
    print(f"  转换失败: {e}")


# 测试列名清理
def clean_column_name(name):
    name = str(name).replace("\n", "").replace(" ", "").strip()
    if name.startswith("Unnamed:"):
        return ""
    return name


col_map = {clean_column_name(str(c)): c for c in row.index}
print("\n清理后的列名映射:")
for k, v in list(col_map.items())[:10]:
    print(f"  '{k}' -> '{v}'")

# 测试获取值
print("\n测试获取字段:")
test_names = ["服务单位", "服务单位名称", "单位"]
for name in test_names:
    clean_name = clean_column_name(name)
    print(f"  查找 '{name}' (清理后: '{clean_name}')")

    if name in col_map:
        val = row[col_map[name]]
        print(f"    直接匹配成功: {val}")
    else:
        print("    直接匹配失败")

    found = False
    for col_clean, col_original in col_map.items():
        if clean_name in col_clean or col_clean in clean_name:
            val = row[col_original]
            print(f"    模糊匹配成功: {col_original} -> {val}")
            found = True
            break
    if not found:
        print("    模糊匹配失败")
