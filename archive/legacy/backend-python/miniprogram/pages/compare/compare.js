/**
 * 对比页 - 岗位对比分析
 */

Page({
  data: {
    jobs: [],
    conclusion: '',
    bestJobId: null
  },

  onLoad(options) {
    if (options.jobs) {
      try {
        const jobs = JSON.parse(decodeURIComponent(options.jobs))
        this.processJobs(jobs)
      } catch (e) {
        console.error('解析岗位数据失败', e)
        wx.showToast({ title: '数据加载失败', icon: 'none' })
        wx.navigateBack()
      }
    } else {
      wx.navigateBack()
    }
  },

  processJobs(jobs) {
    if (!jobs || jobs.length < 2) {
      wx.showToast({ title: '至少需要2个岗位', icon: 'none' })
      wx.navigateBack()
      return
    }

    // 限制最多4个岗位
    const limitedJobs = jobs.slice(0, 4)

    // 计算各项指标最优
    const ratios = limitedJobs.map(j => j.competition_ratio || 0)
    const lowestRatio = Math.min(...ratios)

    const recruits = limitedJobs.map(j => j.recruit_count || 0)
    const highestRecruit = Math.max(...recruits)

    const scores = limitedJobs.map(j => j.match_score || 0)
    const highestScore = Math.max(...scores)

    const probs = limitedJobs.map(j => j.pass_probability || 0)
    const highestProb = Math.max(...probs)

    // 标记最优项
    const processedJobs = limitedJobs.map(j => ({
      ...j,
      isLowestRatio: (j.competition_ratio || 0) === lowestRatio,
      isHighestRecruit: (j.recruit_count || 0) === highestRecruit,
      isHighestScore: (j.match_score || 0) === highestScore,
      isHighestProb: (j.pass_probability || 0) === highestProb
    }))

    // 找出综合最优岗位
    const bestJob = this.findBestJob(processedJobs)

    // 生成分析结论
    const conclusion = this.generateConclusion(processedJobs, bestJob)

    this.setData({
      jobs: processedJobs,
      conclusion,
      bestJobId: bestJob.id
    })
  },

  findBestJob(jobs) {
    // 综合评分：匹配度占40%，上岸概率占30%，竞争比占30%
    // 竞争比越低越好，所以用(1 - ratio/max_ratio)参与计算

    const maxRatio = Math.max(...jobs.map(j => j.competition_ratio || 1))
    const maxScore = Math.max(...jobs.map(j => j.match_score || 0))
    const maxProb = Math.max(...jobs.map(j => j.pass_probability || 0))

    let bestJob = jobs[0]
    let bestScore = 0

    for (const job of jobs) {
      const ratioScore = maxRatio > 0 ? (1 - (job.competition_ratio || 0) / maxRatio) : 1
      const matchScore = maxScore > 0 ? (job.match_score || 0) / maxScore : 0
      const probScore = maxProb > 0 ? (job.pass_probability || 0) / maxProb : 0

      const compositeScore = ratioScore * 0.3 + matchScore * 0.4 + probScore * 0.3

      if (compositeScore > bestScore) {
        bestScore = compositeScore
        bestJob = job
      }
    }

    return bestJob
  },

  generateConclusion(jobs, bestJob) {
    const conclusions = []

    // 找出各项最优
    const lowestRatioJob = jobs.find(j => j.isLowestRatio)
    const highestScoreJob = jobs.find(j => j.isHighestScore)
    const highestProbJob = jobs.find(j => j.isHighestProb)
    const highestRecruitJob = jobs.find(j => j.isHighestRecruit)

    if (lowestRatioJob && lowestRatioJob.id !== bestJob.id) {
      conclusions.push(`竞争比最低的是${lowestRatioJob.unit}（${lowestRatioJob.competition_ratio}:1）`)
    }

    if (highestScoreJob && highestScoreJob.id !== bestJob.id) {
      conclusions.push(`匹配度最高的是${highestScoreJob.unit}（${highestScoreJob.match_score}分）`)
    }

    if (highestProbJob && highestProbJob.id !== bestJob.id) {
      conclusions.push(`上岸概率最高的是${highestProbJob.unit}（${(highestProbJob.pass_probability * 100).toFixed(0)}%）`)
    }

    // 综合推荐
    conclusions.unshift(`综合推荐：${bestJob.unit}（${bestJob.city}）`)

    if (bestJob.recommendation_tier === '稳妥' || bestJob.recommendation_tier === '保底') {
      conclusions.push(`该岗位为【${bestJob.recommendation_tier}】层级，整体竞争较小`)
    } else if (bestJob.recommendation_tier === '冲刺') {
      conclusions.push(`该岗位为【冲刺】层级，需要较高竞争力，请谨慎选择`)
    }

    return conclusions.join('\n\n')
  },

  goBack() {
    wx.navigateBack()
  },

  selectJob(e) {
    const { id } = e.currentTarget.dataset
    if (id) {
      wx.navigateTo({
        url: `/pages/detail/detail?id=${id}`
      })
    }
  }
})