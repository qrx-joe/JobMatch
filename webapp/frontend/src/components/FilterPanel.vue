<template>
  <div class="filter-panel">
    <el-card class="filter-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Filter /></el-icon>
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
              <el-icon><Upload /></el-icon>选择文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">支持 .xlsx 和 .xls 格式</div>
            </template>
          </el-upload>
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
              <el-icon><Upload /></el-icon>选择文件
            </el-button>
          </el-upload>
        </el-form-item>

        <el-divider />

        <!-- 基本信息 -->
        <h4 class="section-title">
          <el-icon><User /></el-icon> 个人信息
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
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="户籍">
          <el-select v-model="form.household" style="width: 100%">
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
          <el-icon><Setting /></el-icon> 高级选项
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

        <el-form-item label="意向城市">
          <el-select
            v-model="form.target_cities"
            multiple
            collapse-tags
            style="width: 100%"
            placeholder="优先显示这些城市的岗位"
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
          <el-icon><Tools /></el-icon> 匹配规则
        </h4>

        <el-form-item>
          <template #label>
            性别限制
            <el-tooltip content="严格=排除限异性岗位，宽松=显示但标记">
              <el-icon><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
          <el-radio-group v-model="form.gender_strict">
            <el-radio :label="true">严格</el-radio>
            <el-radio :label="false">宽松</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <template #label>
            户籍限制
            <el-tooltip content="严格=只报不限或限本户籍，宽松=显示但标记">
              <el-icon><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
          <el-radio-group v-model="form.household_strict">
            <el-radio :label="true">严格</el-radio>
            <el-radio :label="false">宽松</el-radio>
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
          <el-icon><Search /></el-icon>
          {{ loading ? '筛选中...' : '开始筛选' }}
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getCities, getQualifications } from '../services/api'

const API_BASE = import.meta.env.DEV ? '/api' : ''

const props = defineProps({
  loading: Boolean
})

const emit = defineEmits(['filter'])

const jobFileList = ref([])
const statsFileList = ref([])
const cities = ref([])
const qualifications = ref([])

const form = reactive({
  major: '经济学',
  education: '本科',
  degree: '学士',
  gender: '女',
  household: '吕梁市',
  is_fresh_graduate: false,
  political_status: '群众',
  qualifications: [],
  work_years: 0,
  target_cities: ['吕梁市', '太原市'],
  gender_strict: true,
  household_strict: false
})

const canSubmit = computed(() => {
  return jobFileList.value.length > 0 && form.major && form.education
})

onMounted(async () => {
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
  formData.append('is_fresh_graduate', form.is_fresh_graduate)
  formData.append('political_status', form.political_status)
  formData.append('qualifications', form.qualifications.join(','))
  formData.append('work_years', form.work_years)
  formData.append('target_cities', form.target_cities.join(','))
  formData.append('gender_strict', form.gender_strict)
  formData.append('household_strict', form.household_strict)

  emit('filter', formData)
}
</script>

<style scoped>
.filter-panel {
  position: sticky;
  top: 20px;
}

.filter-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  margin: 20px 0 15px;
  font-size: 14px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
