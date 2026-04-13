#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM语义专业匹配器 - 实验版
"""
import os
import json
import re
from typing import Tuple, Dict, List
from functools import lru_cache


class LLMMajorMatcher:
    """
    LLM语义专业匹配器

    策略：
    1. 先走规则匹配（快速通道）
    2. 模糊情况走LLM（慢速但准）
    3. 结果缓存（避免重复调用）
    """

    def __init__(self, user_major: str, use_llm: bool = True):
        self.user_major = user_major.strip()
        self.use_llm = use_llm
        self.cache_file = ".llm_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """加载LLM缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        """保存LLM缓存"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def _get_cache_key(self, job_major: str) -> str:
        """生成缓存key"""
        return f"{self.user_major}|||{job_major}"

    def match(self, job_major: str) -> Tuple[bool, str, str]:
        """
        匹配专业

        返回: (是否匹配, 匹配说明, 匹配来源: rule/cache/llm)
        """
        job_major = str(job_major).strip()

        # === 第一层：规则匹配（明确情况）===
        rule_result = self._rule_match(job_major)
        if rule_result:
            return (*rule_result, "rule")

        # === 第二层：缓存匹配 ===
        cache_key = self._get_cache_key(job_major)
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            return (cached['match'], cached['reason'], "cache")

        # === 第三层：LLM匹配（模糊情况）===
        if self.use_llm:
            llm_result = self._llm_match(job_major)
            # 缓存结果
            self.cache[cache_key] = {
                'match': llm_result[0],
                'reason': llm_result[1]
            }
            self._save_cache()
            return (*llm_result, "llm")

        # 不用LLM时，返回不匹配
        return (False, f"无法确定匹配关系：[{self.user_major}] vs [{job_major}]", "none")

    def _rule_match(self, job_major: str) -> Tuple[bool, str]:
        """
        规则匹配 - 处理明确情况
        返回None表示需要走LLM
        """
        # 1. 不限
        if '不限' in job_major or job_major in ['无', 'nan', '', 'None']:
            return (True, "专业不限")

        # 2. 完全相等
        if self.user_major == job_major:
            return (True, f"完全匹配：{self.user_major}")

        # 3. 简单包含（如"经济学、金融学"包含"经济学"）
        if self.user_major in job_major and len(self.user_major) >= 4:
            return (True, f"包含匹配：{self.user_major} ∈ {job_major}")

        # 4. 类包含（如岗位是"经济学类"，用户是"经济学"）
        if f"{self.user_major}类" in job_major:
            return (True, f"大类包含：{self.user_major} ∈ {job_major}")

        # 5. 代码匹配（0201经济学类）
        if self._code_match(job_major):
            return (True, "专业代码匹配")

        # 6. 明显不匹配（快速排除）
        # 如果岗位是具体专业，用户专业完全不同
        job_keywords = self._extract_keywords(job_major)
        user_keywords = self._extract_keywords(self.user_major)

        # 如果提取的关键词完全无交集，且长度都>2，认为不匹配
        if len(job_keywords) > 0 and len(user_keywords) > 0:
            if not job_keywords & user_keywords:
                # 特殊情况：如果有"类"字，可能是大类，不直接排除
                if '类' not in job_major and '类' not in self.user_major:
                    return (False, f"关键词无交集：{self.user_major} vs {job_major}")

        # 需要LLM判断的情况返回None
        return None

    def _code_match(self, job_major: str) -> bool:
        """检查专业代码匹配"""
        # 常见专业代码映射
        code_map = {
            '0201': '经济学类',
            '0202': '财政学类',
            '0203': '金融学类',
            '0204': '经济与贸易类',
            '0712': '统计学类',
        }

        for code, category in code_map.items():
            if code in job_major:
                # 检查用户专业是否属于这个类别
                if self.user_major in self._get_category_majors(category):
                    return True
        return False

    def _get_category_majors(self, category: str) -> List[str]:
        """获取某类别的所有专业"""
        categories = {
            '经济学类': ['经济学', '经济统计学', '国民经济管理', '资源与环境经济学',
                      '商务经济学', '能源经济', '劳动经济学', '数字经济'],
            '财政学类': ['财政学', '税收学', '国际税收'],
            '金融学类': ['金融学', '金融工程', '保险学', '投资学', '金融数学',
                      '信用管理', '经济与金融', '精算学', '互联网金融', '金融科技'],
            '经济与贸易类': ['国际经济与贸易', '贸易经济'],
            '统计学类': ['统计学', '应用统计学', '数据科学', '生物统计学'],
        }
        return categories.get(category, [])

    def _extract_keywords(self, text: str) -> set:
        """提取专业关键词"""
        # 移除括号内容
        text = re.sub(r'[（(].*?[）)]', '', text)
        # 移除常见连接词
        text = re.sub(r'[、，,和或及]', ' ', text)
        # 分词（按类分）
        words = []
        for part in text.split():
            part = part.strip()
            if len(part) >= 2:
                # 移除"类"、"学"等后缀
                if part.endswith('类'):
                    words.append(part[:-1])
                elif part.endswith('学') and len(part) > 3:
                    words.append(part[:-1])
                else:
                    words.append(part)
        return set(words)

    def _llm_match(self, job_major: str) -> Tuple[bool, str]:
        """
        LLM语义匹配
        使用简单的启发式规则模拟LLM行为
        （实际部署时可接入Claude/GPT API）
        """
        # 这里使用规则模拟LLM的语义理解
        # 实际使用时应该调用LLM API

        # 提取核心专业词
        user_core = self._get_core_major(self.user_major)
        job_cores = [self._get_core_major(m) for m in job_major.replace('、', ',').replace('，', ',').split(',')]

        # 检查是否同一大类
        user_category = self._get_major_category(self.user_major)
        job_categories = [self._get_major_category(j) for j in job_cores]

        if user_category and user_category in job_categories:
            return (True, f"LLM语义匹配：{self.user_major}属于{user_category}，岗位要求包含该大类")

        # 近似匹配（如"金融学" vs "经济学类"）
        if self._is_related_major(user_core, job_cores):
            return (True, f"LLM关联匹配：{self.user_major}与{job_major}属于相近专业")

        return (False, f"LLM判定不匹配：{self.user_major}与{job_major}专业差异较大")

    def _get_core_major(self, major: str) -> str:
        """获取专业核心词"""
        # 移除代码
        major = re.sub(r'[（(].*?[）)]', '', major)
        # 移除类字
        if major.endswith('类'):
            major = major[:-1]
        return major.strip()

    def _get_major_category(self, major: str) -> str:
        """获取专业所属大类"""
        major = self._get_core_major(major)

        # 经济金融类
        if any(kw in major for kw in ['经济', '金融', '财政', '贸易', '税务', '保险', '投资']):
            return '经济金融类'
        # 统计学类
        if any(kw in major for kw in ['统计', '数据', '数学']):
            return '统计学类'
        # 法学类
        if any(kw in major for kw in ['法学', '法律']):
            return '法学类'
        # 教育类
        if any(kw in major for kw in ['教育', '教学', '师范']):
            return '教育学类'
        # 医学类
        if any(kw in major for kw in ['医学', '临床', '护理', '药学']):
            return '医学类'
        # 计算机类
        if any(kw in major for kw in ['计算机', '软件', '信息', '网络', '大数据']):
            return '计算机类'

        return None

    def _is_related_major(self, user_core: str, job_cores: List[str]) -> bool:
        """检查是否关联专业（模拟LLM语义理解）"""
        # 定义专业关联网络
        related_groups = [
            {'经济学', '金融学', '财政学', '税收学', '保险学', '投资学', '贸易', '经济统计'},
            {'计算机', '软件工程', '信息', '网络', '大数据', '人工智能'},
            {'法学', '法律', '知识产权', '监狱学'},
        ]

        for group in related_groups:
            user_in = any(user_core in g or g in user_core for g in group)
            job_in = any(any(j in g or g in j for g in group) for j in job_cores)

            if user_in and job_in:
                return True

        return False


def test_matcher():
    """测试LLM匹配器"""
    print("=" * 80)
    print("LLM语义专业匹配器 - 测试")
    print("=" * 80)

    # 测试案例：(用户专业, 岗位要求, 期望结果)
    test_cases = [
        # 明确情况 - 应该走rule
        ("经济学", "不限", True),
        ("经济学", "经济学", True),
        ("经济学", "经济学类", True),
        ("经济学", "经济学类（0201）", True),

        # 包含情况
        ("经济学", "经济学、金融学", True),

        # 代码匹配
        ("经济学", "本科：0201经济学类", True),

        # 模糊情况 - 应该走LLM或cache
        ("金融学", "经济学类", True),  # 相关
        ("经济统计学", "经济学类", True),  # 属于
        ("国际经济与贸易", "经济学类", True),  # 相关

        # 不匹配情况
        ("经济学", "临床医学", False),
        ("计算机科学", "法学类", False),

        # 复杂情况
        ("经济学", "本科及以上，学士及以上，经济学类（0201）、财政学类（0202）、金融学类（0203）", True),
    ]

    matcher = LLMMajorMatcher("经济学", use_llm=True)

    correct = 0
    total = len(test_cases)

    for user_major, job_major, expected in test_cases:
        matcher.user_major = user_major
        match, reason, source = matcher.match(job_major)

        status = "[OK]" if match == expected else "[FAIL]"
        if match == expected:
            correct += 1

        print(f"\n{status} [{source}]")
        print(f"   用户: {user_major}")
        print(f"   岗位: {job_major[:50]}{'...' if len(job_major) > 50 else ''}")
        print(f"   结果: {'匹配' if match else '不匹配'} (期望: {'匹配' if expected else '不匹配'})")
        print(f"   说明: {reason}")

    print("\n" + "=" * 80)
    print(f"测试结果: {correct}/{total} = {correct/total*100:.1f}%")
    print("=" * 80)

    # 显示缓存统计
    print(f"\n缓存统计: {len(matcher.cache)} 条记录")


if __name__ == "__main__":
    test_matcher()
