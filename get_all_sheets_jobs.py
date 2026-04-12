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
print(f"处理文件: {os.path.basename(file1)}\n")

# 使用ExcelFile读取
xl = pd.ExcelFile(file1)

# 搜索所有sheet
economics_keywords = ['经济', '经济学', '金融', '财务', '会计', '财税', '财政', '审计', '贸易', '商务', '工商']
lvliang_keywords = ['吕梁', '离石', '孝义', '汾阳', '文水', '交城', '兴县', '临县', '柳林', '石楼', '岚县', '方山', '中阳', '交口']

all_matching_jobs = []

for sheet_name in xl.sheet_names:
    df = pd.read_excel(file1, sheet_name=sheet_name, header=None)

    if len(df) < 3:
        continue

    main_headers = df.iloc[1].tolist()
    sub_headers = df.iloc[2].tolist()

    final_headers = []
    for i, (main, sub) in enumerate(zip(main_headers, sub_headers)):
        main_str = str(main) if pd.notna(main) else ''
        sub_str = str(sub) if pd.notna(sub) else ''
        if sub_str.strip() and sub_str != 'nan':
            final_headers.append(f"{main_str}_{sub_str}")
        else:
            final_headers.append(main_str)

    for idx in range(3, len(df)):
        row = df.iloc[idx]
        if pd.notna(row.iloc[0]):
            row_dict = {'sheet': sheet_name}
            for i, val in enumerate(row):
                if i < len(final_headers):
                    row_dict[final_headers[i]] = val

            row_text = ' '.join([str(v) for v in row_dict.values() if pd.notna(v)])
            if any(kw in row_text for kw in economics_keywords) and any(lk in row_text for lk in lvliang_keywords):
                row_dict['row_num'] = idx + 1
                all_matching_jobs.append(row_dict)

# 输出所有匹配岗位
print("=" * 120)
print("山西省2026年度'三支一扶'岗位 - 吕梁市经济学相关专业")
print("=" * 120)
print(f"\n共找到 {len(all_matching_jobs)} 个岗位\n")

output_lines = []
output_lines.append("=" * 120)
output_lines.append("山西省2026年度'三支一扶'岗位 - 吕梁市经济学相关专业")
output_lines.append("=" * 120)
output_lines.append(f"\n共找到 {len(all_matching_jobs)} 个岗位\n")

for i, job in enumerate(all_matching_jobs, 1):
    separator = '━' * 120
    print(f"\n{separator}")
    print(f"【岗位 {i}】 (来源: {job['sheet']}, 行号: {job['row_num']})")
    print(separator)

    output_lines.append(f"\n{separator}")
    output_lines.append(f"【岗位 {i}】 (来源: {job['sheet']}, 行号: {job['row_num']})")
    output_lines.append(separator)

    for col, val in job.items():
        if col not in ['sheet', 'row_num'] and pd.notna(val) and str(val).strip() and str(val) != 'nan':
            line = f"  {col}: {val}"
            print(line)
            output_lines.append(line)

# 保存到文件
with open('吕梁市经济学岗位完整信息.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"\n\n详细结果已保存到: 吕梁市经济学岗位完整信息.txt")
