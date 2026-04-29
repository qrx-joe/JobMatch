#!/usr/bin/env python3
"""
FastAPI 主入口

JobMatch 智能选岗平台 API 服务
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.models.job import Job, JobFilter, MatchLevel
from core.models.user_profile import UserProfile
from core.models.match_result import MatchResult
from core.matchers.composite_matcher import CompositeMatcher
from core.recommenders.tier_recommender import TierRecommender
from core.recommenders.smart_recommender import SmartRecommender
from data.excel.column_mapper import ColumnMapper
from data.excel.universal_parser import UniversalParser
from platforms.sanzhiyifu import SanzhiyifuAdapter


# ==================== 响应模型 ====================


class ProfileRequest(BaseModel):
    """用户画像请求"""

    major: str = ""
    education: str = ""
    degree: str = ""
    gender: str = ""
    age: int = 0
    household: str = ""
    party_status: str = ""
    is_fresh_graduate: bool = False
    grassroots_exp: int = 0
    qualifications: list[str] = []
    estimated_score: float = 0.0
    target_cities: list[str] = []
    target_platforms: list[str] = []


class FilterRequest(BaseModel):
    """筛选请求"""

    profile: ProfileRequest
    platform: Optional[str] = "sanzhiyifu"
    filters: Optional[dict] = {}
    sort_by: str = "competition_ratio"
    order: str = "asc"


class FilterResponse(BaseModel):
    """筛选响应"""

    total: int
    jobs: list[dict]


class RecommendResponse(BaseModel):
    """推荐响应"""

    stretch: list[dict]
    safe: list[dict]
    bottom: list[dict]


# ==================== 生命周期 ====================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时
    print("JobMatch API 服务启动")
    yield
    # 关闭时
    print("JobMatch API 服务关闭")


# ==================== FastAPI 应用 ====================


app = FastAPI(
    title="JobMatch 智能选岗平台",
    description="为考公考编考生提供智能选岗服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API 路由 ====================


@app.get("/")
async def root():
    """根路径"""
    return {"message": "JobMatch 智能选岗平台 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


# ==================== 岗位相关 API ====================


@app.post("/api/jobs/upload", response_model=dict)
async def upload_jobs(file: UploadFile = File(...)):
    """
    上传Excel岗位表

    支持三支一扶、公务员、事业编等格式
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="只支持 Excel 文件")

    # 保存上传的文件
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 解析Excel
        parser = UniversalParser(platform="sanzhiyifu")
        jobs = parser.parse(tmp_path)

        return {
            "total": len(jobs),
            "message": f"成功解析 {len(jobs)} 个岗位",
            "sample": jobs[0].to_dict() if jobs else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")
    finally:
        os.unlink(tmp_path)


@app.post("/api/jobs/filter", response_model=FilterResponse)
async def filter_jobs(request: FilterRequest):
    """
    筛选岗位

    根据用户画像和筛选条件返回匹配的岗位
    """
    # 构建用户画像
    profile = UserProfile(
        major=request.profile.major,
        education=request.profile.education,
        degree=request.profile.degree,
        gender=request.profile.gender,
        age=request.profile.age,
        household=request.profile.household,
        party_status=request.profile.party_status,
        is_fresh_graduate=request.profile.is_fresh_graduate,
        grassroots_exp=request.profile.grassroots_exp,
        qualifications=request.profile.qualifications,
        estimated_score=request.profile.estimated_score,
        target_cities=request.profile.target_cities,
        target_platforms=request.profile.target_platforms,
    )

    # 这里应该从数据库或缓存获取岗位列表
    # 暂时返回模拟数据
    jobs = []
    match_results = []

    # 如果有Excel数据，进行匹配
    # TODO: 集成数据库查询

    return FilterResponse(total=len(jobs), jobs=[job.to_dict() for job in jobs])


@app.post("/api/jobs/recommend", response_model=RecommendResponse)
async def recommend_jobs(request: FilterRequest):
    """
    智能推荐岗位

    返回 冲/稳/保 分层推荐结果
    """
    # 构建用户画像
    profile = UserProfile(
        major=request.profile.major,
        education=request.profile.education,
        degree=request.profile.degree,
        gender=request.profile.gender,
        age=request.profile.age,
        household=request.profile.household,
        party_status=request.profile.party_status,
        estimated_score=request.profile.estimated_score,
        target_cities=request.profile.target_cities,
    )

    # TODO: 从数据库或缓存获取匹配的岗位
    jobs = []
    match_results = []

    # 进行推荐
    recommender = TierRecommender(profile)
    result = recommender.recommend(jobs, match_results)

    return RecommendResponse(
        stretch=[job.to_dict() for job in result.get("冲刺", [])],
        safe=[job.to_dict() for job in result.get("稳妥", [])],
        bottom=[job.to_dict() for job in result.get("保底", [])],
    )


@app.get("/api/jobs/{job_id}")
async def get_job_detail(job_id: int):
    """获取岗位详情"""
    # TODO: 从数据库查询
    return {"id": job_id, "message": "岗位详情"}


# ==================== 用户相关 API ====================


@app.post("/api/auth/login")
async def login(code: str):
    """
    微信登录

    通过 code 获取 openid
    注意：个人账号无法使用微信登录API，需要企业认证小程序
    """
    # 模拟登录
    return {
        "openid": "mock_openid",
        "session_key": "mock_session_key",
        "message": "模拟登录成功（需要企业认证小程序才能使用真实微信登录）",
    }


@app.get("/api/profile/{openid}")
async def get_profile(openid: str):
    """获取用户画像"""
    # TODO: 从数据库查询
    return {"openid": openid, "message": "用户画像"}


@app.put("/api/profile/{openid}")
async def update_profile(openid: str, profile: ProfileRequest):
    """更新用户画像"""
    # TODO: 更新数据库
    return {"openid": openid, "message": "更新成功"}


# ==================== 收藏相关 API ====================


@app.get("/api/favorites/{openid}")
async def get_favorites(openid: str):
    """获取用户收藏"""
    # TODO: 从数据库查询
    return {"openid": openid, "favorites": []}


@app.post("/api/favorites/{openid}/{job_id}")
async def add_favorite(openid: str, job_id: int):
    """添加收藏"""
    # TODO: 添加到数据库
    return {"openid": openid, "job_id": job_id, "message": "收藏成功"}


@app.delete("/api/favorites/{openid}/{job_id}")
async def remove_favorite(openid: str, job_id: int):
    """取消收藏"""
    # TODO: 从数据库删除
    return {"openid": openid, "job_id": job_id, "message": "已取消收藏"}


# ==================== 主程序 ====================


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)