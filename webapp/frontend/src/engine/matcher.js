import { parseOther } from './parseOther.js'

const EDUCATION_ORDER = ['大专', '本科', '研究生']

function getEducationLevel(eduText) {
  if (!eduText) return -1
  const text = String(eduText)
  if (text.includes('研究生') || text.includes('硕士') || text.includes('博士')) {
    return EDUCATION_ORDER.indexOf('研究生')
  }
  if (text.includes('本科')) {
    return EDUCATION_ORDER.indexOf('本科')
  }
  if (text.includes('大专') || text.includes('专科')) {
    return EDUCATION_ORDER.indexOf('大专')
  }
  return -1
}

function getDegreeLevel(degText) {
  if (!degText || degText === '不限') return -1
  const text = String(degText)
  if (text.includes('博士')) return 3
  if (text.includes('硕士')) return 2
  if (text.includes('学士')) return 1
  return -1
}

function getPoliticalLevel(polText) {
  if (!polText) return 0
  const text = String(polText)
  if (text.includes('中共党员')) return 3
  if (text.includes('中共预备党员')) return 2
  if (text.includes('共青团员')) return 1
  return 0
}

function matchesEducation(userEdu, jobEdu) {
  const userLevel = getEducationLevel(userEdu)
  const jobLevel = getEducationLevel(jobEdu)
  if (jobLevel === -1) return true
  if (userLevel === -1) return false
  return userLevel >= jobLevel
}

function matchesDegree(userDeg, jobDeg) {
  const userLevel = getDegreeLevel(userDeg)
  const jobLevel = getDegreeLevel(jobDeg)
  if (jobLevel === -1) return true
  if (userLevel === -1) return false
  return userLevel >= jobLevel
}

function matchesMajor(userMajor, jobMajor) {
  if (!jobMajor || jobMajor === '不限') return true
  if (!userMajor) return false
  return jobMajor.includes(userMajor)
}

function matchesGender(userGender, otherParsed, strict) {
  if (!otherParsed.gender) return { match: true, level: '完全符合' }

  if (otherParsed.gender === 'male') {
    if (userGender === '男') return { match: true, level: '完全符合' }
    return { match: false, level: strict ? '不符合' : '可能符合', reason: '限男性' }
  }
  if (otherParsed.gender === 'female') {
    if (userGender === '女') return { match: true, level: '完全符合' }
    return { match: false, level: strict ? '不符合' : '可能符合', reason: '限女性' }
  }
  if (otherParsed.gender === 'prefer_male') {
    if (userGender === '男') return { match: true, level: '完全符合' }
    return { match: true, level: '可能符合', reason: '适宜男性' }
  }

  return { match: true, level: '完全符合' }
}

function matchesPolitical(userPol, otherParsed) {
  if (!otherParsed.political) return true
  const userLevel = getPoliticalLevel(userPol)
  const jobLevel = getPoliticalLevel(otherParsed.political)
  // 中共党员（含预备党员）→ 预备党员及以上
  if (otherParsed.political.includes('含预备党员')) {
    return userLevel >= 2  // 中共预备党员 or 中共党员
  }
  return userLevel >= jobLevel
}

function matchesHousehold(userHousehold, otherParsed, strict) {
  if (!otherParsed.household) return true
  if (userHousehold === '不限') return true
  // 支持部分匹配：用户填"太原市"，要求"太原市户籍"
  const required = otherParsed.household
  if (userHousehold.includes(required) || required.includes(userHousehold)) return true
  return !strict
}

function matchesQualifications(userQuals, jobQuals) {
  if (!jobQuals || jobQuals === '无' || jobQuals === '不限') return true
  if (!userQuals || userQuals.length === 0) return false
  // 任一用户证书包含岗位要求，或岗位要求的证书包含用户证书
  return userQuals.some(uq => jobQuals.includes(uq) || uq.includes(jobQuals))
}

function matchesAge(userAge, otherParsed) {
  if (!otherParsed.ageMax) return true
  if (!userAge) return true
  return userAge <= otherParsed.ageMax
}

function matchesFreshGraduate(userIsFresh, otherParsed) {
  if (!otherParsed.freshGraduate) return true
  return userIsFresh === true
}

function matchesWorkYears(userYears, otherParsed) {
  if (!otherParsed.workYearsMin) return true
  if (userYears === undefined || userYears === null) return false
  return userYears >= otherParsed.workYearsMin
}

export function matchJobs(jobs, profile) {
  return jobs.map((job) => {
    const otherParsed = parseOther(job.other)
    const matchReasons = []
    const mismatchReasons = []
    let partialReasons = []

    // 学历
    if (matchesEducation(profile.education, job.education)) {
      matchReasons.push(`学历：${job.education || '不限'}`)
    } else {
      mismatchReasons.push(`学历不符：要求${job.education || '不限'}，您是${profile.education}`)
    }

    // 学位
    if (matchesDegree(profile.degree, job.degree)) {
      if (job.degree && job.degree !== '不限') {
        matchReasons.push(`学位：${job.degree}`)
      }
    } else {
      mismatchReasons.push(`学位不符：要求${job.degree}，您是${profile.degree || '无'}`)
    }

    // 专业
    if (matchesMajor(profile.major, job.major)) {
      matchReasons.push(`专业：${job.major || '不限'}`)
    } else {
      mismatchReasons.push(`专业不符：要求${job.major || '不限'}，您是${profile.major}`)
    }

    // 性别（支持宽松模式）
    const genderResult = matchesGender(profile.gender, otherParsed, profile.genderStrict)
    if (genderResult.match) {
      if (genderResult.level === '可能符合') {
        partialReasons.push(`性别建议：${genderResult.reason}`)
      } else if (otherParsed.gender) {
        matchReasons.push(`性别：符合要求`)
      }
    } else {
      mismatchReasons.push(`性别限制：${genderResult.reason}`)
    }

    // 政治面貌
    if (matchesPolitical(profile.politicalStatus, otherParsed)) {
      if (otherParsed.political) {
        matchReasons.push(`政治面貌：${profile.politicalStatus}`)
      }
    } else {
      mismatchReasons.push(`政治面貌不符：要求${otherParsed.political}，您是${profile.politicalStatus || '群众'}`)
    }

    // 户籍
    if (matchesHousehold(profile.household, otherParsed, profile.householdStrict)) {
      if (otherParsed.household) {
        matchReasons.push(`户籍：${otherParsed.household}`)
      }
    } else {
      mismatchReasons.push(`户籍不符：要求${otherParsed.household}，您是${profile.household}`)
    }

    // 资格证书
    if (matchesQualifications(profile.qualifications, job.qualifications)) {
      if (job.qualifications && job.qualifications !== '无') {
        matchReasons.push(`资格：${job.qualifications}`)
      }
    } else {
      mismatchReasons.push(`资格不符：要求${job.qualifications}，您未提供`)
    }

    // 年龄
    if (matchesAge(profile.age, otherParsed)) {
      if (otherParsed.ageMax) {
        matchReasons.push(`年龄：${profile.age}周岁（要求≤${otherParsed.ageMax}）`)
      }
    } else {
      mismatchReasons.push(`年龄不符：要求≤${otherParsed.ageMax}周岁，您是${profile.age}周岁`)
    }

    // 应届
    if (matchesFreshGraduate(profile.isFreshGraduate, otherParsed)) {
      if (otherParsed.freshGraduate) {
        matchReasons.push(`应届毕业生：符合`)
      }
    } else {
      mismatchReasons.push(`应届要求：仅限应届毕业生`)
    }

    // 工作年限
    if (matchesWorkYears(profile.workYears, otherParsed)) {
      if (otherParsed.workYearsMin) {
        matchReasons.push(`工作年限：${profile.workYears}年（要求≥${otherParsed.workYearsMin}）`)
      }
    } else {
      mismatchReasons.push(`工作年限不足：要求≥${otherParsed.workYearsMin}年，您是${profile.workYears}年`)
    }

    // 其他备注（无法解析的条件）
    if (otherParsed.remarks.length > 0) {
      partialReasons.push(`其他要求：${otherParsed.remarks.join('；')}`)
    }

    const hasMismatch = mismatchReasons.length > 0
    const hasPartial = partialReasons.length > 0

    let matchLevel
    if (!hasMismatch && !hasPartial) {
      matchLevel = '完全符合'
    } else if (hasMismatch) {
      matchLevel = '不符合'
    } else {
      matchLevel = '可能符合'
    }

    return {
      ...job,
      match_level: matchLevel,
      match_reasons: matchReasons,
      mismatch_reasons: mismatchReasons,
      partial_reasons: partialReasons,
      _parsed: otherParsed
    }
  })
}
