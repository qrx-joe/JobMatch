/**
 * API服务封装
 * 对接真实后端 API
 * 已重构：使用 shared/api/index.js
 */

const api = require('../../../shared/api/index')

// 直接导出 shared 的 API（平台适配已内置）
module.exports = {
  uploadExcel: api.uploadExcel,
  listJobs: api.listJobs,
  filterJobs: api.filterJobs,
  recommendJobs: api.recommendJobs,
  getJobDetail: api.getJobDetail,
  matchJob: api.matchJob,
  getCities: api.getCities,
  getPlatforms: api.getPlatforms,
  login: api.login,
  getProfile: api.getProfile,
  updateProfile: api.updateProfile,
  getFavorites: api.getFavorites,
  addFavorite: api.addFavorite,
  removeFavorite: api.removeFavorite
}
