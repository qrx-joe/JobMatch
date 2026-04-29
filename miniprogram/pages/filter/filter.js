/**
 * 筛选页 - 填写用户条件
 */

const app = getApp()
const api = require('../../services/api.js')

Page({
  data: {
    platform: 'sanzhiyifu',
    presetProfile: null,

    // 用户画像
    profile: {
      major: '',
      education: '',
      degree: '',
      gender: '',
      age: '',
      household: '',
      party_status: '',
      is_fresh_graduate: false,
      grassroots_exp: 0,
      estimated_score: '',
      target_cities: [],
      target_platforms: []
    },

    // 选项数据
    educationOptions: [
      { value: '大专', label: '大专' },
      { value: '本科', label: '本科' },
      { value: '研究生', label: '研究生' },
    ],
    genderOptions: [
      { value: '男', label: '男' },
      { value: '女', label: '女' },
    ],
    partyStatusOptions: [
      { value: '群众', label: '群众' },
      { value: '共青团员', label: '共青团员' },
      { value: '预备党员', label: '预备党员' },
      { value: '中共党员', label: '中共党员' },
    ],
    cityOptions: [
      '太原市', '大同市', '朔州市', '忻州市', '吕梁市',
      '晋中市', '阳泉市', '长治市', '晋城市', '临汾市', '运城市'
    ],

    // 热门城市
    hotCities: ['太原市', '吕梁市', '运城市', '临汾市', '大同市'],

    // 上传状态
    uploading: false,
    uploadResult: null,

    // 验证状态
    errors: {}
  },

  onLoad(options) {
    if (options.platform) {
      this.setData({ platform: options.platform })
    }

    // 解析预设条件
    if (options.preset) {
      try {
        const preset = JSON.parse(decodeURIComponent(options.preset))
        this.setData({
          presetProfile: preset,
          profile: { ...this.data.profile, ...preset }
        })
      } catch (e) {
        console.error('解析预设条件失败', e)
      }
    }

    // 从缓存加载已保存的条件
    this.loadSavedProfile()
  },

  onShow() {
    if (typeof this.getTabBar === 'function') {
      this.getTabBar().setData({ selected: 1 })
    }
  },

  loadSavedProfile() {
    const saved = wx.getStorageSync('userProfile')
    if (saved) {
      this.setData({
        profile: { ...this.data.profile, ...saved }
      })
    }
  },

  // 输入处理
  onMajorInput(e) {
    this.setData({ 'profile.major': e.detail.value })
  },

  onEducationChange(e) {
    const { value } = e.detail
    this.setData({ 'profile.education': value })
  },

  onGenderChange(e) {
    const { value } = e.detail
    this.setData({ 'profile.gender': value })
  },

  onPartyStatusChange(e) {
    const { value } = e.detail
    this.setData({ 'profile.party_status': value })
  },

  onAgeChange(e) {
    this.setData({ 'profile.age': e.detail.value })
  },

  onHouseholdChange(e) {
    this.setData({ 'profile.household': e.detail.value })
  },

  onScoreInput(e) {
    this.setData({ 'profile.estimated_score': e.detail.value })
  },

  onFreshGraduateChange(e) {
    this.setData({ 'profile.is_fresh_graduate': e.detail.value.length > 0 })
  },

  // 城市选择
  selectCity(e) {
    const { city } = e.currentTarget.dataset
    const { target_cities } = this.data.profile

    if (target_cities.includes(city)) {
      this.setData({
        'profile.target_cities': target_cities.filter(c => c !== city)
      })
    } else if (target_cities.length < 3) {
      this.setData({
        'profile.target_cities': [...target_cities, city]
      })
    } else {
      wx.showToast({ title: '最多选择3个城市', icon: 'none' })
    }
  },

  clearCities() {
    this.setData({ 'profile.target_cities': [] })
  },

  // 验证表单
  validate() {
    const { profile } = this.data
    const errors = {}

    if (!profile.major) {
      errors.major = '请输入专业'
    }

    if (!profile.education) {
      errors.education = '请选择学历'
    }

    this.setData({ errors })
    return Object.keys(errors).length === 0
  },

  // 上传Excel
  uploadExcel() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      success: (res) => {
        const file = res.tempFiles[0]
        if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
          wx.showToast({ title: '请选择Excel文件', icon: 'none' })
          return
        }

        this.setData({ uploading: true })

        api.uploadExcel(file.path)
          .then(result => {
            this.setData({
              uploading: false,
              uploadResult: result
            })
            wx.showToast({ title: `成功解析${result.total}个岗位`, icon: 'success' })
          })
          .catch(err => {
            this.setData({ uploading: false })
            wx.showToast({ title: '上传失败', icon: 'none' })
            console.error('上传失败', err)
          })
      }
    })
  },

  // 开始筛选
  startFilter() {
    if (!this.validate()) {
      return
    }

    // 保存条件到缓存
    wx.setStorageSync('userProfile', this.data.profile)

    // 跳转到结果页
    wx.navigateTo({
      url: `/pages/results/results?platform=${this.data.platform}&profile=${encodeURIComponent(JSON.stringify(this.data.profile))}`
    })
  },

  // 重置表单
  resetForm() {
    wx.showModal({
      title: '确认重置',
      content: '确定要清空所有已填写的信息吗？',
      success: (res) => {
        if (res.confirm) {
          this.setData({
            profile: {
              major: '',
              education: '',
              degree: '',
              gender: '',
              age: '',
              household: '',
              party_status: '',
              is_fresh_graduate: false,
              grassroots_exp: 0,
              estimated_score: '',
              target_cities: [],
              target_platforms: []
            },
            errors: {},
            uploadResult: null
          })
          wx.removeStorageSync('userProfile')
        }
      }
    })
  }
})