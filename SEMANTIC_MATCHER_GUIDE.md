# 语义匹配器使用指南

🧠 智能理解岗位要求中的模糊表达，告别死板的字符串匹配

---

## 功能概览

| 功能模块 | 支持的表达 | 示例 |
|---------|-----------|------|
| **学历语义匹配** | 及以上、全日制、模糊描述 | "本科及以上"、"全日制本科" |
| **户籍语义匹配** | 省市关系、本市户籍 | "限济南市户籍"、"山东省户籍" |
| **工作年限匹配** | 年以上、应届生、范围 | "2年以上"、"应届毕业生" |

---

## 1. 学历语义匹配

### 支持的表达

```python
# 等级模式
"本科及以上"      # 本科、硕士、博士均可
"大专及以上"      # 大专、本科、硕士、博士均可
"硕士研究生"      # 精确匹配
"研究生"          # 匹配硕士和博士

# 修饰词
"全日制本科"      # 识别为本科
"统招本科"        # 识别为本科
"普通本科"        # 识别为本科

# 模糊匹配
"硕士"           # 匹配"硕士研究生"
"博士"           # 匹配"博士研究生"
"大专"           # 匹配"专科"
```

### 使用示例

```python
from semantic_matcher import EducationMatcher

matcher = EducationMatcher("硕士研究生")

# 测试各种表达
result = matcher.match("本科及以上")
print(result.match)     # True
print(result.reason)    # 学历符合：硕士研究生 >= 本科

result = matcher.match("全日制本科")
print(result.match)     # True (学历高于要求)

# 专科 vs 本科要求
matcher = EducationMatcher("大专")
result = matcher.match("本科及以上")
print(result.match)     # False
print(result.reason)    # 学历不足：大专 < 本科
```

### 学历等级定义

| 等级 | 关键词 |
|------|--------|
| 博士 | 博士、博士研究生 |
| 硕士 | 硕士、研究生、硕士研究生 |
| 本科 | 本科、大学本科、全日制本科 |
| 专科 | 专科、大专、高职 |

---

## 2. 户籍语义匹配

### 支持的表达

```python
# 精确匹配
"限济南市户籍"
"限本市户籍"      # 需要结合岗位城市判断
"不限户籍"

# 省级匹配
"山东省户籍"      # 济南市、青岛市等都可匹配
"山西省户籍"

# 包含关系
"济南户籍"        # 模糊匹配
"山东户籍"
```

### 省-市关系映射

系统内置了山东、山西等省份的城市映射：

```python
CITY_TO_PROVINCE = {
    '济南': '山东', '青岛': '山东', '淄博': '山东',
    '太原': '山西', '大同': '山西', '阳泉': '山西',
    '北京': '北京', '上海': '上海',
    # ...
}
```

### 使用示例

```python
from semantic_matcher import HouseholdMatcher

matcher = HouseholdMatcher("济南市")

# 精确匹配
result = matcher.match_household("限济南市户籍")
print(result.match)     # True
print(result.reason)    # 户籍匹配：济南市

# 省级匹配
result = matcher.match_household("山东省户籍")
print(result.match)     # True
print(result.reason)    # 户籍符合：济南市属于山东省

# 不匹配
matcher = HouseholdMatcher("青岛市")
result = matcher.match_household("限济南市户籍")
print(result.match)     # False
```

### 性别匹配

```python
matcher = HouseholdMatcher("济南市", gender="男")

result = matcher.match_gender("限男性")
print(result.match)     # True

result = matcher.match_gender("限女性")
print(result.match)     # False
```

---

## 3. 工作年限语义匹配

### 支持的表达

```python
# 年以上模式
"2年以上"
"2年及以上"
"至少2年"
"不少于2年"

# 应届生模式
"应届毕业生"
"应届生"

# 范围模式
"3-5年工作经验"
"3到5年"
"3~5年"

# 无经验要求
"不限经验"
"无经验要求"
"经验不限"
```

### 使用示例

```python
from semantic_matcher import ExperienceMatcher

matcher = ExperienceMatcher(work_years=5)

# 年以上匹配
result = matcher.match("2年以上")
print(result.match)     # True
print(result.reason)    # 工作年限符合：5年 >= 2年

# 应届生匹配
matcher = ExperienceMatcher(work_years=0, is_fresh_graduate=True)
result = matcher.match("应届毕业生")
print(result.match)     # True

# 范围匹配
matcher = ExperienceMatcher(work_years=4)
result = matcher.match("3-5年工作经验")
print(result.match)     # True (在范围内)

# 年限不足
matcher = ExperienceMatcher(work_years=1)
result = matcher.match("2年以上")
print(result.match)     # False
print(result.reason)    # 工作年限不足：1年 < 2年
```

---

## 4. 统一语义匹配器

### 整合所有匹配维度

```python
from semantic_matcher import SemanticMatcher

# 用户档案
profile = {
    'education': '硕士研究生',
    'household': '济南市',
    'gender': '男',
    'work_years': 3,
    'is_fresh_graduate': False
}

# 创建统一匹配器
matcher = SemanticMatcher(profile)

# 岗位数据
job_data = {
    'education': '本科及以上',
    'household_requirement': '限济南市户籍',
    'gender_requirement': '不限',
    'experience_requirement': '2年以上'
}

# 执行所有匹配
results = matcher.match_all(job_data)

# 查看结果
for dimension, result in results.items():
    if result:
        print(f"{dimension}: {'通过' if result.match else '不通过'}")
        print(f"  原因: {result.reason}")
        print(f"  置信度: {result.confidence}")

# 获取汇总
all_passed, passed_reasons, failed_reasons = matcher.get_summary(results)
print(f"\n汇总: {'全部通过' if all_passed else '有不符合项'}")
```

---

## 5. V3版本集成

### 在JobMatcherV3中使用

```python
from job_matcher_v3 import JobMatcherV3
from dataclasses import dataclass

# 创建匹配器
matcher = JobMatcherV3("config_full.yaml")

# 创建岗位
job = Job(
    sheet_name="济南市",
    unit="济南市财政局",
    job_type="支农",
    major="经济学类",
    education="本科及以上",      # 语义匹配
    other="限济南市户籍，2年以上工作经验",  # 语义匹配
    recruit_count=5
)

# 执行匹配
result = matcher.match(job)

print(f"匹配等级: {result.match_level.value}")
print(f"匹配分数: {result.match_score}")
print("匹配原因:")
for reason in result.match_reasons:
    print(f"  • {reason}")
```

### 匹配流程

```
┌─────────────────────────────────────────────────────┐
│                    JobMatcherV3                      │
├─────────────────────────────────────────────────────┤
│  1. 专业匹配 (LLM/本地)                              │
│  2. 学历匹配 (语义理解) ← 新增                       │
│  3. 户籍匹配 (语义理解) ← 新增                       │
│  4. 工作年限匹配 (语义理解) ← 新增                   │
│  5. 性别匹配 (语义理解) ← 新增                       │
│  6. 计算综合得分                                     │
└─────────────────────────────────────────────────────┘
```

---

## 6. 测试示例

### 运行测试

```bash
# 测试所有语义匹配功能
uv run semantic_matcher.py

# 测试V3匹配器
uv run job_matcher_v3.py
```

### 测试场景

| 场景 | 用户条件 | 岗位要求 | 结果 |
|------|---------|---------|------|
| 学历语义 | 硕士研究生 | 本科及以上 | ✓ 通过 |
| 户籍语义 | 济南市 | 山东省户籍 | ✓ 通过 |
| 年限语义 | 工作3年 | 2年以上 | ✓ 通过 |
| 应届生 | 应届毕业生 | 限应届 | ✓ 通过 |
| 性别语义 | 男性 | 限男性 | ✓ 通过 |
| 范围匹配 | 工作4年 | 3-5年 | ✓ 通过 |

---

## 7. API集成

### FastAPI端点

```python
from fastapi import FastAPI
from semantic_matcher import SemanticMatcher

app = FastAPI()

@app.post("/api/match/semantic")
def semantic_match(profile: dict, job_requirements: dict):
    """
    语义匹配API

    请求:
    {
        "profile": {
            "education": "硕士研究生",
            "household": "济南市",
            "gender": "男",
            "work_years": 3
        },
        "job_requirements": {
            "education": "本科及以上",
            "household": "山东省户籍",
            "experience": "2年以上"
        }
    }
    """
    matcher = SemanticMatcher(profile)
    results = matcher.match_all(job_requirements)
    all_passed, passed, failed = matcher.get_summary(results)

    return {
        "all_passed": all_passed,
        "passed": passed,
        "failed": failed,
        "details": {k: v.__dict__ if v else None for k, v in results.items()}
    }
```

---

## 8. 扩展指南

### 添加新的城市映射

```python
# 在 HouseholdMatcher._check_location 中添加
CITY_TO_PROVINCE = {
    # 山东省
    '济南': '山东', '青岛': '山东',
    # 添加你的省份
    '你的城市': '你的省份',
}
```

### 添加新的学历关键词

```python
# 在 EducationMatcher.EDUCATION_KEYWORDS 中添加
EDUCATION_KEYWORDS = {
    EducationLevel.BENKE: [
        '本科', '大学本科', '全日制本科',
        '你的新关键词'  # 添加这里
    ],
}
```

### 添加新的工作年限模式

```python
# 在 ExperienceMatcher.match 中添加新的正则模式
# 模式4: 你的新模式
match = re.search(r'你的正则表达式', req)
if match:
    # 处理逻辑
    pass
```

---

## 总结

语义匹配器让系统能够：

1. **理解模糊表达** - 不再依赖精确字符串匹配
2. **处理层级关系** - 如省-市包含关系、学历等级
3. **支持多种模式** - 及以上、范围、应届生等
4. **高可扩展性** - 易于添加新的表达模式

**核心文件**:
- `semantic_matcher.py` - 语义匹配器实现
- `job_matcher_v3.py` - V3版本集成
- `SEMANTIC_MATCHER_GUIDE.md` - 本指南

**测试命令**:
```bash
uv run semantic_matcher.py  # 运行测试
uv run job_matcher_v3.py    # V3集成测试
```
