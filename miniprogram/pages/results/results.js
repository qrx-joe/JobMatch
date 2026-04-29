/**
 * 结果页 - 岗位列表展示
 * 对接真实后端API
 */

const app = getApp()
const api = require('../../services/api.js')

Page({
  data: {
    platform: '三支一扶',
    profile: null,
    jobs: [],
    filteredJobs: [],
    total: 0,

    // 筛选状态
    loading: true,
    activeTab: 'all', // all | stretch | safe | bottom
    sortBy: 'competition_ratio', // competition_ratio | match_score
    sortOrder: 'asc',

    // 错误状态
    error: null,
    usingMockData: false,

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
      // 转换平台名称
      const platformMap = {
        'sanzhiyifu': '三支一扶',
        'gongwuyuan': '公务员',
        'shiyedan': '事业编',
        'jiaoshi': '教师'
      }
      this.setData({ platform: platformMap[options.platform] || options.platform })
    }

    if (options.profile) {
      try {
        const profile = JSON.parse(decodeURIComponent(options.profile))
        this.setData({ profile })
        this.loadJobs()
      } catch (e) {
        console.error('解析profile失败', e)
        this.setData({ error: '参数解析失败' })
      }
    } else {
      // 如果没有profile，尝试从缓存获取
      const savedProfile = wx.getStorageSync('userProfile')
      if (savedProfile) {
        this.setData({ profile: savedProfile })
        this.loadJobs()
      } else {
        this.setData({ error: '请先填写筛选条件', loading: false })
      }
    }
  },

  onShow() {
    if (typeof this.getTabBar === 'function') {
      this.getTabBar().setData({ selected: 1 })
    }
  },

  loadJobs() {
    const { profile, platform } = this.data

    if (!profile) {
      this.setData({ error: '请先填写筛选条件', loading: false })
      return
    }

    this.setData({ loading: true, error: null, usingMockData: false })

    // 调用推荐API
    api.recommendJobs(profile, { platform })
      .then(result => {
        const jobs = [
          ...(result.stretch || []),
          ...(result.safe || []),
          ...(result.bottom || [])
        ]

        if (jobs.length === 0) {
          this.setData({
            error: '没有找到符合条件的岗位',
            loading: false,
            jobs: [],
            filteredJobs: [],
            total: 0,
            stats: { stretchCount: 0, safeCount: 0, bottomCount: 0, avgRatio: 0 }
          })
          return
        }

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
        // API失败时使用模拟数据
        this.setData({ usingMockData: true })
        this.loadMockData()
      })
  },

  loadMockData() {
    // 模拟数据用于开发测试或API不可用时
    const mockJobs = [
      {
        id: 1,
        platform: '三支一扶',
        city: '太原市',
        unit: '太原市小店区教育局',
        job_type: '支教',
        major: '教育学类',
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
        unit: '吕梁市离石区农业农村局',
        job_type: '支农',
        major: '农学类',
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
      },
      {
        id: 5,
        platform: '三支一扶',
        city: '临汾市',
        unit: '临汾市尧都区卫健局',
        job_type: '支医',
        major: '护理学',
        education: '本科',
        recruit_count: 2,
        competition_ratio: 5.8,
        match_level: '完全符合',
        match_score: 95,
        recommendation_tier: '冲刺',
        pass_probability: 0.72
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
      loading: false,
      error: '（当前显示模拟数据，请启动后端服务获取真实数据）'
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

    if (!openid) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }

    const job = this.data.jobs.find(j => j.id === id)
    if (!job) return

    const isFavorited = job.isFavorited
    const action = isFavorited ? 'removeFavorite' : 'addFavorite'

    api[action](openid, id)
      .then(() => {
        // 更新本地状态
        const updatedJobs = this.data.jobs.map(j => {
          if (j.id === id) {
            return { ...j, isFavorited: !isFavorited }
          }
          return j
        })
        this.setData({ jobs: updatedJobs })
        this.applyFilter()

        wx.showToast({
          title: isFavorited ? '已取消收藏' : '已收藏',
          icon: 'success'
        })
      })
      .catch(err => {
        console.error('收藏操作失败', err)
        wx.showToast({ title: '操作失败', icon: 'none' })
      })
  },

  // 刷新数据
  refresh() {
    this.loadJobs()
  }
})