#!/usr/bin/env python3
"""
测试匹配器
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.core.matchers.major_matcher import MajorMatcher
from server.core.matchers.education_matcher import EducationMatcher
from server.core.matchers.political_matcher import PoliticalMatcher
from server.core.matchers.age_matcher import AgeMatcher


def test_major_matcher():
    """测试专业匹配器"""
    matcher = MajorMatcher("经济学")

    # 测试不限
    ok, msg = matcher.match("不限")
    assert ok, f"不限应该通过: {msg}"

    # 测试完全匹配
    ok, msg = matcher.match("经济学")
    assert ok, f"经济学应该匹配: {msg}"

    # 测试包含匹配
    ok, msg = matcher.match("经济学、金融学")
    assert ok, f"经济学、金融学应包含经济学: {msg}"

    # 测试大类匹配
    ok, msg = matcher.match("经济学类")
    assert ok, f"经济学类应匹配经济学: {msg}"

    # 测试不匹配
    ok, msg = matcher.match("法学")
    assert not ok, f"法学不应匹配经济学: {msg}"

    print("✓ 专业匹配器测试通过")


def test_education_matcher():
    """测试学历匹配器"""
    matcher = EducationMatcher("本科")

    # 测试不限
    ok, msg = matcher.match("不限")
    assert ok, f"不限应该通过: {msg}"

    # 测试本科及以上
    ok, msg = matcher.match("本科及以上")
    assert ok, f"本科应匹配本科及以上: {msg}"

    # 测试大专
    ok, msg = matcher.match("大专")
    assert ok, f"本科应覆盖大专: {msg}"

    # 测试研究生 - 研究生可以报本科岗位（向下兼容）
    matcher_graduate = EducationMatcher("研究生")
    ok, msg = matcher_graduate.match("本科")
    assert ok, f"研究生应匹配本科: {msg}"

    # 测试研究生不能报研究生及以上（本科不够）
    matcher_undergrad = EducationMatcher("本科")
    ok, msg = matcher_undergrad.match("研究生及以上")
    assert not ok, f"本科不应匹配研究生及以上: {msg}"

    print("✓ 学历匹配器测试通过")


def test_political_matcher():
    """测试政治面貌匹配器"""
    # 党员
    matcher_party = PoliticalMatcher("中共党员")
    ok, msg = matcher_party.match("中共党员")
    assert ok, f"党员应匹配党员要求: {msg}"

    ok, msg = matcher_party.match("群众")
    assert not ok, f"党员不应匹配群众: {msg}"

    # 团员
    matcher_youth = PoliticalMatcher("共青团员")
    ok, msg = matcher_youth.match("中共党员")
    assert not ok, f"团员不应匹配党员: {msg}"

    ok, msg = matcher_youth.match("共青团员")
    assert ok, f"团员应匹配团员: {msg}"

    print("✓ 政治面貌匹配器测试通过")


def test_age_matcher():
    """测试年龄匹配器"""
    matcher = AgeMatcher(28)

    # 测试不限
    ok, msg = matcher.match("不限")
    assert ok, f"不限应该通过: {msg}"

    # 测试30岁以下
    ok, msg = matcher.match("30岁以下")
    assert ok, f"28岁应符合30岁以下: {msg}"

    # 测试25岁以下
    ok, msg = matcher.match("25岁以下")
    assert not ok, f"28岁不应符合25岁以下: {msg}"

    # 测试28-35岁
    ok, msg = matcher.match("28-35岁")
    assert ok, f"28岁应符合28-35岁: {msg}"

    print("✓ 年龄匹配器测试通过")


if __name__ == "__main__":
    test_major_matcher()
    test_education_matcher()
    test_political_matcher()
    test_age_matcher()
    print("\n所有匹配器测试通过! ✓")