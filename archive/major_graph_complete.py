#!/usr/bin/env python3
"""
专业关系图谱 - 完整版
包含所有常见专业类别 + 专业对比功能
"""

from major_graph import MajorRelationGraph


class CompleteMajorGraph(MajorRelationGraph):
    """完整版专业关系图谱"""

    def _build_graph(self):
        """构建完整的专业关系图谱"""

        major_data = {
            # 经济学门类 (02)
            "经济学类": {
                "code": "0201",
                "majors": [
                    {"name": "经济学", "code": "020101", "related": ["金融学", "财政学", "统计学"]},
                    {
                        "name": "经济统计学",
                        "code": "020102",
                        "related": ["统计学", "经济学", "数据科学"],
                    },
                    {"name": "国民经济管理", "code": "020103", "related": ["经济学", "管理学"]},
                    {
                        "name": "资源与环境经济学",
                        "code": "020104",
                        "related": ["经济学", "环境科学"],
                    },
                    {"name": "商务经济学", "code": "020105", "related": ["经济学", "国际贸易"]},
                    {"name": "能源经济", "code": "020106", "related": ["经济学", "能源工程"]},
                    {"name": "劳动经济学", "code": "020107", "related": ["经济学", "人力资源管理"]},
                    {"name": "经济工程", "code": "020108", "related": ["经济学", "工程管理"]},
                    {
                        "name": "数字经济",
                        "code": "020109",
                        "related": ["经济学", "数据科学", "计算机"],
                    },
                ],
            },
            "财政学类": {
                "code": "0202",
                "majors": [
                    {"name": "财政学", "code": "020201", "related": ["税收学", "经济学", "金融学"]},
                    {"name": "税收学", "code": "020202", "related": ["财政学", "会计学", "经济学"]},
                    {"name": "国际税收", "code": "020203", "related": ["税收学", "国际经济与贸易"]},
                ],
            },
            "金融学类": {
                "code": "0203",
                "majors": [
                    {"name": "金融学", "code": "020301", "related": ["经济学", "投资学", "保险学"]},
                    {"name": "金融工程", "code": "020302", "related": ["金融学", "数学", "计算机"]},
                    {"name": "保险学", "code": "020303", "related": ["金融学", "精算学"]},
                    {"name": "投资学", "code": "020304", "related": ["金融学", "经济学"]},
                    {"name": "金融数学", "code": "020305", "related": ["金融学", "数学"]},
                    {"name": "信用管理", "code": "020306", "related": ["金融学", "经济学"]},
                    {"name": "经济与金融", "code": "020307", "related": ["经济学", "金融学"]},
                    {"name": "精算学", "code": "020308", "related": ["金融学", "数学", "统计学"]},
                    {"name": "互联网金融", "code": "020309", "related": ["金融学", "计算机"]},
                    {
                        "name": "金融科技",
                        "code": "020310",
                        "related": ["金融学", "计算机", "数据科学"],
                    },
                ],
            },
            "经济与贸易类": {
                "code": "0204",
                "majors": [
                    {"name": "国际经济与贸易", "code": "020401", "related": ["经济学", "商务英语"]},
                    {"name": "贸易经济", "code": "020402", "related": ["经济学", "国际贸易"]},
                ],
            },
            # 法学门类 (03)
            "法学类": {
                "code": "0301",
                "majors": [
                    {"name": "法学", "code": "030101", "related": ["知识产权", "监狱学"]},
                    {"name": "知识产权", "code": "030102", "related": ["法学", "专利代理"]},
                    {"name": "监狱学", "code": "030103", "related": ["法学", "心理学"]},
                    {
                        "name": "信用风险管理与法律防控",
                        "code": "030104",
                        "related": ["法学", "金融学"],
                    },
                    {"name": "国际经贸规则", "code": "030105", "related": ["法学", "国际贸易"]},
                    {"name": "司法警察学", "code": "030106", "related": ["法学", "公安学"]},
                    {"name": "社区矫正", "code": "030107", "related": ["法学", "社会工作"]},
                ],
            },
            "政治学类": {
                "code": "0302",
                "majors": [
                    {
                        "name": "政治学与行政学",
                        "code": "030201",
                        "related": ["行政管理", "公共管理"],
                    },
                    {"name": "国际政治", "code": "030202", "related": ["外交学", "国际关系"]},
                    {"name": "外交学", "code": "030203", "related": ["国际政治", "外语"]},
                    {
                        "name": "国际事务与国际关系",
                        "code": "030204",
                        "related": ["国际政治", "外交学"],
                    },
                    {
                        "name": "政治学、经济学与哲学",
                        "code": "030205",
                        "related": ["政治学", "经济学", "哲学"],
                    },
                ],
            },
            "社会学类": {
                "code": "0303",
                "majors": [
                    {"name": "社会学", "code": "030301", "related": ["社会工作", "心理学"]},
                    {
                        "name": "社会工作",
                        "code": "030302",
                        "related": ["社会学", "心理学", "公共管理"],
                    },
                    {"name": "人类学", "code": "030303", "related": ["社会学", "民族学"]},
                    {"name": "女性学", "code": "030304", "related": ["社会学", "性别研究"]},
                    {"name": "家政学", "code": "030305", "related": ["社会学", "管理学"]},
                ],
            },
            "马克思主义理论类": {
                "code": "0305",
                "majors": [
                    {
                        "name": "科学社会主义",
                        "code": "030501",
                        "related": ["马克思主义理论", "政治学"],
                    },
                    {
                        "name": "中国共产党历史",
                        "code": "030502",
                        "related": ["历史学", "马克思主义理论"],
                    },
                    {
                        "name": "思想政治教育",
                        "code": "030503",
                        "related": ["教育学", "马克思主义理论"],
                    },
                    {"name": "马克思主义理论", "code": "030504", "related": ["哲学", "政治学"]},
                ],
            },
            # 教育学门类 (04)
            "教育学类": {
                "code": "0401",
                "majors": [
                    {"name": "教育学", "code": "040101", "related": ["心理学", "教育技术学"]},
                    {"name": "科学教育", "code": "040102", "related": ["教育学", "理学"]},
                    {"name": "人文教育", "code": "040103", "related": ["教育学", "文学", "历史学"]},
                    {
                        "name": "教育技术学",
                        "code": "040104",
                        "related": ["教育学", "计算机", "心理学"],
                    },
                    {"name": "艺术教育", "code": "040105", "related": ["教育学", "艺术学"]},
                    {"name": "学前教育", "code": "040106", "related": ["教育学", "心理学"]},
                    {"name": "小学教育", "code": "040107", "related": ["教育学", "心理学"]},
                    {"name": "特殊教育", "code": "040108", "related": ["教育学", "心理学", "医学"]},
                    {"name": "华文教育", "code": "040109", "related": ["教育学", "汉语言文学"]},
                    {
                        "name": "教育康复学",
                        "code": "040110",
                        "related": ["教育学", "康复医学", "心理学"],
                    },
                    {"name": "卫生教育", "code": "040111", "related": ["教育学", "医学"]},
                    {
                        "name": "认知科学与技术",
                        "code": "040112",
                        "related": ["教育学", "心理学", "计算机"],
                    },
                ],
            },
            "体育学类": {
                "code": "0402",
                "majors": [
                    {"name": "体育教育", "code": "040201", "related": ["运动训练", "教育学"]},
                    {"name": "运动训练", "code": "040202", "related": ["体育教育", "运动科学"]},
                    {
                        "name": "社会体育指导与管理",
                        "code": "040203",
                        "related": ["体育学", "管理学"],
                    },
                    {
                        "name": "武术与民族传统体育",
                        "code": "040204",
                        "related": ["体育学", "民族学"],
                    },
                    {
                        "name": "运动人体科学",
                        "code": "040205",
                        "related": ["体育学", "医学", "生物学"],
                    },
                    {"name": "运动康复", "code": "040206", "related": ["体育学", "康复医学"]},
                ],
            },
            # 文学门类 (05)
            "中国语言文学类": {
                "code": "0501",
                "majors": [
                    {
                        "name": "汉语言文学",
                        "code": "050101",
                        "related": ["汉语言", "新闻学", "教育学"],
                    },
                    {"name": "汉语言", "code": "050102", "related": ["汉语言文学", "语言学"]},
                    {
                        "name": "汉语国际教育",
                        "code": "050103",
                        "related": ["汉语言文学", "外语", "教育学"],
                    },
                    {
                        "name": "中国少数民族语言文学",
                        "code": "050104",
                        "related": ["汉语言文学", "民族学"],
                    },
                    {"name": "古典文献学", "code": "050105", "related": ["汉语言文学", "历史学"]},
                    {"name": "应用语言学", "code": "050106", "related": ["语言学", "计算机"]},
                    {"name": "秘书学", "code": "050107", "related": ["汉语言文学", "管理学"]},
                ],
            },
            "外国语言文学类": {
                "code": "0502",
                "majors": [
                    {"name": "英语", "code": "050201", "related": ["翻译", "商务英语"]},
                    {"name": "俄语", "code": "050202", "related": ["翻译", "国际关系"]},
                    {"name": "德语", "code": "050203", "related": ["翻译", "经贸"]},
                    {"name": "法语", "code": "050204", "related": ["翻译", "外交"]},
                    {"name": "西班牙语", "code": "050205", "related": ["翻译", "经贸"]},
                    {"name": "阿拉伯语", "code": "050206", "related": ["翻译", "国际关系"]},
                    {"name": "日语", "code": "050207", "related": ["翻译", "经贸"]},
                    {"name": "商务英语", "code": "050262", "related": ["英语", "国际贸易"]},
                    {"name": "翻译", "code": "050261", "related": ["外语", "语言学"]},
                ],
            },
            "新闻传播学类": {
                "code": "0503",
                "majors": [
                    {"name": "新闻学", "code": "050301", "related": ["传播学", "汉语言文学"]},
                    {"name": "广播电视学", "code": "050302", "related": ["新闻学", "影视"]},
                    {"name": "广告学", "code": "050303", "related": ["传播学", "市场营销"]},
                    {"name": "传播学", "code": "050304", "related": ["新闻学", "社会学"]},
                    {"name": "编辑出版学", "code": "050305", "related": ["新闻学", "汉语言文学"]},
                    {"name": "网络与新媒体", "code": "050306", "related": ["传播学", "计算机"]},
                    {"name": "数字出版", "code": "050307", "related": ["编辑出版学", "计算机"]},
                ],
            },
            # 理学门类 (07)
            "数学类": {
                "code": "0701",
                "majors": [
                    {
                        "name": "数学与应用数学",
                        "code": "070101",
                        "related": ["统计学", "计算机", "物理学"],
                    },
                    {
                        "name": "信息与计算科学",
                        "code": "070102",
                        "related": ["数学", "计算机", "数据科学"],
                    },
                    {"name": "数理基础科学", "code": "070103", "related": ["数学", "物理学"]},
                    {
                        "name": "数据计算及应用",
                        "code": "070104",
                        "related": ["数学", "统计学", "计算机"],
                    },
                ],
            },
            "物理学类": {
                "code": "0702",
                "majors": [
                    {"name": "物理学", "code": "070201", "related": ["应用物理学", "光电信息"]},
                    {
                        "name": "应用物理学",
                        "code": "070202",
                        "related": ["物理学", "材料科学", "电子"],
                    },
                    {"name": "核物理", "code": "070203", "related": ["物理学", "核工程"]},
                    {"name": "声学", "code": "070204", "related": ["物理学", "电子", "通信"]},
                    {
                        "name": "系统科学与工程",
                        "code": "070205",
                        "related": ["物理学", "计算机", "管理学"],
                    },
                ],
            },
            "化学类": {
                "code": "0703",
                "majors": [
                    {"name": "化学", "code": "070301", "related": ["应用化学", "材料化学"]},
                    {"name": "应用化学", "code": "070302", "related": ["化学", "化工", "材料"]},
                    {"name": "化学生物学", "code": "070303", "related": ["化学", "生物学"]},
                    {"name": "分子科学与工程", "code": "070304", "related": ["化学", "材料"]},
                    {"name": "能源化学", "code": "070305", "related": ["化学", "能源工程"]},
                ],
            },
            "生物科学类": {
                "code": "0710",
                "majors": [
                    {"name": "生物科学", "code": "071001", "related": ["生物技术", "生态学"]},
                    {"name": "生物技术", "code": "071002", "related": ["生物科学", "生物工程"]},
                    {
                        "name": "生物信息学",
                        "code": "071003",
                        "related": ["生物学", "计算机", "统计学"],
                    },
                    {"name": "生态学", "code": "071004", "related": ["生物学", "环境科学"]},
                ],
            },
            "统计学类": {
                "code": "0712",
                "majors": [
                    {"name": "统计学", "code": "071201", "related": ["数学", "经济学", "数据科学"]},
                    {
                        "name": "应用统计学",
                        "code": "071202",
                        "related": ["统计学", "计算机", "经济学"],
                    },
                    {"name": "数据科学", "code": "071203", "related": ["统计学", "计算机", "数学"]},
                    {
                        "name": "生物统计学",
                        "code": "071204",
                        "related": ["统计学", "生物学", "医学"],
                    },
                ],
            },
            # 工学门类 (08)
            "计算机类": {
                "code": "0809",
                "majors": [
                    {
                        "name": "计算机科学与技术",
                        "code": "080901",
                        "related": ["软件工程", "网络工程"],
                    },
                    {"name": "软件工程", "code": "080902", "related": ["计算机", "网络工程"]},
                    {"name": "网络工程", "code": "080903", "related": ["计算机", "信息安全"]},
                    {"name": "信息安全", "code": "080904", "related": ["计算机", "密码学"]},
                    {"name": "物联网工程", "code": "080905", "related": ["计算机", "电子", "通信"]},
                    {
                        "name": "数字媒体技术",
                        "code": "080906",
                        "related": ["计算机", "设计", "传媒"],
                    },
                    {"name": "智能科学与技术", "code": "080907", "related": ["计算机", "人工智能"]},
                    {
                        "name": "数据科学与大数据技术",
                        "code": "080910",
                        "related": ["计算机", "统计学", "数学"],
                    },
                    {"name": "网络空间安全", "code": "080911", "related": ["计算机", "信息安全"]},
                    {
                        "name": "人工智能",
                        "code": "080717",
                        "related": ["计算机", "数学", "认知科学"],
                    },
                ],
            },
            "电子信息类": {
                "code": "0807",
                "majors": [
                    {"name": "电子信息工程", "code": "080701", "related": ["通信工程", "电子科学"]},
                    {"name": "电子科学与技术", "code": "080702", "related": ["微电子", "物理电子"]},
                    {"name": "通信工程", "code": "080703", "related": ["电子信息", "网络工程"]},
                    {"name": "微电子科学与工程", "code": "080704", "related": ["电子", "集成电路"]},
                    {
                        "name": "光电信息科学与工程",
                        "code": "080705",
                        "related": ["光学", "电子", "物理"],
                    },
                    {"name": "信息工程", "code": "080706", "related": ["电子信息", "计算机"]},
                ],
            },
            # 医学门类 (10)
            "临床医学类": {
                "code": "1002",
                "majors": [
                    {
                        "name": "临床医学",
                        "code": "100201",
                        "related": ["医学影像学", "麻醉学", "儿科学"],
                    },
                    {"name": "麻醉学", "code": "100202", "related": ["临床医学", "重症医学"]},
                    {"name": "医学影像学", "code": "100203", "related": ["临床医学", "放射医学"]},
                    {"name": "眼视光医学", "code": "100204", "related": ["临床医学", "眼科学"]},
                    {"name": "精神医学", "code": "100205", "related": ["临床医学", "心理学"]},
                    {"name": "放射医学", "code": "100206", "related": ["临床医学", "医学影像"]},
                    {"name": "儿科学", "code": "100207", "related": ["临床医学", "儿科"]},
                ],
            },
            "口腔医学类": {
                "code": "1003",
                "majors": [
                    {"name": "口腔医学", "code": "100301", "related": ["临床医学", "口腔技术"]},
                ],
            },
            "公共卫生与预防医学类": {
                "code": "1004",
                "majors": [
                    {"name": "预防医学", "code": "100401", "related": ["临床医学", "公共卫生"]},
                    {
                        "name": "食品卫生与营养学",
                        "code": "100402",
                        "related": ["预防医学", "营养学"],
                    },
                    {
                        "name": "妇幼保健医学",
                        "code": "100403",
                        "related": ["预防医学", "临床医学", "儿科"],
                    },
                    {"name": "卫生监督", "code": "100404", "related": ["预防医学", "卫生管理"]},
                    {"name": "全球健康学", "code": "100405", "related": ["预防医学", "国际卫生"]},
                ],
            },
            "中医学类": {
                "code": "1005",
                "majors": [
                    {"name": "中医学", "code": "100501", "related": ["针灸推拿学", "中医骨伤科学"]},
                    {"name": "针灸推拿学", "code": "100502", "related": ["中医学", "康复医学"]},
                    {"name": "藏医学", "code": "100503", "related": ["中医学", "民族医学"]},
                    {"name": "蒙医学", "code": "100504", "related": ["中医学", "民族医学"]},
                    {"name": "维医学", "code": "100505", "related": ["中医学", "民族医学"]},
                    {"name": "壮医学", "code": "100506", "related": ["中医学", "民族医学"]},
                    {"name": "哈医学", "code": "100507", "related": ["中医学", "民族医学"]},
                    {"name": "傣医学", "code": "100508", "related": ["中医学", "民族医学"]},
                    {"name": "回医学", "code": "100509", "related": ["中医学", "民族医学"]},
                    {"name": "中医康复学", "code": "100510", "related": ["中医学", "康复医学"]},
                    {"name": "中医养生学", "code": "100511", "related": ["中医学", "预防医学"]},
                    {"name": "中医儿科学", "code": "100512", "related": ["中医学", "儿科学"]},
                    {"name": "中医骨伤科学", "code": "100513", "related": ["中医学", "骨科学"]},
                ],
            },
            "护理学类": {
                "code": "1011",
                "majors": [
                    {"name": "护理学", "code": "101101", "related": ["助产学", "临床医学"]},
                    {
                        "name": "助产学",
                        "code": "101102",
                        "related": ["护理学", "临床医学", "妇产科"],
                    },
                ],
            },
            # 管理学门类 (12)
            "管理科学与工程类": {
                "code": "1201",
                "majors": [
                    {"name": "管理科学", "code": "120101", "related": ["管理学", "数学", "经济学"]},
                    {
                        "name": "信息管理与信息系统",
                        "code": "120102",
                        "related": ["管理学", "计算机", "信息系统"],
                    },
                    {
                        "name": "工程管理",
                        "code": "120103",
                        "related": ["管理学", "土木工程", "经济学"],
                    },
                    {
                        "name": "房地产开发与管理",
                        "code": "120104",
                        "related": ["管理学", "经济学", "土木工程"],
                    },
                    {"name": "工程造价", "code": "120105", "related": ["管理学", "工程", "经济学"]},
                    {
                        "name": "大数据管理与应用",
                        "code": "120108",
                        "related": ["管理学", "数据科学", "计算机"],
                    },
                ],
            },
            "工商管理类": {
                "code": "1202",
                "majors": [
                    {
                        "name": "工商管理",
                        "code": "120201",
                        "related": ["市场营销", "人力资源管理", "财务管理"],
                    },
                    {
                        "name": "市场营销",
                        "code": "120202",
                        "related": ["工商管理", "广告学", "心理学"],
                    },
                    {
                        "name": "会计学",
                        "code": "120203",
                        "related": ["财务管理", "审计学", "经济学"],
                    },
                    {
                        "name": "财务管理",
                        "code": "120204",
                        "related": ["会计学", "金融学", "经济学"],
                    },
                    {
                        "name": "国际商务",
                        "code": "120205",
                        "related": ["工商管理", "国际贸易", "外语"],
                    },
                    {
                        "name": "人力资源管理",
                        "code": "120206",
                        "related": ["工商管理", "心理学", "劳动经济学"],
                    },
                    {"name": "审计学", "code": "120207", "related": ["会计学", "财务管理", "法学"]},
                    {
                        "name": "资产评估",
                        "code": "120208",
                        "related": ["会计学", "金融学", "经济学"],
                    },
                    {
                        "name": "物业管理",
                        "code": "120209",
                        "related": ["工商管理", "房地产", "服务管理"],
                    },
                    {
                        "name": "文化产业管理",
                        "code": "120210",
                        "related": ["工商管理", "文化产业", "艺术管理"],
                    },
                ],
            },
            "公共管理类": {
                "code": "1204",
                "majors": [
                    {
                        "name": "公共事业管理",
                        "code": "120401",
                        "related": ["行政管理", "社会学", "管理学"],
                    },
                    {
                        "name": "行政管理",
                        "code": "120402",
                        "related": ["公共管理", "政治学", "法学"],
                    },
                    {
                        "name": "劳动与社会保障",
                        "code": "120403",
                        "related": ["公共管理", "人力资源管理", "社会学"],
                    },
                    {
                        "name": "土地资源管理",
                        "code": "120404",
                        "related": ["公共管理", "地理学", "经济学"],
                    },
                    {
                        "name": "城市管理",
                        "code": "120405",
                        "related": ["公共管理", "城市规划", "管理学"],
                    },
                    {
                        "name": "海关管理",
                        "code": "120406",
                        "related": ["公共管理", "国际贸易", "法学"],
                    },
                    {
                        "name": "交通管理",
                        "code": "120407",
                        "related": ["公共管理", "交通运输", "管理学"],
                    },
                    {"name": "海事管理", "code": "120408", "related": ["公共管理", "航运", "法学"]},
                    {
                        "name": "公共关系学",
                        "code": "120409",
                        "related": ["公共管理", "传播学", "管理学"],
                    },
                    {
                        "name": "健康服务与管理",
                        "code": "120410",
                        "related": ["公共管理", "医学", "管理学"],
                    },
                ],
            },
        }

        # 创建节点和边
        for category, data in major_data.items():
            # 创建大类节点
            cat_id = f"CAT_{data['code']}"
            from major_graph import MajorNode

            self.nodes[cat_id] = MajorNode(
                id=cat_id, name=category, type="category", code=data["code"]
            )

            # 创建具体专业节点
            for major in data["majors"]:
                major_id = f"MAJ_{major['code']}"
                self.nodes[major_id] = MajorNode(
                    id=major_id,
                    name=major["name"],
                    type="major",
                    category=category,
                    code=major["code"],
                    related=major.get("related", []),
                )

                # 添加边：专业 -> 大类
                self.edges.append((major_id, cat_id, "belongs_to"))

                # 添加边：专业之间的关联
                for related_name in major.get("related", []):
                    # 查找相关专业的ID
                    for node_id, node in self.nodes.items():
                        if node.name == related_name and node.type == "major":
                            self.edges.append((major_id, node_id, "related"))
                            break

    def compare_majors(self, major1: str, major2: str) -> dict:
        """
        对比两个专业
        返回详细的对比分析
        """
        node1 = None
        node2 = None

        for node in self.nodes.values():
            if node.name == major1:
                node1 = node
            if node.name == major2:
                node2 = node

        if not node1 or not node2:
            return {"error": "专业未找到"}

        # 基础信息对比
        comparison = {
            "专业1": {"name": node1.name, "category": node1.category, "code": node1.code},
            "专业2": {"name": node2.name, "category": node2.category, "code": node2.code},
        }

        # 判断是否同一大类
        same_category = node1.category == node2.category
        comparison["同大类"] = same_category

        # 查找关系路径
        path = self.find_path(major1, major2)
        comparison["关系路径"] = path if path else ["无直接关联"]

        # 关联度评分
        if same_category:
            comparison["关联度"] = {
                "score": 100,
                "level": "完全相关",
                "reason": "同属" + node1.category,
            }
        elif major2 in node1.related:
            comparison["关联度"] = {"score": 80, "level": "高度相关", "reason": "相关专业"}
        elif path and len(path) > 2:
            comparison["关联度"] = {"score": 50, "level": "中度相关", "reason": "通过大类间接关联"}
        else:
            comparison["关联度"] = {"score": 0, "level": "低度相关", "reason": "专业领域差异较大"}

        # 报考建议
        if same_category or major2 in node1.related:
            comparison["报考建议"] = f"[OK] {major1}可以报考要求{major2}的岗位"
        elif comparison["关联度"]["score"] >= 50:
            comparison["报考建议"] = (
                f"[MAYBE] {major1}可能可以报考要求{major2}的岗位（建议咨询招考单位）"
            )
        else:
            comparison["报考建议"] = f"[NO] {major1}不建议报考要求{major2}的岗位"

        return comparison


if __name__ == "__main__":
    print("=" * 80)
    print("完整版专业关系图谱")
    print("=" * 80)

    graph = CompleteMajorGraph()

    print("\n图谱统计:")
    print(f"  节点数: {len(graph.nodes)}")
    print(f"  关系数: {len(graph.edges)}")

    # 分类统计
    categories = {}
    for node in graph.nodes.values():
        if node.type == "category":
            categories[node.name] = 0
        elif node.category:
            categories[node.category] = categories.get(node.category, 0) + 1

    print("\n专业大类分布:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}个专业")

    # 专业对比测试
    print("\n" + "=" * 80)
    print("专业对比测试")
    print("=" * 80)

    test_pairs = [
        ("经济学", "金融学"),
        ("统计学", "经济学"),
        ("计算机科学与技术", "软件工程"),
        ("法学", "经济学"),
        ("临床医学", "护理学"),
        ("汉语言文学", "新闻学"),
    ]

    for m1, m2 in test_pairs:
        result = graph.compare_majors(m1, m2)
        print(f"\n{m1} vs {m2}:")
        print(f"  同大类: {'是' if result['同大类'] else '否'}")
        print(f"  关联度: {result['关联度']['level']} ({result['关联度']['score']}分)")
        print(f"  路径: {' -> '.join(result['关系路径'])}")
        print(f"  建议: {result['报考建议']}")
