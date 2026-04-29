#!/usr/bin/env python3
"""
专业匹配器 - 支持大类/代码/模糊匹配
"""

import re
from typing import Tuple

from .base_matcher import BaseMatcher


class MajorMatcher(BaseMatcher):
    """
    专业匹配器

    支持多种匹配策略：
    1. 完全匹配：如"经济学" == "经济学"
    2. 包含匹配：如岗位要求"经济学、金融学"，用户是"经济学"
    3. 大类匹配：如岗位要求"经济学类"，用户是"经济学"
    4. 代码匹配：如岗位要求"0201"，用户是"经济学类"
    """

    # 专业大类映射（教育部专业目录）
    MAJOR_CATEGORIES = {
        "经济学类": [
            "经济学",
            "经济统计学",
            "国民经济管理",
            "资源与环境经济学",
            "商务经济学",
            "能源经济",
            "劳动经济学",
            "经济工程",
            "数字经济",
            "海洋经济学",
        ],
        "财政学类": ["财政学", "税收学", "国际税收", "关税学"],
        "金融学类": [
            "金融学",
            "金融工程",
            "保险学",
            "投资学",
            "金融数学",
            "信用管理",
            "经济与金融",
            "精算学",
            "互联网金融",
            "金融科技",
        ],
        "经济与贸易类": ["国际经济与贸易", "贸易经济", "国际商务"],
        "统计学类": ["统计学", "应用统计学", "数据科学", "生物统计学"],
        "会计学类": ["会计学", "财务管理", "审计学", "资产评估"],
        "工商管理类": [
            "工商管理",
            "市场营销",
            "人力资源管理",
            "旅游管理",
            "酒店管理",
            "会展经济与管理",
            "电子商务",
            "物流管理",
            "供应链管理",
        ],
        "管理科学与工程类": ["管理科学", "信息管理与信息系统", "工程管理", "工程造价"],
        "公共管理类": ["公共事业管理", "行政管理", "劳动与社会保障", "土地资源管理"],
        "社会学类": ["社会学", "社会工作", "人类学", "人口学"],
        "法学类": [
            "法学",
            "知识产权",
            "监狱学",
            "信用风险管理与法律防控",
            "国际经贸规则",
        ],
        "政治学类": ["政治学与行政学", "国际政治", "外交学", "国际事务与国际关系"],
        "社会学类": ["社会学", "社会工作", "人类学"],
        "教育学类": [
            "教育学",
            "学前教育",
            "小学教育",
            "特殊教育",
            "教育技术学",
            "教育康复学",
        ],
        "心理学类": ["心理学", "应用心理学"],
        "中国语言文学类": ["汉语言文学", "汉语言", "汉语国际教育", "古典文献学"],
        "新闻传播学类": ["新闻学", "广播电视学", "广告学", "传播学", "编辑出版学"],
        "外国语言文学类": [
            "英语",
            "俄语",
            "法语",
            "德语",
            "日语",
            "西班牙语",
            "阿拉伯语",
        ],
        "数学类": ["数学与应用数学", "信息与计算科学", "数理基础科学"],
        "物理学类": ["物理学", "应用物理学", "核物理"],
        "化学类": ["化学", "应用化学", "化学生物学", "分子科学与工程"],
        "生物科学类": ["生物科学", "生物技术", "生物信息学", "生态学"],
        "计算机类": [
            "计算机科学与技术",
            "软件工程",
            "网络工程",
            "信息安全",
            "物联网工程",
            "数字媒体技术",
            "数据科学与大数据技术",
            "人工智能",
        ],
        "电子信息类": ["电子信息工程", "电子科学与技术", "通信工程", "微电子科学与工程"],
        "机械类": ["机械工程", "机械设计制造及其自动化", "材料成型及控制工程"],
        "土木类": ["土木工程", "建筑环境与能源应用工程", "给排水科学与工程"],
        "化工与制药类": ["化学工程与工艺", "制药工程", "资源循环科学与工程"],
        "建筑类": ["建筑学", "城乡规划", "风景园林", "历史建筑保护工程"],
        "林学类": ["林学", "园林", "森林保护", "经济林"],
        "农学类": ["农学", "园艺", "植物保护", "植物科学与技术", "种子科学与工程"],
        "动物医学类": ["动物医学", "动物药学", "动植物检疫", "实验动物学"],
        "医学类": ["临床医学", "基础医学", "口腔医学", "公共卫生与预防医学"],
        "艺术学类": ["艺术设计", "音乐学", "美术学", "表演", "戏剧影视文学"],
    }

    # 专业代码映射
    MAJOR_CODES = {
        "0201": "经济学类",
        "0202": "财政学类",
        "0203": "金融学类",
        "0204": "经济与贸易类",
        "0712": "统计学类",
        "1202": "工商管理类",
        "1201": "管理科学与工程类",
        "1204": "公共管理类",
        "0301": "法学类",
        "0302": "政治学类",
        "0303": "社会学类",
        "0401": "教育学类",
        "0402": "心理学类",
        "0501": "中国语言文学类",
        "0503": "新闻传播学类",
        "0502": "外国语言文学类",
        "0701": "数学类",
        "0702": "物理学类",
        "0703": "化学类",
        "0710": "生物科学类",
        "0809": "计算机类",
        "0807": "电子信息类",
        "0802": "机械类",
        "0810": "土木类",
        "0813": "化工与制药类",
        "0828": "建筑类",
        "0905": "林学类",
        "0901": "农学类",
        "0906": "兽医学类",
    }

    def __init__(self, user_major: str):
        """
        初始化专业匹配器

        Args:
            user_major: 用户专业名称
        """
        self.user_major = user_major.strip()
        self.user_categories = self._get_categories(self.user_major)
        self.user_major_code = self._get_major_code(self.user_major)

    def _get_categories(self, major: str) -> list[str]:
        """获取专业所属的大类列表"""
        categories = []
        major = major.strip()
        for cat, majors in self.MAJOR_CATEGORIES.items():
            if major in majors:
                categories.append(cat)
        return categories

    def _get_major_code(self, major: str) -> str:
        """根据专业名查找专业代码"""
        for code, name in self.MAJOR_CODES.items():
            if name == major:
                return code
        # 查找专业是否在大类中
        for cat, majors in self.MAJOR_CATEGORIES.items():
            if major in majors:
                # 找到大类代码
                for code, name in self.MAJOR_CODES.items():
                    if name == cat:
                        return code
        return ""

    def match(self, job_requirement: str, user_major: str = None) -> Tuple[bool, str]:
        """
        匹配专业

        Args:
            job_requirement: 岗位的专业要求
            user_major: 用户专业（可选，默认使用初始化时的专业）

        Returns:
            (是否匹配, 匹配说明)
        """
        if user_major is None:
            user_major = self.user_major
        else:
            user_major = user_major.strip()

        job_major = str(job_requirement).strip()

        # 空值检查
        if not job_major or job_major in ["无", "nan", "", "None", "不限"]:
            return True, "专业不限"

        if not user_major:
            return False, f"专业不匹配：岗位要求[{job_major}]，用户未填写专业"

        # 1. 完全相等
        if user_major == job_major:
            return True, f"专业完全匹配：{user_major}"

        # 2. 包含匹配（如"经济学、金融学"）
        if user_major in job_major:
            return True, f"专业包含匹配：{user_major}"

        # 3. 反向包含（用户是"经济学类"，岗位要求"经济学"）- 不符合
        if job_major in user_major and any(
            keyword in job_major for keyword in ["类", "大类", "一级学科"]
        ):
            return False, f"专业不匹配：要求[{job_major}]，你是[{user_major}]"

        # 4. 大类匹配
        for category in self.user_categories:
            if category in job_major:
                return True, f"专业大类匹配：{category}"

        # 5. 专业代码匹配（如"0201"是经济学类代码）
        for category in self.user_categories:
            codes = [c for c, n in self.MAJOR_CODES.items() if n == category]
            for code in codes:
                if code in job_major or f"({code})" in job_major:
                    return True, f"专业代码匹配：{code}（{category}）"

        # 6. 尝试提取专业代码进行匹配
        extracted_code = self._extract_major_code(job_major)
        if extracted_code:
            # 用户专业所属大类
            for cat, majors in self.MAJOR_CATEGORIES.items():
                if user_major in majors:
                    # 用户的专业大类代码
                    for code, name in self.MAJOR_CODES.items():
                        if name == cat and code == extracted_code:
                            return True, f"专业代码匹配：{code}"

        return False, f"专业不匹配：要求[{job_major}]，你是[{user_major}]"

    def _extract_major_code(self, text: str) -> str:
        """从文本中提取专业代码"""
        # 匹配4位数字代码
        match = re.search(r"\((\d{4})\)|（(\d{4})）|(\d{4})", text)
        if match:
            return match.group(1) or match.group(2) or match.group(3)
        return ""

    def get_user_categories(self) -> list[str]:
        """获取用户专业所属的大类"""
        return self.user_categories


# 导出
__all__ = ["MajorMatcher"]