/**
 * API 服务 - 网页端 (webapp/backend/app.py)
 * 直接调用后端接口，无 /api 前缀
 */

const API_BASE = import.meta.env.DEV ? '' : ''

export const getCities = () => {
  return fetch(`${API_BASE}/cities`).then(res => res.json())
}

export const getQualifications = () => {
  return fetch(`${API_BASE}/qualifications`).then(res => res.json())
}

export const uploadAndFilter = (formData) => {
  return fetch(`${API_BASE}/upload-and-filter`, {
    method: 'POST',
    body: formData
  }).then(res => {
    if (!res.ok) throw new Error(`请求失败: ${res.status}`)
    return res.json()
  })
}

export default {
  getCities,
  getQualifications,
  uploadAndFilter
}
