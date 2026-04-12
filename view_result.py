#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看筛选结果
"""
import pandas as pd
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取结果
df = pd.read_excel('筛选结果.xlsx')

print("=" * 80)
print(f"筛选结果汇总 - 共 {len(df)} 个岗位")
print("=" * 80)

# 匹配度分布
print("\n【匹配度分布】")
for level, count in df['匹配度'].value_counts().items():
    print(f"  {level}: {count} 个岗位")

# 按地市统计（完全符合）
print("\n【完全符合岗位 - 按地市分布】")
perfect_df = df[df['匹配度'] == '完全符合']
for city, count in perfect_df['所属地市'].value_counts().items():
    print(f"  {city}: {count} 个")

# 竞争比分析
print("\n【竞争比分析（完全符合且有数据）】")
perfect_with_data = perfect_df[perfect_df['缴费人数'] > 0]
if len(perfect_with_data) > 0:
    ratios = perfect_with_data['竞争比数值'].tolist()
    avg_ratio = sum(ratios) / len(ratios)
    print(f"  平均竞争比: {avg_ratio:.1f}:1")
    print(f"  最低竞争比: {min(ratios):.1f}:1")
    print(f"  最高竞争比: {max(ratios):.1f}:1")

    # 竞争比分布
    low = len([r for r in ratios if r < 30])
    mid = len([r for r in ratios if 30 <= r < 100])
    high = len([r for r in ratios if r >= 100])
    print(f"\n  竞争比分布:")
    print(f"    低竞争(<30:1):  {low} 个")
    print(f"    中竞争(30-100): {mid} 个")
    print(f"    高竞争(>100):   {high} 个")

# 显示前10个完全符合且竞争比低的岗位
print("\n【推荐岗位（完全符合 + 竞争比最低）】")
top_jobs = perfect_with_data.nsmallest(10, '竞争比数值')
for idx, row in top_jobs.iterrows():
    print(f"\n  [{idx+1}] {row['所属地市']} - {row['服务单位']}")
    major = str(row['专业要求'])[:30] if pd.notna(row['专业要求']) else '不限'
    print(f"      岗位: {row['岗位类型']} | 专业: {major}...")
    print(f"      竞争比: {row['竞争比']} (招{row['招募人数']}人，{int(row['缴费人数'])}人缴费)")
    if row['匹配说明']:
        match_desc = str(row['匹配说明'])[:50] if pd.notna(row['匹配说明']) else ''
    if match_desc:
        print(f"      匹配说明: {match_desc}")

print("\n" + "=" * 80)
print("结果已保存到: 筛选结果.xlsx")
print("=" * 80)
