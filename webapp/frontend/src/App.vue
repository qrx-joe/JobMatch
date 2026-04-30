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
import { uploadAndFilter } from './services/api'
import FilterPanel from './components/FilterPanel.vue'
import ResultPanel from './components/ResultPanel.vue'

const API_BASE = import.meta.env.DEV ? '/api' : ''

const jobs = ref([])
const stats = ref({})
const loading = ref(false)
const excelBase64 = ref('')
const excelFilename = ref('')

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
    excelBase64.value = response.excel_base64
    excelFilename.value = response.excel_filename

  } catch (error) {
    console.error('筛选失败:', error)
    alert('筛选失败，请检查文件格式是否正确')
  } finally {
    loading.value = false
  }
}

const handleDownload = () => {
  if (!excelBase64.value) return

  const link = document.createElement('a')
  link.href = `data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,${excelBase64.value}`
  link.download = excelFilename.value
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
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
