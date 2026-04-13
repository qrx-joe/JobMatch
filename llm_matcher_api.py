#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实LLM API匹配器 - 使用Claude API进行专业语义匹配

功能：
1. 使用Claude Opus 4.6进行专业匹配判断
2. 支持提示缓存（Prompt Caching）降低成本
3. 结构化输出（Structured Output）保证格式
4. 自适应思考（Adaptive Thinking）提升准确率
"""
import os
import json
import time
from dataclasses import dataclass
from typing import Tuple, Optional
from datetime import datetime
import anthropic


@dataclass
class LLMMatchResult:
    """LLM匹配结果"""
    match: bool
    reason: str
    confidence: float
    category_match: bool  # 是否同大类
    related: bool  # 是否相关
    llm_model: str
    response_time: float


class ClaudeMajorMatcher:
    """
    Claude API专业匹配器

    使用Claude Opus 4.6进行语义匹配判断
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("需要设置 ANTHROPIC_API_KEY 环境变量")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-opus-4-6"  # 使用最新模型
        self.cache_used = False
        self.total_tokens = 0

    def _build_system_prompt(self) -> str:
        """构建系统提示词（会被缓存）"""
        return """你是一个专业匹配专家，专门判断中国高等教育专业之间的匹配关系。

你的任务是判断：用户的具体专业是否可以报考岗位要求的专业（可能是大类或具体专业）。

判断规则（按优先级）：

1. **完全匹配** - 专业名称完全相同
   - 例：用户是"经济学"，岗位要求"经济学" → 匹配

2. **大类包含** - 用户专业属于岗位要求的大类
   - 例：用户是"金融学"，岗位要求"经济学类" → 匹配（金融学属于经济学类）
   - 例：用户是"财政学"，岗位要求"经济学类" → 匹配（财政学属于经济学类）

3. **相关匹配** - 专业高度相关但不属于同一严格大类
   - 例：用户是"统计学"，岗位要求"经济学类" → 可能匹配（统计与经济高度相关）
   - 例：用户是"会计学"，岗位要求"经济学类" → 可能匹配（会计与经济相关）

4. **不匹配** - 专业领域完全不同
   - 例：用户是"临床医学"，岗位要求"经济学类" → 不匹配
   - 例：用户是"计算机科学"，岗位要求"法学类" → 不匹配

常见专业大类包含关系：
- **经济学类**：经济学、经济统计学、财政学、金融学、金融工程、保险学、投资学、国际经济与贸易、贸易经济等
- **财政学类**：财政学、税收学
- **金融学类**：金融学、金融工程、保险学、投资学、金融数学、精算学等
- **经济与贸易类**：国际经济与贸易、贸易经济
- **统计学类**：统计学、应用统计学、数据科学
- **计算机类**：计算机科学与技术、软件工程、网络工程、信息安全、数据科学与大数据技术等
- **法学类**：法学、知识产权、监狱学
- **教育学类**：教育学、学前教育、小学教育、特殊教育等
- **医学类**：临床医学、口腔医学、护理学、药学等

输出格式要求：
- 必须返回JSON格式
- match: true/false（是否匹配）
- reason: 简短的中文匹配原因（30字以内）
- confidence: 0.0-1.0（置信度）
- category_match: true/false（是否同一大类）
- related: true/false（是否相关专业）"""

    def match(self, user_major: str, job_major: str) -> LLMMatchResult:
        """
        使用Claude API判断专业匹配

        Args:
            user_major: 用户专业（如："金融学"）
            job_major: 岗位要求（如："经济学类"）

        Returns:
            LLMMatchResult: 匹配结果
        """
        start_time = time.time()

        # 构建用户消息
        user_message = f"""请判断以下专业是否匹配：

用户专业：{user_major}
岗位要求：{job_major}

请分析这两个专业的关系，并返回JSON格式的判断结果。"""

        try:
            # 第一次调用需要完整system prompt，后续可以使用缓存
            system_content = self._build_system_prompt()

            # 使用提示缓存来降低成本
            system_messages = [
                {
                    "type": "text",
                    "text": system_content,
                    "cache_control": {"type": "ephemeral"}  # 启用缓存
                }
            ]

            # 调用Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_messages,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                thinking={"type": "adaptive"},  # 自适应思考
                output_config={
                    "format": {
                        "type": "json_schema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "match": {"type": "boolean"},
                                "reason": {"type": "string"},
                                "confidence": {"type": "number"},
                                "category_match": {"type": "boolean"},
                                "related": {"type": "boolean"}
                            },
                            "required": ["match", "reason", "confidence", "category_match", "related"],
                            "additionalProperties": False
                        }
                    }
                }
            )

            # 解析响应
            result_text = response.content[0].text
            result_json = json.loads(result_text)

            # 记录token使用情况
            self.total_tokens += response.usage.input_tokens + response.usage.output_tokens

            # 检查是否使用了缓存
            if hasattr(response.usage, 'cache_creation_input_tokens'):
                if response.usage.cache_creation_input_tokens > 0:
                    self.cache_used = True

            response_time = time.time() - start_time

            return LLMMatchResult(
                match=result_json.get("match", False),
                reason=result_json.get("reason", ""),
                confidence=result_json.get("confidence", 0.0),
                category_match=result_json.get("category_match", False),
                related=result_json.get("related", False),
                llm_model=self.model,
                response_time=response_time
            )

        except anthropic.BadRequestError as e:
            # API请求错误，回退到本地规则
            return self._fallback_match(user_major, job_major, f"API错误: {e.message}")
        except Exception as e:
            # 其他错误，回退到本地规则
            return self._fallback_match(user_major, job_major, str(e))

    def _fallback_match(self, user_major: str, job_major: str, error_msg: str) -> LLMMatchResult:
        """API失败时的回退方案"""
        from job_matcher_llm import LLMEnhancedMajorMatcher

        # 使用本地语义匹配（不带API key，强制使用本地匹配）
        local_matcher = LLMEnhancedMajorMatcher(user_major, use_llm=False)
        match, reason, source = local_matcher.match(job_major)

        return LLMMatchResult(
            match=match,
            reason=f"{reason} (本地回退: {error_msg})",
            confidence=0.7,
            category_match=False,
            related=source == "semantic",
            llm_model="local_fallback",
            response_time=0.0
        )

    def get_stats(self) -> dict:
        """获取使用统计"""
        return {
            "total_tokens": self.total_tokens,
            "cache_used": self.cache_used,
            "model": self.model
        }


def test_claude_matcher():
    """测试Claude匹配器"""
    print("=" * 80)
    print("Claude API 专业匹配器测试")
    print("=" * 80)

    # 检查API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n[警告] 未设置 ANTHROPIC_API_KEY 环境变量")
        print("请运行: export ANTHROPIC_API_KEY='your-api-key'")
        print("\n将使用本地回退模式进行测试...")
        use_api = False
    else:
        use_api = True
        print(f"\nAPI Key: {api_key[:8]}...{api_key[-4:]}")

    # 测试用例
    test_cases = [
        ("经济学", "经济学类", True),
        ("金融学", "经济学类", True),
        ("投资学", "经济学类", True),
        ("统计学", "经济学类", True),  # 模糊案例
        ("会计学", "经济学类", False),  # 模糊案例
        ("计算机科学", "经济学类", False),
        ("临床医学", "经济学类", False),
        ("财政学", "财政学类", True),
        ("保险学", "金融学类", True),
    ]

    if use_api:
        matcher = ClaudeMajorMatcher()
        print(f"模型: {matcher.model}")
        print(f"缓存: {'已启用' if matcher.cache_used else '未启用'}")
    else:
        matcher = None
        print("模式: 本地语义匹配")

    print("\n" + "-" * 80)

    correct = 0
    total_cost = 0

    for user_major, job_major, expected in test_cases:
        print(f"\n测试: {user_major} vs {job_major}")

        if use_api:
            result = matcher.match(user_major, job_major)
            # 估算成本 (Opus 4.6: $5/1M input, $25/1M output)
            cost = (result.response_time * 0)  # 简化估算
            total_cost += 0.002  # 假设每次约$0.002

            status = "[OK]" if result.match == expected else "[FAIL]"
            print(f"  {status} 结果: {'匹配' if result.match else '不匹配'} "
                  f"(期望: {'匹配' if expected else '不匹配'})")
            print(f"      原因: {result.reason}")
            print(f"      置信度: {result.confidence:.2f}")
            print(f"      同大类: {'是' if result.category_match else '否'}")
            print(f"      相关: {'是' if result.related else '否'}")
            print(f"      响应时间: {result.response_time:.2f}s")

            if result.match == expected:
                correct += 1
        else:
            # 本地模式
            from job_matcher_llm import LLMEnhancedMajorMatcher
            local_matcher = LLMEnhancedMajorMatcher(user_major, use_llm=False)
            match, reason, source = local_matcher.match(job_major)
            status = "[OK]" if match == expected else "[FAIL]"
            print(f"  {status} 结果: {'匹配' if match else '不匹配'} [{source}]")
            print(f"      原因: {reason}")
            if match == expected:
                correct += 1

    print("\n" + "=" * 80)
    print(f"测试结果: {correct}/{len(test_cases)} = {correct/len(test_cases)*100:.1f}%")

    if use_api:
        stats = matcher.get_stats()
        print(f"\nAPI统计:")
        print(f"  总Token: {stats['total_tokens']}")
        print(f"  缓存使用: {'是' if stats['cache_used'] else '否'}")
        print(f"  估算成本: ~${total_cost:.4f}")

    print("=" * 80)


if __name__ == "__main__":
    test_claude_matcher()
