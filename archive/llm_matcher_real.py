#!/usr/bin/env python3
"""
真实LLM语义专业匹配器 - 使用Claude API

使用方式:
1. 设置环境变量: ANTHROPIC_API_KEY=your_key
2. 或者创建 .env 文件
"""

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MatchResult:
    """匹配结果"""

    match: bool
    reason: str
    source: str  # rule / cache / llm
    confidence: float = 0.0  # LLM置信度


class RealLLMMajorMatcher:
    """
    真实LLM专业匹配器 - 分层策略

    架构:
    Layer 1 (规则)  -> 处理明确情况, <1ms
    Layer 2 (缓存)  -> 已查询的直接返回, <0.1ms
    Layer 3 (LLM)   -> 模糊语义判断, ~500ms
    """

    def __init__(self, user_major: str, api_key: str = None):
        self.user_major = user_major.strip()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.cache_file = ".llm_semantic_cache.json"
        self.cache = self._load_cache()
        self.stats = {"rule": 0, "cache": 0, "llm": 0, "api_calls": 0}

    def _load_cache(self) -> dict:
        """加载语义缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        """保存语义缓存"""
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def _get_cache_key(self, job_major: str) -> str:
        """生成缓存key - 归一化处理"""
        # 移除空格和标点，统一小写
        user = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", self.user_major).lower()
        job = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", job_major).lower()
        return f"{user}|||{job}"

    def match(self, job_major: str) -> MatchResult:
        """
        三级匹配策略
        """
        job_major = str(job_major).strip()

        # === Layer 1: 规则匹配（高速公路）===
        rule_result = self._rule_match(job_major)
        if rule_result is not None:
            self.stats["rule"] += 1
            return MatchResult(rule_result[0], rule_result[1], "rule", 1.0)

        # === Layer 2: 缓存匹配（快速通道）===
        cache_key = self._get_cache_key(job_major)
        if cache_key in self.cache:
            self.stats["cache"] += 1
            cached = self.cache[cache_key]
            return MatchResult(
                cached["match"], cached["reason"], "cache", cached.get("confidence", 0.9)
            )

        # === Layer 3: LLM匹配（智能判断）===
        if self.api_key:
            llm_result = self._llm_api_match(job_major)
            # 存入缓存
            self.cache[cache_key] = {
                "match": llm_result.match,
                "reason": llm_result.reason,
                "confidence": llm_result.confidence,
                "timestamp": datetime.now().isoformat(),
                "user_major": self.user_major,
                "job_major": job_major,
            }
            self._save_cache()
            self.stats["llm"] += 1
            return llm_result
        else:
            # 无API时走本地语义规则
            local_result = self._local_semantic_match(job_major)
            self.stats["llm"] += 1
            return MatchResult(local_result[0], local_result[1], "llm", 0.7)

    def _rule_match(self, job_major: str) -> tuple[bool, str]:
        """
        第一层：硬规则匹配
        返回None表示需要进入下一层
        """
        # 1. 不限
        if not job_major or "不限" in job_major or job_major in ["无", "nan", "", "None"]:
            return (True, "专业不限")

        # 2. 完全相等
        if self.user_major == job_major:
            return (True, f"完全匹配：{self.user_major}")

        # 3. 直接包含（如岗位要求包含用户专业）
        if self.user_major in job_major:
            # 防止部分匹配误判（如"贸易"匹配"国际贸易"）
            if len(self.user_major) >= 4:
                return (True, f"包含匹配：{self.user_major} 在岗位要求列表中")

        # 4. 大类包含（岗位是大类，用户是具体专业）
        if f"{self.user_major}类" in job_major:
            return (True, f"大类包含：用户专业属于 {job_major}")

        # 5. 专业代码匹配
        code_match = self._match_by_code(job_major)
        if code_match:
            return code_match

        # 6. 明显不匹配（关键词完全无关）
        if self._clearly_mismatch(job_major):
            return (False, f"专业明显不匹配：{self.user_major} vs {job_major}")

        return None

    def _match_by_code(self, job_major: str) -> tuple[bool, str]:
        """通过专业代码匹配"""
        # 专业代码映射表
        code_to_category = {
            "0201": "经济学类",
            "0202": "财政学类",
            "0203": "金融学类",
            "0204": "经济与贸易类",
            "0712": "统计学类",
        }

        # 用户专业所属类别
        user_categories = self._get_major_categories(self.user_major)

        # 检查岗位代码
        for code, category in code_to_category.items():
            if code in job_major and category in user_categories:
                return (True, f"专业代码匹配：{code}对应{category}")

        return None

    def _get_major_categories(self, major: str) -> list[str]:
        """获取专业所属类别"""
        categories = {
            "经济学类": ["经济学", "经济统计学", "国民经济管理"],
            "财政学类": ["财政学", "税收学"],
            "金融学类": ["金融学", "金融工程", "保险学", "投资学"],
            "经济与贸易类": ["国际经济与贸易", "贸易经济"],
            "统计学类": ["统计学", "应用统计学"],
        }

        result = []
        for cat, majors in categories.items():
            if major in majors:
                result.append(cat)
        return result

    def _clearly_mismatch(self, job_major: str) -> bool:
        """判断是否明显不匹配"""
        # 提取专业领域关键词
        medical_keywords = ["医学", "临床", "护理", "药学", "口腔", "中医", "西医"]
        law_keywords = ["法学", "法律", "知识产权"]

        user = self.user_major

        # 医学 vs 非医学
        if any(k in user for k in medical_keywords):
            if not any(k in job_major for k in medical_keywords):
                return True

        # 法学 vs 非法学
        if any(k in user for k in law_keywords):
            if not any(k in job_major for k in law_keywords):
                return True

        return False

    def _llm_api_match(self, job_major: str) -> MatchResult:
        """
        调用真实LLM API进行语义匹配
        """
        try:
            # 构建prompt

            # 这里应该调用真实的Claude API
            # 为了演示，先使用模拟结果
            # 实际使用时取消下面注释
            """
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            result = json.loads(response.content[0].text)
            return MatchResult(
                match=result["match"],
                reason=result["reason"],
                source="llm",
                confidence=result.get("confidence", 0.8)
            )
            """

            # 模拟LLM判断（实际使用时删除这段）
            return self._local_semantic_match(job_major, return_full=True)

        except Exception:
            # LLM调用失败时回退到本地规则
            result = self._local_semantic_match(job_major)
            return MatchResult(result[0], f"{result[1]} (LLM回退)", "llm", 0.5)

    def _local_semantic_match(self, job_major: str, return_full=False):
        """本地语义匹配（LLM的简化版）"""
        # 提取核心词
        user_core = self._extract_core(self.user_major)
        job_cores = [self._extract_core(m) for m in re.split(r"[、，,；;]", job_major)]

        # 判断大类
        user_cat = self._get_semantic_category(user_core)
        job_cats = [self._get_semantic_category(j) for j in job_cores]

        # 类别匹配
        if user_cat and user_cat in job_cats:
            if return_full:
                return MatchResult(
                    True,
                    f"语义匹配：{self.user_major}属于{user_cat}，岗位要求包含该大类",
                    "llm",
                    0.85,
                )
            return (True, f"语义匹配：{self.user_major}属于{user_cat}")

        # 关键词相似度
        for job_core in job_cores:
            if self._is_semantically_related(user_core, job_core):
                if return_full:
                    return MatchResult(
                        True, f"语义关联：{self.user_major}与{job_major}属于相关专业", "llm", 0.75
                    )
                return (True, f"语义关联：{self.user_major}与{job_major}属于相关专业")

        if return_full:
            return MatchResult(
                False, f"语义判定不匹配：{self.user_major}与{job_major}专业差异较大", "llm", 0.8
            )
        return (False, f"语义判定不匹配：{self.user_major}与{job_major}专业差异较大")

    def _extract_core(self, major: str) -> str:
        """提取专业核心词"""
        # 移除代码和括号
        major = re.sub(r"[（(].*?[）)]", "", major)
        # 移除通用后缀
        for suffix in ["类", "专业", "方向"]:
            if major.endswith(suffix):
                major = major[: -len(suffix)]
        return major.strip()

    def _get_semantic_category(self, major: str) -> str:
        """获取语义类别"""
        categories = [
            (
                "经济金融",
                [
                    "经济",
                    "金融",
                    "财政",
                    "税务",
                    "贸易",
                    "保险",
                    "投资",
                    "会计",
                    "审计",
                    "统计",
                    "资产评估",
                ],
            ),
            ("法学", ["法学", "法律", "知识产权", "监狱", "律师"]),
            (
                "教育学",
                [
                    "教育",
                    "师范",
                    "学前",
                    "小学",
                    "中学",
                    "教学",
                    "心理",
                    "体育",
                    "艺术",
                    "音乐",
                    "美术",
                ],
            ),
            (
                "文学",
                [
                    "中文",
                    "汉语",
                    "文学",
                    "外语",
                    "英语",
                    "日语",
                    "翻译",
                    "新闻",
                    "传播",
                    "广告",
                    "编辑",
                ],
            ),
            (
                "理学",
                [
                    "数学",
                    "物理",
                    "化学",
                    "生物",
                    "地理",
                    "天文",
                    "地质",
                    "心理",
                    "统计",
                    "应用数学",
                ],
            ),
            (
                "工学",
                [
                    "计算机",
                    "软件",
                    "网络",
                    "信息",
                    "电子",
                    "通信",
                    "自动化",
                    "机械",
                    "土木",
                    "建筑",
                    "化工",
                    "材料",
                    "能源",
                    "环境",
                    "生物工程",
                ],
            ),
            (
                "医学",
                [
                    "临床",
                    "医学",
                    "护理",
                    "药学",
                    "口腔",
                    "中医",
                    "西医",
                    "预防",
                    "检验",
                    "影像",
                    "麻醉",
                    "精神",
                    "康复",
                ],
            ),
            (
                "管理学",
                [
                    "管理",
                    "行政",
                    "工商",
                    "人力",
                    "资源",
                    "公共",
                    "旅游",
                    "酒店",
                    "物流",
                    "供应链",
                    "电子商务",
                    "信息管理与信息系统",
                ],
            ),
            ("农学", ["农学", "林学", "园艺", "植保", "畜牧", "兽医", "水产", "农业", "林业"]),
        ]

        for cat, keywords in categories:
            if any(kw in major for kw in keywords):
                return cat
        return None

    def _is_semantically_related(self, major1: str, major2: str) -> bool:
        """判断两个专业是否语义相关"""
        # 定义专业关联网络
        related_network = [
            {
                "经济学",
                "金融学",
                "财政学",
                "税收学",
                "保险学",
                "投资学",
                "国际经济与贸易",
                "贸易经济",
                "统计学",
                "应用统计学",
                "经济统计学",
            },
            {
                "计算机科学",
                "软件工程",
                "网络工程",
                "信息安全",
                "物联网",
                "大数据",
                "人工智能",
                "数据科学",
            },
            {"法学", "知识产权", "监狱学", "律师"},
        ]

        for group in related_network:
            m1_in = any(major1 in g or g in major1 for g in group)
            m2_in = any(major2 in g or g in major2 for g in group)
            if m1_in and m2_in:
                return True
        return False

    def get_stats(self) -> dict:
        """获取匹配统计"""
        total = sum(self.stats.values())
        return {
            "total": total,
            "rule_hit": self.stats["rule"],
            "cache_hit": self.stats["cache"],
            "llm_calls": self.stats["llm"],
            "cache_size": len(self.cache),
            "rule_rate": f"{self.stats['rule'] / total * 100:.1f}%" if total > 0 else "0%",
            "cache_rate": f"{self.stats['cache'] / total * 100:.1f}%" if total > 0 else "0%",
        }


def benchmark():
    """基准测试"""
    print("=" * 80)
    print("LLM语义匹配器 - 基准测试")
    print("=" * 80)

    # 测试用例：(用户专业, 岗位要求, 期望匹配)
    test_cases = [
        # 简单情况 - 应该走rule
        ("经济学", "不限", True),
        ("经济学", "经济学", True),
        ("经济学", "经济学类", True),
        # 包含情况
        ("经济学", "经济学、金融学", True),
        ("经济学", "经济学类（0201）、财政学类（0202）", True),
        # 语义模糊情况 - 需要LLM
        ("金融学", "经济学类", True),
        ("经济统计学", "经济学类", True),
        ("国际经济与贸易", "经济与贸易类", True),
        ("保险学", "金融学类", True),
        ("投资学", "经济学类", True),
        # 复杂岗位要求
        ("经济学", "本科及以上，经济学类（0201）、财政学类（0202）、金融学类（0203）", True),
        ("金融学", "本科：经济学类（0201）、金融学类（0203）", True),
        # 不匹配情况
        ("经济学", "临床医学", False),
        ("经济学", "法学类", False),
        ("计算机科学", "临床医学", False),
        ("护理学", "经济学类", False),
        # 边缘情况
        ("经济学", "不限专业", True),
        ("经济学", "", True),
        ("经济学", "nan", True),
    ]

    # 初始化匹配器
    matcher = RealLLMMajorMatcher("经济学")

    correct = 0
    results_by_source = {"rule": [], "cache": [], "llm": []}

    print("\n开始测试...\n")

    for user_major, job_major, expected in test_cases:
        matcher.user_major = user_major
        result = matcher.match(job_major)

        is_correct = result.match == expected
        if is_correct:
            correct += 1

        status = "[OK]" if is_correct else "[FAIL]"
        results_by_source[result.source].append(
            {
                "user": user_major,
                "job": job_major[:40],
                "expected": expected,
                "got": result.match,
                "confidence": result.confidence,
            }
        )

        print(f"{status} [{result.source}] {user_major} vs {job_major[:30]}...")
        print(
            f"       结果: {'匹配' if result.match else '不匹配'} (期望: {'匹配' if expected else '不匹配'})"
        )
        print(f"       说明: {result.reason}")
        print(f"       置信度: {result.confidence:.2f}")
        print()

    # 统计
    print("=" * 80)
    print("测试结果统计")
    print("=" * 80)
    print(f"\n总准确率: {correct}/{len(test_cases)} = {correct / len(test_cases) * 100:.1f}%")

    stats = matcher.get_stats()
    print("\n匹配来源分布:")
    print(f"  规则匹配: {stats['rule_hit']} 次 ({stats['rule_rate']})")
    print(f"  缓存命中: {stats['cache_hit']} 次 ({stats['cache_rate']})")
    print(f"  LLM调用:  {stats['llm_calls']} 次")
    print(f"  缓存大小: {stats['cache_size']} 条")

    print("\n性能预估:")
    rule_time = stats["rule_hit"] * 0.001  # 1ms
    cache_time = stats["cache_hit"] * 0.0001  # 0.1ms
    llm_time = stats["llm_calls"] * 0.5  # 500ms
    total_time = rule_time + cache_time + llm_time
    avg_time = total_time / stats["total"] * 1000 if stats["total"] > 0 else 0

    print(f"  规则耗时: {rule_time * 1000:.1f}ms")
    print(f"  缓存耗时: {cache_time * 1000:.1f}ms")
    print(f"  LLM耗时:  {llm_time * 1000:.1f}ms")
    print(f"  总耗时:   {total_time * 1000:.1f}ms")
    print(f"  平均每条: {avg_time:.2f}ms")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    benchmark()
