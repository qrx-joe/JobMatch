import * as XLSX from 'xlsx'

const JOB_HEADER_PATTERNS = {
  index: ['序号'],
  department: ['招录部门', '招聘部门', '服务类别'],
  unit: ['服务单位', '招录单位', '招聘单位'],
  position: ['岗位类型', '招录职位', '岗位名称', '职位'],
  recruitCount: ['招募人数', '招录人数', '招聘人数'],
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

function detectColumn(headers, patterns) {
  for (let i = 0; i < headers.length; i++) {
    const h = String(headers[i] || '').trim()
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
      const hs = String(h || '')
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

function extractCity(filename) {
  const match = filename.match(
    /(山西|太原|大同|朔州|忻州|吕梁|晋中|阳泉|长治|晋城|临汾|运城)/)
  return match ? match[1] + '市' : '未知地市'
}

export function readJobFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const worksheet = workbook.Sheets[workbook.SheetNames[0]]
        const rows = XLSX.utils.sheet_to_json(worksheet, { header: 1 })

        const headerRowIdx = detectHeaderRow(rows)
        if (headerRowIdx === -1) {
          reject(new Error('无法识别岗位表的表头，请检查文件格式'))
          return
        }

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
            // 合并子表头到有效表头（子表头覆盖主表头中的空值或合并项）
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
            benefits: normalizeText(row[benefitsIdx]),
            sheet_name: extractCity(file.name)
          }))
          .filter(
            (job) =>
              job.index !== undefined &&
              job.index !== null &&
              job.unit
          )

        resolve(jobs)
      } catch (err) {
        reject(err)
      }
    }
    reader.onerror = reject
    reader.readAsArrayBuffer(file)
  })
}
