/**
 * 我的页面 - 用户信息和设置
 */

const app = getApp()
const api = require('../../services/api.js')

Page({
  data: {
    userInfo: null,
    profile: null,
    stats: {
      filterCount: 0,
      favoriteCount: 0,
      viewCount: 0
    }
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    if (typeof this.getTabBar === 'function') {
      this.getTabBar().setData({ selected: 3 })
    }
    this.loadUserInfo()
  },

  checkLogin() {
    const openid = wx.getStorageSync('openid')
    if (!openid) {
      app.login((newOpenid) => {
        this.loadUserInfo()
      })
    }
  },

  loadUserInfo() {
    const userInfo = app.globalData.userInfo || { openid: wx.getStorageSync('openid') }
    const profile = app.globalData.profile

    this.setData({
      userInfo,
      profile: profile || {}
    })

    // 加载使用统计
    this.loadStats()
  },

  loadStats() {
    // 从本地存储获取统计
    const filterCount = wx.getStorageSync('filterCount') || 0
    const favoriteCount = wx.getStorageSync('favoriteCount') || 0
    const viewCount = wx.getStorageSync('viewCount') || 0

    this.setData({
      stats: { filterCount, favoriteCount, viewCount }
    })
  },

  goToEditProfile() {
    wx.navigateTo({
      url: '/pages/filter/filter?mode=edit'
    })
  },

  clearCache() {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空所有缓存数据吗？',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorageSync()
          this.setData({
            profile: {},
            stats: { filterCount: 0, favoriteCount: 0, viewCount: 0 }
          })
          wx.showToast({ title: '已清空', icon: 'success' })
        }
      }
    })
  },

  viewAbout() {
    wx.showModal({
      title: '关于 JobMatch',
      content: 'JobMatch 智能选岗平台\n\n版本: 1.0.0\n\n为考公考编考生提供智能选岗服务',
      showCancel: false
    })
  },

  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('openid')
          wx.removeStorageSync('userProfile')
          app.globalData.userInfo = null
          app.globalData.profile = null
          this.setData({
            userInfo: null,
            profile: null
          })
          this.checkLogin()
        }
      }
    })
  }
})