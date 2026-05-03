#!/usr/bin/env python3
"""
组合匹配器 - 协调多个匹配器进行综合匹配
"""

from typing import Dict, List, Optional, Tuple

from ..models.job import Job, MatchLevel
from ..models.user_profile import UserProfile
from ..models.match_result import MatchResult

from .base_matcher import BaseMatcher
from .major_matcher import MajorMatcher
from .education_matcher import EducationMatcher, DegreeMatcher
from .political_matcher import PoliticalMatcher
from .age_matcher import AgeMatcher
from .level_matcher import ComputerLevelMatcher, EnglishLevelMatcher
from .qualification_matcher import QualificationMatcher


class CompositeMatcher:
    """
    组合匹配器

    协调多个匹配器进行综合评估

    匹配权重（总分100分）：
    - 专业：40分
    - 学历：20分
    - 学位：10分
    - 政治面貌：10分
    - 年龄：10分
    - 户籍/生源地：5分
    - 性别：5分
    """

    DEFAULT_WEIGHTS = {
        "major": 40,
        "education": 20,
        "degree": 10,
        "political": 10,
        "age": 10,
        "household": 5,
        "gender": 5,
        "computer_level": 5,
        "english_level": 5,
        "qualification": 10,
    }

    def __init__(self, weights: Optional[Dict[str, int]] = None):
        """
        初始化组合匹配器

        Args:
            weights: 自定义权重
        """
        self.weights = weights or self.DEFAULT_WEIGHTS

        # 各维度匹配器
        self._major_matcher: Optional[MajorMatcher] = None
        self._edu_matcher: Optional[EducationMatcher] = None
        self._degree_matcher: Optional[DegreeMatcher] = None
        self._political_matcher: Optional[PoliticalMatcher] = None
        self._age_matcher: Optional[AgeMatcher] = None
        self._computer_matcher: Optional[ComputerLevelMatcher] = None
        self._english_matcher: Optional[EnglishLevelMatcher] = None
        self._qualification_matcher: Optional[QualificationMatcher] = None

    def _ensure_matchers(self, profile: UserProfile) -> None:
        """确保所有匹配器已初始化"""
        if self._major_matcher is None:
            self._major_matcher = MajorMatcher(profile.major)
        if self._edu_matcher is None:
            self._edu_matcher = EducationMatcher(profile.education)
        if self._degree_matcher is None:
            self._degree_matcher = DegreeMatcher(profile.degree)
        if self._political_matcher is None:
            self._political_matcher = PoliticalMatcher(profile.party_status)
        if self._age_matcher is None:
            self._age_matcher = AgeMatcher(profile.age)
        if self._computer_matcher is None:
            self._computer_matcher = ComputerLevelMatcher(profile.computer_level)
        if self._english_matcher is None:
            self._english_matcher = EnglishLevelMatcher(profile.english_level)
        if self._qualification_matcher is None:
            self._qualification_matcher = QualificationMatcher(profile.qualifications)

    def match(self, job: Job, profile: UserProfile) -> MatchResult:
        """
        对岗位和用户进行综合匹配

        Args:
            job: 岗位
            profile: 用户画像

        Returns:
            MatchResult: 匹配结果
        """
        self._ensure_matchers(profile)

        result = MatchResult(job_id=job.id, user_id=profile.id)

        match_reasons = []
        mismatch_reasons = []
        total_score = 0

        # 1. 专业匹配 (40分)
        major_ok, major_msg = self._major_matcher.match(job.major)
        result.major_match = (major_ok, major_msg)
        if major_ok:
            total_score += self.weights.get("major", 40)
            match_reasons.append(major_msg)
        else:
            mismatch_reasons.append(major_msg)

        # 2. 学历匹配 (20分)
        edu_ok, edu_msg = self._edu_matcher.match(job.education)
        result.education_match = (edu_ok, edu_msg)
        if edu_ok:
            total_score += self.weights.get("education", 20)
            match_reasons.append(edu_msg)
        else:
            mismatch_reasons.append(edu_msg)

        # 3. 学位匹配 (10分)
        deg_ok, deg_msg = self._degree_matcher.match(job.degree)
        result.degree_match = (deg_ok, deg_msg)
        if deg_ok:
            total_score += self.weights.get("degree", 10)
            match_reasons.append(deg_msg)
        else:
            mismatch_reasons.append(deg_msg)

        # 4. 政治面貌匹配 (10分)
        pol_ok, pol_msg = self._political_matcher.match(job.political_requirement)
        result.political_match = (pol_ok, pol_msg)
        if pol_ok:
            total_score += self.weights.get("political", 10)
            match_reasons.append(pol_msg)
        else:
            mismatch_reasons.append(pol_msg)

        # 5. 年龄匹配 (10分)
        age_ok, age_msg = self._age_matcher.match(job.age_limit)
        result.age_match = (age_ok, age_msg)
        if age_ok:
            total_score += self.weights.get("age", 10)
            match_reasons.append(age_msg)
        else:
            mismatch_reasons.append(age_msg)

        # 6. 户籍匹配 (5分)
        household_ok, household_msg = self._match_household(job, profile)
        result.household_match = (household_ok, household_msg)
        if household_ok:
            total_score += self.weights.get("household", 5)
            match_reasons.append(household_msg)
        else:
            mismatch_reasons.append(household_msg)

        # 7. 性别匹配 (5分)
        gender_ok, gender_msg = self._match_gender(job, profile)
        result.gender_match = (gender_ok, gender_msg)
        if gender_ok:
            total_score += self.weights.get("gender", 5)
            match_reasons.append(gender_msg)
        else:
            mismatch_reasons.append(gender_msg)

        # 8. 计算机等级匹配 (5分)
        computer_ok, computer_msg = self._computer_matcher.match(job.other or "")
        result.computer_match = (computer_ok, computer_msg)
        if computer_ok:
            total_score += self.weights.get("computer_level", 5)
            match_reasons.append(computer_msg)
        else:
            mismatch_reasons.append(computer_msg)

        # 9. 英语等级匹配 (5分)
        english_ok, english_msg = self._english_matcher.match(job.other or "")
        result.english_match = (english_ok, english_msg)
        if english_ok:
            total_score += self.weights.get("english_level", 5)
            match_reasons.append(english_msg)
        else:
            mismatch_reasons.append(english_msg)

        # 10. 资格证书匹配 (10分)
        qual_ok, qual_msg = self._qualification_matcher.match(job.qualifications or "")
        result.qualifications_match = (qual_ok, qual_msg)
        if qual_ok:
            total_score += self.weights.get("qualification", 10)
            match_reasons.append(qual_msg)
        else:
            mismatch_reasons.append(qual_msg)

        # 计算综合结果
        result.total_score = total_score
        result.match_reasons = match_reasons
        result.mismatch_reasons = mismatch_reasons

        # 判断匹配等级
        must_match_fields = [
            result.major_match,
            result.education_match,
            result.political_match,
            result.age_match,
        ]
        all_must_ok = all(ok for ok, _ in must_match_fields)

        if all_must_ok:
            if total_score >= 80:
                result.match_level = MatchLevel.PERFECT
            else:
                result.match_level = MatchLevel.PARTIAL
        else:
            result.match_level = MatchLevel.MISMATCH

        # 竞争比
        result.competition_ratio = job.competition_ratio

        return result

    def _match_household(self, job: Job, profile: UserProfile) -> Tuple[bool, str]:
        """匹配户籍/生源地"""
        other = str(job.other or "").strip()

        # 岗位要求"不限户籍"时直接通过
        if "不限户籍" in other or "户籍不限" in other:
            return True, "户籍不限"

        # 检查是否有户籍限制
        import re

        if "限" in other and "户籍" in other:
            match = re.search(r"限([^户籍]+)户籍", other)
            if match:
                required = match.group(1).strip()
                if required in profile.household:
                    return True, f"户籍符合：限{required}户籍"
                else:
                    return False, f"户籍不符合：限{required}户籍，你是{profile.household}"

        # 检查生源地限制
        if "限" in other and "生源" in other:
            match = re.search(r"限([^生源]+)生源", other)
            if match:
                required = match.group(1).strip()
                if required in profile.household:
                    return True, f"生源地符合：限{required}生源"
                else:
                    return False, f"生源地不符合：限{required}生源，你是{profile.household}"

        return True, "户籍/生源地不限"

    def _match_gender(self, job: Job, profile: UserProfile) -> Tuple[bool, str]:
        """匹配性别"""
        other = str(job.other or "").strip()

        if "限男性" in other or "限男" in other:
            if profile.gender == "男":
                return True, "性别符合：限男性"
            else:
                return False, "性别不符合：限男性"

        if "限女性" in other or "限女" in other:
            if profile.gender == "女":
                return True, "性别符合：限女性"
            else:
                return False, "性别不符合：限女性"

        return True, "性别不限"


class GenderMatcher(BaseMatcher):
    """性别匹配器（独立版本）"""

    def __init__(self, user_gender: str):
        self.user_gender = user_gender.strip()

    def match(self, job_requirement: str, user_gender: str = None) -> Tuple[bool, str]:
        """匹配性别要求"""
        if user_gender is None:
            user_gender = self.user_gender

        other = str(job_requirement).strip()

        if "限男性" in other or "限男" in other:
            if user_gender == "男":
                return True, "性别符合：限男性"
            else:
                return False, "性别不符合：限男性"

        if "限女性" in other or "限女" in other:
            if user_gender == "女":
                return True, "性别符合：限女性"
            else:
                return False, "性别不符合：限女性"

        return True, "性别不限"


class HouseholdMatcher(BaseMatcher):
    """户籍匹配器（独立版本）"""

    def __init__(self, user_household: str):
        self.user_household = user_household.strip()

    def match(self, job_requirement: str, user_household: str = None) -> Tuple[bool, str]:
        """匹配户籍要求"""
        import re

        if user_household is None:
            user_household = self.user_household

        other = str(job_requirement).strip()

        # 检查是否有户籍限制
        if "限" in other and "户籍" in other:
            match = re.search(r"限([^户籍]+)户籍", other)
            if match:
                required = match.group(1).strip()
                if required in user_household:
                    return True, f"户籍符合：限{required}户籍"
                else:
                    return False, f"户籍不符合：限{required}户籍，你是{user_household}"

        return True, "户籍不限"


# 导出
__all__ = ["CompositeMatcher", "GenderMatcher", "HouseholdMatcher"]