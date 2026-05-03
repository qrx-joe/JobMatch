<template>
  <div class="filter-panel">
    <el-card class="filter-card" shadow="hover">
      <!-- 文件上传行 -->
      <el-row :gutter="16" class="file-row">
        <el-col :xs="24" :sm="12">
          <div class="upload-wrap">
            <span class="field-label">岗位表</span>
            <el-upload
              v-model:file-list="jobFileList"
              :auto-upload="false"
              :limit="1"
              accept=".xlsx,.xls"
              class="upload-inline"
            >
              <el-button type="primary" size="default">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
                选择文件
              </el-button>
            </el-upload>
            <span v-if="jobFileList.length > 0" class="file-tag">{{ jobFileList[0].name }}</span>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12">
          <div class="upload-wrap">
            <span class="field-label">统计表</span>
            <el-upload
              v-model:file-list="statsFileList"
              :auto-upload="false"
              :limit="1"
              accept=".xlsx,.xls"
              class="upload-inline"
            >
              <el-button size="default">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
                选择文件
              </el-button>
            </el-upload>
            <span v-if="statsFileList.length > 0" class="file-tag">{{ statsFileList[0].name }}</span>
          </div>
        </el-col>
      </el-row>

      <el-divider class="compact-divider" />

      <!-- 核心筛选条件 -->
      <el-form :model="form" class="core-form">
        <el-row :gutter="8" align="bottom">
          <el-col :xs="12" :sm="6" :md="4" :lg="4">
            <el-form-item label="专业">
              <el-input v-model="form.major" placeholder="如：经济学" size="default" />
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="6" :md="3" :lg="3">
            <el-form-item label="学历">
              <el-select v-model="form.education" size="default" style="width: 100%">
                <el-option label="大专" value="大专" />
                <el-option label="本科" value="本科" />
                <el-option label="研究生" value="研究生" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="6" :md="3" :lg="3">
            <el-form-item label="学位">
              <el-select v-model="form.degree" size="default" style="width: 100%">
                <el-option label="无" value="无" />
                <el-option label="学士" value="学士" />
                <el-option label="硕士" value="硕士" />
                <el-option label="博士" value="博士" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="6" :md="3" :lg="3">
            <el-form-item label="性别">
              <el-radio-group v-model="form.gender" size="small">
                <el-radio value="男">男</el-radio>
                <el-radio value="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="8" :md="4" :lg="4">
            <el-form-item label="户籍">
              <el-select v-model="form.household" size="default" style="width: 100%">
                <el-option label="不限户籍" value="不限" />
                <el-option
                  v-for="city in cities"
                  :key="city"
                  :label="city"
                  :value="city"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="12" :sm="8" :md="4" :lg="4">
            <el-form-item label="意向城市">
              <el-select
                v-model="form.target_cities"
                multiple
                collapse-tags
                size="default"
                placeholder="城市"
                style="width: 100%"
              >
                <el-option
                  v-for="city in cities"
                  :key="city"
                  :label="city"
                  :value="city"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="8" :md="3" :lg="3">
            <el-form-item>
              <el-button
                type="primary"
                size="default"
                style="width: 100%"
                :loading="loading"
                :disabled="!canSubmit"
                @click="submit"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                {{ loading ? '筛选中...' : '开始筛选' }}
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <!-- 高级筛选（折叠） -->
      <el-collapse v-model="activeCollapse" class="advanced-collapse">
        <el-collapse-item title="高级筛选" name="advanced">
          <el-form :model="form" class="advanced-form">
            <el-row :gutter="8">
              <el-col :xs="12" :sm="6" :md="3">
                <el-form-item label="政治面貌">
                  <el-select v-model="form.political_status" size="default" style="width: 100%">
                    <el-option label="群众" value="群众" />
                    <el-option label="共青团员" value="共青团员" />
                    <el-option label="中共党员" value="中共党员" />
                    <el-option label="中共预备党员" value="中共预备党员" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="6" :md="2">
                <el-form-item label="应届">
                  <el-switch v-model="form.is_fresh_graduate" />
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="6" :md="3">
                <el-form-item label="工作年限">
                  <el-input-number v-model="form.work_years" :min="0" :max="50" size="default" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="6" :md="3">
                <el-form-item label="年龄">
                  <el-input-number v-model="form.age" :min="18" :max="40" size="default" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="8" :md="4">
                <el-form-item label="资格证书">
                  <el-select
                    v-model="form.qualifications"
                    multiple
                    collapse-tags
                    size="default"
                    placeholder="证书"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="q in qualifications"
                      :key="q"
                      :label="q"
                      :value="q"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="8" :md="3">
                <el-form-item label="计算机">
                  <el-select v-model="form.computer_level" size="default" placeholder="等级" style="width: 100%">
                    <el-option label="无要求" value="" />
                    <el-option label="一级" value="一级" />
                    <el-option label="二级" value="二级" />
                    <el-option label="三级" value="三级" />
                    <el-option label="四级" value="四级" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="8" :md="3">
                <el-form-item label="英语">
                  <el-select v-model="form.english_level" size="default" placeholder="等级" style="width: 100%">
                    <el-option label="无要求" value="" />
                    <el-option label="CET-4" value="大学英语四级" />
                    <el-option label="CET-6" value="大学英语六级" />
                    <el-option label="专四" value="专业英语四级" />
                    <el-option label="专八" value="专业英语八级" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="8" :md="3">
                <el-form-item label="基层经历">
                  <el-select v-model="form.basic_experience" size="default" placeholder="项目" style="width: 100%">
                    <el-option label="无" value="" />
                    <el-option label="西部计划" value="西部计划" />
                    <el-option label="三支一扶" value="三支一扶" />
                    <el-option label="大学生村官" value="大学生村官" />
                    <el-option label="特岗教师" value="特岗教师" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="8" class="match-rule-row">
              <el-col :xs="12" :sm="6" :md="4">
                <el-form-item>
                  <template #label>
                    性别限制
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="help-icon"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
                  </template>
                  <el-radio-group v-model="form.gender_strict" size="small">
                    <el-radio :value="true">严格</el-radio>
                    <el-radio :value="false">宽松</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="6" :md="4">
                <el-form-item>
                  <template #label>
                    户籍限制
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="help-icon"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
                  </template>
                  <el-radio-group v-model="form.household_strict" size="small">
                    <el-radio :value="true">严格</el-radio>
                    <el-radio :value="false">宽松</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCities, getQualifications } from '../services/api'

const PROFILE_KEY = 'jobmatch_profile'

const props = defineProps({
  loading: Boolean
})

const emit = defineEmits(['filter', 'clear'])

const jobFileList = ref([])
const statsFileList = ref([])
const cities = ref([])
const qualifications = ref([])
const activeCollapse = ref([])

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

  localStorage.removeItem(PROFILE_KEY)
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
.filter-card {
  border-radius: 6px;
  border: 1px solid #D8DEE7;
  margin-bottom: 16px;
}

.filter-card :deep(.el-card__body) {
  padding: 16px 20px 12px;
}

.file-row {
  margin-bottom: 4px;
}

.upload-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: #1B3A5F;
  white-space: nowrap;
}

.file-tag {
  font-size: 12px;
  color: #2E7D32;
  background: #E8F5E9;
  padding: 2px 8px;
  border-radius: 4px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.compact-divider {
  margin: 12px 0;
}

.core-form :deep(.el-form-item__label) {
  font-size: 12px;
  font-weight: 500;
  color: #5A6978;
  padding-bottom: 4px;
  line-height: 1.2;
}

.core-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.advanced-collapse {
  margin-top: 8px;
}

.advanced-collapse :deep(.el-collapse-item__header) {
  font-size: 13px;
  font-weight: 500;
  color: #4A6FA5;
  height: 32px;
  line-height: 32px;
  border: none;
}

.advanced-collapse :deep(.el-collapse-item__arrow) {
  margin: 0 6px 0 0;
}

.advanced-collapse :deep(.el-collapse-item__wrap) {
  border: none;
}

.advanced-collapse :deep(.el-collapse-item__content) {
  padding-bottom: 8px;
}

.advanced-form :deep(.el-form-item__label) {
  font-size: 12px;
  font-weight: 500;
  color: #5A6978;
  padding-bottom: 4px;
  line-height: 1.2;
}

.advanced-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.match-rule-row {
  margin-top: 8px;
}

.help-icon {
  color: #5A6978;
  cursor: help;
  margin-left: 4px;
  vertical-align: middle;
}

/* 隐藏 el-upload 默认文件列表 */
:deep(.el-upload-list) {
  display: none;
}

:deep(.el-upload) {
  display: inline-block;
}
</style>
