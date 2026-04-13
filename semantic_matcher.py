#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义匹配器 - 处理学历、户籍、工作年限等模糊表达
使用规则+语义理解的方式处理各种非标准化输入
"""
import re
from typing import Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


class EducationLevel(Enum):
    """学历等级"""
    UNKNOWN = 0
    ZHUANKE = 1      # 专科
    BENKE = 2        # 本科
    YANJIUSHENG = 3  # 硕士研究生
    BOSHI = 4        # 博士研究生


class MatchResult:
    """匹配结果"""
    def __init__(self, match: bool, reason: str, confidence: float = 1.0):
        self.match = match
        self.reason = reason
        self.confidence = confidence

    def __repr__(self):
        return f"MatchResult(match={self.match}, reason='{self.reason}', confidence={self.confidence})"


class EducationMatcher:
    """
    学历语义匹配器

    处理各种学历表达方式：
    - "本科及以上"、"本科以上"、"全日制本科"
    - "大专"、"专科"、"高职"
    - "研究生"、"硕士"、"硕士研究生"
    - "博士"、"博士研究生"
    """

    # 学历关键词映射
    EDUCATION_KEYWORDS = {
        EducationLevel.ZHUANKE: ['专科', '大专', '高职', '高专', '专科生', '大专生'],
        EducationLevel.BENKE: ['本科', '大学本科', '全日制本科', '本科生', '学士'],
        EducationLevel.YANJIUSHENG: ['硕士', '研究生', '硕士研究生', '硕士生', '全日制硕士'],
        EducationLevel.BOSHI: ['博士', '博士研究生', '博士生', '全日制博士']
    }

    # 学历等级数值
    LEVEL_VALUES = {
        EducationLevel.UNKNOWN: 0,
        EducationLevel.ZHUANKE: 1,
        EducationLevel.BENKE: 2,
        EducationLevel.YANJIUSHENG: 3,
        EducationLevel.BOSHI: 4
    }

    def __init__(self, user_education: str):
        self.user_education = self._normalize(user_education)
        self.user_level = self._parse_level(self.user_education)

    def _normalize(self, edu: str) -> str:
        """标准化学历字符串"""
        if not edu:
            return ""
        edu = str(edu).strip().lower()
        # 移除常见干扰词
        edu = re.sub(r'(全日制|统招|普通|国家承认|国民教育)', '', edu)
        return edu.strip()

    def _parse_level(self, edu: str) -> EducationLevel:
        """解析学历等级"""
        if not edu:
            return EducationLevel.UNKNOWN

        for level, keywords in self.EDUCATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in edu:
                    return level

        return EducationLevel.UNKNOWN

    def match(self, job_education: str) -> MatchResult:
        """
        匹配学历要求

        Args:
            job_education: 岗位要求，如"本科及以上"、"全日制本科"

        Returns:
            MatchResult: 匹配结果
        """
        job_edu = self._normalize(job_education)

        if not job_edu or job_edu in ['不限', '无要求', 'nan', '']:
            return MatchResult(True, "学历不限", 1.0)

        # 检查"及以上"模式
        if '及以上' in job_edu or '以上' in job_edu:
            required_level = self._parse_level(job_edu.replace('及以上', '').replace('以上', ''))
            if required_level == EducationLevel.UNKNOWN:
                # 尝试直接解析
                required_level = self._parse_level(job_edu)

            if required_level != EducationLevel.UNKNOWN:
                user_value = self.LEVEL_VALUES[self.user_level]
                required_value = self.LEVEL_VALUES[required_level]

                if user_value >= required_value:
                    return MatchResult(
                        True,
                        f"学历符合：{self.user_education} >= {self._level_to_str(required_level)}",
                        1.0
                    )
                else:
                    return MatchResult(
                        False,
                        f"学历不足：{self.user_education} < {self._level_to_str(required_level)}",
                        1.0
                    )

        # 精确匹配
        job_level = self._parse_level(job_edu)
        if job_level != EducationLevel.UNKNOWN:
            if self.user_level == job_level:
                return MatchResult(True, f"学历匹配：{self.user_education}", 1.0)
            elif self.user_level.value > job_level.value:
                return MatchResult(True, f"学历符合：{self.user_education} 高于要求", 0.9)
            else:
                return MatchResult(False, f"学历不匹配：要求{job_edu}，你是{self.user_education}", 1.0)

        # 模糊匹配
        return self._fuzzy_match(job_edu)

    def _fuzzy_match(self, job_edu: str) -> MatchResult:
        """模糊匹配"""
        # 提取学历关键词
        job_keywords = set()
        user_keywords = set()

        for level, keywords in self.EDUCATION_KEYWORDS.items():
            for kw in keywords:
                if kw in job_edu:
                    job_keywords.add(level)
                if kw in self.user_education:
                    user_keywords.add(level)

        if job_keywords and user_keywords:
            # 取最高等级比较
            job_max = max(job_keywords, key=lambda x: x.value)
            user_max = max(user_keywords, key=lambda x: x.value)

            if user_max.value >= job_max.value:
                return MatchResult(True, f"学历符合：{self.user_education}", 0.8)
            else:
                return MatchResult(False, f"学历不足：{self.user_education}", 0.8)

        return MatchResult(False, f"无法判断学历匹配：{job_edu}", 0.5)

    def _level_to_str(self, level: EducationLevel) -> str:
        """等级转字符串"""
        mapping = {
            EducationLevel.ZHUANKE: "专科",
            EducationLevel.BENKE: "本科",
            EducationLevel.YANJIUSHENG: "硕士研究生",
            EducationLevel.BOSHI: "博士研究生"
        }
        return mapping.get(level, "未知")


class HouseholdMatcher:
    """
    户籍语义匹配器

    处理各种户籍表达方式：
    - "限济南市户籍"、"限本市户籍"
    - "山西省户籍"、"山东户籍"
    - "不限"、"无限制"
    - "限男性"、"限女性"（性别相关）
    """

    def __init__(self, user_household: str, user_gender: str = ""):
        self.user_household = self._normalize(user_household)
        self.user_gender = user_gender

    def _normalize(self, text: str) -> str:
        """标准化户籍字符串"""
        if not text:
            return ""
        text = str(text).strip()
        # 移除"省"、"市"、"县"等后缀统一处理
        text = re.sub(r'(省|市|县|区)$', '', text)
        return text

    def match_household(self, job_requirement: str) -> MatchResult:
        """
        匹配户籍要求

        Args:
            job_requirement: 岗位要求，如"限济南市户籍"

        Returns:
            MatchResult: 匹配结果
        """
        req = str(job_requirement).strip()

        if not req or req in ['不限', '无限制', 'nan', '']:
            return MatchResult(True, "户籍不限", 1.0)

        # 检查是否包含户籍关键词
        if '户籍' not in req and '户口' not in req:
            return MatchResult(True, "无户籍限制", 1.0)

        # 提取要求的地区
        # 模式1: "限XX户籍"
        match = re.search(r'限(.+?)户籍', req)
        if match:
            required_location = self._normalize(match.group(1))
            return self._check_location(required_location, req)

        # 模式2: "XX户籍"
        match = re.search(r'(.+?)户籍', req)
        if match:
            required_location = self._normalize(match.group(1))
            return self._check_location(required_location, req)

        # 模式3: "限本市/本地"
        if '本市' in req or '本地' in req:
            # 这里需要根据具体城市判断，简化处理
            return MatchResult(
                True,
                "本地户籍要求（需手动确认）",
                0.6
            )

        return MatchResult(True, "户籍要求不明确，默认通过", 0.5)

    def _check_location(self, required: str, original: str) -> MatchResult:
        """检查地区是否匹配"""
        if not self.user_household:
            return MatchResult(
                False,
                f"未提供户籍信息，岗位要求：{original}",
                0.8
            )

        # 完全匹配
        if required == self.user_household:
            return MatchResult(
                True,
                f"户籍匹配：{self.user_household}",
                1.0
            )

        # 包含关系（如"山东"包含"济南"）- 需要省份城市映射表
        CITY_TO_PROVINCE = {
            '济南': '山东', '青岛': '山东', '淄博': '山东', '枣庄': '山东', '东营': '山东',
            '烟台': '山东', '潍坊': '山东', '济宁': '山东', '泰安': '山东', '威海': '山东',
            '日照': '山东', '莱芜': '山东', '临沂': '山东', '德州': '山东', '聊城': '山东',
            '滨州': '山东', '菏泽': '山东',
            '太原': '山西', '大同': '山西', '阳泉': '山西', '长治': '山西', '晋城': '山西',
            '朔州': '山西', '晋中': '山西', '运城': '山西', '忻州': '山西', '临汾': '山西',
            '吕梁': '山西',
            '北京': '北京', '上海': '上海', '天津': '天津', '重庆': '重庆',
        }

        # 检查是否是省-市关系
        user_province = CITY_TO_PROVINCE.get(self.user_household)
        required_province = CITY_TO_PROVINCE.get(required)

        if user_province and required_province:
            if user_province == required_province:
                return MatchResult(
                    True,
                    f"户籍符合：{self.user_household}市属于{required}省",
                    0.9
                )

        # 检查是否是省包含市
        if required in ['山东', '山西', '河南', '河北', '湖南', '湖北', '广东', '广西']:
            if user_province == required:
                return MatchResult(
                    True,
                    f"户籍符合：{self.user_household}属于{required}省",
                    0.9
                )

        # 简单包含检查
        if required in self.user_household or self.user_household in required:
            return MatchResult(
                True,
                f"户籍符合：{self.user_household} 包含/属于 {required}",
                0.9
            )

        return MatchResult(
            False,
            f"户籍不符：要求{required}，你是{self.user_household}",
            0.9
        )

    def match_gender(self, job_requirement: str) -> MatchResult:
        """
        匹配性别要求

        Args:
            job_requirement: 岗位要求，如"限男性"

        Returns:
            MatchResult: 匹配结果
        """
        req = str(job_requirement).strip()

        if not req or req in ['不限', 'nan', '']:
            return MatchResult(True, "性别不限", 1.0)

        # 提取性别要求
        if '限男性' in req or '男性' in req:
            if self.user_gender == '男':
                return MatchResult(True, "性别符合：男性", 1.0)
            else:
                return MatchResult(False, "性别不符：限男性", 1.0)

        if '限女性' in req or '女性' in req:
            if self.user_gender == '女':
                return MatchResult(True, "性别符合：女性", 1.0)
            else:
                return MatchResult(False, "性别不符：限女性", 1.0)

        return MatchResult(True, "无性别限制", 1.0)


class ExperienceMatcher:
    """
    工作年限语义匹配器

    处理各种工作年限表达方式：
    - "2年以上"、"2年及以上"、"至少2年"
    - "应届毕业生"、"应届生"
    - "不限经验"、"无经验要求"
    - "3-5年工作经验"
    """

    def __init__(self, user_years: int = 0, is_fresh_graduate: bool = False):
        self.user_years = user_years
        self.is_fresh_graduate = is_fresh_graduate

    def match(self, job_requirement: str) -> MatchResult:
        """
        匹配工作年限要求

        Args:
            job_requirement: 岗位要求，如"2年以上"

        Returns:
            MatchResult: 匹配结果
        """
        req = str(job_requirement).strip().lower()

        if not req or req in ['不限', '无要求', 'nan', '']:
            return MatchResult(True, "工作年限不限", 1.0)

        # 检查是否要求应届生
        if '应届' in req:
            return self._match_fresh_graduate()

        # 检查"年以上"模式
        # 模式1: "X年以上"
        match = re.search(r'(\d+)年以上?', req)
        if match:
            required_years = int(match.group(1))
            return self._check_years(required_years, f"{required_years}年以上")

        # 模式2: "至少X年"
        match = re.search(r'至少(\d+)年', req)
        if match:
            required_years = int(match.group(1))
            return self._check_years(required_years, f"至少{required_years}年")

        # 模式3: "X-Y年"
        match = re.search(r'(\d+)[-\~到](\d+)年', req)
        if match:
            min_years = int(match.group(1))
            max_years = int(match.group(2))
            return self._check_range(min_years, max_years)

        # 模式4: 纯数字（默认年）
        match = re.search(r'(\d+)', req)
        if match:
            required_years = int(match.group(1))
            if required_years <= 10:  # 合理的年限范围
                return self._check_years(required_years, f"{required_years}年")

        return MatchResult(True, "工作年限要求不明确，默认通过", 0.5)

    def _match_fresh_graduate(self) -> MatchResult:
        """匹配应届生要求"""
        if self.is_fresh_graduate:
            return MatchResult(
                True,
                "符合应届生要求",
                1.0
            )
        else:
            return MatchResult(
                False,
                "不符合：限应届毕业生",
                1.0
            )

    def _check_years(self, required: int, description: str) -> MatchResult:
        """检查年限是否满足"""
        if self.user_years >= required:
            return MatchResult(
                True,
                f"工作年限符合：{self.user_years}年 >= {required}年",
                1.0
            )
        else:
            return MatchResult(
                False,
                f"工作年限不足：{self.user_years}年 < {required}年",
                1.0
            )

    def _check_range(self, min_years: int, max_years: int) -> MatchResult:
        """检查年限是否在范围内"""
        if min_years <= self.user_years <= max_years:
            return MatchResult(
                True,
                f"工作年限符合：{self.user_years}年在{min_years}-{max_years}年范围内",
                1.0
            )
        elif self.user_years < min_years:
            return MatchResult(
                False,
                f"工作年限不足：{self.user_years}年 < {min_years}年",
                1.0
            )
        else:
            return MatchResult(
                False,
                f"工作年限超限：{self.user_years}年 > {max_years}年",
                1.0
            )


class SemanticMatcher:
    """
    统一语义匹配器
    整合学历、户籍、工作年限等所有语义匹配功能
    """

    def __init__(self, profile: dict):
        """
        初始化语义匹配器

        Args:
            profile: 用户档案，包含education、household、gender、work_years等
        """
        self.education_matcher = EducationMatcher(profile.get('education', ''))
        self.household_matcher = HouseholdMatcher(
            profile.get('household', ''),
            profile.get('gender', '')
        )
        self.experience_matcher = ExperienceMatcher(
            profile.get('work_years', 0),
            profile.get('is_fresh_graduate', False)
        )

    def match_all(self, job_data: dict) -> dict:
        """
        对所有条件进行语义匹配

        Args:
            job_data: 岗位数据，包含education、household_requirement等

        Returns:
            dict: 各维度匹配结果
        """
        results = {
            'education': None,
            'household': None,
            'gender': None,
            'experience': None
        }

        # 学历匹配
        if 'education' in job_data:
            results['education'] = self.education_matcher.match(job_data['education'])

        # 户籍匹配
        if 'household_requirement' in job_data or 'other' in job_data:
            household_req = job_data.get('household_requirement', job_data.get('other', ''))
            results['household'] = self.household_matcher.match_household(household_req)

        # 性别匹配
        if 'gender_requirement' in job_data or 'other' in job_data:
            gender_req = job_data.get('gender_requirement', job_data.get('other', ''))
            results['gender'] = self.household_matcher.match_gender(gender_req)

        # 工作年限匹配
        if 'experience_requirement' in job_data or 'other' in job_data:
            exp_req = job_data.get('experience_requirement', job_data.get('other', ''))
            results['experience'] = self.experience_matcher.match(exp_req)

        return results

    def get_summary(self, results: dict) -> Tuple[bool, List[str], List[str]]:
        """
        获取匹配汇总

        Returns:
            (是否全部通过, 通过原因列表, 不通过原因列表)
        """
        all_passed = True
        passed_reasons = []
        failed_reasons = []

        for dimension, result in results.items():
            if result is None:
                continue

            if result.match:
                passed_reasons.append(f"{dimension}: {result.reason}")
            else:
                all_passed = False
                failed_reasons.append(f"{dimension}: {result.reason}")

        return all_passed, passed_reasons, failed_reasons


# ============== 测试代码 ==============

def test_education_matcher():
    """测试学历匹配"""
    print("=" * 80)
    print("学历语义匹配测试")
    print("=" * 80)

    test_cases = [
        # (用户学历, 岗位要求, 预期结果)
        ("本科", "本科及以上", True),
        ("硕士研究生", "本科及以上", True),
        ("专科", "本科及以上", False),
        ("本科", "全日制本科", True),
        ("硕士研究生", "研究生", True),
        ("博士研究生", "硕士", True),
        ("大专", "专科", True),
        ("本科", "大专及以上", True),
    ]

    for user_edu, job_edu, expected in test_cases:
        matcher = EducationMatcher(user_edu)
        result = matcher.match(job_edu)
        status = "[OK]" if result.match == expected else "[FAIL]"
        print(f"\n{status} {user_edu} vs {job_edu}")
        print(f"    结果: {'通过' if result.match else '不通过'}")
        print(f"    原因: {result.reason}")
        print(f"    置信度: {result.confidence}")


def test_household_matcher():
    """测试户籍匹配"""
    print("\n" + "=" * 80)
    print("户籍语义匹配测试")
    print("=" * 80)

    test_cases = [
        # (用户户籍, 岗位要求, 预期结果)
        ("济南市", "限济南市户籍", True),
        ("济南市", "山东省户籍", True),  # 济南属于山东
        ("青岛市", "限济南市户籍", False),
        ("", "不限户籍", True),
        ("济南市", "不限", True),
    ]

    for user_hh, job_req, expected in test_cases:
        matcher = HouseholdMatcher(user_hh)
        result = matcher.match_household(job_req)
        status = "[OK]" if result.match == expected else "[FAIL]"
        print(f"\n{status} 户籍:{user_hh} vs 要求:{job_req}")
        print(f"    结果: {'通过' if result.match else '不通过'}")
        print(f"    原因: {result.reason}")

    # 测试性别匹配
    print("\n--- 性别匹配测试 ---")
    gender_cases = [
        ("男", "限男性", True),
        ("女", "限男性", False),
        ("男", "不限", True),
    ]

    for user_gender, job_req, expected in gender_cases:
        matcher = HouseholdMatcher("济南市", user_gender)
        result = matcher.match_gender(job_req)
        status = "[OK]" if result.match == expected else "[FAIL]"
        print(f"{status} 性别:{user_gender} vs 要求:{job_req} -> {'通过' if result.match else '不通过'}")


def test_experience_matcher():
    """测试工作年限匹配"""
    print("\n" + "=" * 80)
    print("工作年限语义匹配测试")
    print("=" * 80)

    test_cases = [
        # (用户年限, 是否应届, 岗位要求, 预期结果)
        (5, False, "2年以上", True),
        (1, False, "2年以上", False),
        (0, True, "应届毕业生", True),
        (3, False, "应届毕业生", False),
        (4, False, "3-5年工作经验", True),
        (6, False, "3-5年工作经验", False),
        (0, False, "不限经验", True),
    ]

    for user_years, is_fresh, job_req, expected in test_cases:
        matcher = ExperienceMatcher(user_years, is_fresh)
        result = matcher.match(job_req)
        status = "[OK]" if result.match == expected else "[FAIL]"
        fresh_tag = "(应届)" if is_fresh else ""
        print(f"\n{status} 工作{user_years}年{fresh_tag} vs {job_req}")
        print(f"    结果: {'通过' if result.match else '不通过'}")
        print(f"    原因: {result.reason}")


def test_unified_matcher():
    """测试统一匹配器"""
    print("\n" + "=" * 80)
    print("统一语义匹配器测试")
    print("=" * 80)

    profile = {
        'education': '硕士研究生',
        'household': '济南市',
        'gender': '男',
        'work_years': 3,
        'is_fresh_graduate': False
    }

    job_data = {
        'education': '本科及以上',
        'household_requirement': '限济南市户籍',
        'gender_requirement': '不限',
        'experience_requirement': '2年以上'
    }

    matcher = SemanticMatcher(profile)
    results = matcher.match_all(job_data)

    print("\n用户档案:")
    for k, v in profile.items():
        print(f"  {k}: {v}")

    print("\n岗位要求:")
    for k, v in job_data.items():
        print(f"  {k}: {v}")

    print("\n匹配结果:")
    for dimension, result in results.items():
        if result:
            status = "✓ 通过" if result.match else "✗ 不通过"
            print(f"  {dimension}: {status} - {result.reason}")

    all_passed, passed_reasons, failed_reasons = matcher.get_summary(results)
    print(f"\n汇总: {'全部通过' if all_passed else '有不符合项'}")
    if failed_reasons:
        print("不符合项:")
        for reason in failed_reasons:
            print(f"  - {reason}")


if __name__ == "__main__":
    test_education_matcher()
    test_household_matcher()
    test_experience_matcher()
    test_unified_matcher()
