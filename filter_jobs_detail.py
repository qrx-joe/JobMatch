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

# 获取当前目录下所有Excel文件
excel_files = glob.glob('*.xlsx') + glob.glob('*.xls')

# 吕梁市相关关键词
lvliang_keywords = ['吕梁', '离石', '孝义', '汾阳', '文水', '交城', '兴县', '临县', '柳林', '石楼', '岚县', '方山', '中阳', '交口']
# 经济学相关关键词
economics_keywords = ['经济', '经济学', '金融', '财务', '会计', '财税', '财政', '审计', '贸易', '商务', '工商', '管理']

print("=" * 120)
print("山西省2026年度'三支一扶'岗位详细信息 - 吕梁市经济学相关岗位")
print("=" * 120)

for f in excel_files:
    if 'P020260410598205300172.xls' in f:
        # 这个是报名统计表，跳过
        continue

    print(f"\n正在处理文件: {f}")
    print("=" * 120)

    try:
        # 读取Excel
        df_raw = pd.read_excel(f, header=None)

        # 找到表头行
        header_row = None
        for idx in range(min(10, len(df_raw))):
            row_text = str(df_raw.iloc[idx].values)
            if any(k in row_text for k in ['序号', '服务单位', '岗位名称', '学历', '专业']):
                header_row = idx
                break

        if header_row is None:
            header_row = 0

        # 重新读取，使用正确的表头
        df = pd.read_excel(f, header=header_row)

        # 查找吕梁市+经济学相关的岗位
        matching_jobs = []
        for idx, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue

            row_text = ' '.join([str(v) for v in row.values if pd.notna(v)])

            has_lvliang = any(kw in row_text for kw in lvliang_keywords)
            has_economics = any(kw in row_text for kw in economics_keywords)

            if has_lvliang and has_economics:
                matching_jobs.append({
                    '行号': idx + 1,
                    '数据': row.to_dict()
                })

        # 输出详细信息
        print(f"\n找到 {len(matching_jobs)} 个吕梁市经济学相关岗位\n")

        for i, job in enumerate(matching_jobs, 1):
            print(f"\n{'━'*120}")
            print(f"【岗位 {i}】")
            print('━'*120)

            data = job['数据']
            for col, val in data.items():
                if pd.notna(val) and str(val).strip() and str(val) != 'nan':
                    print(f"  {col}: {val}")

        # 保存到文件
        output_lines = []
        output_lines.append("=" * 120)
        output_lines.append("山西省2026年度'三支一扶'岗位详细信息 - 吕梁市经济学相关岗位")
        output_lines.append("=" * 120)
        output_lines.append(f"\n找到 {len(matching_jobs)} 个岗位\n")

        for i, job in enumerate(matching_jobs, 1):
            output_lines.append(f"\n{'━'*120}")
            output_lines.append(f"【岗位 {i}】")
            output_lines.append('━'*120)

            data = job['数据']
            for col, val in data.items():
                if pd.notna(val) and str(val).strip() and str(val) != 'nan':
                    output_lines.append(f"  {col}: {val}")

        with open('吕梁市经济学岗位详情.txt', 'w', encoding='utf-8') as out:
            out.write('\n'.join(output_lines))

        print(f"\n\n详细结果已保存到: 吕梁市经济学岗位详情.txt")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
