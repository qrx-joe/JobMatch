#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版专业关系图谱 - 包含所有学科门类
支持专业对比、关系路径分析、导出报告
"""
import json
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from enum import Enum
import os


class MajorCategory(Enum):
    """学科门类"""
    ECONOMICS = "经济学"
    LAW = "法学"
    EDUCATION = "教育学"
    MEDICINE = "医学"
    ENGINEERING = "工学"
    LITERATURE = "文学"
    HISTORY = "历史学"
    SCIENCE = "理学"
    MANAGEMENT = "管理学"
    AGRICULTURE = "农学"


@dataclass
class Major:
    """专业节点"""
    id: str
    name: str
    category: MajorCategory
    subcategory: str  # 专业类
    description: str = ""
    related_majors: List[str] = field(default_factory=list)
    parent_categories: List[str] = field(default_factory=list)


@dataclass
class MajorGraph:
    """专业关系图谱"""
    majors: Dict[str, Major] = field(default_factory=dict)
    categories: Dict[str, List[str]] = field(default_factory=dict)

    def __post_init__(self):
        self._init_all_majors()

    def _init_all_majors(self):
        """初始化所有专业数据"""
        # 经济学类
        self._add_major(Major(
            id="economics",
            name="经济学",
            category=MajorCategory.ECONOMICS,
            subcategory="经济学类",
            description="研究资源配置和经济运行规律",
            related_majors=["finance", "accounting", "statistics"],
            parent_categories=["经济学类", "人文社科类"]
        ))
        self._add_major(Major(
            id="finance",
            name="金融学",
            category=MajorCategory.ECONOMICS,
            subcategory="金融学类",
            description="研究资金融通和金融市场",
            related_majors=["economics", "investment", "insurance"],
            parent_categories=["金融学类", "经济学类"]
        ))
        self._add_major(Major(
            id="investment",
            name="投资学",
            category=MajorCategory.ECONOMICS,
            subcategory="金融学类",
            description="研究投资决策和资产管理",
            related_majors=["finance", "economics"],
            parent_categories=["金融学类"]
        ))
        self._add_major(Major(
            id="insurance",
            name="保险学",
            category=MajorCategory.ECONOMICS,
            subcategory="金融学类",
            description="研究风险管理和保险机制",
            related_majors=["finance", "actuarial"],
            parent_categories=["金融学类"]
        ))
        self._add_major(Major(
            id="actuarial",
            name="精算学",
            category=MajorCategory.ECONOMICS,
            subcategory="金融学类",
            description="研究保险精算和风险评估",
            related_majors=["insurance", "statistics"],
            parent_categories=["金融学类"]
        ))
        self._add_major(Major(
            id="public_finance",
            name="财政学",
            category=MajorCategory.ECONOMICS,
            subcategory="财政学类",
            description="研究政府收支和公共财政",
            related_majors=["economics", "taxation"],
            parent_categories=["财政学类", "经济学类"]
        ))
        self._add_major(Major(
            id="taxation",
            name="税收学",
            category=MajorCategory.ECONOMICS,
            subcategory="财政学类",
            description="研究税收制度和政策",
            related_majors=["public_finance", "accounting"],
            parent_categories=["财政学类"]
        ))
        self._add_major(Major(
            id="accounting",
            name="会计学",
            category=MajorCategory.MANAGEMENT,
            subcategory="工商管理类",
            description="研究财务信息记录和报告",
            related_majors=["economics", "finance", "auditing"],
            parent_categories=["工商管理类", "管理学类"]
        ))
        self._add_major(Major(
            id="auditing",
            name="审计学",
            category=MajorCategory.MANAGEMENT,
            subcategory="工商管理类",
            description="研究财务监督和审查",
            related_majors=["accounting", "finance"],
            parent_categories=["工商管理类"]
        ))
        self._add_major(Major(
            id="statistics",
            name="统计学",
            category=MajorCategory.SCIENCE,
            subcategory="统计学类",
            description="研究数据收集和分析方法",
            related_majors=["economics", "data_science", "actuarial"],
            parent_categories=["统计学类", "理学类"]
        ))
        self._add_major(Major(
            id="data_science",
            name="数据科学",
            category=MajorCategory.SCIENCE,
            subcategory="统计学类",
            description="研究大数据分析和挖掘",
            related_majors=["statistics", "computer_science"],
            parent_categories=["统计学类"]
        ))

        # 法学类
        self._add_major(Major(
            id="law",
            name="法学",
            category=MajorCategory.LAW,
            subcategory="法学类",
            description="研究法律规范和法律制度",
            related_majors=["intellectual_property", "prison_management"],
            parent_categories=["法学类"]
        ))
        self._add_major(Major(
            id="intellectual_property",
            name="知识产权",
            category=MajorCategory.LAW,
            subcategory="法学类",
            description="研究知识产权保护和运用",
            related_majors=["law", "computer_science"],
            parent_categories=["法学类"]
        ))
        self._add_major(Major(
            id="prison_management",
            name="监狱学",
            category=MajorCategory.LAW,
            subcategory="法学类",
            description="研究监狱管理和罪犯矫正",
            related_majors=["law", "sociology"],
            parent_categories=["法学类"]
        ))
        self._add_major(Major(
            id="sociology",
            name="社会学",
            category=MajorCategory.LAW,
            subcategory="社会学类",
            description="研究社会结构和社会行为",
            related_majors=["law", "social_work"],
            parent_categories=["社会学类", "法学类"]
        ))
        self._add_major(Major(
            id="social_work",
            name="社会工作",
            category=MajorCategory.LAW,
            subcategory="社会学类",
            description="研究社会服务和福利保障",
            related_majors=["sociology", "psychology"],
            parent_categories=["社会学类"]
        ))
        self._add_major(Major(
            id="political_science",
            name="政治学与行政学",
            category=MajorCategory.LAW,
            subcategory="政治学类",
            description="研究政治制度和行政管理",
            related_majors=["law", "public_administration"],
            parent_categories=["政治学类", "法学类"]
        ))
        self._add_major(Major(
            id="public_administration",
            name="公共事业管理",
            category=MajorCategory.MANAGEMENT,
            subcategory="公共管理类",
            description="研究公共事务管理和政策",
            related_majors=["political_science", "sociology"],
            parent_categories=["公共管理类", "管理学类"]
        ))

        # 教育学类
        self._add_major(Major(
            id="education",
            name="教育学",
            category=MajorCategory.EDUCATION,
            subcategory="教育学类",
            description="研究教育理论和教育方法",
            related_majors=["preschool_edu", "primary_edu", "psychology"],
            parent_categories=["教育学类"]
        ))
        self._add_major(Major(
            id="preschool_edu",
            name="学前教育",
            category=MajorCategory.EDUCATION,
            subcategory="教育学类",
            description="研究幼儿教育理论和实践",
            related_majors=["education", "psychology"],
            parent_categories=["教育学类"]
        ))
        self._add_major(Major(
            id="primary_edu",
            name="小学教育",
            category=MajorCategory.EDUCATION,
            subcategory="教育学类",
            description="研究小学教育方法和课程",
            related_majors=["education", "chinese_lang"],
            parent_categories=["教育学类"]
        ))
        self._add_major(Major(
            id="special_edu",
            name="特殊教育",
            category=MajorCategory.EDUCATION,
            subcategory="教育学类",
            description="研究特殊儿童教育方法",
            related_majors=["education", "psychology"],
            parent_categories=["教育学类"]
        ))
        self._add_major(Major(
            id="physical_edu",
            name="体育教育",
            category=MajorCategory.EDUCATION,
            subcategory="体育学类",
            description="研究体育教学和训练方法",
            related_majors=["education", "sports_training"],
            parent_categories=["体育学类", "教育学类"]
        ))
        self._add_major(Major(
            id="sports_training",
            name="运动训练",
            category=MajorCategory.EDUCATION,
            subcategory="体育学类",
            description="研究竞技体育训练方法",
            related_majors=["physical_edu"],
            parent_categories=["体育学类"]
        ))
        self._add_major(Major(
            id="psychology",
            name="心理学",
            category=MajorCategory.EDUCATION,
            subcategory="心理学类",
            description="研究心理活动和行为规律",
            related_majors=["education", "sociology"],
            parent_categories=["心理学类", "教育学类"]
        ))
        self._add_major(Major(
            id="applied_psychology",
            name="应用心理学",
            category=MajorCategory.EDUCATION,
            subcategory="心理学类",
            description="研究心理学在实际中的应用",
            related_majors=["psychology", "human_resources"],
            parent_categories=["心理学类"]
        ))

        # 医学类
        self._add_major(Major(
            id="clinical_medicine",
            name="临床医学",
            category=MajorCategory.MEDICINE,
            subcategory="临床医学类",
            description="研究疾病诊断和治疗方法",
            related_majors=["nursing", "pharmacy"],
            parent_categories=["临床医学类", "医学类"]
        ))
        self._add_major(Major(
            id="nursing",
            name="护理学",
            category=MajorCategory.MEDICINE,
            subcategory="护理学类",
            description="研究护理理论和护理技术",
            related_majors=["clinical_medicine"],
            parent_categories=["护理学类", "医学类"]
        ))
        self._add_major(Major(
            id="pharmacy",
            name="药学",
            category=MajorCategory.MEDICINE,
            subcategory="药学类",
            description="研究药物研发和药物应用",
            related_majors=["clinical_medicine", "pharmaceutical_eng"],
            parent_categories=["药学类", "医学类"]
        ))
        self._add_major(Major(
            id="pharmaceutical_eng",
            name="制药工程",
            category=MajorCategory.ENGINEERING,
            subcategory="化工与制药类",
            description="研究药物生产工艺和设备",
            related_majors=["pharmacy", "chemical_eng"],
            parent_categories=["化工与制药类", "工学类"]
        ))
        self._add_major(Major(
            id="stomatology",
            name="口腔医学",
            category=MajorCategory.MEDICINE,
            subcategory="口腔医学类",
            description="研究口腔疾病诊治",
            related_majors=["clinical_medicine"],
            parent_categories=["口腔医学类", "医学类"]
        ))
        self._add_major(Major(
            id="preventive_medicine",
            name="预防医学",
            category=MajorCategory.MEDICINE,
            subcategory="公共卫生与预防医学类",
            description="研究疾病预防和健康促进",
            related_majors=["clinical_medicine", "public_health"],
            parent_categories=["公共卫生与预防医学类", "医学类"]
        ))
        self._add_major(Major(
            id="public_health",
            name="公共事业管理(卫生)",
            category=MajorCategory.MANAGEMENT,
            subcategory="公共管理类",
            description="研究卫生事业管理和政策",
            related_majors=["preventive_medicine", "public_administration"],
            parent_categories=["公共管理类", "管理学类"]
        ))
        self._add_major(Major(
            id="traditional_chinese_medicine",
            name="中医学",
            category=MajorCategory.MEDICINE,
            subcategory="中医学类",
            description="研究中医理论和诊疗方法",
            related_majors=["clinical_medicine", "chinese_pharmacy"],
            parent_categories=["中医学类", "医学类"]
        ))
        self._add_major(Major(
            id="chinese_pharmacy",
            name="中药学",
            category=MajorCategory.MEDICINE,
            subcategory="中药学类",
            description="研究中药资源和药物开发",
            related_majors=["traditional_chinese_medicine", "pharmacy"],
            parent_categories=["中药学类", "医学类"]
        ))
        self._add_major(Major(
            id="medical_imaging",
            name="医学影像学",
            category=MajorCategory.MEDICINE,
            subcategory="临床医学类",
            description="研究医学影像诊断技术",
            related_majors=["clinical_medicine"],
            parent_categories=["临床医学类", "医学类"]
        ))

        # 工学类
        self._add_major(Major(
            id="computer_science",
            name="计算机科学与技术",
            category=MajorCategory.ENGINEERING,
            subcategory="计算机类",
            description="研究计算机系统和软件开发",
            related_majors=["software_eng", "data_science", "intellectual_property"],
            parent_categories=["计算机类", "工学类"]
        ))
        self._add_major(Major(
            id="software_eng",
            name="软件工程",
            category=MajorCategory.ENGINEERING,
            subcategory="计算机类",
            description="研究软件开发和工程管理",
            related_majors=["computer_science", "information_security"],
            parent_categories=["计算机类", "工学类"]
        ))
        self._add_major(Major(
            id="information_security",
            name="信息安全",
            category=MajorCategory.ENGINEERING,
            subcategory="计算机类",
            description="研究信息安全和密码技术",
            related_majors=["computer_science", "network_eng"],
            parent_categories=["计算机类", "工学类"]
        ))
        self._add_major(Major(
            id="network_eng",
            name="网络工程",
            category=MajorCategory.ENGINEERING,
            subcategory="计算机类",
            description="研究计算机网络和通信",
            related_majors=["computer_science", "information_security"],
            parent_categories=["计算机类", "工学类"]
        ))

        # 文学类
        self._add_major(Major(
            id="chinese_lang",
            name="汉语言文学",
            category=MajorCategory.LITERATURE,
            subcategory="中国语言文学类",
            description="研究汉语和中国文学",
            related_majors=["primary_edu", "journalism"],
            parent_categories=["中国语言文学类", "文学类"]
        ))
        self._add_major(Major(
            id="journalism",
            name="新闻学",
            category=MajorCategory.LITERATURE,
            subcategory="新闻传播学类",
            description="研究新闻传播和媒体运营",
            related_majors=["chinese_lang", "advertising"],
            parent_categories=["新闻传播学类", "文学类"]
        ))
        self._add_major(Major(
            id="advertising",
            name="广告学",
            category=MajorCategory.LITERATURE,
            subcategory="新闻传播学类",
            description="研究广告策划和创意设计",
            related_majors=["journalism", "marketing"],
            parent_categories=["新闻传播学类", "文学类"]
        ))
        self._add_major(Major(
            id="marketing",
            name="市场营销",
            category=MajorCategory.MANAGEMENT,
            subcategory="工商管理类",
            description="研究市场分析和营销策略",
            related_majors=["advertising", "business_admin"],
            parent_categories=["工商管理类", "管理学类"]
        ))
        self._add_major(Major(
            id="business_admin",
            name="工商管理",
            category=MajorCategory.MANAGEMENT,
            subcategory="工商管理类",
            description="研究企业管理和经营决策",
            related_majors=[["accounting", "marketing", "human_resources"]],
            parent_categories=["工商管理类", "管理学类"]
        ))
        self._add_major(Major(
            id="human_resources",
            name="人力资源管理",
            category=MajorCategory.MANAGEMENT,
            subcategory="工商管理类",
            description="研究人力资源开发和配置",
            related_majors=["business_admin", "applied_psychology"],
            parent_categories=["工商管理类", "管理学类"]
        ))

    def _add_major(self, major: Major):
        """添加专业节点"""
        self.majors[major.id] = major
        # 按类别分组
        category_key = major.category.value
        if category_key not in self.categories:
            self.categories[category_key] = []
        self.categories[category_key].append(major.id)

    def get_major(self, name_or_id: str) -> Optional[Major]:
        """通过名称或ID获取专业"""
        # 先尝试直接ID匹配
        if name_or_id in self.majors:
            return self.majors[name_or_id]
        # 再尝试名称匹配
        for major in self.majors.values():
            if major.name == name_or_id or name_or_id in major.name:
                return major
        return None

    def find_path(self, from_name: str, to_name: str) -> List[str]:
        """
        查找两个专业之间的关系路径
        使用BFS算法找到最短路径
        """
        from_major = self.get_major(from_name)
        to_major = self.get_major(to_name)

        if not from_major or not to_major:
            return []

        if from_major.id == to_major.id:
            return [from_major.name]

        # BFS查找最短路径
        visited = {from_major.id}
        queue = [(from_major.id, [from_major.name])]

        while queue:
            current_id, path = queue.pop(0)
            current = self.majors.get(current_id)

            if not current:
                continue

            # 检查所有相关节点
            neighbors = current.related_majors + current.parent_categories

            for neighbor_id in neighbors:
                if neighbor_id in self.majors and neighbor_id not in visited:
                    new_path = path + [self.majors[neighbor_id].name]
                    if neighbor_id == to_major.id:
                        return new_path
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, new_path))

        return []

    def compare_majors(self, name1: str, name2: str) -> Dict:
        """对比两个专业的关系"""
        major1 = self.get_major(name1)
        major2 = self.get_major(name2)

        if not major1 or not major2:
            return {"error": "专业未找到"}

        # 查找关系路径
        path = self.find_path(name1, name2)

        # 判断关系类型
        relationship = self._analyze_relationship(major1, major2, path)

        return {
            "major1": {
                "name": major1.name,
                "category": major1.category.value,
                "subcategory": major1.subcategory,
                "description": major1.description
            },
            "major2": {
                "name": major2.name,
                "category": major2.category.value,
                "subcategory": major2.subcategory,
                "description": major2.description
            },
            "relationship": relationship,
            "path": path,
            "same_category": major1.category == major2.category,
            "same_subcategory": major1.subcategory == major2.subcategory
        }

    def _analyze_relationship(self, m1: Major, m2: Major, path: List[str]) -> str:
        """分析两个专业之间的关系类型"""
        if m1.id == m2.id:
            return "完全相同"

        if m2.id in m1.related_majors or m1.id in m2.related_majors:
            return "直接相关"

        if m1.category == m2.category:
            if m1.subcategory == m2.subcategory:
                return "同一大类下的同专业类"
            return "同一大类下的不同专业类"

        # 检查是否有共同的相关专业
        common = set(m1.related_majors) & set(m2.related_majors)
        if common:
            return f"间接相关（通过{self.majors[list(common)[0]].name}）"

        if len(path) > 0:
            return f"通过{len(path)-1}层关系关联"

        return "关联较弱"

    def get_category_majors(self, category: str) -> List[Major]:
        """获取某个门类下的所有专业"""
        if category in self.categories:
            return [self.majors[mid] for mid in self.categories[category]]
        return []

    def export_to_json(self, filepath: str):
        """导出图谱为JSON"""
        data = {
            "majors": {
                mid: {
                    "name": m.name,
                    "category": m.category.value,
                    "subcategory": m.subcategory,
                    "description": m.description,
                    "related": m.related_majors,
                    "parents": m.parent_categories
                }
                for mid, m in self.majors.items()
            },
            "categories": self.categories
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath


# 全局图谱实例
_graph = None


def get_graph() -> MajorGraph:
    """获取全局图谱实例（单例模式）"""
    global _graph
    if _graph is None:
        _graph = MajorGraph()
    return _graph


def compare_majors(major1: str, major2: str) -> Dict:
    """对比两个专业（便捷函数）"""
    return get_graph().compare_majors(major1, major2)


def find_path(from_major: str, to_major: str) -> List[str]:
    """查找专业路径（便捷函数）"""
    return get_graph().find_path(from_major, to_major)


if __name__ == "__main__":
    # 测试
    graph = get_graph()

    print("=" * 80)
    print("专业关系图谱测试")
    print("=" * 80)

    # 测试专业对比
    test_cases = [
        ("金融学", "经济学"),
        ("金融学", "会计学"),
        ("法学", "知识产权"),
        ("临床医学", "护理学"),
        ("计算机科学与技术", "软件工程"),
        ("教育学", "心理学"),
    ]

    for m1, m2 in test_cases:
        result = compare_majors(m1, m2)
        print(f"\n{m1} vs {m2}:")
        print(f"  关系: {result['relationship']}")
        print(f"  同大类: {'是' if result['same_category'] else '否'}")
        if result['path']:
            print(f"  路径: {' -> '.join(result['path'])}")

    # 导出JSON
    export_path = graph.export_to_json("major_graph_data.json")
    print(f"\n图谱已导出到: {export_path}")
