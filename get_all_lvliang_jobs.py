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

# 使用ExcelFile读取
xl = pd.ExcelFile(file1)

# 搜索所有sheet中的吕梁岗位
lvliang_keywords = ['吕梁', '离石', '孝义', '汾阳', '文水', '交城', '兴县', '临县', '柳林', '石楼', '岚县', '方山', '中阳', '交口']

all_lvliang_jobs = []

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
            if any(lk in row_text for lk in lvliang_keywords):
                row_dict['row_num'] = idx + 1
                # 检查是否是管理类岗位
                if '管理' in row_text or '管理1' in row_text or '管理2' in row_text:
                    row_dict['is_management'] = True
                else:
                    row_dict['is_management'] = False
                all_lvliang_jobs.append(row_dict)

# 输出所有吕梁岗位
print("=" * 120)
print("山西省2026年度'三支一扶'岗位 - 吕梁市所有岗位")
print("=" * 120)
print(f"\n共找到 {len(all_lvliang_jobs)} 个吕梁市岗位\n")

# 分类输出
management_jobs = [j for j in all_lvliang_jobs if j.get('is_management')]
other_jobs = [j for j in all_lvliang_jobs if not j.get('is_management')]

print(f"\n管理类岗位: {len(management_jobs)} 个")
print(f"其他岗位: {len(other_jobs)} 个")

output_lines = []
output_lines.append("=" * 120)
output_lines.append("山西省2026年度'三支一扶'岗位 - 吕梁市所有岗位")
output_lines.append("=" * 120)
output_lines.append(f"\n共找到 {len(all_lvliang_jobs)} 个岗位\n")
output_lines.append(f"管理类岗位: {len(management_jobs)} 个")
output_lines.append(f"其他岗位: {len(other_jobs)} 个")

# 输出管理类岗位
print("\n" + "=" * 120)
print("【管理类岗位】")
print("=" * 120)
output_lines.append("\n" + "=" * 120)
output_lines.append("【管理类岗位】")
output_lines.append("=" * 120)

for i, job in enumerate(management_jobs, 1):
    separator = '━' * 120
    print(f"\n{separator}")
    print(f"【岗位 {i}】 (来源: {job['sheet']}, 行号: {job['row_num']})")
    print(separator)

    output_lines.append(f"\n{separator}")
    output_lines.append(f"【岗位 {i}】 (来源: {job['sheet']}, 行号: {job['row_num']})")
    output_lines.append(separator)

    for col, val in job.items():
        if col not in ['sheet', 'row_num', 'is_management'] and pd.notna(val) and str(val).strip() and str(val) != 'nan':
            line = f"  {col}: {val}"
            print(line)
            output_lines.append(line)

# 保存到文件
with open('吕梁市所有岗位信息.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"\n\n详细结果已保存到: 吕梁市所有岗位信息.txt")
