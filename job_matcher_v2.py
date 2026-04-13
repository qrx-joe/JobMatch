#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
岗位筛选匹配引擎 V2 - 支持更多筛选条件
"""
import pandas as pd
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum
import yaml


class MatchLevel(Enum):
    PERFECT = "完全符合"      # 绿色
    PARTIAL = "可能符合"      # 黄色
    MISMATCH = "不符合"       # 红色


@dataclass
class Job:
    """岗位数据模型"""
    sheet_name: str = ""           # 所属地市
    index: int = 0                 # 序号
    unit: str = ""                 # 服务单位
    job_type: str = ""             # 岗位类型
    service_category: str = ""     # 服务类别
    recruit_count: int = 1         # 招募人数

    education: str = ""            # 学历要求
    degree: str = ""               # 学位要求
    major: str = ""                # 专业要求
    qualifications: str = ""       # 相关资格
    other: str = ""                # 其他要求（性别/户籍/应届等）
    phone: str = ""                # 联系电话
    contact: str = ""              # 联系人

    applicants: int = 0            # 填报信息人数
    approved: int = 0              # 初审通过人数
    paid: int = 0                  # 缴费人数

    match_level: MatchLevel = MatchLevel.MISMATCH
    match_score: int = 0
    match_reasons: List[str] = field(default_factory=list)
    mismatch_reasons: List[str] = field(default_factory=list)
    competition_ratio: float = 0.0


@dataclass
class UserProfile:
    """用户档案"""
    major: str = ""
    education: str = ""
    degree: str = ""
    gender: str = ""
    household: str = ""
    is_fresh_graduate: bool = False      # 是否应届
    political_status: str = "群众"        # 政治面貌
    qualifications: List[str] = field(default_factory=list)  # 拥有的证书
    work_years: int = 0                   # 工作年限
    target_cities: List[str] = field(default_factory=list)


class QualificationMatcher:
    """资格证书匹配器"""

    # 常见资格证书及其别名
    QUALIFICATION_ALIASES = {
        '教师资格证': ['教师资格证', '教师资格'],
        '法律职业资格': ['法律职业资格', '法律职业资格证', '律师资格'],
        '医师资格证': ['医师资格证', '执业医师', '执业助理医师'],
        '护士资格证': ['护士资格证', '护士执业证'],
        '会计证': ['会计证', '会计从业资格', '会计专业技术资格'],
        '注册会计师': ['注册会计师', 'CPA'],
        '建造师证': ['建造师', '一级建造师', '二级建造师'],
    }

    def __init__(self, user_qualifications: List[str]):
        self.user_quals = [q.strip() for q in (user_qualifications or [])]

    def match(self, job_qual: str) -> Tuple[bool, str]:
        """
        匹配资格证书要求
        """
        job_qual = str(job_qual).strip()

        # 空或无要求
        if not job_qual or job_qual in ['无', '不限', 'nan', '']:
            return True, "无资格要求"

        # 检查是否要求特定资格
        required_quals = self._extract_qualifications(job_qual)

        if not required_quals:
            return True, "资格要求不明确"

        # 检查用户是否拥有
        for req in required_quals:
            if self._has_qualification(req):
                return True, f"拥有资格：{req}"

        return False, f"缺少资格：{', '.join(required_quals)}"

    def _extract_qualifications(self, text: str) -> List[str]:
        """从文本中提取资格要求"""
        quals = []

        for qual_name, aliases in self.QUALIFICATION_ALIASES.items():
            for alias in aliases:
                if alias in text:
                    quals.append(qual_name)
                    break

        return quals

    def _has_qualification(self, required: str) -> bool:
        """检查用户是否有某资格"""
        for user_qual in self.user_quals:
            if required in user_qual or user_qual in required:
                return True

            # 检查别名
            if required in self.QUALIFICATION_ALIASES:
                for alias in self.QUALIFICATION_ALIASES[required]:
                    if alias in user_qual:
                        return True

        return False


class OtherRequirementsMatcher:
    """其他要求匹配器（性别、户籍、应届、党员等）"""

    def __init__(self, profile: UserProfile, rules: dict):
        self.profile = profile
        self.rules = rules

    def match(self, other_field: str) -> Tuple[bool, List[str], List[str]]:
        """
        匹配其他要求
        返回: (是否通过, 匹配说明列表, 不匹配原因列表)
        """
        other = str(other_field).strip()
        match_reasons = []
        mismatch_reasons = []

        if not other or other in ['无', 'nan', '']:
            return True, ["无其他要求"], []

        # 1. 性别限制
        gender_ok, gender_msg = self._match_gender(other)
        if gender_ok:
            match_reasons.append(gender_msg)
        else:
            mismatch_reasons.append(gender_msg)

        # 2. 户籍限制
        household_ok, household_msg = self._match_household(other)
        if household_ok:
            match_reasons.append(household_msg)
        else:
            mismatch_reasons.append(household_msg)

        # 3. 应届限制
        fresh_ok, fresh_msg = self._match_fresh_graduate(other)
        if fresh_ok:
            match_reasons.append(fresh_msg)
        else:
            mismatch_reasons.append(fresh_msg)

        # 4. 党员限制
        party_ok, party_msg = self._match_political_status(other)
        if party_ok:
            match_reasons.append(party_msg)
        else:
            mismatch_reasons.append(party_msg)

        # 5. 工作年限
        exp_ok, exp_msg = self._match_experience(other)
        if exp_ok:
            match_reasons.append(exp_msg)
        else:
            mismatch_reasons.append(exp_msg)

        # 判断是否通过
        all_ok = gender_ok and household_ok and fresh_ok and party_ok and exp_ok

        return all_ok, match_reasons, mismatch_reasons

    def _match_gender(self, text: str) -> Tuple[bool, str]:
        """匹配性别要求"""
        if '限男性' in text:
            if self.profile.gender == '男':
                return True, "性别符合：限男性"
            else:
                return self.rules.get('性别限制', {}).get('模式', 'strict') != 'strict', "性别不符合：限男性"

        if '限女性' in text:
            if self.profile.gender == '女':
                return True, "性别符合：限女性"
            else:
                return self.rules.get('性别限制', {}).get('模式', 'strict') != 'strict', "性别不符合：限女性"

        return True, "性别不限"

    def _match_household(self, text: str) -> Tuple[bool, str]:
        """匹配户籍要求"""
        match = re.search(r'限(.+?)户籍', text)
        if match:
            required = match.group(1)
            if required in self.profile.household:
                return True, f"户籍符合：限{required}户籍"
            else:
                mode = self.rules.get('户籍匹配', {}).get('模式', 'loose')
                if mode == 'strict':
                    return False, f"户籍不符合：限{required}户籍"
                else:
                    return True, f"户籍不匹配但允许查看：限{required}户籍"

        return True, "户籍不限"

    def _match_fresh_graduate(self, text: str) -> Tuple[bool, str]:
        """匹配应届生要求"""
        if '应届' in text and '往届' not in text:
            if self.profile.is_fresh_graduate:
                return True, "符合应届生要求"
            else:
                mode = self.rules.get('应届生匹配', {}).get('模式', 'loose')
                if mode == 'strict':
                    return False, "不符合：限应届毕业生"
                else:
                    return True, "非应届但允许查看"

        if '往届' in text:
            if not self.profile.is_fresh_graduate:
                return True, "符合往届生要求"
            else:
                return True, "应届生可报往届岗位"

        return True, "不限应往届"

    def _match_political_status(self, text: str) -> Tuple[bool, str]:
        """匹配政治面貌要求"""
        if '中共党员' in text or '党员' in text:
            if self.profile.political_status in ['中共党员', '中共预备党员']:
                return True, "政治面貌符合：党员"
            else:
                mode = self.rules.get('政治面貌匹配', {}).get('模式', 'loose')
                if mode == 'strict':
                    return False, "政治面貌不符合：限党员"
                else:
                    return True, "非党员但允许查看"

        return True, "政治面貌不限"

    def _match_experience(self, text: str) -> Tuple[bool, str]:
        """匹配工作经验要求"""
        match = re.search(r'(\d+)年以上?', text)
        if match:
            required_years = int(match.group(1))
            if self.profile.work_years >= required_years:
                return True, f"工作经验符合：{self.profile.work_years}年 >= {required_years}年"
            else:
                return False, f"工作经验不足：{self.profile.work_years}年 < {required_years}年"

        return True, "无工作经验要求"


class JobMatcherV2:
    """增强版岗位匹配引擎"""

    def __init__(self, config_path: str = "config_full.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.profile = UserProfile(
            major=self.config['profile']['专业'],
            education=self.config['profile']['学历'],
            degree=self.config['profile']['学位'],
            gender=self.config['profile']['性别'],
            household=self.config['profile']['户籍'],
            is_fresh_graduate=self.config['profile'].get('是否应届', False),
            political_status=self.config['profile'].get('政治面貌', '群众'),
            qualifications=self.config['profile'].get('相关资格', []),
            work_years=self.config['profile'].get('工作年限', 0),
            target_cities=self.config['preference'].get('意向城市', [])
        )

        self.rules = self.config.get('rules', {})
        self.filter_config = self.config.get('filter', {})

        # 初始化专业匹配器（LLM增强版）
        from job_matcher_llm import LLMEnhancedMajorMatcher
        self.major_matcher = LLMEnhancedMajorMatcher(self.profile.major, use_llm=False)

    def match(self, job: Job) -> Job:
        """对单个岗位进行匹配"""
        checks = {}
        match_reasons = []
        mismatch_reasons = []
        score = 0

        # 1. 专业匹配
        major_ok, major_msg, major_source = self.major_matcher.match(job.major)
        checks['专业'] = major_ok
        if major_ok:
            score += 30
            match_reasons.append(major_msg)
        else:
            mismatch_reasons.append(major_msg)

        # 2. 学历匹配
        from job_matcher import EducationMatcher
        edu_matcher = EducationMatcher(self.profile.education)
        edu_ok, edu_msg = edu_matcher.match(job.education)
        checks['学历'] = edu_ok
        if edu_ok:
            score += 25
            match_reasons.append(edu_msg)
        else:
            mismatch_reasons.append(edu_msg)

        # 3. 学位匹配
        degree_ok, degree_msg = self._match_degree(job.degree)
        checks['学位'] = degree_ok
        if degree_ok:
            score += 10
            match_reasons.append(degree_msg)
        else:
            mismatch_reasons.append(degree_msg)

        # 4. 资格证书匹配
        qual_matcher = QualificationMatcher(self.profile.qualifications)
        qual_ok, qual_msg = qual_matcher.match(job.qualifications)
        checks['资格'] = qual_ok
        if qual_ok:
            score += 15
            match_reasons.append(qual_msg)
        else:
            mismatch_reasons.append(qual_msg)

        # 5. 其他要求匹配（性别、户籍、应届、党员等）
        other_matcher = OtherRequirementsMatcher(self.profile, self.rules)
        other_ok, other_reasons, other_mismatches = other_matcher.match(job.other)
        checks['其他'] = other_ok
        if other_ok:
            score += 15
            match_reasons.extend(other_reasons)
        mismatch_reasons.extend(other_mismatches)

        # 6. 城市偏好
        city_ok, city_score = self._match_city(job.sheet_name)
        if city_ok:
            score += city_score
            match_reasons.append(f"意向城市：{job.sheet_name}")
        else:
            score -= 5
            match_reasons.append(f"非意向城市：{job.sheet_name}")

        # 7. 竞争比检查
        if job.paid > 0 and job.recruit_count > 0:
            ratio = job.paid / job.recruit_count
            max_ratio = self.filter_config.get('最大竞争比', 100)
            if ratio > max_ratio:
                match_reasons.append(f"竞争比高({ratio:.0f}:1)")
                score -= 10

        # 计算竞争比
        if job.recruit_count > 0 and job.paid > 0:
            job.competition_ratio = job.paid / job.recruit_count

        # 确定匹配等级
        critical_checks = ['专业', '学历', '学位']
        all_critical = all(checks.get(k, False) for k in critical_checks)

        if all_critical and other_ok and qual_ok:
            if job.sheet_name in self.profile.target_cities:
                job.match_level = MatchLevel.PERFECT
            else:
                job.match_level = MatchLevel.PARTIAL
        elif all_critical:
            job.match_level = MatchLevel.PARTIAL
        else:
            job.match_level = MatchLevel.MISMATCH

        job.match_score = score
        job.match_reasons = match_reasons
        job.mismatch_reasons = mismatch_reasons

        return job

    def _match_degree(self, job_degree: str) -> Tuple[bool, str]:
        """匹配学位"""
        job_degree = str(job_degree).strip()

        if not job_degree or job_degree in ['无', '无要求', '不限', 'nan', '']:
            return True, "学位不限"

        user_degree = self.profile.degree

        if user_degree == job_degree:
            return True, f"学位匹配：{user_degree}"

        if '及以上' in job_degree:
            degree_levels = {'学士': 1, '硕士': 2, '博士': 3}
            user_level = degree_levels.get(user_degree, 0)
            job_level = degree_levels.get(job_degree.replace('及以上', ''), 0)
            if user_level >= job_level:
                return True, f"学位符合：{user_degree} >= {job_degree}"

        return False, f"学位不匹配：要求{job_degree}，你是{user_degree}"

    def _match_city(self, city: str) -> Tuple[bool, int]:
        """匹配意向城市"""
        if not self.profile.target_cities:
            return True, 5  # 无偏好，所有城市一样

        if city in self.profile.target_cities:
            # 按优先级给分
            idx = self.profile.target_cities.index(city)
            score = max(20 - idx * 5, 10)
            return True, score

        return False, 0


if __name__ == "__main__":
    # 测试
    matcher = JobMatcherV2()
    print(f"用户专业：{matcher.profile.major}")
    print(f"用户学历：{matcher.profile.education}")
    print(f"用户性别：{matcher.profile.gender}")
    print(f"用户户籍：{matcher.profile.household}")
    print(f"是否应届：{matcher.profile.is_fresh_graduate}")
    print(f"政治面貌：{matcher.profile.political_status}")
    print(f"资格证书：{matcher.profile.qualifications}")
