/**
 * 冲/稳/保 标签组件
 */

Component({
  properties: {
    tier: {
      type: String,
      value: ''
    },
    size: {
      type: String,
      value: 'medium' // small | medium | large
    }
  },

  data: {
    tierClass: ''
  },

  observers: {
    'tier': function(tier) {
      const tierMap = {
        '冲刺': 'stretch',
        '稳妥': 'safe',
        '保底': 'bottom'
      }
      this.setData({ tierClass: tierMap[tier] || '' })
    }
  }
})