#!/usr/bin/env python3
"""
岗位筛选匹配引擎
"""

import re
from dataclasses import dataclass, field
from enum import Enum

import yaml


class MatchLevel(Enum):
    PERFECT = "完全符合"  # 绿色
    PARTIAL = "可能符合"  # 黄色
    MISMATCH = "不符合"  # 红色


@dataclass
class Job:
    """岗位数据模型"""

    # 基本信息
    sheet_name: str = ""  # 所属地市（Sheet名）
    index: int = 0  # 序号
    unit: str = ""  # 服务单位
    job_type: str = ""  # 岗位类型
    service_category: str = ""  # 服务类别
    recruit_count: int = 1  # 招募人数

    # 要求
    education: str = ""  # 学历要求
    degree: str = ""  # 学位要求
    major: str = ""  # 专业要求
    qualifications: str = ""  # 相关资格
    other: str = ""  # 其他要求（性别/户籍等）
    phone: str = ""  # 联系电话
    contact: str = ""  # 联系人
    description: str = ""  # 岗位描述
    benefits: str = ""  # 福利待遇

    # 竞争数据
    applicants: int = 0  # 填报信息人数
    approved: int = 0  # 初审通过人数
    paid: int = 0  # 缴费人数

    # 匹配结果
    match_level: MatchLevel = MatchLevel.MISMATCH
    match_score: int = 0  # 匹配分数（用于排序）
    match_reasons: list[str] = field(default_factory=list)
    mismatch_reasons: list[str] = field(default_factory=list)
    competition_ratio: float = 0.0


@dataclass
class UserProfile:
    """用户档案"""

    major: str = ""
    education: str = ""
    degree: str = ""
    gender: str = ""
    household: str = ""
    qualifications: list[str] = field(default_factory=list)
    target_cities: list[str] = field(default_factory=list)


class MajorMatcher:
    """专业匹配器"""

    # 专业大类映射（教育部专业目录代码）
    MAJOR_CATEGORIES = {
        "经济学类": [
            "经济学",
            "经济统计学",
            "国民经济管理",
            "资源与环境经济学",
            "商务经济学",
            "能源经济",
            "劳动经济学",
            "经济工程",
            "数字经济",
        ],
        "财政学类": ["财政学", "税收学", "国际税收"],
        "金融学类": [
            "金融学",
            "金融工程",
            "保险学",
            "投资学",
            "金融数学",
            "信用管理",
            "经济与金融",
            "精算学",
            "互联网金融",
            "金融科技",
        ],
        "经济与贸易类": ["国际经济与贸易", "贸易经济"],
    }

    # 专业代码映射（部分常见代码）
    MAJOR_CODES = {
        "经济学类": ["0201"],
        "经济学": ["020101"],
        "经济统计学": ["020102"],
        "财政学类": ["0202"],
        "金融学类": ["0203"],
        "经济与贸易类": ["0204"],
    }

    def __init__(self, user_major: str):
        self.user_major = user_major.strip()
        self.user_categories = self._get_categories(user_major)

    def _get_categories(self, major: str) -> list[str]:
        """获取专业所属的大类"""
        categories = []
        for cat, majors in self.MAJOR_CATEGORIES.items():
            if major in majors:
                categories.append(cat)
        return categories

    def match(self, job_major: str) -> tuple[bool, str]:
        """
        匹配专业
        返回: (是否匹配, 匹配说明)
        """
        job_major = str(job_major).strip()

        # 情况1: 不限
        if "不限" in job_major or job_major in ["无", "nan", "", "None"]:
            return True, "专业不限"

        # 情况2: 完全相等
        if self.user_major == job_major:
            return True, f"专业完全匹配：{self.user_major}"

        # 情况3: 包含匹配（如"经济学、金融学"）
        if self.user_major in job_major:
            return True, f"专业包含：{self.user_major}"

        # 情况4: 大类匹配（如岗位是"经济学类"，用户是"经济学"）
        for category in self.user_categories:
            if category in job_major:
                return True, f"专业大类匹配：{category}"

        # 情况5: 专业代码匹配（使用完整的6位代码匹配）
        # 从岗位要求中提取所有括号内的代码
        import re
        job_codes = re.findall(r'[（(](\d{6})[）)]', job_major)
        if job_codes:
            for category in self.user_categories:
                for code in self.MAJOR_CODES.get(category, []):
                    # 用户专业代码（如020101）应该完整匹配岗位代码（如020101）
                    if code in job_codes or code.zfill(6) in job_codes:
                        return True, f"专业代码匹配：{code}"
        else:
            # 如果没有6位代码，尝试4位大类代码（需要精确匹配，不是子串）
            for category in self.user_categories:
                codes = self.MAJOR_CODES.get(category, [])
                for code in codes:
                    # 匹配4位代码，但必须是完整的大类代码
                    # 例如：0201匹配"经济学类（0201）"，但不匹配"会计学（120201）"
                    if re.search(r'[（(]0\d{3}[）)]', job_major) and code in job_major:
                        # 确保是4位代码且不在更大的代码中
                        if f"（{code}）" in job_major or f"({code})" in job_major:
                            return True, f"专业大类代码匹配：{code}"

        # 情况6: 反向包含（岗位是具体专业，用户是大类）- 这种情况不符合
        # 例如：岗位要求"经济学"，用户是"经济学类" -> 不符合

        return False, f"专业不匹配：要求[{job_major}]，你是[{self.user_major}]"


class EducationMatcher:
    """学历匹配器"""

    # 学历层级
    EDU_LEVELS = {
        "大专": 1,
        "专科": 1,
        "高职": 1,
        "本科": 2,
        "大学": 2,
        "研究生": 3,
        "硕士": 3,
        "博士": 3,
    }

    def __init__(self, user_edu: str):
        self.user_level = self._get_level(user_edu)

    def _get_level(self, edu: str) -> int:
        """获取学历等级"""
        edu = str(edu).strip()
        for key, level in self.EDU_LEVELS.items():
            if key in edu:
                return level
        return 0

    def match(self, job_edu: str) -> tuple[bool, str]:
        """
        匹配学历
        规则：用户学历 >= 岗位要求学历
        例如：本科可以报"大专及以上"
        """
        job_edu = str(job_edu).strip()

        # 提取岗位要求的最低学历
        job_min_level = 3  # 默认最高
        for edu, level in sorted(self.EDU_LEVELS.items(), key=lambda x: x[1]):
            if edu in job_edu:
                job_min_level = level
                break

        # 检查"及以上"
        if "及以上" in job_edu:
            if self.user_level >= job_min_level:
                return True, f"学历符合：{self._level_to_str(self.user_level)} >= {job_edu}"
            else:
                return False, f"学历不够：你是{self._level_to_str(self.user_level)}，要求{job_edu}"
        else:
            # 没有"及以上"，要求精确匹配
            if self.user_level == job_min_level:
                return True, f"学历符合：{self._level_to_str(self.user_level)}"
            else:
                return (
                    False,
                    f"学历不匹配：你是{self._level_to_str(self.user_level)}，要求{job_edu}",
                )

    def _level_to_str(self, level: int) -> str:
        """学历等级转字符串"""
        mapping = {1: "大专", 2: "本科", 3: "研究生"}
        return mapping.get(level, "未知")


class GenderMatcher:
    """性别匹配器"""

    def __init__(self, user_gender: str):
        self.user_gender = user_gender.strip()

    def match(self, other_field: str) -> tuple[bool, str]:
        """
        匹配性别要求
        other_field: "其他"列的内容
        """
        other = str(other_field).strip()

        # 检查是否有性别限制
        if "限男性" in other:
            if self.user_gender == "男":
                return True, "性别符合：限男性"
            else:
                return False, "性别不符合：限男性"

        if "限女性" in other:
            if self.user_gender == "女":
                return True, "性别符合：限女性"
            else:
                return False, "性别不符合：限女性"

        return True, "性别不限"


class HouseholdMatcher:
    """户籍匹配器"""

    def __init__(self, user_household: str):
        self.user_household = user_household.strip()

    def match(self, other_field: str) -> tuple[bool, str]:
        """
        匹配户籍要求
        """
        other = str(other_field).strip()

        # 检查是否有户籍限制
        if "限" in other and "户籍" in other:
            # 提取限制的户籍地
            match = re.search(r"限(.*?)户籍", other)
            if match:
                required = match.group(1)
                if required in self.user_household:
                    return True, f"户籍符合：限{required}户籍"
                else:
                    return False, f"户籍不符合：限{required}户籍，你是{self.user_household}"

        return True, "户籍不限"


class JobMatcher:
    """岗位匹配引擎"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.profile = UserProfile(
            major=self.config["profile"]["专业"],
            education=self.config["profile"]["学历"],
            degree=self.config["profile"]["学位"],
            gender=self.config["profile"]["性别"],
            household=self.config["profile"]["户籍"],
            qualifications=self.config["profile"].get("相关资格", []),
            target_cities=self.config["preference"].get("意向城市", []),
        )

        # 初始化各匹配器
        self.major_matcher = MajorMatcher(self.profile.major)
        self.edu_matcher = EducationMatcher(self.profile.education)
        self.gender_matcher = GenderMatcher(self.profile.gender)
        self.household_matcher = HouseholdMatcher(self.profile.household)

    def match(self, job: Job) -> Job:
        """
        对单个岗位进行匹配
        """
        checks = {}
        match_reasons = []
        mismatch_reasons = []
        score = 0

        # 1. 专业匹配
        major_ok, major_msg = self.major_matcher.match(job.major)
        checks["专业"] = major_ok
        if major_ok:
            score += 40
            match_reasons.append(major_msg)
        else:
            mismatch_reasons.append(major_msg)

        # 2. 学历匹配
        edu_ok, edu_msg = self.edu_matcher.match(job.education)
        checks["学历"] = edu_ok
        if edu_ok:
            score += 30
            match_reasons.append(edu_msg)
        else:
            mismatch_reasons.append(edu_msg)

        # 3. 性别匹配
        gender_ok, gender_msg = self.gender_matcher.match(job.other)
        checks["性别"] = gender_ok
        if gender_ok:
            score += 15
            match_reasons.append(gender_msg)
        else:
            mismatch_reasons.append(gender_msg)

        # 4. 户籍匹配
        household_ok, household_msg = self.household_matcher.match(job.other)
        checks["户籍"] = household_ok
        if household_ok:
            score += 15
            match_reasons.append(household_msg)
        else:
            mismatch_reasons.append(household_msg)

        # 5. 城市偏好（不强制，只影响分数）
        if self.profile.target_cities:
            if job.sheet_name in self.profile.target_cities:
                score += 20
                match_reasons.append(f"意向城市：{job.sheet_name}")
            else:
                score -= 10
                match_reasons.append(f"非意向城市：{job.sheet_name}")

        # 判断是否匹配
        must_checks = ["专业", "学历", "性别", "户籍"]
        all_must_ok = all(checks.get(k, False) for k in must_checks)

        if all_must_ok:
            if job.sheet_name in self.profile.target_cities:
                job.match_level = MatchLevel.PERFECT
            else:
                job.match_level = MatchLevel.PARTIAL
        else:
            job.match_level = MatchLevel.MISMATCH

        job.match_score = score
        job.match_reasons = match_reasons
        job.mismatch_reasons = mismatch_reasons

        # 计算竞争比
        if job.recruit_count > 0 and job.paid > 0:
            job.competition_ratio = job.paid / job.recruit_count

        return job


if __name__ == "__main__":
    # 测试匹配器
    matcher = JobMatcher()

    # 测试专业匹配
    test_cases = [
        "不限",
        "经济学",
        "经济学类",
        "经济学类（0201）",
        "本科：经济学类（0201）、统计学类（0712）",
        "金融学",
    ]

    print("=" * 80)
    print(f"用户专业：{matcher.profile.major}")
    print("=" * 80)

    for test in test_cases:
        ok, msg = matcher.major_matcher.match(test)
        status = "✓" if ok else "✗"
        print(f"{status} [{test}] -> {msg}")
