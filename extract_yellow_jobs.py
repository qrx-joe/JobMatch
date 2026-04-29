#!/usr/bin/env python3
"""
提取标黄的岗位，并与统计数据对照，生成Excel报告
"""

import glob
import io
import os
import sys
import warnings

import openpyxl
import pandas as pd

warnings.filterwarnings("ignore")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 文件路径
dir_path = r"D:\EdgeDownload\QQ音乐\three-zhi-one-fu"
xlsx_files = [
    f for f in glob.glob(dir_path + "\\*.xlsx") if not os.path.basename(f).startswith("~$")
]

if not xlsx_files:
    print("未找到xlsx文件")
    sys.exit(1)

jobs_file = xlsx_files[0]
stats_file = r"D:\EdgeDownload\QQ音乐\three-zhi-one-fu\P020260410598205300172.xls"

print(f"处理岗位文件: {os.path.basename(jobs_file)}")
print(f"处理统计文件: {os.path.basename(stats_file)}")

# ========== 第一步：读取统计文件 ==========
print("\n" + "=" * 80)
print("第一步：读取统计数据")
print("=" * 80)

stats_df = pd.read_excel(stats_file, sheet_name="sheet1", header=1)
stats_df.columns = ["服务单位", "岗位类型", "招募人数", "填报信息人数", "初审通过人数", "缴费人数"]

# 清理服务单位名称，用于匹配
stats_map = {}
for _idx, row in stats_df.iterrows():
    if pd.notna(row["服务单位"]):
        key = str(row["服务单位"]).strip()
        stats_map[key] = {
            "填报信息人数": row["填报信息人数"] if pd.notna(row["填报信息人数"]) else 0,
            "初审通过人数": row["初审通过人数"] if pd.notna(row["初审通过人数"]) else 0,
            "缴费人数": row["缴费人数"] if pd.notna(row["缴费人数"]) else 0,
            "招募人数": row["招募人数"] if pd.notna(row["招募人数"]) else 0,
        }

print(f"统计文件共 {len(stats_map)} 条记录")

# ========== 第二步：读取岗位文件并识别黄色背景 ==========
print("\n" + "=" * 80)
print("第二步：识别标黄的岗位")
print("=" * 80)

# 使用openpyxl读取以获取样式
wb = openpyxl.load_workbook(jobs_file)

yellow_jobs = []

for sheet_name in wb.sheetnames:
    if sheet_name == "省林草局":  # 跳过省林草局
        continue

    ws = wb[sheet_name]
    print(f"\n检查Sheet: {sheet_name}")

    # 查找表头行（通常在第2行，索引为2）
    # 数据从第4行开始（索引为4）

    yellow_count = 0
    for row_idx, row in enumerate(ws.iter_rows(min_row=4, max_row=ws.max_row), start=4):
        # 检查该行的第一个单元格（序号列）是否有黄色背景
        first_cell = row[0] if len(row) > 0 else None

        if first_cell and first_cell.value is not None:
            # 检查单元格填充颜色
            fill = first_cell.fill
            is_yellow = False

            if fill and fill.patternType == "solid" and fill.fgColor:
                # 检查黄色（RGB: FFFF00 或索引 6）
                color = fill.fgColor
                if (
                    color.rgb
                    and "FFFF00" in str(color.rgb).upper()
                    or color.rgb
                    and "FF00" in str(color.rgb).upper()
                    and str(color.rgb).upper().startswith("FF")
                    or color.index == 6
                    or color.index == "6"
                ):
                    is_yellow = True

            if is_yellow:
                yellow_count += 1
                # 提取该行数据
                row_data = {
                    "所属地市": sheet_name,
                    "行号": row_idx,
                    "序号": str(row[0].value) if len(row) > 0 and row[0].value else "",
                    "服务单位": str(row[1].value) if len(row) > 1 and row[1].value else "",
                    "岗位类型": str(row[2].value) if len(row) > 2 and row[2].value else "",
                    "服务类别": str(row[3].value) if len(row) > 3 and row[3].value else "",
                    "招募人数": str(row[4].value) if len(row) > 4 and row[4].value else "",
                    "学历": str(row[5].value) if len(row) > 5 and row[5].value else "",
                    "学位": str(row[6].value) if len(row) > 6 and row[6].value else "",
                    "专业": str(row[7].value) if len(row) > 7 and row[7].value else "",
                    "相关资格": str(row[8].value) if len(row) > 8 and row[8].value else "",
                    "其他": str(row[9].value) if len(row) > 9 and row[9].value else "",
                    "联系电话": str(row[10].value) if len(row) > 10 and row[10].value else "",
                    "联系人": str(row[11].value) if len(row) > 11 and row[11].value else "",
                    "岗位描述": str(row[12].value) if len(row) > 12 and row[12].value else "",
                    "福利待遇": str(row[13].value) if len(row) > 13 and row[13].value else "",
                }
                yellow_jobs.append(row_data)

    print(f"  找到 {yellow_count} 个标黄岗位")

print(f"\n总共找到 {len(yellow_jobs)} 个标黄岗位")

# ========== 第三步：对照统计文件，补充数据 ==========
print("\n" + "=" * 80)
print("第三步：对照统计数据")
print("=" * 80)

# 尝试匹配统计数据
for job in yellow_jobs:
    service_unit = job["服务单位"].strip()
    job_type = job["岗位类型"].strip()

    # 构建匹配键（地市-区县-单位名称）
    city = job["所属地市"]

    # 尝试多种匹配方式
    matched = False

    # 方式1：完整匹配（地市+区县+单位）
    for stats_key in stats_map:
        # 检查服务单位是否包含在统计的服务单位中
        if service_unit in stats_key or stats_key in service_unit:
            # 进一步检查岗位类型
            stats_type = stats_key.split("-")[-1] if "-" in stats_key else ""
            if job_type in stats_key:
                job["填报信息人数"] = stats_map[stats_key]["填报信息人数"]
                job["初审通过人数"] = stats_map[stats_key]["初审通过人数"]
                job["缴费人数"] = stats_map[stats_key]["缴费人数"]
                job["统计招募人数"] = stats_map[stats_key]["招募人数"]
                job["匹配状态"] = "已匹配"
                matched = True
                break

    if not matched:
        # 方式2：仅匹配单位名称
        for stats_key in stats_map:
            # 提取单位名称部分（最后一个-后面的内容）
            unit_name = stats_key.split("-")[-1] if "-" in stats_key else stats_key
            if unit_name in service_unit or service_unit in unit_name:
                job["填报信息人数"] = stats_map[stats_key]["填报信息人数"]
                job["初审通过人数"] = stats_map[stats_key]["初审通过人数"]
                job["缴费人数"] = stats_map[stats_key]["缴费人数"]
                job["统计招募人数"] = stats_map[stats_key]["招募人数"]
                job["匹配状态"] = "部分匹配"
                matched = True
                break

    if not matched:
        job["填报信息人数"] = 0
        job["初审通过人数"] = 0
        job["缴费人数"] = 0
        job["统计招募人数"] = 0
        job["匹配状态"] = "未匹配"

matched_count = sum(1 for job in yellow_jobs if job["匹配状态"] == "已匹配")
partial_count = sum(1 for job in yellow_jobs if job["匹配状态"] == "部分匹配")
unmatched_count = sum(1 for job in yellow_jobs if job["匹配状态"] == "未匹配")

print(
    f"匹配结果：已匹配 {matched_count} 条，部分匹配 {partial_count} 条，未匹配 {unmatched_count} 条"
)

# ========== 第四步：生成Excel文件 ==========
print("\n" + "=" * 80)
print("第四步：生成Excel文件")
print("=" * 80)

# 准备输出数据
output_data = []
for job in yellow_jobs:
    output_data.append(
        {
            "所属地市": job["所属地市"],
            "序号": job["序号"],
            "服务单位": job["服务单位"],
            "岗位类型": job["岗位类型"],
            "服务类别": job["服务类别"],
            "招募人数": job["招募人数"],
            "学历": job["学历"],
            "学位": job["学位"],
            "专业": job["专业"],
            "相关资格": job["相关资格"],
            "其他": job["其他"],
            "联系电话": job["联系电话"],
            "联系人": job["联系人"],
            "岗位描述": job["岗位描述"],
            "福利待遇": job["福利待遇"],
            "填报信息人数": job["填报信息人数"],
            "初审通过人数": job["初审通过人数"],
            "缴费人数": job["缴费人数"],
            "匹配状态": job["匹配状态"],
        }
    )

# 创建DataFrame并保存
output_df = pd.DataFrame(output_data)

output_file = r"D:\EdgeDownload\QQ音乐\three-zhi-one-fu\标黄岗位统计信息.xlsx"
output_df.to_excel(output_file, index=False, sheet_name="标黄岗位")

print(f"\n✓ Excel文件已生成: {output_file}")
print(f"  共 {len(output_data)} 条记录")

# 显示前5条
print("\n前5条记录预览:")
print(output_df.head().to_string())
