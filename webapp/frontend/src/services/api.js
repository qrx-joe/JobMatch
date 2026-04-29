/**
 * API 服务 - 网页端
 * 从 shared/api/web.js 导入
 */
import api from '../../../../shared/api/web'

export const {
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
} = api
