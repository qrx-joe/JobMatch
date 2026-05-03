/**
 * 首页 - 搜索入口和快捷筛选
 */

const app = getApp()
const api = require('../../services/api.js')

Page({
  data: {
    platforms: [
      { id: 'sanzhiyifu', name: '三支一扶', icon: '&#xe601;', color: '#1890ff' },
      { id: 'gongwuyuan', name: '公务员', icon: '&#xe600;', color: '#52c41a' },
      { id: 'shiyedan', name: '事业编', icon: '&#xe602;', color: '#faad14' },
      { id: 'jiaoshi', name: '教师招聘', icon: '&#xe603;', color: '#f5222d' },
    ],
    recentSearches: [],
    hotCities: ['太原市', '大同市', '运城市', '临汾市', '吕梁市'],
    selectedPlatform: 'sanzhiyifu',
    newsList: [
      { title: '2026年山西省三支一扶公告发布', date: '2026-04-15' },
      { title: '笔试时间确定为5月25日', date: '2026-04-20' },
      { title: '报名入口已开启', date: '2026-04-22' },
    ]
  },

  onLoad() {
    this.loadRecentSearches()
    this.checkLogin()
  },

  onShow() {
    // 更新tabBar显示
    if (typeof this.getTabBar === 'function') {
      this.getTabBar().setData({ selected: 0 })
    }
  },

  checkLogin() {
    const openid = wx.getStorageSync('openid')
    if (!openid) {
      app.login((newOpenid) => {
        console.log('登录成功:', newOpenid)
      })
    }
  },

  loadRecentSearches() {
    const searches = wx.getStorageSync('recentSearches') || []
    this.setData({ recentSearches: searches.slice(0, 5) })
  },

  selectPlatform(e) {
    const { id } = e.currentTarget.dataset
    this.setData({ selectedPlatform: id })
  },

  goToFilter() {
    wx.navigateTo({
      url: `/pages/filter/filter?platform=${this.data.selectedPlatform}`
    })
  },

  searchByCity(e) {
    const { city } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/filter/filter?platform=${this.data.selectedPlatform}&city=${city}`
    })
  },

  viewNews(e) {
    const { url } = e.currentTarget.dataset
    // 可以跳转到详情页或展示公告内容
    wx.showModal({
      title: '公告详情',
      content: '公告内容详情页开发中...',
      showCancel: false
    })
  },

  quickFilter(e) {
    const { type } = e.currentTarget.dataset
    let profile = {}

    switch (type) {
      case 'fresh':
        profile = { is_fresh_graduate: true }
        break
      case 'party':
        profile = { party_status: '中共党员' }
        break
      case 'under30':
        profile = { age: 25 }
        break
    }

    // 跳转到筛选页并预填条件
    wx.navigateTo({
      url: `/pages/filter/filter?platform=${this.data.selectedPlatform}&preset=${encodeURIComponent(JSON.stringify(profile))}`
    })
  },

  goToResults() {
    wx.navigateTo({
      url: '/pages/results/results'
    })
  }
})