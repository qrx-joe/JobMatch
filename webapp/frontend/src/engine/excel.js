import * as XLSX from 'xlsx'

const JOB_HEADER_PATTERNS = {
  index: ['序号', '职位代码', '岗位代码'],
  department: ['招录部门', '招聘部门', '服务类别', '招录机关'],
  unit: ['服务单位', '招录单位', '招聘单位', '招录机关'],
  position: ['岗位类型', '招录职位', '岗位名称', '职位', '职位名称'],
  recruitCount: ['招募人数', '招录人数', '招聘人数', '招考人数'],
  education: ['学历要求', '学历'],
  degree: ['学位要求', '学位'],
  major: ['专业要求', '专业（学科）类别', '专业'],
  qualifications: ['相关资格', '资格证书', '资格'],
  political: ['对政治面貌有何要求', '政治面貌'],
  workYears: ['基层工作经历要求', '工作经历'],
  age: ['年龄要求', '年龄'],
  other: ['其他', '备注'],
  description: ['岗位描述', '职位简介', '职位描述'],
  phone: ['联系电话', '电话'],
  contact: ['联系人'],
  benefits: ['福利待遇']
}

function normalizeHeader(text) {
  return String(text || '').replace(/\s+/g, '')
}

function detectColumn(headers, patterns) {
  for (let i = 0; i < headers.length; i++) {
    const h = normalizeHeader(headers[i])
    for (const p of patterns) {
      if (h.includes(p)) return i
    }
  }
  return -1
}

function detectHeaderRow(rows) {
  let bestRow = -1
  let bestScore = 0

  for (let i = 0; i < Math.min(rows.length, 5); i++) {
    const row = rows[i]
    if (!Array.isArray(row)) continue

    let score = 0
    for (const h of row) {
      const hs = normalizeHeader(h)
      for (const patterns of Object.values(JOB_HEADER_PATTERNS)) {
        if (patterns.some((p) => hs.includes(p))) {
          score++
          break
        }
      }
    }

    if (score > bestScore) {
      bestScore = score
      bestRow = i
    }
  }

  return bestRow
}

function normalizeText(val) {
  if (val === undefined || val === null) return ''
  return String(val).trim()
}

function buildOtherField(row, indices) {
  const parts = []
  if (indices.otherIdx >= 0 && row[indices.otherIdx]) {
    parts.push(row[indices.otherIdx])
  }
  if (indices.polIdx >= 0 && row[indices.polIdx]) {
    parts.push(row[indices.polIdx])
  }
  if (indices.workIdx >= 0 && row[indices.workIdx]) {
    parts.push(row[indices.workIdx])
  }
  if (indices.ageIdx >= 0 && row[indices.ageIdx]) {
    parts.push(row[indices.ageIdx])
  }
  return parts
    .map((p) => String(p).trim())
    .filter(Boolean)
    .join('；')
}

const CITY_PATTERN = /(太原市|大同市|朔州市|忻州市|吕梁市|晋中市|阳泉市|长治市|晋城市|临汾市|运城市)/

function extractCityFromUnit(unit) {
  if (!unit) return ''
  const m = String(unit).match(CITY_PATTERN)
  return m ? m[1] : ''
}

function normalizeSheetName(name) {
  if (!name) return ''
  const text = String(name).trim()
  if (text.endsWith('市')) return text
  // 常见城市名补"市"
  const cityMap = {
    '太原': '太原市', '大同': '大同市', '朔州': '朔州市',
    '忻州': '忻州市', '吕梁': '吕梁市', '晋中': '晋中市',
    '阳泉': '阳泉市', '长治': '长治市', '晋城': '晋城市',
    '临汾': '临汾市', '运城': '运城市'
  }
  for (const [short, full] of Object.entries(cityMap)) {
    if (text.includes(short)) return full
  }
  return text
}

function parseSheet(rows, sheetName) {
  const headerRowIdx = detectHeaderRow(rows)
  if (headerRowIdx === -1) return []

  let headers = rows[headerRowIdx]

  // 检测是否有子表头（如三支一扶的学历/学位/专业子表头）
  let dataStartIdx = headerRowIdx + 1
  const nextRow = rows[headerRowIdx + 1]
  if (nextRow) {
    const nextRowText = nextRow.map((c) => String(c || '')).join('')
    const hasSubHeaders = ['学历', '学位', '专业', '相关资格', '其他'].some((k) =>
      nextRowText.includes(k)
    )
    if (hasSubHeaders) {
      dataStartIdx = headerRowIdx + 2
      const merged = [...headers]
      for (let i = 0; i < nextRow.length; i++) {
        if (nextRow[i] && (!merged[i] || merged[i] === '服务岗位要求')) {
          merged[i] = nextRow[i]
        }
      }
      headers = merged
    }
  }

  const indexIdx = detectColumn(headers, JOB_HEADER_PATTERNS.index)
  const deptIdx = detectColumn(headers, JOB_HEADER_PATTERNS.department)
  const unitIdx = detectColumn(headers, JOB_HEADER_PATTERNS.unit)
  const posIdx = detectColumn(headers, JOB_HEADER_PATTERNS.position)
  const recruitIdx = detectColumn(headers, JOB_HEADER_PATTERNS.recruitCount)
  const eduIdx = detectColumn(headers, JOB_HEADER_PATTERNS.education)
  const degIdx = detectColumn(headers, JOB_HEADER_PATTERNS.degree)
  const majorIdx = detectColumn(headers, JOB_HEADER_PATTERNS.major)
  const qualIdx = detectColumn(headers, JOB_HEADER_PATTERNS.qualifications)
  const polIdx = detectColumn(headers, JOB_HEADER_PATTERNS.political)
  const workIdx = detectColumn(headers, JOB_HEADER_PATTERNS.workYears)
  const ageIdx = detectColumn(headers, JOB_HEADER_PATTERNS.age)
  const otherIdx = detectColumn(headers, JOB_HEADER_PATTERNS.other)
  const descIdx = detectColumn(headers, JOB_HEADER_PATTERNS.description)
  const phoneIdx = detectColumn(headers, JOB_HEADER_PATTERNS.phone)
  const contactIdx = detectColumn(headers, JOB_HEADER_PATTERNS.contact)
  const benefitsIdx = detectColumn(headers, JOB_HEADER_PATTERNS.benefits)

  // 兜底：unit 和 position 都识别失败说明这不是有效岗位表（或表头格式陌生），
  // 直接跳过，避免解析出全空岗位被 matcher 静默归到"完全符合"
  if (unitIdx === -1 && posIdx === -1) {
    console.warn(`[excel.js] 跳过 sheet "${sheetName}"：未能识别"服务单位"和"岗位类型"列`)
    return []
  }

  const jobs = rows
    .slice(dataStartIdx)
    .map((row) => ({
      index: row[indexIdx],
      department: normalizeText(row[deptIdx]),
      unit: normalizeText(row[unitIdx]),
      job_type: normalizeText(row[posIdx]),
      recruit_count: row[recruitIdx] || 0,
      education: normalizeText(row[eduIdx]),
      degree: normalizeText(row[degIdx]),
      major: normalizeText(row[majorIdx]),
      qualifications: normalizeText(row[qualIdx]),
      other: buildOtherField(row, { otherIdx, polIdx, workIdx, ageIdx }),
      description: normalizeText(row[descIdx]),
      phone: normalizeText(row[phoneIdx]),
      contact_person: normalizeText(row[contactIdx]),
      benefits: normalizeText(row[benefitsIdx])
    }))
    .filter(
      (job) =>
        job.unit || job.job_type || job.department
    )

  // sheet_name 优先用 sheet 名称，其次从单位名提取
  let city = normalizeSheetName(sheetName)
  if (!city && jobs.length > 0) {
    city = extractCityFromUnit(jobs[0].unit)
  }

  return jobs.map((job) => ({ ...job, sheet_name: city || '未知' }))
}

export function readJobFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })

        let allJobs = []
        for (const sheetName of workbook.SheetNames) {
          const worksheet = workbook.Sheets[sheetName]
          const rows = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
          const jobs = parseSheet(rows, sheetName)
          allJobs = allJobs.concat(jobs)
        }

        resolve(allJobs)
      } catch (err) {
        reject(err)
      }
    }
    reader.onerror = reject
    reader.readAsArrayBuffer(file)
  })
}
