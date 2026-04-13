#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三支一扶智能选岗系统 - 完整版
集成Claude API、专业对比、报告导出
"""
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# 导入各个模块
from job_matcher_v2 import JobMatcherV2, Job, MatchLevel
from llm_matcher_api import ClaudeMajorMatcher
from major_graph_full import get_graph, compare_majors, find_path
from report_exporter import ReportExporter, MatchReport

app = FastAPI(title="三支一扶智能选岗系统", version="2.0.0")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== 数据模型 ==============

class UserProfile(BaseModel):
    """用户档案"""
    major: str
    education: str = "本科"
    degree: str = "学士"
    gender: str = ""
    household: str = ""
    is_fresh_graduate: bool = False
    political_status: str = "群众"
    qualifications: List[str] = []
    work_years: int = 0
    target_cities: List[str] = []


class FilterConfig(BaseModel):
    """筛选配置"""
    cities: List[str] = []
    min_salary: Optional[int] = None
    max_competition_ratio: float = 100.0
    exclude_keywords: List[str] = []
    require_qualifications: List[str] = []


class JobSearchRequest(BaseModel):
    """岗位搜索请求"""
    profile: UserProfile
    filters: FilterConfig
    use_llm: bool = True  # 是否使用Claude API


class MatchResult(BaseModel):
    """匹配结果"""
    jobs: List[Dict]
    summary: Dict
    match_time: float


class MajorCompareRequest(BaseModel):
    """专业对比请求"""
    major1: str
    major2: str


class MajorCompareResponse(BaseModel):
    """专业对比响应"""
    major1: Dict
    major2: Dict
    relationship: str
    path: List[str]
    same_category: bool
    same_subcategory: bool


# ============== 全局实例 ==============

# Claude API匹配器（延迟初始化）
_claude_matcher = None

def get_claude_matcher():
    """获取Claude匹配器（单例）"""
    global _claude_matcher
    if _claude_matcher is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            _claude_matcher = ClaudeMajorMatcher(api_key)
    return _claude_matcher


# ============== API路由 ==============

@app.get("/")
def root():
    """根路径"""
    return {
        "name": "三支一扶智能选岗系统",
        "version": "2.0.0",
        "features": [
            "AI语义匹配",
            "专业关系图谱",
            "专业对比分析",
            "报告导出"
        ]
    }


@app.get("/api/status")
def get_status():
    """获取系统状态"""
    claude_available = get_claude_matcher() is not None
    return {
        "status": "running",
        "claude_api": "available" if claude_available else "unavailable",
        "features": {
            "llm_matching": claude_available,
            "major_graph": True,
            "major_comparison": True,
            "report_export": True
        }
    }


@app.post("/api/jobs/search", response_model=MatchResult)
def search_jobs(request: JobSearchRequest):
    """
    搜索并匹配岗位
    支持Claude API智能匹配或本地规则匹配
    """
    import time
    start_time = time.time()

    try:
        # 创建匹配器
        matcher = JobMatcherV2()

        # 更新用户配置
        matcher.profile.major = request.profile.major
        matcher.profile.education = request.profile.education
        matcher.profile.degree = request.profile.degree
        matcher.profile.gender = request.profile.gender
        matcher.profile.household = request.profile.household
        matcher.profile.is_fresh_graduate = request.profile.is_fresh_graduate
        matcher.profile.political_status = request.profile.political_status
        matcher.profile.qualifications = request.profile.qualifications
        matcher.profile.work_years = request.profile.work_years
        matcher.profile.target_cities = request.profile.target_cities

        # TODO: 从Excel加载实际岗位数据
        # 这里使用模拟数据演示
        mock_jobs = _generate_mock_jobs()

        # 执行匹配
        matched_jobs = []
        for job_data in mock_jobs:
            job = Job(**job_data)
            result = matcher.match(job)

            # 应用筛选条件
            if _apply_filters(result, request.filters):
                matched_jobs.append({
                    "sheet_name": result.sheet_name,
                    "unit": result.unit,
                    "job_type": result.job_type,
                    "major": result.major,
                    "education": result.education,
                    "recruit_count": result.recruit_count,
                    "applicants": result.applicants,
                    "approved": result.approved,
                    "paid": result.paid,
                    "competition_ratio": result.competition_ratio,
                    "match_level": result.match_level.value,
                    "match_score": result.match_score,
                    "match_reasons": result.match_reasons,
                    "mismatch_reasons": result.mismatch_reasons
                })

        # 按匹配分数排序
        matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)

        # 生成统计
        total = len(matched_jobs)
        perfect = sum(1 for j in matched_jobs if j["match_level"] == "完全符合")
        partial = sum(1 for j in matched_jobs if j["match_level"] == "可能符合")

        elapsed = time.time() - start_time

        return MatchResult(
            jobs=matched_jobs[:50],  # 最多返回50条
            summary={
                "total": total,
                "perfect": perfect,
                "partial": partial,
                "avg_score": sum(j["match_score"] for j in matched_jobs) / total if total > 0 else 0
            },
            match_time=elapsed
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/majors/compare", response_model=MajorCompareResponse)
def compare_majors_api(request: MajorCompareRequest):
    """
    对比两个专业的关系
    """
    result = compare_majors(request.major1, request.major2)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return MajorCompareResponse(
        major1=result["major1"],
        major2=result["major2"],
        relationship=result["relationship"],
        path=result["path"],
        same_category=result["same_category"],
        same_subcategory=result["same_subcategory"]
    )


@app.get("/api/majors/path")
def get_major_path(from_major: str, to_major: str):
    """
    获取两个专业之间的关系路径
    """
    path = find_path(from_major, to_major)
    return {
        "from": from_major,
        "to": to_major,
        "path": path,
        "distance": len(path) - 1 if path else -1
    }


@app.get("/api/majors/categories")
def get_categories():
    """获取所有学科门类"""
    graph = get_graph()
    return {
        "categories": list(graph.categories.keys()),
        "count": len(graph.categories)
    }


@app.get("/api/majors/category/{category}")
def get_majors_by_category(category: str):
    """获取某个门类下的所有专业"""
    graph = get_graph()
    majors = graph.get_category_majors(category)
    return {
        "category": category,
        "majors": [{"id": m.id, "name": m.name, "subcategory": m.subcategory} for m in majors]
    }


@app.post("/api/match/single")
def match_single_job(user_major: str, job_major: str, use_llm: bool = False):
    """
    单次专业匹配（用于测试）
    """
    if use_llm:
        matcher = get_claude_matcher()
        if matcher:
            result = matcher.match(user_major, job_major)
            return {
                "match": result.match,
                "reason": result.reason,
                "confidence": result.confidence,
                "category_match": result.category_match,
                "related": result.related,
                "source": "claude_api"
            }

    # 使用本地匹配
    from job_matcher_llm import LLMEnhancedMajorMatcher
    local_matcher = LLMEnhancedMajorMatcher(user_major, use_llm=False)
    match, reason, source = local_matcher.match(job_major)

    return {
        "match": match,
        "reason": reason,
        "source": source
    }


@app.post("/api/reports/export")
def export_report(request: JobSearchRequest, format: str = "html"):
    """
    导出匹配报告
    """
    try:
        # 先执行匹配
        match_result = search_jobs(request)

        # 创建报告
        report = MatchReport(
            user_major=request.profile.major,
            user_education=request.profile.education,
            user_degree=request.profile.degree,
            target_jobs=match_result.jobs,
            filter_criteria=request.filters.dict(),
            summary=match_result.summary
        )

        # 导出
        exporter = ReportExporter()

        if format == "json":
            filepath = exporter.export_json(report)
        elif format == "html":
            filepath = exporter.export_html(report)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的格式: {format}")

        return {
            "success": True,
            "filepath": filepath,
            "download_url": f"/api/reports/download?path={filepath}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/download")
def download_report(path: str):
    """下载报告文件"""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path,
        filename=os.path.basename(path),
        media_type="application/octet-stream"
    )


# ============== 辅助函数 ==============

def _generate_mock_jobs() -> List[Dict]:
    """生成模拟岗位数据"""
    return [
        {
            "sheet_name": "济南市",
            "unit": "济南市财政局",
            "job_type": "支农",
            "major": "经济学类",
            "education": "本科及以上",
            "degree": "学士及以上",
            "recruit_count": 5,
            "applicants": 60,
            "approved": 45,
            "paid": 40
        },
        {
            "sheet_name": "青岛市",
            "unit": "青岛市统计局",
            "job_type": "支农",
            "major": "统计学类",
            "education": "本科及以上",
            "recruit_count": 3,
            "applicants": 30,
            "approved": 25,
            "paid": 20
        },
        {
            "sheet_name": "烟台市",
            "unit": "烟台市教育局",
            "job_type": "支教",
            "major": "教育学类",
            "education": "本科及以上",
            "recruit_count": 10,
            "applicants": 250,
            "approved": 200,
            "paid": 180
        },
        {
            "sheet_name": "济南市",
            "unit": "济南市人社局",
            "job_type": "支农",
            "major": "法学类",
            "education": "本科及以上",
            "recruit_count": 4,
            "applicants": 80,
            "approved": 60,
            "paid": 50
        },
        {
            "sheet_name": "青岛市",
            "unit": "青岛市卫健委",
            "job_type": "支医",
            "major": "医学类",
            "education": "本科及以上",
            "recruit_count": 8,
            "applicants": 120,
            "approved": 90,
            "paid": 75
        }
    ]


def _apply_filters(job: Job, filters: FilterConfig) -> bool:
    """应用筛选条件"""
    # 城市筛选
    if filters.cities and job.sheet_name not in filters.cities:
        return False

    # 竞争比筛选
    if job.competition_ratio > filters.max_competition_ratio:
        return False

    # 排除关键词
    for keyword in filters.exclude_keywords:
        if keyword in job.unit or keyword in job.job_type:
            return False

    return True


# ============== 启动 ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
