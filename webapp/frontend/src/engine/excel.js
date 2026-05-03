import * as XLSX from 'xlsx'

export function readJobFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const worksheet = workbook.Sheets[workbook.SheetNames[0]]
        const rows = XLSX.utils.sheet_to_json(worksheet, { header: 1 })

        const jobs = rows
          .slice(3)
          .map((row) => ({
            index: row[0],
            unit: row[1] || '',
            job_type: row[2] || '',
            service_category: row[3] || '',
            recruit_count: row[4] || 0,
            education: normalizeText(row[5]),
            degree: normalizeText(row[6]),
            major: normalizeText(row[7]),
            qualifications: normalizeText(row[8]),
            other: normalizeText(row[9]),
            phone: row[10] || '',
            contact_person: row[11] || '',
            description: row[12] || '',
            benefits: row[13] || '',
            sheet_name: extractCity(file.name)
          }))
          .filter((job) => job.index !== undefined && job.index !== null && job.unit)

        resolve(jobs)
      } catch (err) {
        reject(err)
      }
    }
    reader.onerror = reject
    reader.readAsArrayBuffer(file)
  })
}

function normalizeText(val) {
  if (val === undefined || val === null) return ''
  return String(val).trim()
}

function extractCity(filename) {
  const match = filename.match(/^(.+?)202\d/)
  return match ? match[1] : '未知地市'
}
