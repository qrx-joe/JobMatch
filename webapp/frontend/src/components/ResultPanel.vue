<template>
  <div class="result-panel">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-statistic title="总岗位数" :value="stats.total">
          <template #prefix><el-icon><OfficeBuilding /></el-icon></template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="完全符合" :value="stats.perfect" value-style="color: #67c23a">
          <template #prefix><el-icon><CircleCheck /></el-icon></template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="可能符合" :value="stats.partial" value-style="color: #e6a23c">
          <template #prefix><el-icon><Warning /></el-icon></template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="不符合" :value="stats.mismatch" value-style="color: #f56c6c">
          <template #prefix><el-icon><CircleClose /></el-icon></template>
        </el-statistic>
      </el-col>
    </el-row>

    <!-- 操作栏 -->
    <el-card class="toolbar-card" shadow="never">
      <el-row :gutter="20" align="middle">
        <el-col :span="8">
          <el-input
            v-model="searchText"
            placeholder="搜索单位或岗位"
            clearable
            prefix-icon="Search"
          />
        </el-col>
        <el-col :span="10">
          <el-checkbox-group v-model="filterLevels">
            <el-checkbox label="完全符合">
              <el-tag type="success" size="small">完全符合</el-tag>
            </el-checkbox>
            <el-checkbox label="可能符合">
              <el-tag type="warning" size="small">可能符合</el-tag>
            </el-checkbox>
            <el-checkbox label="不符合">
              <el-tag type="danger" size="small">不符合</el-tag>
            </el-checkbox>
          </el-checkbox-group>
        </el-col>
        <el-col :span="6" style="text-align: right">
          <el-button type="success" @click="$emit('download')" :disabled="!jobs.length">
            <el-icon><Download /></el-icon>下载Excel
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 岗位列表 -->
    <el-card class="jobs-card" shadow="never" v-loading="loading">
      <el-table
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
              <span class="unit-name">{{ row.unit }}</span>
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
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredJobs.length"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
      />

      <!-- 空状态 -->
      <el-empty v-if="!jobs.length && !loading" description="请先上传文件并开始筛选" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  jobs: Array,
  stats: Object,
  loading: Boolean
})

const emit = defineEmits(['download'])

const searchText = ref('')
const filterLevels = ref(['完全符合', '可能符合'])
const currentPage = ref(1)
const pageSize = ref(20)

const filteredJobs = computed(() => {
  let result = props.jobs

  // 按匹配度筛选
  if (filterLevels.value.length > 0) {
    result = result.filter(job => filterLevels.value.includes(job.match_level))
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
  padding-bottom: 40px;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-row :deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: bold;
}

.toolbar-card {
  margin-bottom: 20px;
}

.jobs-card {
  min-height: 400px;
}

.unit-cell {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.unit-name {
  font-weight: 500;
}

.ratio-low { color: #67c23a; font-weight: bold; }
.ratio-medium { color: #e6a23c; font-weight: bold; }
.ratio-high { color: #f56c6c; font-weight: bold; }

.job-detail {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.match-info, .mismatch-info {
  margin-top: 15px;
}

.match-info h4, .mismatch-info h4 {
  margin-bottom: 10px;
  font-size: 14px;
}

.match-tag {
  margin: 5px 5px 5px 0;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>
