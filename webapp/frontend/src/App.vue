<template>
  <div class="app">
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-content">
          <h1><el-icon><OfficeBuilding /></el-icon> 三支一扶岗位筛选系统</h1>
          <p>智能匹配 · 精准筛选 · 高效选岗</p>
        </div>
      </el-header>

      <el-main class="main">
        <el-row :gutter="20">
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
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
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
    const response = await axios.post(`${API_BASE}/upload-and-filter`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    jobs.value = response.data.jobs
    stats.value = {
      total: response.data.total,
      perfect: response.data.perfect,
      partial: response.data.partial,
      mismatch: response.data.mismatch
    }
    excelBase64.value = response.data.excel_base64
    excelFilename.value = response.data.excel_filename

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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

.header-content h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.header-content p {
  color: #666;
  font-size: 14px;
}

.main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}
</style>
