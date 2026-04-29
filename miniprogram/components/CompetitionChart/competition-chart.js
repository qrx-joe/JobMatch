/**
 * 竞争比图表组件
 */

Component({
  properties: {
    data: {
      type: Array,
      value: []
    },
    title: {
      type: String,
      value: '竞争比趋势'
    }
  },

  data: {
    maxRatio: 0,
    chartData: []
  },

  observers: {
    'data': function(data) {
      this.updateChart(data)
    }
  },

  methods: {
    updateChart(data) {
      if (!data || data.length === 0) return

      // 计算最大值
      const maxRatio = Math.max(...data.map(d => d.competition_ratio || 0))

      // 转换数据用于渲染
      const chartData = data.map(d => ({
        year: d.year,
        ratio: d.competition_ratio || 0,
        height: maxRatio > 0 ? ((d.competition_ratio || 0) / maxRatio) * 100 : 0
      }))

      this.setData({ maxRatio, chartData })
    }
  }
})