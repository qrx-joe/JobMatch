/**
 * API服务封装
 */

const app = getApp()

const request = (options) => {
  return new Promise((resolve, reject) => {
    const apiBaseUrl = app.globalData.apiBaseUrl || 'http://localhost:8000'

    wx.request({
      url: apiBaseUrl + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
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

// 上传Excel文件
const uploadExcel = (filePath) => {
  const apiBaseUrl = app.globalData.apiBaseUrl || 'http://localhost:8000'

  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: apiBaseUrl + '/api/jobs/upload',
      filePath: filePath,
      name: 'file',
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(JSON.parse(res.data))
        } else {
          reject(new Error(`上传失败: ${res.statusCode}`))
        }
      },
      fail: reject
    })
  })
}

// 筛选岗位
const filterJobs = (profile, options = {}) => {
  return request({
    url: '/api/jobs/filter',
    method: 'POST',
    data: {
      profile,
      ...options
    }
  })
}

// 推荐岗位
const recommendJobs = (profile, options = {}) => {
  return request({
    url: '/api/jobs/recommend',
    method: 'POST',
    data: {
      profile,
      ...options
    }
  })
}

// 获取岗位详情
const getJobDetail = (jobId) => {
  return request({
    url: `/api/jobs/${jobId}`
  })
}

// 获取用户画像
const getProfile = (openid) => {
  return request({
    url: `/api/profile/${openid}`
  })
}

// 更新用户画像
const updateProfile = (openid, profile) => {
  return request({
    url: `/api/profile/${openid}`,
    method: 'PUT',
    data: profile
  })
}

// 获取收藏列表
const getFavorites = (openid) => {
  return request({
    url: `/api/favorites/${openid}`
  })
}

// 添加收藏
const addFavorite = (openid, jobId) => {
  return request({
    url: `/api/favorites/${openid}/${jobId}`,
    method: 'POST'
  })
}

// 取消收藏
const removeFavorite = (openid, jobId) => {
  return request({
    url: `/api/favorites/${openid}/${jobId}`,
    method: 'DELETE'
  })
}

module.exports = {
  request,
  uploadExcel,
  filterJobs,
  recommendJobs,
  getJobDetail,
  getProfile,
  updateProfile,
  getFavorites,
  addFavorite,
  removeFavorite
}