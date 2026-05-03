/**
 * 收藏页 - 用户收藏的岗位列表
 */

const app = getApp()
const api = require('../../services/api.js')

Page({
  data: {
    favorites: [],
    loading: true,
    empty: true
  },

  onLoad() {
    // 检查登录
    const openid = wx.getStorageSync('openid')
    if (!openid) {
      app.login(() => {
        this.loadFavorites()
      })
    } else {
      this.loadFavorites()
    }
  },

  onShow() {
    if (typeof this.getTabBar === 'function') {
      this.getTabBar().setData({ selected: 2 })
    }
    // 每次显示页面时刷新收藏
    this.loadFavorites()
  },

  loadFavorites() {
    const openid = app.globalData.userInfo?.openid || wx.getStorageSync('openid')
    if (!openid) {
      this.setData({ loading: false, empty: true })
      return
    }

    this.setData({ loading: true })

    api.getFavorites(openid)
      .then(res => {
        const favorites = res.favorites || []
        this.setData({
          favorites,
          loading: false,
          empty: favorites.length === 0
        })
      })
      .catch(err => {
        console.error('加载收藏失败', err)
        this.setData({ loading: false, empty: true })
      })
  },

  goToDetail(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  },

  removeFavorite(e) {
    const { id } = e.currentTarget.dataset
    const openid = app.globalData.userInfo?.openid || wx.getStorageSync('openid')
    if (!openid) return

    wx.showModal({
      title: '确认取消',
      content: '确定要取消收藏这个岗位吗？',
      success: (res) => {
        if (res.confirm) {
          api.removeFavorite(openid, id)
            .then(() => {
              const favorites = this.data.favorites.filter(f => f.id !== id)
              this.setData({
                favorites,
                empty: favorites.length === 0
              })
              wx.showToast({ title: '已取消收藏', icon: 'success' })
            })
            .catch(() => {
              wx.showToast({ title: '操作失败', icon: 'none' })
            })
        }
      }
    })
  },

  compareJobs() {
    if (this.data.favorites.length < 2) {
      wx.showToast({ title: '至少需要2个岗位进行对比', icon: 'none' })
      return
    }

    // 限制最多4个岗位进行对比
    const jobsToCompare = this.data.favorites.slice(0, 4)
    wx.navigateTo({
      url: `/pages/compare/compare?jobs=${encodeURIComponent(JSON.stringify(jobsToCompare))}`
    })
  }
})