<template>
  <div class="app">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-content">
        <h1>
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          岗位筛选系统
        </h1>
        <p>智能匹配 · 精准筛选 · 高效选岗</p>
      </div>
    </header>

    <main class="main">
      <el-row :gutter="16">
        <!-- 左侧：条件设置 -->
        <el-col :xs="24" :sm="24" :md="8" :lg="6">
          <FilterPanel
            @filter="handleFilter"
            :loading="loading"
          />
        </el-col>

        <!-- 右侧：结果展示 -->
        <el-col :xs="24" :sm="24" :md="16" :lg="18">
          <ResultPanel
            :jobs="filteredJobs"
            :stats="stats"
            :loading="loading"
            @download="handleDownload"
          />
        </el-col>
      </el-row>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import * as XLSX from 'xlsx'
import { uploadAndFilter } from './services/api'
import FilterPanel from './components/FilterPanel.vue'
import ResultPanel from './components/ResultPanel.vue'

const jobs = ref([])
const stats = ref({})
const loading = ref(false)

const filteredJobs = computed(() => {
  return jobs.value
})

const handleFilter = async (formData) => {
  loading.value = true
  try {
    const response = await uploadAndFilter(formData)

    jobs.value = response.jobs
    stats.value = {
      total: response.total,
      perfect: response.perfect,
      partial: response.partial,
      mismatch: response.mismatch
    }

  } catch (error) {
    console.error('筛选失败:', error)
    const detail = error?.message || String(error)
    alert(`筛选失败：${detail}`)
  } finally {
    loading.value = false
  }
}

const handleDownload = () => {
  if (!jobs.value.length) return

  const exportData = jobs.value.map(job => {
    const base = {
      '序号': job.index,
      '服务单位': job.unit,
      '岗位类型': job.job_type,
      '服务类别': job.service_category,
      '招募人数': job.recruit_count,
      '学历要求': job.education,
      '学位要求': job.degree,
      '专业要求': job.major,
      '相关资格': job.qualifications,
      '其他要求': job.other,
      '联系电话': job.phone,
      '匹配结果': job.match_level,
      '匹配说明': job.match_reasons.join('；'),
      '不匹配原因': job.mismatch_reasons.join('；'),
      '注意事项': job.partial_reasons ? job.partial_reasons.join('；') : ''
    }
    if (job.hasStats) {
      base['报名人数'] = job.applicants
      base['初审通过'] = job.approved
      base['缴费人数'] = job.paid
      base['竞争比'] = job.competition_ratio ? job.competition_ratio + ':1' : '-'
    }
    return base
  })

  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '筛选结果')
  XLSX.writeFile(wb, `筛选结果_${new Date().toISOString().slice(0, 10)}.xlsx`)
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #EEF2F7;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #D8DEE7;
  width: 100%;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  box-sizing: border-box;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1B3A5F;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.header-content h1 svg {
  color: #4A6FA5;
}

.header-content p {
  color: #5A6978;
  font-size: 14px;
  margin: 0;
}

.main {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}
</style>
