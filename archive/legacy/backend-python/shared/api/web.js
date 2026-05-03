/**
 * 统一 API 服务 - 网页版
 * 同时支持小程序和网页端
 */

const API_BASE_URL = ''

export const createApi = (baseUrl = API_BASE_URL) => {
  const request = (options) => {
    const { url, method = 'GET', data, headers = {} } = options

    return fetch(`${baseUrl}${url}`, {
      method,
      headers: { 'Content-Type': 'application/json', ...headers },
      body: method !== 'GET' && method !== 'HEAD' ? JSON.stringify(data) : undefined
    }).then(res => {
      if (!res.ok) throw new Error(`请求失败: ${res.status}`)
      return res.json()
    })
  }

  const uploadFile = (options) => {
    const { url, filePath, name = 'file', formData = {} } = options
    const form = new FormData()
    Object.entries(formData).forEach(([k, v]) => form.append(k, v))
    form.append(name, filePath)

    return fetch(`${baseUrl}${url}`, {
      method: 'POST',
      body: form
    }).then(res => {
      if (!res.ok) throw new Error(`上传失败: ${res.status}`)
      return res.json()
    })
  }

  // ==================== 岗位相关 API ====================

  /**
   * 上传Excel文件
   */
  const uploadExcel = (filePath, name = 'file', platform = '三支一扶') => {
    return uploadFile({
      url: '/api/jobs/upload',
      filePath,
      name,
      formData: { platform }
    })
  }

  /**
   * 上传并筛选(网页端专用)
   * @param {FormData} formData - 表单数据
   */
  const uploadAndFilter = (formData) => {
    return fetch(`${baseUrl}/upload-and-filter`, {
      method: 'POST',
      body: formData
    }).then(res => {
      if (!res.ok) throw new Error(`请求失败: ${res.status}`)
      return res.json()
    })
  }

  /**
   * 获取岗位列表
   */
  const listJobs = (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request({
      url: `/api/jobs${qs ? '?' + qs : ''}`,
      method: 'GET'
    })
  }

  /**
   * 筛选岗位并推荐
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
   */
  const getJobDetail = (jobId) => {
    return request({ url: `/api/jobs/${jobId}` })
  }

  /**
   * 获取岗位匹配分析
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
    return request({ url: '/api/platforms' })
  }

  /**
   * 获取资质证书列表
   */
  const getQualifications = () => {
    return request({ url: '/api/qualifications' })
  }

  // ==================== 用户相关 API ====================

  /**
   * 微信登录
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
   */
  const getProfile = (openid) => {
    return request({ url: `/api/profile/${openid}` })
  }

  /**
   * 更新用户画像
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
   */
  const getFavorites = (openid) => {
    return request({ url: `/api/favorites/${openid}` })
  }

  /**
   * 添加收藏
   */
  const addFavorite = (openid, jobId) => {
    return request({
      url: `/api/favorites/${openid}/${jobId}`,
      method: 'POST'
    })
  }

  /**
   * 取消收藏
   */
  const removeFavorite = (openid, jobId) => {
    return request({
      url: `/api/favorites/${openid}/${jobId}`,
      method: 'DELETE'
    })
  }

  return {
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
}

export default createApi()
