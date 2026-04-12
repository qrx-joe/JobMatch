#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import glob
import os
import warnings
import io
import sys
warnings.filterwarnings('ignore')

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

dir_path = r'D:\EdgeDownload\QQ音乐\three-zhi-one-fu'
xlsx_files = [f for f in glob.glob(dir_path + '\\*.xlsx') if not os.path.basename(f).startswith('~$')]

if not xlsx_files:
    print("未找到xlsx文件")
    sys.exit(1)

file1 = xlsx_files[0]
print(f"处理文件: {os.path.basename(file1)}")

# 使用ExcelFile读取
xl = pd.ExcelFile(file1)
print(f"包含的sheet: {xl.sheet_names}")

# 读取吕梁市sheet
df = pd.read_excel(file1, sheet_name='吕梁市', header=None)
print("=" * 120)
print("吕梁市2026年'三支一扶'岗位详细信息")
print("=" * 120)

# 从输出看，表头在第1行和第2行
# 第1行是主表头，第2行是子表头
# 数据从第3行开始

# 手动构建表头
main_headers = df.iloc[1].tolist()
sub_headers = df.iloc[2].tolist()

# 合并表头
final_headers = []
for i, (main, sub) in enumerate(zip(main_headers, sub_headers)):
    main_str = str(main) if pd.notna(main) else ''
    sub_str = str(sub) if pd.notna(sub) else ''
    if sub_str.strip() and sub_str != 'nan':
        final_headers.append(f"{main_str}_{sub_str}")
    else:
        final_headers.append(main_str)

print(f"列名: {final_headers}\n")

# 从第3行开始读取数据
data_rows = []
for idx in range(3, len(df)):
    row = df.iloc[idx]
    if pd.notna(row.iloc[0]):
        row_dict = {}
        for i, val in enumerate(row):
            if i < len(final_headers):
                row_dict[final_headers[i]] = val
        data_rows.append(row_dict)

print(f"吕梁市总岗位数: {len(data_rows)}")

# 筛选经济学相关岗位
economics_keywords = ['经济', '经济学', '金融', '财务', '会计', '财税', '财政', '审计', '贸易', '商务', '工商']

economics_jobs = []
for row in data_rows:
    row_text = ' '.join([str(v) for v in row.values() if pd.notna(v)])
    if any(kw in row_text for kw in economics_keywords):
        economics_jobs.append(row)

# 输出结果
output_lines = []
output_lines.append("=" * 120)
output_lines.append("吕梁市2026年'三支一扶'岗位详细信息 - 经济学相关专业")
output_lines.append("=" * 120)
output_lines.append(f"\n共找到 {len(economics_jobs)} 个经济学相关专业岗位\n")

print(f"\n共找到 {len(economics_jobs)} 个经济学相关专业岗位\n")

for i, job in enumerate(economics_jobs, 1):
    separator = '━' * 120
    output_lines.append(f"\n{separator}")
    output_lines.append(f"【岗位 {i}】")
    output_lines.append(separator)

    print(f"\n{separator}")
    print(f"【岗位 {i}】")
    print(separator)

    for col, val in job.items():
        if pd.notna(val) and str(val).strip() and str(val) != 'nan':
            line = f"  {col}: {val}"
            print(line)
            output_lines.append(line)

# 保存到文件
with open('吕梁市经济学岗位详细信息.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"\n\n详细结果已保存到: 吕梁市经济学岗位详细信息.txt")
