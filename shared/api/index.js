/**
 * 统一 API 服务
 * 同时支持小程序和网页端
 */

const { createAdapter } = require('./base')

// API 基础地址配置
const API_BASE_URL = 'http://localhost:8000'

const { request, uploadFile } = createAdapter('auto')

// ==================== 岗位相关 API ====================

/**
 * 上传Excel文件
 * @param {string} filePath - 文件临时路径(小程序) 或 File 对象(网页)
 * @param {string} name - 文件字段名
 * @param {string} platform - 平台类型，默认"三支一扶"
 */
const uploadExcel = (filePath, name = 'file', platform = '三支一扶') => {
  return uploadFile({
    url: API_BASE_URL + '/api/jobs/upload',
    filePath,
    name,
    formData: { platform }
  })
}

/**
 * 上传并筛选(网页端专用，因为用的是 FormData)
 * @param {FormData} formData - 表单数据
 */
const uploadAndFilter = (formData) => {
  return fetch(API_BASE_URL + '/api/jobs/upload-and-filter', {
    method: 'POST',
    body: formData
  }).then(res => {
    if (!res.ok) throw new Error(`请求失败: ${res.status}`)
    return res.json()
  })
}

/**
 * 获取岗位列表
 * @param {object} params - 查询参数
 */
const listJobs = (params = {}) => {
  return request({
    url: API_BASE_URL + '/api/jobs',
    method: 'GET',
    data: params
  })
}

/**
 * 筛选岗位并推荐
 * @param {object} profile - 用户画像
 * @param {object} options - 筛选选项
 */
const filterJobs = (profile, options = {}) => {
  return request({
    url: API_BASE_URL + '/api/jobs/filter',
    method: 'POST',
    data: {
      profile: {
        major: profile.major || '',
        education: profile.education || '',
        degree: profile.degree || '',
        gender: profile.gender || '',
        age: profile.age || 0,
        household: profile.household || '',
        party_status: profile.party_status || '',
        is_fresh_graduate: profile.is_fresh_graduate || false,
        grassroots_exp: profile.grassroots_exp || 0,
        qualifications: profile.qualifications || [],
        estimated_score: profile.estimated_score || 0,
        target_cities: profile.target_cities || [],
        target_platforms: profile.target_platforms || []
      },
      platform: options.platform || '三支一扶',
      city: options.city || null,
      max_competition_ratio: options.max_competition_ratio || null,
      min_recruit_count: options.min_recruit_count || 1,
      limit: options.limit || 100
    }
  })
}

/**
 * 智能推荐岗位
 * @param {object} profile - 用户画像
 * @param {object} options - 筛选选项
 */
const recommendJobs = (profile, options = {}) => {
  return request({
    url: API_BASE_URL + '/api/jobs/recommend',
    method: 'POST',
    data: {
      profile: {
        major: profile.major || '',
        education: profile.education || '',
        degree: profile.degree || '',
        gender: profile.gender || '',
        age: profile.age || 0,
        household: profile.household || '',
        party_status: profile.party_status || '',
        estimated_score: profile.estimated_score || 0,
        target_cities: profile.target_cities || []
      },
      platform: options.platform || '三支一扶',
      city: options.city || null,
      max_competition_ratio: options.max_competition_ratio || null,
      limit: options.limit || 100
    }
  })
}

/**
 * 获取岗位详情
 * @param {number} jobId - 岗位ID
 */
const getJobDetail = (jobId) => {
  return request({
    url: API_BASE_URL + `/api/jobs/${jobId}`
  })
}

/**
 * 获取岗位匹配分析
 * @param {number} jobId - 岗位ID
 * @param {object} profile - 用户画像
 */
const matchJob = (jobId, profile) => {
  return request({
    url: API_BASE_URL + `/api/jobs/${jobId}/match`,
    method: 'POST',
    data: {
      major: profile.major || '',
      education: profile.education || '',
      degree: profile.degree || '',
      gender: profile.gender || '',
      age: profile.age || 0,
      household: profile.household || '',
      party_status: profile.party_status || '',
      is_fresh_graduate: profile.is_fresh_graduate || false,
      grassroots_exp: profile.grassroots_exp || 0,
      qualifications: profile.qualifications || [],
      estimated_score: profile.estimated_score || 0
    }
  })
}

// ==================== 城市和平台 API ====================

/**
 * 获取城市列表
 * @param {string} platform - 平台类型
 */
const getCities = (platform) => {
  return request({
    url: API_BASE_URL + '/api/cities',
    method: 'GET',
    data: platform ? { platform } : {}
  })
}

/**
 * 获取平台类型列表
 */
const getPlatforms = () => {
  return request({
    url: API_BASE_URL + '/api/platforms'
  })
}

/**
 * 获取资质证书列表
 */
const getQualifications = () => {
  return request({
    url: API_BASE_URL + '/api/qualifications'
  })
}

// ==================== 用户相关 API ====================

/**
 * 微信登录
 * @param {string} code - 微信授权code
 */
const login = (code) => {
  return request({
    url: API_BASE_URL + '/api/auth/login',
    method: 'POST',
    data: { code }
  })
}

/**
 * 获取用户画像
 * @param {string} openid - 用户openid
 */
const getProfile = (openid) => {
  return request({
    url: API_BASE_URL + `/api/profile/${openid}`
  })
}

/**
 * 更新用户画像
 * @param {string} openid - 用户openid
 * @param {object} profile - 用户画像
 */
const updateProfile = (openid, profile) => {
  return request({
    url: API_BASE_URL + `/api/profile/${openid}`,
    method: 'PUT',
    data: {
      major: profile.major || '',
      education: profile.education || '',
      degree: profile.degree || '',
      gender: profile.gender || '',
      age: profile.age || 0,
      household: profile.household || '',
      party_status: profile.party_status || '',
      is_fresh_graduate: profile.is_fresh_graduate || false,
      grassroots_exp: profile.grassroots_exp || 0,
      qualifications: profile.qualifications || [],
      estimated_score: profile.estimated_score || 0,
      target_cities: profile.target_cities || [],
      target_platforms: profile.target_platforms || []
    }
  })
}

// ==================== 收藏相关 API ====================

/**
 * 获取收藏列表
 * @param {string} openid - 用户openid
 */
const getFavorites = (openid) => {
  return request({
    url: API_BASE_URL + `/api/favorites/${openid}`
  })
}

/**
 * 添加收藏
 * @param {string} openid - 用户openid
 * @param {number} jobId - 岗位ID
 */
const addFavorite = (openid, jobId) => {
  return request({
    url: API_BASE_URL + `/api/favorites/${openid}/${jobId}`,
    method: 'POST'
  })
}

/**
 * 取消收藏
 * @param {string} openid - 用户openid
 * @param {number} jobId - 岗位ID
 */
const removeFavorite = (openid, jobId) => {
  return request({
    url: API_BASE_URL + `/api/favorites/${openid}/${jobId}`,
    method: 'DELETE'
  })
}

module.exports = {
  uploadExcel,
  uploadAndFilter,
  listJobs,
  filterJobs,
  recommendJobs,
  getJobDetail,
  matchJob,
  getCities,
  getPlatforms,
  getQualifications,
  login,
  getProfile,
  updateProfile,
  getFavorites,
  addFavorite,
  removeFavorite
}