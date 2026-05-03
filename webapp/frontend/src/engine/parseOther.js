// 解析"其他"列中的隐含条件
// 这类字段通常是自由文本，包含多个条件，用"；"分隔

export function parseOther(text) {
  if (!text || text === '无') {
    return { gender: null, political: null, household: null, ageMax: null, remarks: [] }
  }

  const parts = String(text).split(/[；;]/).map(s => s.trim()).filter(Boolean)
  const result = {
    gender: null,        // 'male' | 'female' | 'prefer_male' | null
    political: null,     // required political status text
    household: null,     // required household city
    ageMax: null,        // max age in years
    freshGraduate: null, // boolean
    workYearsMin: null,  // minimum work years
    remarks: []          // unparsed parts
  }

  for (const part of parts) {
    // 性别限制
    if (part.includes('限男性')) {
      result.gender = 'male'
    } else if (part.includes('限女性')) {
      result.gender = 'female'
    } else if (part.includes('适宜男性') || part.includes('适合男性')) {
      result.gender = 'prefer_male'
    }
    // 政治面貌
    else if (part.includes('中共党员') || part.includes('党员')) {
      result.political = '中共党员（含预备党员）'
    }
    // 户籍
    else if (part.includes('户籍')) {
      const m = part.match(/(.+?)户籍/)
      if (m) result.household = m[1].trim()
    }
    // 年龄
    else if (/\d+周岁/.test(part) || /年龄.*\d+/.test(part)) {
      const m = part.match(/(\d+).{0,2}周岁/)
      if (m) result.ageMax = parseInt(m[1])
    }
    // 应届
    else if (part.includes('应届毕业生') || part.includes('应届高校毕业生')) {
      result.freshGraduate = true
    }
    // 工作年限
    else if (/\d+年.*工作/.test(part) || /工作.*\d+年/.test(part)) {
      const m = part.match(/(\d+)/)
      if (m) result.workYearsMin = parseInt(m[1])
    }
    // 无法识别的归入备注
    else {
      result.remarks.push(part)
    }
  }

  return result
}
