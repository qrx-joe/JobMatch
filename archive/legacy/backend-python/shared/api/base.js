/**
 * API 请求基础封装
 * 兼容小程序 wx.request 和 网页 fetch
 */

/**
 * 获取当前环境的请求方法
 * @param {string} adapterType - 'wechat' | 'web' | 'auto'
 * @returns {object} { request, uploadFile }
 */
export const createAdapter = (adapterType = 'auto') => {
  // 自动检测环境
  if (adapterType === 'auto') {
    if (typeof wx !== 'undefined' && wx.request) {
      adapterType = 'wechat'
    } else {
      adapterType = 'web'
    }
  }

  const request = (options) => {
    const { url, method = 'GET', data, headers = {} } = options

    if (adapterType === 'wechat') {
      return new Promise((resolve, reject) => {
        wx.request({
          url,
          method,
          data,
          header: { 'Content-Type': 'application/json', ...headers },
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
          fail: reject
        })
      })
    } else {
      // web
      return fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', ...headers },
        body: method !== 'GET' && method !== 'HEAD' ? JSON.stringify(data) : undefined
      }).then(res => {
        if (!res.ok) throw new Error(`请求失败: ${res.status}`)
        return res.json()
      })
    }
  }

  const uploadFile = (options) => {
    const { url, filePath, name = 'file', formData = {} } = options

    if (adapterType === 'wechat') {
      return new Promise((resolve, reject) => {
        wx.uploadFile({
          url,
          filePath,
          name,
          formData,
          success: (res) => {
            if (res.statusCode === 200) {
              try {
                resolve(JSON.parse(res.data))
              } catch (e) {
                resolve(res.data)
              }
            } else {
              reject(new Error(`上传失败: ${res.statusCode}`))
            }
          },
          fail: reject
        })
      })
    } else {
      // web - 使用 FormData
      const form = new FormData()
      Object.entries(formData).forEach(([k, v]) => form.append(k, v))
      form.append(name, filePath)

      return fetch(url, {
        method: 'POST',
        body: form
      }).then(res => {
        if (!res.ok) throw new Error(`上传失败: ${res.status}`)
        return res.json()
      })
    }
  }

  return { request, uploadFile }
}
