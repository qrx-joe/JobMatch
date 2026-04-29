/**
 * API服务封装
 * 对接真实后端 API
 */

const app = getApp()

// API 基础地址配置
// 开发环境: http://localhost:8000
// 生产环境: 需要配置为实际服务器地址
const API_BASE_URL = 'http://localhost:8000'

const request = (options) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API_BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 404) {
          reject(new Error('请求的资源不存在'))
        } else if (res.statusCode >= 500) {
          reject(new Error('服务器错误'))
        } else {
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// ==================== 岗位相关 API ====================

/**
 * 上传Excel文件
 * @param {string} filePath - 文件临时路径
 * @param {string} platform - 平台类型，默认"三支一扶"
 */
const uploadExcel = (filePath, platform = '三支一扶') => {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: API_BASE_URL + '/api/jobs/upload',
      filePath: filePath,
      name: 'file',
      formData: { platform },
      success: (res) => {
        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(res.data))
          } catch (e) {
            reject(new Error('解析响应失败'))
          }
        } else {
          reject(new Error(`上传失败: ${res.statusCode}`))
        }
      },
      fail: reject
    })
  })
}

/**
 * 获取岗位列表
 * @param {object} params - 查询参数
 */
const listJobs = (params = {}) => {
  return request({
    url: '/api/jobs',
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
    url: '/api/jobs/filter',
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
    url: '/api/jobs/recommend',
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
    url: `/api/jobs/${jobId}`
  })
}

/**
 * 获取岗位匹配分析
 * @param {number} jobId - 岗位ID
 * @param {object} profile - 用户画像
 */
const matchJob = (jobId, profile) => {
  return request({
    url: `/api/jobs/${jobId}/match`,
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
    url: '/api/cities',
    method: 'GET',
    data: platform ? { platform } : {}
  })
}

/**
 * 获取平台类型列表
 */
const getPlatforms = () => {
  return request({
    url: '/api/platforms'
  })
}

// ==================== 用户相关 API ====================

/**
 * 微信登录
 * @param {string} code - 微信授权code
 */
const login = (code) => {
  return request({
    url: '/api/auth/login',
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
    url: `/api/profile/${openid}`
  })
}

/**
 * 更新用户画像
 * @param {string} openid - 用户openid
 * @param {object} profile - 用户画像
 */
const updateProfile = (openid, profile) => {
  return request({
    url: `/api/profile/${openid}`,
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
    url: `/api/favorites/${openid}`
  })
}

/**
 * 添加收藏
 * @param {string} openid - 用户openid
 * @param {number} jobId - 岗位ID
 */
const addFavorite = (openid, jobId) => {
  return request({
    url: `/api/favorites/${openid}/${jobId}`,
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
    url: `/api/favorites/${openid}/${jobId}`,
    method: 'DELETE'
  })
}

module.exports = {
  request,
  uploadExcel,
  listJobs,
  filterJobs,
  recommendJobs,
  getJobDetail,
  matchJob,
  getCities,
  getPlatforms,
  login,
  getProfile,
  updateProfile,
  getFavorites,
  addFavorite,
  removeFavorite
}