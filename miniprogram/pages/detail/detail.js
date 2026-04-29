/**
 * 详情页 - 岗位完整信息展示
 */

const app = getApp()
const api = require('../../services/api.js')

Page({
  data: {
    job: null,
    loading: true,
    isFavorited: false,
    relatedJobs: []
  },

  onLoad(options) {
    const { id } = options
    if (id) {
      this.loadJobDetail(id)
    }
  },

  loadJobDetail(id) {
    this.setData({ loading: true })

    api.getJobDetail(id)
      .then(job => {
        this.setData({
          job,
          loading: false
        })
        this.checkFavoriteStatus()
      })
      .catch(err => {
        console.error('加载失败', err)
        // 使用模拟数据
        this.setData({
          job: this.getMockJob(id),
          loading: false
        })
      })
  },

  getMockJob(id) {
    return {
      id: parseInt(id),
      platform: '三支一扶',
      city: '太原市',
      unit: '太原市某区教育局',
      job_type: '支教',
      service_category: '教育类',
      recruit_count: 2,
      education: '本科及以上',
      degree: '学士及以上',
      major: '教育学类',
      age_limit: '30岁以下',
      political_requirement: '不限',
      qualifications: '教师资格证',
      competition_ratio: 8.5,
      applicants: 120,
      approved: 45,
      paid: 17,
      match_level: '完全符合',
      match_score: 92,
      recommendation_tier: '冲刺',
      pass_probability: 0.65,
      phone: '0351-1234567',
      contact: '李老师',
      match_reasons: [
        '专业完全匹配：教育学类',
        '学历符合：本科 >= 本科及以上',
        '竞争比较低(8.5:1)'
      ],
      historical_stats: [
        { year: 2024, competition_ratio: 6.2, passing_score: 58 },
        { year: 2023, competition_ratio: 5.8, passing_score: 55 }
      ]
    }
  },

  checkFavoriteStatus() {
    const openid = app.globalData.userInfo?.openid
    if (!openid || !this.data.job) return

    api.getFavorites(openid)
      .then(res => {
        const favorites = res.favorites || []
        this.setData({ isFavorited: favorites.includes(this.data.job.id) })
      })
  },

  toggleFavorite() {
    const openid = app.globalData.userInfo?.openid
    if (!openid) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }

    const jobId = this.data.job.id
    const action = this.data.isFavorited ? 'removeFavorite' : 'addFavorite'

    api[action](openid, jobId)
      .then(() => {
        this.setData({ isFavorited: !this.data.isFavorited })
        wx.showToast({
          title: this.data.isFavorited ? '已收藏' : '已取消收藏',
          icon: 'success'
        })
      })
      .catch(() => {
        wx.showToast({ title: '操作失败', icon: 'none' })
      })
  },

  shareJob() {
    const { job } = this.data
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  onShareAppMessage() {
    const { job } = this.data
    return {
      title: `${job.unit} - ${job.city}`,
      path: `/pages/detail/detail?id=${job.id}`
    }
  },

  viewHistory() {
    // 跳转到历史分析页面或展示历史弹窗
    wx.showModal({
      title: '历年数据',
      content: JSON.stringify(this.data.job.historical_stats, null, 2),
      showCancel: false
    })
  }
})