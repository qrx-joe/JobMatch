/**
 * 岗位卡片组件
 */

Component({
  properties: {
    job: {
      type: Object,
      value: {}
    },
    showActions: {
      type: Boolean,
      value: true
    }
  },

  data: {
    isFavorited: false
  },

  methods: {
    onTap() {
      this.triggerEvent('tap', { job: this.properties.job })
    },

    onFavorite() {
      this.triggerEvent('favorite', { job: this.properties.job })
    }
  }
})