import * as XLSX from 'xlsx'

const STATS_HEADER_PATTERNS = {
  unit: ['服务单位', '招录单位', '招聘单位', '单位'],
  position: ['岗位类型', '招录职位', '招聘岗位', '岗位名称', '职位'],
  code: ['岗位代码', '职位代码', '代码'],
  recruitCount: ['招募人数', '招录人数', '招聘人数'],
  applicants: ['填报信息人数', '提交报名申请', '报名人数'],
  approved: ['初审通过人数', '审查通过人数'],
  paid: ['缴费人数']
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
  for (let i = 0; i < Math.min(rows.length, 5); i++) {
    const row = rows[i]
    if (!Array.isArray(row)) continue
    const text = row.map(c => String(c || '')).join('')
    // 如果一行包含多个已知列名，就是表头行
    let matchCount = 0
    for (const h of row) {
      const hs = String(h || '')
      for (const patterns of Object.values(STATS_HEADER_PATTERNS)) {
        if (patterns.some(p => hs.includes(p))) {
          matchCount++
          break
        }
      }
    }
    if (matchCount >= 2) return i
  }
  return -1
}

function normalizeUnitName(name) {
  if (!name) return ''
  // 三支一扶统计表的格式："太原市-杏花岭区-太原市杏花岭区XXX"
  // 提取最后一段（实际单位名）
  const segments = String(name).split(/[-–—]/)
  if (segments.length >= 2) {
    const last = segments[segments.length - 1].trim()
    // 如果最后一段已经包含了前面的信息，直接返回
    if (last.length > 4) return last
  }
  return String(name).trim()
}

function normalizeKey(text) {
  return String(text || '')
    .trim()
    .replace(/[\s　]/g, '')  // 去掉所有空格和全角空格
    .replace(/[Ａ-Ｚａ-ｚ０-９]/g, ch => String.fromCharCode(ch.charCodeAt(0) - 0xFEE0)) // 全角转半角
    .toLowerCase()
}

export function readStatsFile(file) {
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
          reject(new Error('无法识别统计表的表头，请检查文件格式'))
          return
        }

        const headers = rows[headerRowIdx]
        const unitIdx = detectColumn(headers, STATS_HEADER_PATTERNS.unit)
        const posIdx = detectColumn(headers, STATS_HEADER_PATTERNS.position)
        const codeIdx = detectColumn(headers, STATS_HEADER_PATTERNS.code)
        const recruitIdx = detectColumn(headers, STATS_HEADER_PATTERNS.recruitCount)
        const appIdx = detectColumn(headers, STATS_HEADER_PATTERNS.applicants)
        const apprIdx = detectColumn(headers, STATS_HEADER_PATTERNS.approved)
        const paidIdx = detectColumn(headers, STATS_HEADER_PATTERNS.paid)

        // 构建 join key：优先用代码，否则用单位+岗位
        const dataRows = rows.slice(headerRowIdx + 1).map((row, idx) => {
          const unit = normalizeUnitName(row[unitIdx])
          const position = String(row[posIdx] || '').trim()
          const code = codeIdx >= 0 ? String(row[codeIdx] || '').trim() : ''

          let joinKey
          if (code) {
            joinKey = normalizeKey(code)
          } else if (unit && position) {
            joinKey = normalizeKey(unit + '|' + position)
          } else {
            joinKey = ''
          }

          return {
            _rowIndex: idx,
            joinKey,
            unit,
            position,
            code,
            recruitCount: row[recruitIdx] || 0,
            applicants: row[appIdx] || 0,
            approved: row[apprIdx] || 0,
            paid: row[paidIdx] || 0
          }
        }).filter(r => r.joinKey)

        resolve({
          headers: headers.map(h => String(h || '').trim()),
          rows: dataRows,
          joinType: codeIdx >= 0 ? 'code' : 'unit_position',
          columnMap: { unitIdx, posIdx, codeIdx, recruitIdx, appIdx, apprIdx, paidIdx }
        })
      } catch (err) {
        reject(err)
      }
    }
    reader.onerror = reject
    reader.readAsArrayBuffer(file)
  })
}

export function buildJobJoinKey(job, joinType) {
  if (joinType === 'code' && job.code) {
    return normalizeKey(job.code)
  }
  // 默认用单位+岗位类型；unit 为空时回退到 department
  const unit = normalizeUnitName(job.unit) || normalizeUnitName(job.department)
  const position = String(job.job_type || '').trim()
  if (unit && position) {
    return normalizeKey(unit + '|' + position)
  }
  return ''
}

export function joinJobsWithStats(jobs, statsResult) {
  if (!statsResult || !statsResult.rows) return jobs

  const statsMap = new Map()
  for (const row of statsResult.rows) {
    // 同一个 key 可能出现多次？理论上不应该，但做个覆盖处理
    statsMap.set(row.joinKey, row)
  }

  return jobs.map(job => {
    const key = buildJobJoinKey(job, statsResult.joinType)
    const stat = statsMap.get(key)

    if (stat) {
      const competitionRatio = stat.paid > 0 && job.recruit_count > 0
        ? (stat.paid / job.recruit_count).toFixed(1)
        : 0

      return {
        ...job,
        applicants: stat.applicants,
        approved: stat.approved,
        paid: stat.paid,
        competition_ratio: parseFloat(competitionRatio),
        hasStats: true
      }
    }

    return {
      ...job,
      applicants: 0,
      approved: 0,
      paid: 0,
      competition_ratio: 0,
      hasStats: false
    }
  })
}
