#!/usr/bin/env python3
"""
验证生成的Excel文件
"""

import io
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

output_file = r"D:\EdgeDownload\QQ音乐\three-zhi-one-fu\标黄岗位统计信息.xlsx"

# 读取生成的Excel文件
df = pd.read_excel(output_file)

print("=" * 100)
print("标黄岗位统计信息 - 完整报告")
print("=" * 100)

print(f"\n总计：{len(df)} 个标黄岗位")
print(f"包含字段：{list(df.columns)}")

print("\n" + "=" * 100)
print("按地市分布")
print("=" * 100)
city_counts = df["所属地市"].value_counts().sort_values(ascending=False)
for city, count in city_counts.items():
    print(f"  {city}: {count} 个")

print("\n" + "=" * 100)
print("按匹配状态分布")
print("=" * 100)
match_counts = df["匹配状态"].value_counts()
for status, count in match_counts.items():
    print(f"  {status}: {count} 个")

print("\n" + "=" * 100)
print("所有标黄岗位详情")
print("=" * 100)

for idx, row in df.iterrows():
    print(f"\n【{idx + 1}】{row['所属地市']} - {row['服务单位']}")
    print(
        f"  岗位类型: {row['岗位类型']} | 服务类别: {row['服务类别']} | 招募人数: {row['招募人数']}"
    )
    print(f"  学历: {row['学历']} | 学位: {row['学位']} | 专业: {row['专业']}")
    print(f"  其他: {row['其他']} | 联系电话: {row['联系电话']} | 联系人: {row['联系人']}")
    print(
        f"  填报信息人数: {row['填报信息人数']} | 初审通过人数: {row['初审通过人数']} | 缴费人数: {row['缴费人数']}"
    )
    print(f"  匹配状态: {row['匹配状态']}")

print("\n" + "=" * 100)
print("统计摘要")
print("=" * 100)
print(f"总招募人数: {df['招募人数'].sum()}")
print(f"总填报信息人数: {df['填报信息人数'].sum()}")
print(f"总初审通过人数: {df['初审通过人数'].sum()}")
print(f"总缴费人数: {df['缴费人数'].sum()}")

if df["缴费人数"].sum() > 0:
    ratio = df["缴费人数"].sum() / df["招募人数"].sum()
    print(f"平均竞争比: {ratio:.2f} : 1")
