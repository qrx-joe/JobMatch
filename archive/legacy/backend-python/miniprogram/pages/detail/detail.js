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
    relatedJobs: [],
    matchDetail: null
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
        // 加载匹配详情
        this.loadMatchDetail(id)
        // 检查收藏状态
        this.checkFavoriteStatus()
      })
      .catch(err => {
        console.error('加载失败', err)
        // 使用模拟数据
        this.setData({
          job: this.getMockJob(id),
          loading: false,
          matchDetail: this.getMockMatchDetail()
        })
      })
  },

  loadMatchDetail(jobId) {
    const profile = wx.getStorageSync('userProfile') || {}
    if (!profile.major) return

    api.matchJob(jobId, profile)
      .then(result => {
        this.setData({ matchDetail: result })
      })
      .catch(err => {
        console.error('加载匹配详情失败', err)
      })
  },

  getMockJob(id) {
    return {
      id: parseInt(id),
      platform: '三支一扶',
      city: '太原市',
      unit: '太原市小店区教育局',
      job_type: '支教',
      service_category: '教育类',
      recruit_count: 2,
      education: '本科及以上',
      degree: '学士及以上',
      major: '教育学类',
      age_limit: '30岁以下',
      political_requirement: '不限',
      qualifications: '教师资格证',
      phone: '0351-1234567',
      contact: '李老师',
      competition_ratio: 8.5,
      applicants: 120,
      approved: 45,
      paid: 17
    }
  },

  getMockMatchDetail() {
    return {
      match_result: {
        total_score: 92,
        match_level: '完全符合',
        major_match: '专业完全匹配：教育学类',
        education_match: '学历符合：本科 >= 本科及以上',
        match_reasons: ['专业完全匹配', '学历符合要求', '竞争比较低(8.5:1)'],
        mismatch_reasons: []
      },
      recommendation: {
        tier: '冲刺',
        pass_probability: 0.65
      }
    }
  },

  checkFavoriteStatus() {
    const openid = app.globalData.userInfo?.openid
    if (!openid || !this.data.job) return

    api.getFavorites(openid)
      .then(res => {
        const favorites = res.favorites || []
        // favorites 是岗位对象数组，需要检查 id
        const isFavorited = favorites.some(f => f.id === this.data.job.id)
        this.setData({ isFavorited })
      })
      .catch(err => {
        console.error('检查收藏状态失败', err)
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
      .catch(err => {
        console.error('收藏操作失败', err)
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
    // 展示历年数据
    const job = this.data.job
    if (!job) return

    let content = '暂无历年数据'
    if (job.historical_stats && job.historical_stats.length > 0) {
      content = job.historical_stats.map(s =>
        `${s.year}年: 竞争比 ${s.competition_ratio}:1, 进面分 ${s.passing_score}`
      ).join('\n')
    }

    wx.showModal({
      title: '历年数据',
      content: content,
      showCancel: false
    })
  },

  viewMatchDetail() {
    // 展示匹配详情
    const detail = this.data.matchDetail
    if (!detail) {
      wx.showToast({ title: '暂无匹配详情', icon: 'none' })
      return
    }

    const { match_result, recommendation } = detail
    let content = `匹配分数: ${match_result.total_score}/100\n`
    content += `匹配等级: ${match_result.match_level}\n\n`
    content += `推荐层级: ${recommendation.tier}\n`
    content += `上岸概率: ${(recommendation.pass_probability * 100).toFixed(0)}%\n\n`

    if (match_result.match_reasons && match_result.match_reasons.length > 0) {
      content += `匹配理由:\n${match_result.match_reasons.join('\n')}`
    }

    if (match_result.mismatch_reasons && match_result.mismatch_reasons.length > 0) {
      content += `\n\n不匹配理由:\n${match_result.mismatch_reasons.join('\n')}`
    }

    wx.showModal({
      title: '匹配分析',
      content: content,
      showCancel: false
    })
  }
})