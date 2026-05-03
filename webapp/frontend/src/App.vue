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
      <!-- 全屏解析遮罩 -->
      <div v-if="parsing" class="parsing-overlay">
        <div class="parsing-box">
          <div class="spinner"></div>
          <p class="parsing-text">{{ parsingText }}</p>
          <p class="parsing-sub">大文件解析可能需要几秒，请稍候</p>
        </div>
      </div>

      <FilterPanel
        :key="filterKey"
        @filter="handleFilter"
        @clear="handleClear"
        :loading="loading"
      />

      <ResultPanel
        :jobs="filteredJobs"
        :stats="stats"
        :loading="loading"
        @download="handleDownload"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'
import { uploadAndFilter } from './services/api'
import FilterPanel from './components/FilterPanel.vue'
import ResultPanel from './components/ResultPanel.vue'

const RESULT_KEY = 'jobmatch_result'
const CACHE_DAYS = 7

const jobs = ref([])
const stats = ref({})
const loading = ref(false)
const parsing = ref(false)
const parsingText = ref('正在解析...')

const filteredJobs = computed(() => {
  return jobs.value
})

function saveResult(jobs, stats) {
  const payload = {
    jobs,
    stats,
    timestamp: Date.now()
  }
  try {
    localStorage.setItem(RESULT_KEY, JSON.stringify(payload))
  } catch (e) {
    // localStorage 满或不可用，静默失败
  }
}

function loadResult() {
  try {
    const raw = localStorage.getItem(RESULT_KEY)
    if (!raw) return null
    const data = JSON.parse(raw)
    const age = Date.now() - (data.timestamp || 0)
    const maxAge = CACHE_DAYS * 24 * 60 * 60 * 1000
    if (age > maxAge) {
      localStorage.removeItem(RESULT_KEY)
      return null
    }
    return data
  } catch (e) {
    return null
  }
}

function clearResultCache() {
  localStorage.removeItem(RESULT_KEY)
  jobs.value = []
  stats.value = {}
}

onMounted(() => {
  const cached = loadResult()
  if (cached) {
    jobs.value = cached.jobs || []
    stats.value = cached.stats || {}
  }
})

const currentFileName = ref('')

const handleFilter = async (formData, fileInfo = {}) => {
  loading.value = true
  parsing.value = true
  currentFileName.value = fileInfo.jobFileName || ''
  parsingText.value = currentFileName.value
    ? `正在解析：${currentFileName.value}`
    : '正在读取Excel文件...'

  // 给UI一个渲染机会，再开始阻塞解析
  await new Promise(resolve => setTimeout(resolve, 50))

  try {
    parsingText.value = '正在匹配岗位...'
    const response = await uploadAndFilter(formData)

    jobs.value = response.jobs
    stats.value = {
      total: response.total,
      perfect: response.perfect,
      partial: response.partial,
      mismatch: response.mismatch
    }

    saveResult(jobs.value, stats.value)

    const summary = `筛选完成：共${response.total}个岗位，完全符合${response.perfect}个，可能符合${response.partial}个`
    ElMessage.success({ message: summary, duration: 4000 })

  } catch (error) {
    console.error('筛选失败:', error)
    const detail = error?.message || String(error)

    let friendlyMsg = detail
    if (detail.includes('无法识别') || detail.includes('表头')) {
      friendlyMsg = '无法识别Excel文件的表头，请检查文件格式是否包含岗位名称、单位名称等必要列'
    } else if (detail.includes('请选择')) {
      friendlyMsg = detail
    } else if (detail.includes('format') || detail.includes('格式')) {
      friendlyMsg = '文件格式不支持，请上传 .xlsx 或 .xls 格式的Excel文件'
    }

    ElMessage.error({ message: friendlyMsg, duration: 6000, showClose: true })
  } finally {
    loading.value = false
    parsing.value = false
    currentFileName.value = ''
  }
}

const filterKey = ref(0)

function handleClear() {
  localStorage.removeItem(RESULT_KEY)
  jobs.value = []
  stats.value = {}
  filterKey.value++
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
  position: relative;
}

.parsing-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.parsing-box {
  text-align: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 3px solid #E0E6F0;
  border-top-color: #4A6FA5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.parsing-text {
  font-size: 18px;
  font-weight: 600;
  color: #1B3A5F;
  margin: 0 0 8px;
}

.parsing-sub {
  font-size: 13px;
  color: #5A6978;
  margin: 0;
}
</style>
