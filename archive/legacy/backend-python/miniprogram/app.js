/**
 * JobMatch 微信小程序入口
 */

App({
  globalData: {
    apiBaseUrl: 'http://localhost:8000',
    userInfo: null,
    profile: null,
    cachedJobs: [],
  },

  onLaunch() {
    // 检查登录状态
    this.checkLoginStatus()
  },

  checkLoginStatus() {
    const openid = wx.getStorageSync('openid')
    if (openid) {
      this.globalData.userInfo = { openid }
      this.loadProfile(openid)
    }
  },

  login(callback) {
    // 微信登录
    wx.login({
      success: (res) => {
        if (res.code) {
          // 请求后端登录
          wx.request({
            url: `${this.globalData.apiBaseUrl}/api/auth/login`,
            method: 'POST',
            data: { code: res.code },
            success: (loginRes) => {
              const { openid } = loginRes.data
              this.globalData.userInfo = { openid }
              wx.setStorageSync('openid', openid)
              callback && callback(openid)
            },
            fail: () => {
              // 模拟登录（用于开发测试）
              const mockOpenid = 'mock_openid_' + Date.now()
              this.globalData.userInfo = { openid: mockOpenid }
              wx.setStorageSync('openid', mockOpenid)
              callback && callback(mockOpenid)
            }
          })
        }
      },
      fail: () => {
        // 模拟登录
        const mockOpenid = 'mock_openid_' + Date.now()
        this.globalData.userInfo = { openid: mockOpenid }
        wx.setStorageSync('openid', mockOpenid)
        callback && callback(mockOpenid)
      }
    })
  },

  loadProfile(openid) {
    wx.request({
      url: `${this.globalData.apiBaseUrl}/api/profile/${openid}`,
      success: (res) => {
        if (res.data) {
          this.globalData.profile = res.data
        }
      }
    })
  },

  saveProfile(profile, callback) {
    const openid = this.globalData.userInfo?.openid
    if (!openid) return

    wx.request({
      url: `${this.globalData.apiBaseUrl}/api/profile/${openid}`,
      method: 'PUT',
      data: profile,
      success: (res) => {
        this.globalData.profile = profile
        callback && callback(res.data)
      }
    })
  }
})