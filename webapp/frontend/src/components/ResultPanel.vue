<template>
  <div class="result-panel">
    <!-- 统计卡片 -->
    <el-card class="stats-card" shadow="never" v-if="hasJobs">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-statistic title="总岗位数" :value="stats.total">
            <template #prefix>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="完全符合" :value="stats.perfect" value-style="color: #2E7D32">
            <template #prefix>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="可能符合" :value="stats.partial" value-style="color: #B8860B">
            <template #prefix>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="不符合" :value="stats.mismatch" value-style="color: #C41E3A">
            <template #prefix>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="toolbar-card" shadow="never" v-if="hasJobs">
      <el-row :gutter="12" align="middle">
        <el-col :span="6">
          <el-input
            v-model="searchText"
            placeholder="搜索单位或岗位"
            clearable
            size="default"
          >
            <template #prefix>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            </template>
          </el-input>
        </el-col>
        <el-col :span="5">
          <el-select
            v-model="filterCities"
            multiple
            collapse-tags
            size="default"
            placeholder="筛选城市"
            style="width: 100%"
          >
            <el-option
              v-for="city in availableCities"
              :key="city"
              :label="city"
              :value="city"
            />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-checkbox-group v-model="filterLevels">
            <el-checkbox value="完全符合">
              <el-tag type="success" size="small">完全符合</el-tag>
            </el-checkbox>
            <el-checkbox value="可能符合">
              <el-tag type="warning" size="small">可能符合</el-tag>
            </el-checkbox>
            <el-checkbox value="不符合">
              <el-tag type="danger" size="small">不符合</el-tag>
            </el-checkbox>
          </el-checkbox-group>
        </el-col>
        <el-col :span="5" style="text-align: right">
          <el-button type="success" @click="$emit('download')" :disabled="!filteredJobs.length">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
            下载Excel
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 岗位列表 -->
    <el-card class="jobs-card" shadow="never" v-loading="loading">
      <el-table
        v-if="hasJobs && paginatedJobs.length"
        :data="paginatedJobs"
        style="width: 100%"
        stripe
        highlight-current-row
        @row-click="handleRowClick"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="job-detail">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="服务单位">{{ row.unit }}</el-descriptions-item>
                <el-descriptions-item label="岗位类型">{{ row.job_type }}</el-descriptions-item>
                <el-descriptions-item label="服务类别">{{ row.service_category }}</el-descriptions-item>
                <el-descriptions-item label="招募人数">{{ row.recruit_count }}人</el-descriptions-item>
                <el-descriptions-item label="学历要求">{{ row.education }}</el-descriptions-item>
                <el-descriptions-item label="学位要求">{{ row.degree }}</el-descriptions-item>
                <el-descriptions-item label="专业要求" :span="2">{{ row.major }}</el-descriptions-item>
                <el-descriptions-item label="相关资格" :span="2">{{ row.qualifications || '无' }}</el-descriptions-item>
                <el-descriptions-item label="其他要求" :span="2">{{ row.other || '无' }}</el-descriptions-item>
                <el-descriptions-item label="联系电话">{{ row.phone || '无' }}</el-descriptions-item>
                <el-descriptions-item label="竞争比">
                  <el-tag :type="getRatioType(row.competition_ratio)">
                    {{ row.competition_ratio ? row.competition_ratio + ':1' : '暂无' }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <div class="match-info" v-if="row.match_reasons.length">
                <h4>匹配说明：</h4>
                <el-tag
                  v-for="reason in row.match_reasons"
                  :key="reason"
                  type="success"
                  effect="plain"
                  class="match-tag"
                >{{ reason }}</el-tag>
              </div>

              <div class="partial-info" v-if="row.partial_reasons && row.partial_reasons.length">
                <h4>注意事项：</h4>
                <el-tag
                  v-for="reason in row.partial_reasons"
                  :key="reason"
                  type="warning"
                  effect="plain"
                  class="match-tag"
                >{{ reason }}</el-tag>
              </div>

              <div class="mismatch-info" v-if="row.mismatch_reasons.length">
                <h4>不匹配原因：</h4>
                <el-tag
                  v-for="reason in row.mismatch_reasons"
                  :key="reason"
                  type="danger"
                  effect="plain"
                  class="match-tag"
                >{{ reason }}</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="匹配度" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getMatchType(row.match_level)" effect="dark">
              {{ row.match_level }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="地市" width="100" prop="sheet_name" sortable />

        <el-table-column label="服务单位" min-width="200">
          <template #default="{ row }">
            <div class="unit-cell">
              <span class="unit-name">{{ row.unit || row.department || '未知单位' }}</span>
              <el-tag v-if="row.recruit_count > 1" type="info" size="small">
                招{{ row.recruit_count }}人
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="岗位类型" width="120" prop="job_type" />

        <el-table-column label="专业要求" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.major || '不限' }}
          </template>
        </el-table-column>

        <el-table-column label="学历要求" width="100">
          <template #default="{ row }">
            {{ row.education || '不限' }}
          </template>
        </el-table-column>

        <el-table-column label="竞争比" width="100" align="center" sortable>
          <template #default="{ row }">
            <span :class="getRatioClass(row.competition_ratio)">
              {{ row.competition_ratio ? row.competition_ratio + ':1' : '-' }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="缴费人数" width="100" align="center">
          <template #default="{ row }">
            {{ row.paid || '-' }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="hasJobs && filteredJobs.length > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredJobs.length"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
      />

      <!-- 空状态：从未筛选 -->
      <el-empty v-if="!hasJobs && !loading">
        <template #description>
          <div class="empty-desc">
            <p class="empty-title">还没有筛选结果</p>
            <p class="empty-tip">在上方上传岗位表并设置筛选条件</p>
          </div>
        </template>
      </el-empty>

      <!-- 空状态：被过滤筛光 -->
      <div v-if="hasJobs && !paginatedJobs.length && !loading" class="empty-filtered">
        <el-empty description="当前筛选条件下无岗位" />
        <div class="empty-suggestions">
          <p>尝试以下操作：</p>
          <ul>
            <li>勾选更多匹配级别（如"不符合"）</li>
            <li>扩大城市选择范围</li>
            <li>清空搜索关键词</li>
          </ul>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  jobs: Array,
  stats: Object,
  loading: Boolean
})

const emit = defineEmits(['download'])

const searchText = ref('')
const filterLevels = ref(['完全符合', '可能符合', '不符合'])
const filterCities = ref([])
const currentPage = ref(1)
const pageSize = ref(20)

const hasJobs = computed(() => props.jobs && props.jobs.length > 0)

const availableCities = computed(() => {
  const cities = new Set(props.jobs.map(job => job.sheet_name).filter(Boolean))
  return Array.from(cities).sort()
})

watch(availableCities, (cities) => {
  // 当数据变化时，默认全选所有城市
  filterCities.value = [...cities]
}, { immediate: true })

const filteredJobs = computed(() => {
  let result = props.jobs

  // 按匹配度筛选
  if (filterLevels.value.length > 0) {
    result = result.filter(job => filterLevels.value.includes(job.match_level))
  }

  // 按城市筛选
  if (filterCities.value.length > 0) {
    result = result.filter(job => filterCities.value.includes(job.sheet_name))
  }

  // 按搜索词筛选
  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    result = result.filter(job =>
      job.unit.toLowerCase().includes(keyword) ||
      job.job_type.toLowerCase().includes(keyword)
    )
  }

  return result
})

const paginatedJobs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredJobs.value.slice(start, end)
})

const getMatchType = (level) => {
  const map = {
    '完全符合': 'success',
    '可能符合': 'warning',
    '不符合': 'danger'
  }
  return map[level] || 'info'
}

const getRatioType = (ratio) => {
  if (!ratio || ratio === 0) return 'info'
  if (ratio < 30) return 'success'
  if (ratio < 100) return 'warning'
  return 'danger'
}

const getRatioClass = (ratio) => {
  if (!ratio || ratio === 0) return ''
  if (ratio < 30) return 'ratio-low'
  if (ratio < 100) return 'ratio-medium'
  return 'ratio-high'
}

const handleRowClick = (row) => {
  // 可以在这里添加点击行的逻辑
}
</script>

<style scoped>
.result-panel {
  padding-top: 0;
  padding-bottom: 40px;
}

.stats-card {
  margin-bottom: 16px;
  border-radius: 6px;
  border: 1px solid #D8DEE7;
}

.stats-card :deep(.el-card__body) {
  padding: 16px 20px;
}

.stats-card :deep(.el-col) {
  text-align: center;
}

.stats-card :deep(.el-statistic__head) {
  color: #5A6978;
  font-size: 13px;
}

.stats-card :deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: 600;
}

.stats-card :deep(.el-statistic__prefix) {
  display: inline-flex;
  align-items: center;
  margin-right: 6px;
}

.stats-card :deep(.el-statistic__prefix svg) {
  color: #4A6FA5;
}

.toolbar-card {
  margin-bottom: 16px;
  border-radius: 6px;
  border: 1px solid #D8DEE7;
}

.jobs-card {
  min-height: 400px;
  border-radius: 6px;
  border: 1px solid #D8DEE7;
}

.unit-cell {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.unit-name {
  font-weight: 500;
}

.ratio-low { color: #2E7D32; font-weight: 600; }
.ratio-medium { color: #B8860B; font-weight: 600; }
.ratio-high { color: #C41E3A; font-weight: 600; }

.job-detail {
  padding: 20px;
  background: #F5F7FA;
  border-radius: 6px;
}

.match-info, .mismatch-info, .partial-info {
  margin-top: 15px;
}

.match-info h4, .mismatch-info h4, .partial-info h4 {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
}

.match-tag {
  margin: 5px 5px 5px 0;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}

:deep(.el-table) {
  --el-table-border-color: #D8DEE7;
  --el-table-header-bg-color: #F5F7FA;
  --el-table-header-text-color: #1B3A5F;
}

:deep(.el-button--success) {
  --el-button-bg-color: #2E7D32;
  --el-button-border-color: #2E7D32;
}

.empty-desc {
  text-align: center;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #1B3A5F;
  margin: 0 0 6px;
}

.empty-tip {
  font-size: 13px;
  color: #5A6978;
  margin: 0;
}

.empty-filtered {
  text-align: center;
  padding: 20px 0 40px;
}

.empty-suggestions {
  display: inline-block;
  text-align: left;
  background: #F5F7FA;
  border-radius: 6px;
  padding: 16px 24px;
  margin-top: 10px;
}

.empty-suggestions p {
  font-size: 14px;
  font-weight: 600;
  color: #1B3A5F;
  margin: 0 0 10px;
}

.empty-suggestions ul {
  margin: 0;
  padding-left: 18px;
  color: #5A6978;
  font-size: 13px;
  line-height: 1.8;
}
</style>
