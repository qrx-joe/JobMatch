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

function matchesEducation(userEdu, jobEdu) {
  const userLevel = getEducationLevel(userEdu)
  const jobLevel = getEducationLevel(jobEdu)
  if (jobLevel === -1) return true
  if (userLevel === -1) return false
  return userLevel >= jobLevel
}

function matchesMajor(userMajor, jobMajor) {
  if (!jobMajor || jobMajor === '不限') return true
  if (!userMajor) return false
  return jobMajor.includes(userMajor)
}

function matchesGender(userGender, jobOther) {
  if (!jobOther) return true
  if (jobOther.includes('限男性') && userGender !== '男') return false
  if (jobOther.includes('限女性') && userGender !== '女') return false
  return true
}

export function matchJobs(jobs, profile) {
  return jobs.map((job) => {
    const matchReasons = []
    const mismatchReasons = []

    if (matchesEducation(profile.education, job.education)) {
      matchReasons.push(`学历：${job.education}`)
    } else {
      mismatchReasons.push(`学历不符：要求${job.education || '不限'}，您是${profile.education}`)
    }

    if (matchesMajor(profile.major, job.major)) {
      matchReasons.push(`专业：${job.major || '不限'}`)
    } else {
      mismatchReasons.push(`专业不符：要求${job.major || '不限'}，您是${profile.major}`)
    }

    if (matchesGender(profile.gender, job.other)) {
      if (job.other && job.other !== '无') {
        matchReasons.push(`其他：${job.other}`)
      }
    } else {
      mismatchReasons.push(`性别限制：${job.other}`)
    }

    const isPerfect = mismatchReasons.length === 0
    const isMismatch = matchReasons.length === 0

    return {
      ...job,
      match_level: isPerfect ? '完全符合' : isMismatch ? '不符合' : '可能符合',
      match_reasons: matchReasons,
      mismatch_reasons: mismatchReasons
    }
  })
}
