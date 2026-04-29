/**
 * 结果页 - 岗位列表展示
 */

const app = getApp()
const api = require('../../services/api.js')

Page({
  data: {
    platform: 'sanzhiyifu',
    profile: null,
    jobs: [],
    filteredJobs: [],
    total: 0,

    // 筛选状态
    loading: true,
    activeTab: 'all', // all | stretch | safe | bottom
    sortBy: 'competition_ratio', // competition_ratio | match_score
    sortOrder: 'asc',

    // 统计数据
    stats: {
      stretchCount: 0,
      safeCount: 0,
      bottomCount: 0,
      avgRatio: 0
    }
  },

  onLoad(options) {
    if (options.platform) {
      this.setData({ platform: options.platform })
    }

    if (options.profile) {
      try {
        const profile = JSON.parse(decodeURIComponent(options.profile))
        this.setData({ profile })
        this.loadJobs()
      } catch (e) {
        console.error('解析profile失败', e)
      }
    }
  },

  onShow() {
    if (typeof this.getTabBar === 'function') {
      this.getTabBar().setData({ selected: 1 })
    }
  },

  loadJobs() {
    this.setData({ loading: true })

    const { profile, platform } = this.data

    // 调用推荐API
    api.recommendJobs(profile, { platform })
      .then(result => {
        const jobs = [
          ...(result.stretch || []),
          ...(result.safe || []),
          ...(result.bottom || [])
        ]

        // 计算统计数据
        const stats = this.calcStats(result)

        this.setData({
          jobs,
          filteredJobs: jobs,
          total: jobs.length,
          stats,
          loading: false
        })
      })
      .catch(err => {
        console.error('加载岗位失败', err)
        this.setData({ loading: false })
        // 使用模拟数据
        this.loadMockData()
      })
  },

  loadMockData() {
    // 模拟数据用于开发测试
    const mockJobs = [
      {
        id: 1,
        platform: '三支一扶',
        city: '太原市',
        unit: '太原市某区教育局',
        job_type: '支教',
        major: '教育学',
        education: '本科及以上',
        recruit_count: 2,
        competition_ratio: 8.5,
        match_level: '完全符合',
        match_score: 92,
        recommendation_tier: '冲刺',
        pass_probability: 0.65
      },
      {
        id: 2,
        platform: '三支一扶',
        city: '吕梁市',
        unit: '吕梁市农业农村局',
        job_type: '支农',
        major: '农学',
        education: '本科',
        recruit_count: 3,
        competition_ratio: 15.2,
        match_level: '完全符合',
        match_score: 88,
        recommendation_tier: '稳妥',
        pass_probability: 0.45
      },
      {
        id: 3,
        platform: '三支一扶',
        city: '运城市',
        unit: '运城市中心医院',
        job_type: '支医',
        major: '临床医学',
        education: '本科及以上',
        recruit_count: 5,
        competition_ratio: 25.0,
        match_level: '可能符合',
        match_score: 75,
        recommendation_tier: '保底',
        pass_probability: 0.30
      },
      {
        id: 4,
        platform: '三支一扶',
        city: '大同市',
        unit: '大同市人社局',
        job_type: '扶贫',
        major: '不限',
        education: '大专及以上',
        recruit_count: 4,
        competition_ratio: 32.5,
        match_level: '可能符合',
        match_score: 60,
        recommendation_tier: '稳妥',
        pass_probability: 0.25
      }
    ]

    const stats = {
      stretchCount: mockJobs.filter(j => j.recommendation_tier === '冲刺').length,
      safeCount: mockJobs.filter(j => j.recommendation_tier === '稳妥').length,
      bottomCount: mockJobs.filter(j => j.recommendation_tier === '保底').length,
      avgRatio: (mockJobs.reduce((sum, j) => sum + j.competition_ratio, 0) / mockJobs.length).toFixed(1)
    }

    this.setData({
      jobs: mockJobs,
      filteredJobs: mockJobs,
      total: mockJobs.length,
      stats,
      loading: false
    })
  },

  calcStats(result) {
    const stretch = result.stretch || []
    const safe = result.safe || []
    const bottom = result.bottom || []
    const all = [...stretch, ...safe, ...bottom]

    const avgRatio = all.length > 0
      ? (all.reduce((sum, j) => sum + (j.competition_ratio || 0), 0) / all.length).toFixed(1)
      : 0

    return {
      stretchCount: stretch.length,
      safeCount: safe.length,
      bottomCount: bottom.length,
      avgRatio
    }
  },

  // Tab切换
  switchTab(e) {
    const { tab } = e.currentTarget.dataset
    this.setData({ activeTab: tab })
    this.applyFilter()
  },

  applyFilter() {
    const { jobs, activeTab } = this.data

    let filtered = jobs
    if (activeTab !== 'all') {
      const tierMap = { stretch: '冲刺', safe: '稳妥', bottom: '保底' }
      filtered = jobs.filter(j => j.recommendation_tier === tierMap[activeTab])
    }

    this.setData({ filteredJobs: filtered })
  },

  // 排序
  changeSort(e) {
    const { field } = e.currentTarget.dataset
    if (this.data.sortBy === field) {
      this.setData({ sortOrder: this.data.sortOrder === 'asc' ? 'desc' : 'asc' })
    } else {
      this.setData({ sortBy: field, sortOrder: 'asc' })
    }
    this.applySort()
  },

  applySort() {
    const { filteredJobs, sortBy, sortOrder } = this.data
    const sorted = [...filteredJobs].sort((a, b) => {
      let valA = a[sortBy] || 0
      let valB = b[sortBy] || 0

      if (sortBy === 'match_score') {
        valA = parseFloat(valA)
        valB = parseFloat(valB)
      } else if (sortBy === 'competition_ratio') {
        valA = parseFloat(valA)
        valB = parseFloat(valB)
      }

      return sortOrder === 'asc' ? valA - valB : valB - valA
    })

    this.setData({ filteredJobs: sorted })
  },

  // 查看详情
  goToDetail(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  },

  // 收藏岗位
  toggleFavorite(e) {
    const { id } = e.currentTarget.dataset
    const openid = app.globalData.userInfo?.openid
    if (!openid) return

    const job = this.data.jobs.find(j => j.id === id)
    if (!job) return

    const action = job.isFavorited ? 'removeFavorite' : 'addFavorite'
    api[action](openid, id)
      .then(() => {
        job.isFavorited = !job.isFavorited
        this.setData({ jobs: this.data.jobs })
        wx.showToast({
          title: job.isFavorited ? '已收藏' : '已取消收藏',
          icon: 'success'
        })
      })
      .catch(err => {
        wx.showToast({ title: '操作失败', icon: 'none' })
      })
  },

  // 刷新数据
  refresh() {
    this.loadJobs()
  }
})