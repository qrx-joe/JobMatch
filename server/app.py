#!/usr/bin/env python3
"""
FastAPI 主入口

JobMatch 智能选岗平台 API 服务
连接数据库，支持岗位筛选、推荐等完整功能
"""

from contextlib import asynccontextmanager
from typing import Optional
import asyncio

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from server.core.models.job import Job, MatchLevel, RecommendationTier
from server.core.models.user_profile import UserProfile
from server.core.models.match_result import MatchResult
from server.core.matchers.composite_matcher import CompositeMatcher
from server.core.recommenders.tier_recommender import TierRecommender
from server.core.recommenders.smart_recommender import SmartRecommender
from server.data.database.connection import init_db, get_db_session, JobModel, UserModel
from server.data.excel.universal_parser import UniversalParser
from server.data.excel.job_pipeline import JobPipeline


# ==================== 数据模型 ====================


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
    computer_level: str = ""
    english_level: str = ""
    basic_experience: str = ""
    work_years: int = 0


class FilterRequest(BaseModel):
    """筛选请求"""
    profile: ProfileRequest
    platform: Optional[str] = "三支一扶"
    city: Optional[str] = None
    max_competition_ratio: Optional[float] = None
    min_recruit_count: int = 1
    limit: int = 100


class FilterResponse(BaseModel):
    """筛选响应"""
    total: int
    jobs: list[dict]
    stretch_count: int = 0
    safe_count: int = 0
    bottom_count: int = 0


class JobDetailResponse(BaseModel):
    """岗位详情响应"""
    id: int
    platform: str
    city: str
    unit: str
    job_type: str
    service_category: str
    recruit_count: int
    education: str
    degree: str
    major: str
    age_limit: str
    political_requirement: str
    competition_ratio: float
    match_score: int = 0
    match_level: str = ""
    recommendation_tier: str = ""
    pass_probability: float = 0.0


# ==================== 生命周期 ====================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    print("JobMatch API 服务启动")
    # 初始化数据库
    init_db()
    print("数据库连接已初始化")
    yield
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


# ==================== 辅助函数 ====================


def model_to_job(model: JobModel) -> Job:
    """将数据库模型转换为 Job 对象"""
    return Job(
        id=model.id,
        platform=model.platform,
        city=model.city,
        unit=model.unit,
        job_type=model.job_type,
        service_category=model.service_category,
        recruit_count=model.recruit_count,
        education=model.education,
        degree=model.degree,
        major=model.major,
        age_limit=model.age_limit,
        political_requirement=model.political_requirement,
        qualifications=model.qualifications,
        other=model.other,
        phone=model.phone,
        contact=model.contact,
        applicants=model.applicants,
        approved=model.approved,
        paid=model.paid,
        competition_ratio=model.competition_ratio,
    )


def job_to_dict(job: Job) -> dict:
    """将 Job 对象转换为字典"""
    return {
        "id": job.id,
        "platform": job.platform,
        "city": job.city,
        "unit": job.unit,
        "job_type": job.job_type,
        "service_category": job.service_category,
        "recruit_count": job.recruit_count,
        "education": job.education,
        "degree": job.degree,
        "major": job.major,
        "age_limit": job.age_limit,
        "political_requirement": job.political_requirement,
        "qualifications": job.qualifications,
        "competition_ratio": round(job.competition_ratio, 2) if job.competition_ratio else 0,
        "match_score": job.match_score,
        "match_level": job.match_level.value if job.match_level else None,
        "recommendation_tier": job.recommendation_tier.value if job.recommendation_tier else None,
        "pass_probability": round(job.pass_probability, 4) if job.pass_probability else 0,
    }


# ==================== API 路由 ====================


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "JobMatch 智能选岗平台 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "JobMatch API"}


# ==================== 岗位相关 API ====================


@app.post("/api/jobs/upload")
async def upload_jobs(file: UploadFile = File(...), platform: str = "三支一扶"):
    """
    上传Excel岗位表并导入数据库

    支持三支一扶、公务员、事业编等格式
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="只支持 Excel 文件")

    import tempfile
    import os

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 解析并导入数据库
        pipeline = JobPipeline()
        result = pipeline.parse_and_save(tmp_path, platform)

        return {
            "total": result["total"],
            "success": result["success"],
            "updated": result["updated"],
            "errors": result["errors"],
            "message": f"成功导入 {result['success']} 个岗位"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
    finally:
        os.unlink(tmp_path)


@app.get("/api/jobs")
async def list_jobs(
    platform: Optional[str] = None,
    city: Optional[str] = None,
    major: Optional[str] = None,
    education: Optional[str] = None,
    max_competition_ratio: Optional[float] = None,
    min_recruit_count: int = Query(default=1, ge=1),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """
    获取岗位列表（支持分页和筛选）
    """
    with get_db_session() as session:
        query = session.query(JobModel)

        if platform:
            query = query.filter(JobModel.platform == platform)
        if city:
            query = query.filter(JobModel.city == city)
        if major:
            query = query.filter(JobModel.major.like(f"%{major}%"))
        if education:
            query = query.filter(JobModel.education.like(f"%{education}%"))
        if max_competition_ratio:
            query = query.filter(JobModel.competition_ratio <= max_competition_ratio)
        if min_recruit_count:
            query = query.filter(JobModel.recruit_count >= min_recruit_count)

        total = query.count()
        models = query.offset(offset).limit(limit).all()

        jobs = [model_to_job(m) for m in models]

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "jobs": [job_to_dict(j) for j in jobs]
        }


@app.post("/api/jobs/filter", response_model=FilterResponse)
async def filter_jobs(request: FilterRequest):
    """
    筛选岗位并智能推荐

    根据用户画像返回匹配的岗位，带冲/稳/保标签
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

    # 从数据库查询岗位
    with get_db_session() as session:
        query = session.query(JobModel)

        if request.platform:
            query = query.filter(JobModel.platform == request.platform)
        if request.city:
            query = query.filter(JobModel.city == request.city)
        if request.max_competition_ratio:
            query = query.filter(JobModel.competition_ratio <= request.max_competition_ratio)
        if request.min_recruit_count:
            query = query.filter(JobModel.recruit_count >= request.min_recruit_count)

        query = query.limit(request.limit)
        models = query.all()

        # 转换为 Job 对象
        jobs = [model_to_job(m) for m in models]

    if not jobs:
        return FilterResponse(total=0, jobs=[])

    # 匹配
    matcher = CompositeMatcher()
    match_results = []
    for job in jobs:
        result = matcher.match(job, profile)
        match_results.append(result)
        job.match_score = result.total_score
        job.match_level = result.match_level

    # 推荐
    recommender = TierRecommender(profile)
    tier_result = recommender.recommend(jobs, match_results)

    # 展平结果
    all_jobs = (
        tier_result.get("冲刺", []) +
        tier_result.get("稳妥", []) +
        tier_result.get("保底", [])
    )

    return FilterResponse(
        total=len(all_jobs),
        jobs=[job_to_dict(j) for j in all_jobs],
        stretch_count=len(tier_result.get("冲刺", [])),
        safe_count=len(tier_result.get("稳妥", [])),
        bottom_count=len(tier_result.get("保底", [])),
    )


@app.post("/api/jobs/recommend")
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

    # 从数据库查询岗位
    with get_db_session() as session:
        query = session.query(JobModel)

        if request.platform:
            query = query.filter(JobModel.platform == request.platform)
        if request.city:
            query = query.filter(JobModel.city == request.city)
        if request.max_competition_ratio:
            query = query.filter(JobModel.competition_ratio <= request.max_competition_ratio)

        query = query.limit(request.limit)
        models = query.all()

        jobs = [model_to_job(m) for m in models]

    if not jobs:
        return {"stretch": [], "safe": [], "bottom": []}

    # 匹配
    matcher = CompositeMatcher()
    match_results = []
    for job in jobs:
        result = matcher.match(job, profile)
        match_results.append(result)

    # 推荐
    recommender = TierRecommender(profile)
    tier_result = recommender.recommend(jobs, match_results)

    return {
        "stretch": [job_to_dict(j) for j in tier_result.get("冲刺", [])],
        "safe": [job_to_dict(j) for j in tier_result.get("稳妥", [])],
        "bottom": [job_to_dict(j) for j in tier_result.get("保底", [])],
    }


@app.get("/api/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job_detail(job_id: int):
    """获取岗位详情"""
    with get_db_session() as session:
        model = session.query(JobModel).filter(JobModel.id == job_id).first()

        if not model:
            raise HTTPException(status_code=404, detail="岗位不存在")

        job = model_to_job(model)

        return JobDetailResponse(
            id=job.id,
            platform=job.platform,
            city=job.city,
            unit=job.unit,
            job_type=job.job_type,
            service_category=job.service_category or "",
            recruit_count=job.recruit_count,
            education=job.education or "",
            degree=job.degree or "",
            major=job.major or "",
            age_limit=job.age_limit or "",
            political_requirement=job.political_requirement or "",
            competition_ratio=round(job.competition_ratio, 2) if job.competition_ratio else 0,
        )


@app.post("/api/jobs/{job_id}/match")
async def match_job(job_id: int, profile: ProfileRequest):
    """
    对特定岗位进行匹配分析

    返回该岗位与用户画像的详细匹配结果
    """
    user_profile = UserProfile(
        major=profile.major,
        education=profile.education,
        degree=profile.degree,
        gender=profile.gender,
        age=profile.age,
        household=profile.household,
        party_status=profile.party_status,
        is_fresh_graduate=profile.is_fresh_graduate,
        grassroots_exp=profile.grassroots_exp,
        qualifications=profile.qualifications,
        estimated_score=profile.estimated_score,
    )

    with get_db_session() as session:
        model = session.query(JobModel).filter(JobModel.id == job_id).first()

        if not model:
            raise HTTPException(status_code=404, detail="岗位不存在")

        job = model_to_job(model)

        # 匹配
        matcher = CompositeMatcher()
        result = matcher.match(job, user_profile)

        # 推荐
        recommender = TierRecommender(user_profile)
        prob = recommender._calc_probability(job, result)
        job.pass_probability = prob

        # 判断推荐层级
        tier_result = recommender.recommend([job], [result])

        return {
            "job": job_to_dict(job),
            "match_result": {
                "total_score": result.total_score,
                "match_level": result.match_level.value if result.match_level else None,
                "major_match": result.major_match[1] if result.major_match else "",
                "education_match": result.education_match[1] if result.education_match else "",
                "political_match": result.political_match[1] if result.political_match else "",
                "age_match": result.age_match[1] if result.age_match else "",
                "match_reasons": result.match_reasons,
                "mismatch_reasons": result.mismatch_reasons,
            },
            "recommendation": {
                "tier": "冲刺" if tier_result.get("冲刺") else "稳妥" if tier_result.get("稳妥") else "保底",
                "pass_probability": round(prob, 4),
            }
        }


# ==================== 城市和平台 API ====================


@app.get("/api/cities")
async def list_cities(platform: Optional[str] = None):
    """获取所有城市列表"""
    with get_db_session() as session:
        query = session.query(JobModel.city).distinct()
        if platform:
            query = query.filter(JobModel.platform == platform)
        cities = [city for city, in query.all() if city]
        return {"cities": cities}


@app.get("/api/platforms")
async def list_platforms():
    """获取所有平台类型"""
    with get_db_session() as session:
        query = session.query(JobModel.platform).distinct()
        platforms = [p for p, in query.all() if p]
        return {"platforms": platforms}


# ==================== 用户相关 API ====================


@app.post("/api/auth/login")
async def login(code: str = ""):
    """
    微信登录（模拟）

    注意：个人账号无法使用微信登录API，需要企业认证小程序
    """
    # 模拟登录，返回一个临时 openid
    import uuid
    mock_openid = f"mock_{uuid.uuid4().hex[:16]}"

    return {
        "openid": mock_openid,
        "session_key": "mock_session_key",
        "message": "模拟登录成功（需要企业认证小程序才能使用真实微信登录）",
    }


@app.get("/api/profile/{openid}")
async def get_profile(openid: str):
    """获取用户画像"""
    with get_db_session() as session:
        user = session.query(UserModel).filter(UserModel.openid == openid).first()

        if not user:
            return {
                "openid": openid,
                "major": "",
                "education": "",
                "gender": "",
                "age": 0,
                "household": "",
                "party_status": "",
            }

        return {
            "openid": user.openid,
            "major": user.major or "",
            "education": user.education or "",
            "gender": user.gender or "",
            "age": user.age or 0,
            "household": user.household or "",
            "party_status": user.party_status or "",
            "is_fresh_graduate": user.is_fresh_graduate,
            "grassroots_exp": user.grassroots_exp or 0,
            "qualifications": user.qualifications or [],
            "estimated_score": user.estimated_score or 0,
            "target_cities": user.target_cities or [],
            "target_platforms": user.target_platforms or [],
        }


@app.put("/api/profile/{openid}")
async def update_profile(openid: str, profile: ProfileRequest):
    """更新用户画像"""
    with get_db_session() as session:
        user = session.query(UserModel).filter(UserModel.openid == openid).first()

        if not user:
            # 创建新用户
            user = UserModel(openid=openid)
            session.add(user)

        # 更新字段
        user.major = profile.major
        user.education = profile.education
        user.degree = profile.degree
        user.gender = profile.gender
        user.age = profile.age
        user.household = profile.household
        user.party_status = profile.party_status
        user.is_fresh_graduate = profile.is_fresh_graduate
        user.grassroots_exp = profile.grassroots_exp
        user.qualifications = profile.qualifications
        user.estimated_score = profile.estimated_score
        user.target_cities = profile.target_cities
        user.target_platforms = profile.target_platforms

        # session.commit() 由 context manager 处理

        return {"openid": openid, "message": "更新成功"}


# ==================== 收藏相关 API ====================


@app.get("/api/favorites/{openid}")
async def get_favorites(openid: str):
    """获取用户收藏"""
    from server.data.database.connection import FavoriteModel

    with get_db_session() as session:
        user = session.query(UserModel).filter(UserModel.openid == openid).first()
        if not user:
            return {"openid": openid, "favorites": []}

        favorites = (
            session.query(FavoriteModel)
            .filter(FavoriteModel.user_id == user.id)
            .all()
        )

        job_ids = [fav.job_id for fav in favorites]

        # 获取岗位详情
        if job_ids:
            jobs = session.query(JobModel).filter(JobModel.id.in_(job_ids)).all()
            return {
                "openid": openid,
                "favorites": [job_to_dict(model_to_job(j)) for j in jobs]
            }

        return {"openid": openid, "favorites": []}


@app.post("/api/favorites/{openid}/{job_id}")
async def add_favorite(openid: str, job_id: int):
    """添加收藏"""
    from server.data.database.connection import FavoriteModel

    with get_db_session() as session:
        # 查找或创建用户
        user = session.query(UserModel).filter(UserModel.openid == openid).first()
        if not user:
            user = UserModel(openid=openid)
            session.add(user)
            session.flush()

        # 检查是否已收藏
        existing = (
            session.query(FavoriteModel)
            .filter(FavoriteModel.user_id == user.id, FavoriteModel.job_id == job_id)
            .first()
        )

        if existing:
            return {"message": "已经收藏过了"}

        # 添加收藏
        favorite = FavoriteModel(user_id=user.id, job_id=job_id)
        session.add(favorite)

        return {"openid": openid, "job_id": job_id, "message": "收藏成功"}


@app.delete("/api/favorites/{openid}/{job_id}")
async def remove_favorite(openid: str, job_id: int):
    """取消收藏"""
    from server.data.database.connection import FavoriteModel

    with get_db_session() as session:
        user = session.query(UserModel).filter(UserModel.openid == openid).first()
        if not user:
            return {"message": "用户不存在"}

        favorite = (
            session.query(FavoriteModel)
            .filter(FavoriteModel.user_id == user.id, FavoriteModel.job_id == job_id)
            .first()
        )

        if favorite:
            session.delete(favorite)

        return {"openid": openid, "job_id": job_id, "message": "已取消收藏"}


# ==================== 主程序 ====================


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)