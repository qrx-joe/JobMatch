#!/usr/bin/env python3
import glob

# 设置输出编码
import io
import os
import sys

import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 找到文件
files = glob.glob("*.xlsx")
files = [f for f in files if not os.path.basename(f).startswith("~$")]
files = [f for f in files if "岗位汇总表" in f or "附件1" in f]

if not files:
    print("未找到岗位表文件")
    exit(1)

file_path = files[0]

# 输出到文件
output_lines = []
output_lines.append(f"分析文件: {file_path}")
output_lines.append("=" * 80)

# 读取所有sheet
xl = pd.ExcelFile(file_path)
output_lines.append(f"\n共有 {len(xl.sheet_names)} 个Sheet:")
for i, name in enumerate(xl.sheet_names, 1):
    output_lines.append(f"  {i}. {name}")

output_lines.append("\n" + "=" * 80)

# 分析第一个sheet的详细结构
sheet_name = xl.sheet_names[0]
output_lines.append(f"\n【Sheet: {sheet_name}】")
output_lines.append("-" * 80)

# 不指定header读取
df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
output_lines.append(f"总行数: {len(df_raw)}, 总列数: {len(df_raw.columns)}")

# 显示前10行
output_lines.append("\n前10行内容:")
for idx in range(min(10, len(df_raw))):
    row = df_raw.iloc[idx]
    row_str = " | ".join([str(v)[:25] if pd.notna(v) else "" for v in row.values])
    output_lines.append(f"  行{idx + 1}: {row_str}")

# 找表头
output_lines.append("\n尝试找表头行...")
for idx in range(min(10, len(df_raw))):
    row_text = str(df_raw.iloc[idx].values)
    if any(k in row_text for k in ["序号", "服务单位", "岗位名称", "学历", "专业"]):
        output_lines.append(f"  -> 可能的表头在第 {idx + 1} 行")
        header_row = df_raw.iloc[idx]
        output_lines.append(f"  -> 列名: {list(header_row.values)}")

        # 如果有下一行，显示子表头
        if idx + 1 < len(df_raw):
            sub_header = df_raw.iloc[idx + 1]
            output_lines.append(f"  -> 子表头: {list(sub_header.values)}")
        break

# 显示一条数据样例
output_lines.append("\n数据样例（第1条）:")
df_data = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
if len(df_data) > 0:
    for col in df_data.columns:
        val = df_data.iloc[0][col]
        if pd.notna(val):
            output_lines.append(f"  {col}: {val}")

# 写入文件
with open("excel_structure_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("分析完成！结果已保存到: excel_structure_analysis.txt")
