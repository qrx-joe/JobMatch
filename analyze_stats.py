#!/usr/bin/env python3
import glob
import io
import os
import sys

import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 找到统计表
files = glob.glob("*.xls") + glob.glob("*.xlsx")
files = [f for f in files if "P0" in f or "统计" in f]
files = [f for f in files if not os.path.basename(f).startswith("~$")]

if not files:
    print("未找到统计表文件")
    exit(1)

output_lines = []

for file_path in files:
    output_lines.append(f"\n{'=' * 80}")
    output_lines.append(f"分析文件: {file_path}")
    output_lines.append("=" * 80)

    try:
        # 读取所有sheet
        xl = pd.ExcelFile(file_path)
        output_lines.append(f"\n共有 {len(xl.sheet_names)} 个Sheet: {xl.sheet_names}")

        # 分析第一个sheet
        sheet_name = xl.sheet_names[0]
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        output_lines.append(f"\n总行数: {len(df_raw)}, 总列数: {len(df_raw.columns)}")
        output_lines.append("\n前15行内容:")
        for idx in range(min(15, len(df_raw))):
            row = df_raw.iloc[idx]
            row_str = " | ".join([str(v)[:30] if pd.notna(v) else "" for v in row.values])
            output_lines.append(f"  行{idx + 1}: {row_str}")

    except Exception as e:
        output_lines.append(f"错误: {e}")

# 写入文件
with open("stats_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("分析完成！结果已保存到: stats_analysis.txt")
