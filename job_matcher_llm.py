#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
岗位筛选匹配引擎 - LLM增强版

在原有规则匹配基础上，增加LLM语义匹配作为第三层判断

使用方法:
1. 常规模式（纯规则）: JobMatcher(config_path)
2. LLM模式: JobMatcher(config_path, use_llm=True)
3. 需要设置 ANTHROPIC_API_KEY 环境变量
"""
import os
import sys
import json
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum
from datetime import datetime

# 导入原模块
from job_matcher import (
    MatchLevel, Job, UserProfile,
    EducationMatcher, GenderMatcher, HouseholdMatcher, JobMatcher as BaseJobMatcher
)
from llm_matcher_real import RealLLMMajorMatcher


class LLMEnhancedMajorMatcher:
    """
    LLM增强版专业匹配器

    三层架构:
    1. 规则层: 处理明确情况（不限、完全相等、包含）
    2. 缓存层: 已查询过的专业对
    3. LLM层: 语义模糊判断（同大类、相关专业）
    """

    def __init__(self, user_major: str, use_llm: bool = False, api_key: str = None):
        self.user_major = user_major.strip()
        self.use_llm = use_llm
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        # 初始化LLM匹配器（如果启用）
        if self.use_llm:
            self.llm_matcher = RealLLMMajorMatcher(user_major, self.api_key)
        else:
            self.llm_matcher = None

        # 基础规则匹配器
        self._init_basic_rules()

    def _init_basic_rules(self):
        """初始化基础规则"""
        # 专业大类映射
        self.major_categories = {
            '经济学类': ['经济学', '经济统计学', '国民经济管理', '资源与环境经济学',
                      '商务经济学', '能源经济', '劳动经济学', '数字经济'],
            '财政学类': ['财政学', '税收学', '国际税收'],
            '金融学类': ['金融学', '金融工程', '保险学', '投资学', '金融数学',
                      '信用管理', '经济与金融', '精算学', '互联网金融', '金融科技'],
            '经济与贸易类': ['国际经济与贸易', '贸易经济'],
            '统计学类': ['统计学', '应用统计学', '数据科学', '生物统计学'],
        }

        # 代码映射
        self.code_map = {
            '0201': '经济学类',
            '0202': '财政学类',
            '0203': '金融学类',
            '0204': '经济与贸易类',
            '0712': '统计学类',
        }

    def match(self, job_major: str) -> Tuple[bool, str, str]:
        """
        三级匹配

        返回: (是否匹配, 说明, 来源)
        """
        job_major = str(job_major).strip()

        # === Layer 1: 规则匹配 ===
        rule_result = self._rule_match(job_major)
        if rule_result is not None:
            return (rule_result[0], rule_result[1], "rule")

        # === Layer 2 & 3: LLM匹配（如果启用）===
        if self.use_llm and self.llm_matcher:
            result = self.llm_matcher.match(job_major)
            return (result.match, result.reason, result.source)

        # 未启用LLM时，使用本地语义规则
        return self._local_semantic_match(job_major)

    def _rule_match(self, job_major: str) -> Optional[Tuple[bool, str]]:
        """规则匹配 - 明确情况"""
        # 1. 不限
        if not job_major or "不限" in job_major or job_major.lower() in ['无', 'nan', '', 'none']:
            return (True, "专业不限")

        # 2. 完全相等
        if self.user_major == job_major:
            return (True, f"完全匹配：{self.user_major}")

        # 3. 直接包含
        if self.user_major in job_major and len(self.user_major) >= 4:
            return (True, f"包含匹配：{self.user_major}")

        # 4. 大类包含
        if f"{self.user_major}类" in job_major:
            return (True, f"大类包含：{self.user_major} ∈ {job_major}")

        # 5. 代码匹配
        code_result = self._match_by_code(job_major)
        if code_result:
            return code_result

        # 6. 明显不匹配
        if self._clearly_mismatch(job_major):
            return (False, f"专业明显不匹配：{self.user_major} vs {job_major}")

        return None

    def _match_by_code(self, job_major: str) -> Optional[Tuple[bool, str]]:
        """通过专业代码匹配"""
        # 用户专业所属类别
        user_cats = []
        for cat, majors in self.major_categories.items():
            if self.user_major in majors:
                user_cats.append(cat)

        # 检查岗位代码
        for code, category in self.code_map.items():
            if code in job_major:
                if category in user_cats:
                    return (True, f"代码匹配：{code}→{category}")

        return None

    def _clearly_mismatch(self, job_major: str) -> bool:
        """明显不匹配的字段"""
        # 简单关键词判断
        medical = ["医学", "临床", "护理", "药学", "口腔"]
        law = ["法学", "法律", "律师"]
        edu = ["教育", "师范", "学前"]

        user = self.user_major

        # 用户是医学，岗位非医学
        if any(k in user for k in medical):
            if not any(k in job_major for k in medical + ["不限"]):
                return True

        # 用户是法学，岗位非法学
        if any(k in user for k in law):
            if not any(k in job_major for k in law + ["不限"]):
                return True

        return False

    def _local_semantic_match(self, job_major: str) -> Tuple[bool, str, str]:
        """本地语义匹配（无LLM时使用）"""
        # 提取核心词
        user_core = self._extract_core(self.user_major)
        job_parts = re.split(r'[、，,；;]', job_major)
        job_cores = [self._extract_core(p) for p in job_parts]

        # 检查是否同一大类
        user_cat = self._get_category(user_core)
        job_cats = [self._get_category(j) for j in job_cores]

        if user_cat and user_cat in job_cats:
            return (True, f"语义匹配：{self.user_major}属于{user_cat}", "semantic")

        # 检查关联专业
        for job_core in job_cores:
            if self._is_related(user_core, job_core):
                return (True, f"关联匹配：{self.user_major}与{job_major}相关", "semantic")

        return (False, f"不匹配：{self.user_major}与{job_major}", "semantic")

    def _extract_core(self, text: str) -> str:
        """提取专业核心词"""
        text = re.sub(r'[（(].*?[）)]', '', text)
        for suffix in ["类", "专业", "方向"]:
            if text.endswith(suffix):
                text = text[:-len(suffix)]
        return text.strip()

    def _get_category(self, major: str) -> Optional[str]:
        """获取专业类别"""
        categories = [
            ("经济金融", ["经济", "金融", "财政", "税务", "贸易", "保险", "投资", "统计"]),
            ("法学", ["法学", "法律", "知识产权"]),
            ("教育学", ["教育", "师范", "学前", "教学"]),
            ("理学", ["数学", "物理", "化学", "生物", "统计"]),
            ("工学", ["计算机", "软件", "网络", "信息", "电子", "机械", "土木"]),
            ("医学", ["临床", "医学", "护理", "药学", "口腔"]),
            ("管理学", ["管理", "行政", "工商", "人力", "物流"]),
            ("农学", ["农学", "林学", "园艺", "畜牧", "兽医"]),
        ]

        for cat, keywords in categories:
            if any(kw in major for kw in keywords):
                return cat
        return None

    def _is_related(self, m1: str, m2: str) -> bool:
        """检查专业是否相关"""
        related_groups = [
            {"经济学", "金融学", "财政学", "税收学", "保险学", "投资学", "贸易", "统计"},
            {"计算机", "软件", "网络", "信息", "大数据", "人工智能"},
        ]

        for group in related_groups:
            in1 = any(m1 in g or g in m1 for g in group)
            in2 = any(m2 in g or g in m2 for g in group)
            if in1 and in2:
                return True
        return False


class JobMatcherLLM(BaseJobMatcher):
    """
    LLM增强版岗位匹配引擎

    继承原JobMatcher，替换专业匹配器为LLM增强版
    """

    def __init__(self, config_path: str = "config.yaml", use_llm: bool = False):
        # 调用父类初始化
        super().__init__(config_path)

        # 替换专业匹配器为LLM增强版
        self.major_matcher = LLMEnhancedMajorMatcher(
            self.profile.major,
            use_llm=use_llm
        )

        self.use_llm = use_llm
        self.match_stats = {"rule": 0, "cache": 0, "llm": 0, "semantic": 0}

    def match(self, job: Job) -> Job:
        """
        执行匹配（重写以收集统计）
        """
        # 专业匹配
        major_ok, major_msg, major_source = self.major_matcher.match(job.major)
        self.match_stats[major_source] = self.match_stats.get(major_source, 0) + 1

        # 调用父类的其余匹配逻辑
        # ...这里简化处理，实际应该调用父类完整逻辑

        # 为简化，直接返回父类匹配结果
        job = super().match(job)

        # 更新匹配说明（如果有LLM信息）
        if self.use_llm and major_source in ["llm", "semantic"]:
            # 将语义匹配信息添加到匹配原因
            if major_ok and major_msg not in job.match_reasons:
                job.match_reasons.insert(0, major_msg)

        return job

    def get_stats(self) -> Dict:
        """获取匹配统计"""
        return self.match_stats.copy()


def test_comparison():
    """
    对比测试：原规则 vs LLM增强版
    """
    print("=" * 80)
    print("专业匹配器对比测试")
    print("=" * 80)

    # 模糊测试案例
    fuzzy_cases = [
        ("金融学", "经济学类"),  # 相关但不同
        ("投资学", "经济学类"),  # 相关但不同
        ("经济统计学", "经济学类"),  # 属于
        ("保险学", "金融学类"),  # 属于
        ("税收学", "财政学类"),  # 属于
        ("国际经济与贸易", "经济与贸易类"),  # 属于
        ("应用统计学", "统计学类"),  # 属于
        ("统计学", "经济学类"),  # 相关但不同类
        ("会计学", "经济学类"),  # 相关但不同
        ("经济学", "经济学、金融学、财政学"),  # 列表包含
        ("经济学", "经济学类（0201）、财政学类（0202）"),  # 代码+大类
    ]

    print("\n对比测试结果:\n")

    from job_matcher import MajorMatcher as OldMatcher

    for user_major, job_major in fuzzy_cases:
        print(f"\n用户: {user_major} | 岗位: {job_major}")
        print("-" * 60)

        # 原匹配器
        old = OldMatcher(user_major)
        old_ok, old_msg = old.match(job_major)
        status_old = "[OK]" if old_ok else "[NO]"
        print(f"原规则: {status_old} {old_msg}")

        # LLM增强版（本地语义）
        new = LLMEnhancedMajorMatcher(user_major, use_llm=False)
        new_ok, new_msg, new_src = new.match(job_major)
        status_new = "[OK]" if new_ok else "[NO]"
        print(f"语义版: {status_new} [{new_src}] {new_msg}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_comparison()
