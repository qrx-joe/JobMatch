<template>
  <div class="filter-panel">
    <el-card class="filter-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
          <span>筛选条件设置</span>
        </div>
      </template>

      <el-form :model="form" label-position="top" size="large">
        <!-- 文件上传 -->
        <el-form-item label="岗位表文件 (Excel)">
          <el-upload
            v-model:file-list="jobFileList"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            class="upload-demo"
          >
            <el-button type="primary">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
              选择文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">支持 .xlsx 和 .xls 格式</div>
            </template>
          </el-upload>
          <div v-if="jobFileList.length > 0" class="file-selected">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
            <span class="file-name">{{ jobFileList[0].name }}</span>
            <span class="file-size" v-if="jobFileList[0].size">{{ (jobFileList[0].size / 1024).toFixed(1) }} KB</span>
          </div>
        </el-form-item>

        <el-form-item label="统计表文件 (可选)">
          <el-upload
            v-model:file-list="statsFileList"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            class="upload-demo"
          >
            <el-button>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
              选择文件
            </el-button>
          </el-upload>
          <div v-if="statsFileList.length > 0" class="file-selected">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
            <span class="file-name">{{ statsFileList[0].name }}</span>
            <span class="file-size" v-if="statsFileList[0].size">{{ (statsFileList[0].size / 1024).toFixed(1) }} KB</span>
          </div>
        </el-form-item>

        <el-divider />

        <!-- 基本信息 -->
        <h4 class="section-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          个人信息
        </h4>

        <el-form-item label="专业">
          <el-input v-model="form.major" placeholder="如：经济学" />
        </el-form-item>

        <el-form-item label="学历">
          <el-select v-model="form.education" style="width: 100%">
            <el-option label="大专" value="大专" />
            <el-option label="本科" value="本科" />
            <el-option label="研究生" value="研究生" />
          </el-select>
        </el-form-item>

        <el-form-item label="学位">
          <el-select v-model="form.degree" style="width: 100%">
            <el-option label="无" value="无" />
            <el-option label="学士" value="学士" />
            <el-option label="硕士" value="硕士" />
            <el-option label="博士" value="博士" />
          </el-select>
        </el-form-item>

        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="户籍">
          <el-select v-model="form.household" style="width: 100%">
            <el-option label="不限户籍" value="不限" />
            <el-option
              v-for="city in cities"
              :key="city"
              :label="city"
              :value="city"
            />
          </el-select>
        </el-form-item>

        <el-divider />

        <!-- 高级选项 -->
        <h4 class="section-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
          高级选项
        </h4>

        <el-form-item label="政治面貌">
          <el-select v-model="form.political_status" style="width: 100%">
            <el-option label="群众" value="群众" />
            <el-option label="共青团员" value="共青团员" />
            <el-option label="中共党员" value="中共党员" />
            <el-option label="中共预备党员" value="中共预备党员" />
          </el-select>
        </el-form-item>

        <el-form-item label="是否应届毕业生">
          <el-switch v-model="form.is_fresh_graduate" />
        </el-form-item>

        <el-form-item label="工作年限">
          <el-input-number v-model="form.work_years" :min="0" :max="50" style="width: 100%" />
        </el-form-item>

        <el-form-item label="年龄">
          <el-input-number v-model="form.age" :min="18" :max="40" style="width: 100%" />
        </el-form-item>

        <el-form-item label="相关资格证书">
          <el-select
            v-model="form.qualifications"
            multiple
            collapse-tags
            style="width: 100%"
            placeholder="选择你拥有的证书"
          >
            <el-option
              v-for="q in qualifications"
              :key="q"
              :label="q"
              :value="q"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="计算机等级">
          <el-select v-model="form.computer_level" style="width: 100%" placeholder="选择计算机等级">
            <el-option label="无要求" value="" />
            <el-option label="一级" value="一级" />
            <el-option label="二级" value="二级" />
            <el-option label="三级" value="三级" />
            <el-option label="四级" value="四级" />
          </el-select>
        </el-form-item>

        <el-form-item label="英语等级">
          <el-select v-model="form.english_level" style="width: 100%" placeholder="选择英语等级">
            <el-option label="无要求" value="" />
            <el-option label="大学英语四级" value="大学英语四级" />
            <el-option label="大学英语六级" value="大学英语六级" />
            <el-option label="专业英语四级" value="专业英语四级" />
            <el-option label="专业英语八级" value="专业英语八级" />
          </el-select>
        </el-form-item>

        <el-form-item label="服务基层项目经历">
          <el-select v-model="form.basic_experience" style="width: 100%" placeholder="选择服务基层项目">
            <el-option label="无" value="" />
            <el-option label="大学生志愿服务西部计划" value="西部计划" />
            <el-option label="三支一扶" value="三支一扶" />
            <el-option label="大学生村官" value="大学生村官" />
            <el-option label="特岗教师" value="特岗教师" />
          </el-select>
        </el-form-item>

        <el-form-item label="意向城市">
          <el-select
            v-model="form.target_cities"
            multiple
            collapse-tags
            style="width: 100%"
            placeholder="只显示选中城市的岗位"
          >
            <el-option
              v-for="city in cities"
              :key="city"
              :label="city"
              :value="city"
            />
          </el-select>
        </el-form-item>

        <el-divider />

        <!-- 匹配规则 -->
        <h4 class="section-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="4" y1="21" y2="14"/><line x1="4" x2="4" y1="10" y2="3"/><line x1="12" x2="12" y1="21" y2="12"/><line x1="12" x2="12" y1="8" y2="3"/><line x1="20" x2="20" y1="21" y2="16"/><line x1="20" x2="20" y1="12" y2="3"/><line x1="2" x2="6" y1="14" y2="14"/><line x1="10" x2="14" y1="8" y2="8"/><line x1="18" x2="22" y1="16" y2="16"/></svg>
          匹配规则
        </h4>

        <el-form-item>
          <template #label>
            性别限制
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="help-icon"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
          </template>
          <el-radio-group v-model="form.gender_strict">
            <el-radio :value="true">严格</el-radio>
            <el-radio :value="false">宽松</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <template #label>
            户籍限制
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="help-icon"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
          </template>
          <el-radio-group v-model="form.household_strict">
            <el-radio :value="true">严格</el-radio>
            <el-radio :value="false">宽松</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 开始筛选按钮 -->
        <el-button
          type="primary"
          size="large"
          style="width: 100%; margin-top: 20px"
          :loading="loading"
          :disabled="!canSubmit"
          @click="submit"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          {{ loading ? '筛选中...' : '开始筛选' }}
        </el-button>

        <el-button
          size="small"
          text
          style="width: 100%; margin-top: 8px"
          @click="clearCache"
        >
          清除缓存并重置
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCities, getQualifications } from '../services/api'

const PROFILE_KEY = 'jobmatch_profile'

const API_BASE = import.meta.env.DEV ? '/api' : ''

const props = defineProps({
  loading: Boolean
})

const emit = defineEmits(['filter', 'clear'])

const jobFileList = ref([])
const statsFileList = ref([])
const cities = ref([])
const qualifications = ref([])

function createDefaultForm() {
  return {
    major: '经济学',
    education: '本科',
    degree: '学士',
    gender: '女',
    household: '吕梁市',
    age: 25,
    is_fresh_graduate: false,
    political_status: '群众',
    qualifications: [],
    computer_level: '',
    english_level: '',
    basic_experience: '',
    work_years: 0,
    target_cities: ['吕梁市', '太原市'],
    gender_strict: true,
    household_strict: false
  }
}

const form = reactive(createDefaultForm())

function saveProfile() {
  try {
    localStorage.setItem(PROFILE_KEY, JSON.stringify(form))
  } catch (e) {
    // 静默失败
  }
}

function loadProfile() {
  try {
    const raw = localStorage.getItem(PROFILE_KEY)
    if (!raw) return
    const data = JSON.parse(raw)
    Object.assign(form, data)
  } catch (e) {
    // 解析失败就忽略
  }
}

async function clearCache() {
  try {
    await ElMessageBox.confirm(
      '这将清除所有缓存的个人信息和筛选结果，确定继续吗？',
      '清除缓存',
      { confirmButtonText: '确定清除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  const before = localStorage.getItem(PROFILE_KEY)
  console.log('[清除前] localStorage:', before)

  localStorage.removeItem(PROFILE_KEY)

  const after = localStorage.getItem(PROFILE_KEY)
  console.log('[清除后] localStorage:', after)

  emit('clear')
  ElMessage.success('已清除，页面即将刷新...')

  setTimeout(() => {
    window.location.reload()
  }, 800)
}

const canSubmit = computed(() => {
  return jobFileList.value.length > 0 && form.major && form.education
})

onMounted(async () => {
  loadProfile()
  try {
    const [citiesRes, qualRes] = await Promise.all([
      getCities(),
      getQualifications()
    ])
    cities.value = citiesRes.cities
    qualifications.value = qualRes.qualifications
  } catch (e) {
    // 使用默认值
    cities.value = ['太原市', '大同市', '朔州市', '忻州市', '吕梁市', '晋中市', '阳泉市', '长治市', '晋城市', '临汾市', '运城市']
    qualifications.value = ['教师资格证', '法律职业资格证书', '医师资格证', '护士资格证', '会计证', '注册会计师', '建造师证']
  }
})

const submit = () => {
  const formData = new FormData()

  // 添加文件
  if (jobFileList.value[0]) {
    formData.append('job_file', jobFileList.value[0].raw)
  }
  if (statsFileList.value[0]) {
    formData.append('stats_file', statsFileList.value[0].raw)
  }

  // 添加表单数据
  formData.append('major', form.major)
  formData.append('education', form.education)
  formData.append('degree', form.degree)
  formData.append('gender', form.gender)
  formData.append('household', form.household)
  formData.append('age', form.age)
  formData.append('is_fresh_graduate', form.is_fresh_graduate)
  formData.append('political_status', form.political_status)
  formData.append('qualifications', form.qualifications.join(','))
  formData.append('computer_level', form.computer_level)
  formData.append('english_level', form.english_level)
  formData.append('basic_experience', form.basic_experience)
  formData.append('work_years', form.work_years)
  formData.append('target_cities', form.target_cities.join(','))
  formData.append('gender_strict', form.gender_strict)
  formData.append('household_strict', form.household_strict)

  saveProfile()
  emit('filter', formData, {
    jobFileName: jobFileList.value[0]?.name || ''
  })
}
</script>

<style scoped>
.filter-panel {
  /* 移除sticky，避免遮挡其他内容 */
}

.filter-card {
  border-radius: 6px;
  border: 1px solid #D8DEE7;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1B3A5F;
}

.card-header svg {
  color: #4A6FA5;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1B3A5F;
  margin: 20px 0 15px;
  font-size: 14px;
  font-weight: 600;
}

.section-title svg {
  color: #4A6FA5;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #1A1A2E;
}

:deep(.el-divider) {
  margin: 20px 0;
  border-color: #D8DEE7;
}

.help-icon {
  color: #5A6978;
  cursor: help;
  margin-left: 4px;
  vertical-align: middle;
}

/* 隐藏 el-upload 默认文件列表，用自己样式替代 */
:deep(.el-upload-list) {
  display: none;
}

.file-selected {
  margin-top: 4px;
  padding-left: 2px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  line-height: 1.5;
}

.file-selected svg {
  color: #2E7D32;
  flex-shrink: 0;
}

.file-name {
  color: #1B3A5F;
  font-weight: 500;
}

.file-size {
  color: #8A96A8;
  font-size: 12px;
}
</style>
