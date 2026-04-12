#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import glob
import warnings
import io
import sys
warnings.filterwarnings('ignore')

# 重定向输出到UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置显示选项
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# 获取当前目录下所有Excel文件
excel_files = glob.glob('*.xlsx') + glob.glob('*.xls')

print("=" * 100)
print("山西省2026年度'三支一扶'岗位筛选结果")
print("筛选条件：专业=经济学相关、学历=本科及以上、吕梁市")
print("=" * 100)

# 吕梁市相关关键词
lvliang_keywords = ['吕梁', '离石', '孝义', '汾阳', '文水', '交城', '兴县', '临县', '柳林', '石楼', '岚县', '方山', '中阳', '交口']
# 经济学相关关键词
economics_keywords = ['经济', '经济学', '金融', '财务', '会计', '财税', '财政', '审计', '贸易', '商务', '工商', '管理']
# 学历关键词
edu_keywords = ['本科', '学士', '大学', '大专及以上', '本科及以上', '研究生', '硕士']

all_matching_jobs = []

for f in excel_files:
    print(f"\n{'='*100}")
    print(f"处理文件: {f}")
    print('=' * 100)

    try:
        # 读取查看结构
        df_raw = pd.read_excel(f, header=None)
        print(f"总行数: {len(df_raw)}, 总列数: {len(df_raw.columns)}")

        # 找到真正的表头行
        header_row = None
        for idx in range(min(10, len(df_raw))):
            row_text = str(df_raw.iloc[idx].values)
            if any(k in row_text for k in ['序号', '服务单位', '岗位名称', '学历', '专业', '招募人数']):
                header_row = idx
                print(f"表头在第 {idx+1} 行")
                break

        if header_row is None:
            header_row = 0

        # 使用找到的表头重新读取
        df = pd.read_excel(f, header=header_row)

        # 打印列名
        print(f"列名: {list(df.columns)}")

        # 逐行筛选
        for idx, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue

            row_text = ' '.join([str(v) for v in row.values if pd.notna(v)])

            # 检查是否满足条件
            has_lvliang = any(kw in row_text for kw in lvliang_keywords)
            has_economics = any(kw in row_text for kw in economics_keywords)
            has_bachelor = any(kw in row_text for kw in edu_keywords)

            if has_lvliang:
                job_info = {
                    '文件名': f,
                    '行号': idx + 1,
                    '吕梁相关': has_lvliang,
                    '经济相关': has_economics,
                    '本科相关': has_bachelor,
                    '原始数据': row.to_dict()
                }
                all_matching_jobs.append(job_info)

    except Exception as e:
        print(f"错误: {e}")

# 输出结果到控制台和文件
output_lines = []
output_lines.append("=" * 100)
output_lines.append(f"找到 {len(all_matching_jobs)} 个吕梁市相关岗位")
output_lines.append("=" * 100)

# 按文件分组
from collections import defaultdict
jobs_by_file = defaultdict(list)
for job in all_matching_jobs:
    jobs_by_file[job['文件名']].append(job)

for fname, jobs in jobs_by_file.items():
    output_lines.append(f"\n{'─'*100}")
    output_lines.append(f"文件: {fname}")
    output_lines.append('─'*100)

    # 经济学相关岗位
    economics_jobs = [j for j in jobs if j['经济相关']]
    if economics_jobs:
        output_lines.append(f"\n  ★ 经济学相关专业岗位 ({len(economics_jobs)}个):")
        for job in economics_jobs:
            output_lines.append(f"\n    行号: {job['行号']}")
            for k, v in job['原始数据'].items():
                if pd.notna(v) and str(v).strip():
                    output_lines.append(f"      {k}: {v}")

    # 其他岗位
    other_jobs = [j for j in jobs if not j['经济相关']]
    if other_jobs:
        output_lines.append(f"\n  ○ 其他专业岗位 ({len(other_jobs)}个):")
        for job in other_jobs[:20]:  # 最多显示20个
            output_lines.append(f"\n    行号: {job['行号']}")
            for k, v in job['原始数据'].items():
                if pd.notna(v) and str(v).strip():
                    output_lines.append(f"      {k}: {v}")

# 输出到控制台
for line in output_lines:
    print(line)

# 同时写入文件
with open('筛选结果.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"\n\n结果已保存到: 筛选结果.txt")
