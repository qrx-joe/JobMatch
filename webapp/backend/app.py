#!/usr/bin/env python3
"""
岗位筛选后端 API (FastAPI)
"""

import base64
import os
import tempfile

# 导入现有模块
import sys

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from excel_exporter import ExcelExporter
from excel_reader_v2 import SimpleJobReader as JobReader
from job_matcher_v2 import JobMatcherV2, MatchLevel

app = FastAPI(title="岗位筛选系统", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 数据模型
class UserProfile(BaseModel):
    major: str = "经济学"
    education: str = "本科"
    degree: str = "学士"
    gender: str = "女"
    household: str = "吕梁市"
    is_fresh_graduate: bool = False
    political_status: str = "群众"
    qualifications: list[str] = []
    work_years: int = 0
    target_cities: list[str] = []


class FilterConfig(BaseModel):
    gender_strict: bool = True
    household_strict: bool = False
    qualification_strict: bool = False
    max_ratio: int = 100


class JobResponse(BaseModel):
    sheet_name: str
    index: int
    unit: str
    job_type: str
    service_category: str
    recruit_count: int
    education: str
    degree: str
    major: str
    qualifications: str
    other: str
    phone: str
    paid: int
    match_level: str
    match_score: int
    competition_ratio: float
    match_reasons: list[str]
    mismatch_reasons: list[str]


@app.get("/")
def root():
    return {"message": "岗位筛选系统API", "version": "1.0.0"}


@app.post("/upload-and-filter")
async def upload_and_filter(
    job_file: UploadFile = File(...),
    stats_file: UploadFile | None = File(None),
    major: str = Form("经济学"),
    education: str = Form("本科"),
    degree: str = Form("学士"),
    gender: str = Form("女"),
    household: str = Form("吕梁市"),
    age: int = Form(25),
    is_fresh_graduate: bool = Form(False),
    political_status: str = Form("群众"),
    qualifications: str = Form(""),
    computer_level: str = Form(""),
    english_level: str = Form(""),
    basic_experience: str = Form(""),
    work_years: int = Form(0),
    target_cities: str = Form("吕梁市,太原市"),
    gender_strict: bool = Form(True),
    household_strict: bool = Form(False),
):
    """
    上传Excel文件并进行筛选
    """
    # 解析参数
    qual_list = [q.strip() for q in qualifications.split(",") if q.strip()]
    city_list = [c.strip() for c in target_cities.split(",") if c.strip()]

    # 保存上传的文件（使用 ASCII 安全的临时文件名，避免中文路径与 pandas 不兼容）
    temp_dir = tempfile.gettempdir()
    print(f"[upload] received job_file: {job_file.filename}, content_type={job_file.content_type}")
    job_path = os.path.join(temp_dir, "jobmatch_jobs.xlsx")
    with open(job_path, "wb") as f:
        content = await job_file.read()
        f.write(content)
    print(f"[upload] saved to: {job_path}, size={os.path.getsize(job_path)} bytes")

    stats_path = None
    if stats_file:
        stats_path = os.path.join(temp_dir, "jobmatch_stats.xlsx")
        with open(stats_path, "wb") as f:
            content = await stats_file.read()
            f.write(content)
        print(f"[upload] saved stats to: {stats_path}")

    # 读取岗位数据
    reader = JobReader(job_path)
    jobs = reader.read_all()
    print(f"[reader] total jobs: {len(jobs)}")

    # 关联统计数据
    if stats_path:
        from excel_reader_v2 import StatsReader

        stats_reader = StatsReader(stats_path)
        stats_reader.read()
        for job in jobs:
            stats = stats_reader.match_job(job)
            if stats:
                job.applicants = stats["applicants"]
                job.approved = stats["approved"]
                job.paid = stats["paid"]

    # 创建临时配置文件
    config = {
        "profile": {
            "专业": major,
            "学历": education,
            "学位": degree,
            "性别": gender,
            "户籍": household,
            "年龄": age,
            "是否应届": is_fresh_graduate,
            "政治面貌": political_status,
            "相关资格": qual_list,
            "计算机等级": computer_level,
            "英语等级": english_level,
            "服务基层项目": basic_experience,
            "工作年限": work_years,
        },
        "preference": {"意向城市": city_list, "服务类别": []},
        "rules": {
            "专业匹配模式": "智能",
            "学历匹配": "向下兼容",
            "户籍匹配": {"模式": "strict" if household_strict else "loose", "优先显示户籍地": True},
            "性别限制": {"模式": "strict" if gender_strict else "loose"},
            "相关资格匹配": {"模式": "strict" if False else "loose"},
            "应届生匹配": {"模式": "loose"},
            "政治面貌匹配": {"模式": "loose"},
            "年龄匹配": {"模式": "strict"},
            "计算机等级匹配": {"模式": "loose"},
            "英语等级匹配": {"模式": "loose"},
            "服务基层项目匹配": {"模式": "loose"},
        },
        "filter": {"最大竞争比": 100, "最低招募人数": 1, "排除关键词": []},
        "output": {
            "排序方式": "匹配度降序",
            "输出模式": "全量标记",
            "显示字段": [
                "所属地市",
                "服务单位",
                "岗位类型",
                "专业要求",
                "学历要求",
                "竞争比",
                "匹配度",
            ],
        },
    }

    import yaml

    config_path = os.path.join(temp_dir, "jobmatch_config.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True)

    # 执行匹配
    matcher = JobMatcherV2(config_path)
    for job in jobs:
        matcher.match(job)

    # 统计匹配结果
    perfect_count = len([j for j in jobs if j.match_level == MatchLevel.PERFECT])
    partial_count = len([j for j in jobs if j.match_level == MatchLevel.PARTIAL])
    mismatch_count = len([j for j in jobs if j.match_level == MatchLevel.MISMATCH])
    print(f"[matcher] perfect={perfect_count}, partial={partial_count}, mismatch={mismatch_count}")

    # 转换为响应格式
    results = []
    for job in jobs:
        results.append(
            {
                "sheet_name": job.sheet_name,
                "index": job.index,
                "unit": job.unit,
                "job_type": job.job_type,
                "service_category": job.service_category,
                "recruit_count": job.recruit_count,
                "education": job.education,
                "degree": job.degree,
                "major": job.major,
                "qualifications": job.qualifications,
                "other": job.other,
                "phone": job.phone,
                "paid": job.paid,
                "match_level": job.match_level.value,
                "match_score": job.match_score,
                "competition_ratio": round(job.competition_ratio, 2)
                if job.recruit_count > 0
                else 0,
                "match_reasons": job.match_reasons,
                "mismatch_reasons": job.mismatch_reasons,
            }
        )

    # 生成Excel
    exporter = ExcelExporter(config_path)
    excel_path = os.path.join(temp_dir, "jobmatch_result.xlsx")
    exporter.export(jobs, excel_path)

    # 读取Excel为base64
    with open(excel_path, "rb") as f:
        excel_base64 = base64.b64encode(f.read()).decode()

    return {
        "total": len(jobs),
        "perfect": perfect_count,
        "partial": partial_count,
        "mismatch": mismatch_count,
        "jobs": results,
        "excel_base64": excel_base64,
        "excel_filename": "筛选结果.xlsx",
    }


@app.get("/cities")
def get_cities():
    """获取所有地市列表"""
    return {
        "cities": [
            "太原市",
            "大同市",
            "朔州市",
            "忻州市",
            "吕梁市",
            "晋中市",
            "阳泉市",
            "长治市",
            "晋城市",
            "临汾市",
            "运城市",
        ]
    }


@app.get("/qualifications")
def get_qualifications():
    """获取资格证书列表"""
    return {
        "qualifications": [
            "教师资格证",
            "法律职业资格证书",
            "医师资格证",
            "护士资格证",
            "会计证",
            "注册会计师",
            "建造师证",
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
