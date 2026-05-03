import { readJobFile } from '../engine/excel.js'
import { matchJobs } from '../engine/matcher.js'

export const getCities = async () => ({
  cities: ['太原市', '大同市', '朔州市', '忻州市', '吕梁市', '晋中市', '阳泉市', '长治市', '晋城市', '临汾市', '运城市']
})

export const getQualifications = async () => ({
  qualifications: ['教师资格证', '法律职业资格证书', '医师资格证', '护士资格证', '会计证', '注册会计师', '建造师证']
})

export const uploadAndFilter = async (formData) => {
  const jobFile = formData.get('job_file')
  if (!jobFile) {
    throw new Error('请选择岗位表文件')
  }

  const profile = {
    major: formData.get('major') || '',
    education: formData.get('education') || '',
    gender: formData.get('gender') || '',
    household: formData.get('household') || '',
    degree: formData.get('degree') || '',
    age: parseInt(formData.get('age')) || 25,
    isFreshGraduate: formData.get('is_fresh_graduate') === 'true',
    politicalStatus: formData.get('political_status') || '',
    qualifications: (formData.get('qualifications') || '').split(',').filter(Boolean),
    computerLevel: formData.get('computer_level') || '',
    englishLevel: formData.get('english_level') || '',
    basicExperience: formData.get('basic_experience') || '',
    workYears: parseInt(formData.get('work_years')) || 0,
    targetCities: (formData.get('target_cities') || '').split(',').filter(Boolean),
    genderStrict: formData.get('gender_strict') === 'true',
    householdStrict: formData.get('household_strict') === 'true'
  }

  const jobs = await readJobFile(jobFile)
  const matchedJobs = matchJobs(jobs, profile)

  const perfect = matchedJobs.filter((j) => j.match_level === '完全符合')
  const partial = matchedJobs.filter((j) => j.match_level === '可能符合')
  const mismatch = matchedJobs.filter((j) => j.match_level === '不符合')

  return {
    jobs: [...perfect, ...partial, ...mismatch],
    total: jobs.length,
    perfect: perfect.length,
    partial: partial.length,
    mismatch: mismatch.length,
    excel_base64: '',
    excel_filename: '筛选结果.xlsx'
  }
}

export default {
  getCities,
  getQualifications,
  uploadAndFilter
}
