#!/usr/bin/env python3
"""
Claude API演示脚本
展示AI智能专业匹配的实际效果
"""

from api_config import APIConfig


def test_with_claude_api():
    """使用真实Claude API进行测试"""
    from llm_matcher_api import ClaudeMajorMatcher

    config = APIConfig()
    if not config.is_configured:
        print("[错误] API Key未配置")
        print("请运行: uv run api_config.py")
        return False

    print("=" * 80)
    print("Claude API 专业匹配演示")
    print("=" * 80)
    print(f"API Key: {config.anthropic_api_key[:12]}...")
    print()

    # 初始化匹配器
    try:
        matcher = ClaudeMajorMatcher(config.anthropic_api_key)
        print("[OK] Claude API连接成功")
        print(f"模型: {matcher.model}")
        print()
    except Exception as e:
        print(f"[错误] 连接失败: {e}")
        return False

    # 测试用例 - 越来越难
    test_cases = [
        # (用户专业, 岗位要求, 预期结果, 难度)
        ("经济学", "经济学类", True, "简单"),
        ("金融学", "经济学类", True, "简单"),
        ("统计学", "经济学类", True, "中等"),  # 模糊案例
        ("会计学", "经济学类", False, "困难"),  # 边缘案例
        ("数据科学", "统计学类", True, "中等"),
        ("精算学", "金融学类", True, "中等"),
        ("法学", "经济学类", False, "简单"),
        ("计算机科学", "经济学类", False, "简单"),
        ("临床医学", "经济学类", False, "简单"),
    ]

    print("-" * 80)
    print("开始测试...")
    print("-" * 80)

    correct = 0
    total_cost = 0

    for user_major, job_major, expected, difficulty in test_cases:
        print(f"\n[测试] {user_major} vs {job_major} (难度: {difficulty})")

        try:
            result = matcher.match(user_major, job_major)

            # 估算成本 ($5/M input + $25/M output)
            input_cost = 2000 / 1_000_000 * 5  # ~2000 tokens input
            output_cost = 200 / 1_000_000 * 25  # ~200 tokens output
            call_cost = input_cost + output_cost
            total_cost += call_cost

            is_correct = result.match == expected
            status = "[OK]" if is_correct else "[FAIL]"

            print(f"  {status} 结果: {'匹配' if result.match else '不匹配'}")
            print(f"       期望: {'匹配' if expected else '不匹配'}")
            print(f"       原因: {result.reason}")
            print(f"       置信度: {result.confidence:.2f}")
            print(f"       响应时间: {result.response_time:.2f}s")
            print(f"       估算成本: ${call_cost:.4f}")

            if is_correct:
                correct += 1

        except Exception as e:
            print(f"  [错误] {e}")

    print("\n" + "=" * 80)
    print(f"测试结果: {correct}/{len(test_cases)} = {correct / len(test_cases) * 100:.1f}%")
    print(f"总估算成本: ${total_cost:.4f}")

    # 显示API统计
    stats = matcher.get_stats()
    print("\nAPI统计:")
    print(f"  总Token: {stats['total_tokens']}")
    print(f"  缓存使用: {'是' if stats['cache_used'] else '否'}")

    print("=" * 80)
    return correct == len(test_cases)


def test_without_api():
    """不使用API的本地测试"""
    from job_matcher_llm import LLMEnhancedMajorMatcher

    print("=" * 80)
    print("本地语义匹配演示 (无API)")
    print("=" * 80)
    print()

    test_cases = [
        ("经济学", "经济学类", True),
        ("金融学", "经济学类", True),
        ("统计学", "经济学类", True),
        ("会计学", "经济学类", False),
        ("计算机科学", "经济学类", False),
    ]

    correct = 0

    for user_major, job_major, expected in test_cases:
        matcher = LLMEnhancedMajorMatcher(user_major, use_llm=False)
        match, reason, source = matcher.match(job_major)

        is_correct = match == expected
        status = "[OK]" if is_correct else "[FAIL]"

        print(f"\n{status} {user_major} vs {job_major}")
        print(f"   结果: {'匹配' if match else '不匹配'}")
        print(f"   原因: {reason}")
        print(f"   来源: {source}")

        if is_correct:
            correct += 1

    print(f"\n测试结果: {correct}/{len(test_cases)}")
    return correct == len(test_cases)


def compare_matching_methods():
    """对比不同匹配方法的效果"""
    print("=" * 80)
    print("匹配方法对比")
    print("=" * 80)
    print()

    test_cases = [
        ("金融学", "经济学类"),
        ("统计学", "经济学类"),
        ("会计学", "经济学类"),
        ("数据科学", "统计学类"),
    ]

    print("测试案例:")
    for user, job in test_cases:
        print(f"  - {user} vs {job}")

    print("\n" + "-" * 80)
    print("方法1: 本地规则匹配")
    print("-" * 80)

    from job_matcher import MajorMatcher

    for user, job in test_cases:
        matcher = MajorMatcher(user)
        match, reason, source = matcher.match(job)
        print(f"  {user} vs {job}: {'匹配' if match else '不匹配'} ({reason})")

    print("\n" + "-" * 80)
    print("方法2: 本地语义匹配")
    print("-" * 80)

    from job_matcher_llm import LLMEnhancedMajorMatcher

    for user, job in test_cases:
        matcher = LLMEnhancedMajorMatcher(user, use_llm=False)
        match, reason, source = matcher.match(job)
        print(f"  {user} vs {job}: {'匹配' if match else '不匹配'} ({reason})")

    config = APIConfig()
    if config.is_configured:
        print("\n" + "-" * 80)
        print("方法3: Claude API匹配 (真实LLM)")
        print("-" * 80)

        from llm_matcher_api import ClaudeMajorMatcher

        matcher = ClaudeMajorMatcher(config.anthropic_api_key)

        for user, job in test_cases:
            result = matcher.match(user, job)
            print(f"  {user} vs {job}: {'匹配' if result.match else '不匹配'} ({result.reason})")
            print(f"       置信度: {result.confidence:.2f}")

    print("\n" + "=" * 80)
    print("对比结论:")
    print("  - 本地规则: 速度最快，但只能处理明确规则")
    print("  - 本地语义: 速度较快，能处理相似专业")
    print("  - Claude API: 最智能，能理解复杂语义关系")
    print("=" * 80)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Claude API演示")
    parser.add_argument(
        "--mode", choices=["api", "local", "compare", "all"], default="all", help="测试模式"
    )
    args = parser.parse_args()

    config = APIConfig()

    if args.mode == "api":
        if config.is_configured:
            test_with_claude_api()
        else:
            print("[错误] API Key未配置，请先运行: uv run api_config.py")

    elif args.mode == "local":
        test_without_api()

    elif args.mode == "compare":
        compare_matching_methods()

    else:  # all
        print("\n" + "=" * 80)
        print("本地匹配测试")
        print("=" * 80)
        test_without_api()

        print("\n" + "=" * 80)
        print("方法对比")
        print("=" * 80)
        compare_matching_methods()

        if config.is_configured:
            print("\n")
            test_with_claude_api()
        else:
            print("\n" + "=" * 80)
            print("Claude API测试跳过")
            print("=" * 80)
            print("API Key未配置，如要测试API功能:")
            print("  1. 访问 https://console.anthropic.com/ 获取API Key")
            print("  2. 运行: uv run api_config.py")
            print("  3. 再次运行本脚本")


if __name__ == "__main__":
    main()
