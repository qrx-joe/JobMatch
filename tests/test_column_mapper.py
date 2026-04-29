#!/usr/bin/env python3
"""
测试列名映射器
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from server.data.excel.column_mapper import ColumnMapper


def test_detect_columns():
    """测试列名检测"""
    # 创建模拟数据
    data = {
        "服务单位": ["单位1", "单位2"],
        "专业要求": ["经济学", "金融学"],
        "学历要求": ["本科", "研究生"],
        "Unnamed: 0": [1, 2],
    }
    df = pd.DataFrame(data)

    mapper = ColumnMapper()
    result = mapper.detect_columns(df)

    print("检测结果:", result)
    assert "服务单位" in result
    assert "专业" in result
    assert "学历" in result
    print("✓ 列名检测测试通过")


def test_synonym_matching():
    """测试同义词匹配"""
    mapper = ColumnMapper()

    # 测试标准列名
    assert mapper._match_column("服务单位") == "服务单位"
    assert mapper._match_column("用人单位") == "服务单位"
    assert mapper._match_column("招录机关") == "服务单位"

    # 测试专业
    assert mapper._match_column("专业要求") == "专业"
    assert mapper._match_column("所学专业") == "专业"

    print("✓ 同义词匹配测试通过")


def test_similarity():
    """测试相似度计算"""
    mapper = ColumnMapper()

    # 相同
    assert mapper._calculate_similarity("服务单位", "服务单位") == 1.0

    # 包含
    assert mapper._calculate_similarity("服务单位名称", "服务单位") > 0.6

    print("✓ 相似度计算测试通过")


if __name__ == "__main__":
    test_detect_columns()
    test_synonym_matching()
    test_similarity()
    print("\n所有测试通过! ✓")