# JobMatch 智能选岗平台 - 商业级实施方案

> 版本：v1.0
> 日期：2026-04-29
> 目标：达到华图/中公等商业筛选工具水平

---

## 一、项目背景与目标

### 1.1 现状问题

| 问题 | 说明 |
|-----|------|
| 硬编码列名 | 仅支持三支一扶特定Excel格式 |
| 匹配维度不足 | 缺少政治面貌、年龄、基层经验等 |
| 无智能推荐 | 只有"符合/不符合"，无冲/稳/保分层 |
| 无历史分析 | 无法查看历年分数线和竞争趋势 |
| 只有CLI界面 | 非技术人员无法使用 |

### 1.2 目标

**短期**：支持多种考公考编岗位筛选（公务员、事业编、教师等）

**长期**：成为考生的智能选岗助手，提供竞争分析、智能推荐、历年对比

### 1.3 目标平台

**微信小程序** + **FastAPI后端** + **MySQL数据库**

---

## 二、技术架构

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      微信小程序 (WeChat MiniApp)                  │
│                                                                   │
│   pages: index / filter / results / detail / favorites / profile │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI 后端服务                             │
│                                                                   │
│   /api/auth/login        - 微信登录                               │
│   /api/jobs/upload       - Excel上传                              │
│   /api/jobs/search       - 岗位搜索                                │
│   /api/jobs/filter       - 条件筛选                               │
│   /api/jobs/recommend    - 智能推荐                               │
│   /api/favorites         - 收藏管理                                │
│   /api/profile           - 用户画像                                │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ 岗位数据  │   │ 用户画像  │   │ 历史数据  │
        │ (MySQL)  │   │ (MySQL)  │   │ (MySQL)  │
        └──────────┘   └──────────┘   └──────────┘
```

### 2.2 项目目录结构

```
jobmatch-platform/
│
├── miniprogram/                    # 微信小程序前端
│   ├── pages/
│   │   ├── index/                  # 首页（搜索入口）
│   │   ├── filter/                 # 筛选页（填写条件）
│   │   ├── results/                # 结果页（岗位列表）
│   │   ├── detail/                 # 详情页（完整信息）
│   │   ├── favorites/              # 收藏页
│   │   └── profile/                # 我的（个人信息）
│   ├── components/
│   │   ├── JobCard/                # 岗位卡片组件
│   │   ├── FilterForm/             # 筛选表单组件
│   │   ├── TierBadge/              # 冲/稳/保标签
│   │   └── CompetitionChart/       # 竞争比图表
│   ├── services/
│   │   └── api.js                  # API调用封装
│   └── app.js
│
├── server/                          # FastAPI 后端服务
│   ├── app.py                      # 主入口、路由配置
│   ├── core/                       # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── models/                 # 数据模型
│   │   │   ├── job.py              # 岗位模型（扩展版）
│   │   │   ├── user_profile.py     # 用户画像模型
│   │   │   ├── match_result.py     # 匹配结果模型
│   │   │   └── historical_stats.py # 历史统计数据
│   │   ├── matchers/               # 匹配器
│   │   │   ├── base_matcher.py     # 基类
│   │   │   ├── major_matcher.py    # 专业匹配
│   │   │   ├── education_matcher.py # 学历匹配
│   │   │   ├── political_matcher.py # 政治面貌匹配
│   │   │   ├── age_matcher.py      # 年龄匹配
│   │   │   └── composite_matcher.py # 组合匹配器
│   │   ├── recommenders/           # 推荐系统
│   │   │   ├── tier_recommender.py # 冲/稳/保推荐
│   │   │   └── smart_recommender.py # 智能推荐
│   │   └── analyzers/              # 分析器
│   │       ├── historical_analyzer.py # 历史分析
│   │       └── difficulty_analyzer.py # 难度分析
│   ├── data/                       # 数据处理层
│   │   ├── __init__.py
│   │   ├── excel/                  # Excel处理
│   │   │   ├── column_mapper.py    # 列名映射器 ⭐
│   │   │   ├── universal_parser.py # 通用解析器 ⭐
│   │   │   ├── job_sheet_parser.py # 岗位表解析
│   │   │   └── stats_sheet_parser.py # 统计表解析
│   │   └── database/               # 数据库操作
│   │       ├── connection.py       # 数据库连接
│   │       ├── job_dao.py          # 岗位DAO
│   │       └── user_dao.py         # 用户DAO
│   ├── platforms/                  # 平台适配层
│   │   ├── base_platform.py        # 平台基类
│   │   ├── sanzhiyifu.py           # 三支一扶适配器
│   │   ├── gongwuyuan.py           # 公务员适配器
│   │   ├── shiyedanwei.py          # 事业单位适配器
│   │   └── jiaoshi.py              # 教师招聘适配器
│   └── utils/                      # 工具函数
│       ├── date_utils.py           # 日期/倒计时
│       └── string_utils.py         # 字符串处理
│
├── database/                        # 数据库相关
│   ├── schema.sql                   # 数据库Schema
│   └── migrations/                  # 数据库迁移
│
├── tests/                           # 测试
│   ├── test_column_mapper.py
│   ├── test_matchers.py
│   └── test_recommenders.py
│
├── config.yaml                      # 配置文件
├── pyproject.toml                   # Python依赖
└── README.md                        # 项目说明
```

---

## 三、功能规划

### 3.1 用户输入维度

| 维度 | 说明 | 优先级 |
|-----|------|-------|
| 专业 | 一级/二级学科、专业代码 | P0 |
| 学历 | 大专/本科/研究生 | P0 |
| 学位 | 学士/硕士/博士 | P1 |
| 户籍/生源地 | 按省份/城市 | P1 |
| 政治面貌 | 中共党员/团员/群众 | P1 |
| 性别 | 男/女 | P0 |
| 年龄 | 周岁计算 | P2 |
| 基层工作经验 | 2年/5年基层经历 | P2 |
| 资格证书 | 教师资格证、法律职业资格证等 | P2 |
| 定向招录 | 三支一扶/退役士兵/大学生村官 | P2 |
| 预估分数 | 用于推荐和预测 | P3 |

### 3.2 岗位类型支持

| 类型 | 说明 | 优先级 |
|-----|------|-------|
| 三支一扶 | 现有数据 | P0 |
| 公务员（国考/省考） | 中央/省级机关 | P1 |
| 事业单位 | 综合类、教育类、医疗卫生 | P1 |
| 教师招聘 | 编制教师、特岗教师 | P2 |
| 医疗卫生 | 医院、卫生系统 | P3 |
| 银行/国企 | 金融机构、国企 | P3 |
| 选调生 | 定向/非定向 | P3 |
| 军队文职 | 部队文职招聘 | P3 |

### 3.3 输出信息

| 信息类型 | 说明 | 优先级 |
|---------|------|-------|
| 匹配度评分 | 综合评分 0-100 | P0 |
| 匹配等级 | 完全符合/可能符合/不符合 | P0 |
| 竞争比 | 报名人数/招录人数 | P0 |
| 冲/稳/保推荐 | 分层推荐策略 | P1 |
| 历年进面分数 | 历史分数线参考 | P1 |
| 预测进面分数 | 基于历年的预测 | P2 |
| 上岸概率 | 计算的上岸可能性 | P2 |
| 报名倒计时 | 截止时间提醒 | P3 |

### 3.4 小程序页面功能

| 页面 | 核心功能 |
|-----|---------|
| **首页** | 搜索入口、热门岗位快捷筛选、考试类型切换 |
| **筛选页** | 专业选择器、学历/政治面貌/年龄表单、上传Excel |
| **结果页** | 岗位列表（带推荐标签）、竞争比排序、筛选条件展示 |
| **详情页** | 完整岗位信息、匹配理由、历年对比、收藏/分享 |
| **收藏页** | 收藏列表、多岗位对比、竞争比图表 |
| **我的** | 个人信息、筛选历史、设置 |

---

## 四、数据模型设计

### 4.1 Job 岗位模型（扩展版）

```python
@dataclass
class Job:
    # 基本信息
    id: int = 0
    platform: str = ""                    # 平台类型（三支一扶/公务员等）
    city: str = ""                        # 地市
    unit: str = ""                        # 服务单位
    job_type: str = ""                    # 岗位类型
    service_category: str = ""            # 服务类别
    recruit_count: int = 1                # 招募人数

    # 要求（扩展）
    education: str = ""                    # 学历要求
    degree: str = ""                      # 学位要求
    major: str = ""                        # 专业要求
    qualifications: str = ""             # 资格证书要求
    other: str = ""                        # 其他要求

    # 新增字段
    age_limit: str = ""                   # 年龄要求 "30岁以下"
    political_requirement: str = ""      # 政治面貌要求 "中共党员"
    grassroots_experience: str = ""      # 基层工作经验要求
    directional_recruit: str = ""         # 定向招录

    # 竞争数据
    applicants: int = 0                   # 报名人数
    approved: int = 0                     # 初审通过人数
    paid: int = 0                         # 缴费人数
    competition_ratio: float = 0.0        # 竞争比

    # 历史数据
    historical_stats: dict[int, HistoricalStats] = None  # 历年统计

    # 匹配结果
    match_level: MatchLevel = None        # 匹配等级
    match_score: int = 0                  # 匹配分数
    match_reasons: list[str] = None       # 匹配原因
    mismatch_reasons: list[str] = None    # 不匹配原因

    # 推荐相关
    recommendation_tier: str = ""         # "冲刺" / "稳妥" / "保底"
    predicted_score: float = 0.0          # 预测进面分数
    pass_probability: float = 0.0         # 上岸概率
```

### 4.2 UserProfile 用户画像模型

```python
@dataclass
class UserProfile:
    id: int = 0
    openid: str = ""                      # 微信openid

    # 基本信息
    major: str = ""                       # 所学专业
    education: str = ""                    # 学历
    degree: str = ""                       # 学位
    gender: str = ""                      # 性别
    age: int = 0                          # 年龄

    # 户籍与政治面貌
    household: str = ""                   # 户籍所在地
    party_status: str = ""                # 政治面貌

    # 附加条件
    is_fresh_graduate: bool = False       # 是否应届生
    grassroots_exp: int = 0               # 基层工作年限
    qualifications: list[str] = None      # 持有资格证书
    estimated_score: float = 0.0          # 预估考试成绩

    # 偏好设置
    target_cities: list[str] = None       # 意向城市
    target_platforms: list[str] = None    # 意向平台类型

    # 收藏
    favorite_jobs: list[int] = None       # 收藏的岗位ID列表
```

### 4.3 MatchResult 匹配结果模型

```python
@dataclass
class MatchResult:
    job_id: int = 0
    user_id: int = 0

    # 各维度匹配结果
    major_match: tuple[bool, str] = None  # (是否匹配, 原因)
    education_match: tuple[bool, str] = None
    political_match: tuple[bool, str] = None
    age_match: tuple[bool, str] = None
    grassroots_match: tuple[bool, str] = None

    # 综合评分
    total_score: int = 0                  # 总分 0-100
    match_level: MatchLevel = None       # 匹配等级

    # 推荐
    recommendation_tier: str = ""         # 冲/稳/保

    # 竞争分析
    competition_ratio: float = 0.0       # 当前竞争比
    historical_avg_ratio: float = 0.0    # 历史平均竞争比
```

---

## 五、核心模块设计

### 5.1 通用Excel解析器（⭐核心）

**设计目标**：不依赖硬编码列名，自动识别任意格式的Excel表头

**列名同义词映射**：

```python
COLUMN_SYNONYMS = {
    "专业": ["所学专业", "报考专业", "专业要求", "专业条件", "招录专业"],
    "学历": ["学历要求", "文化程度", "文化水平", "学历条件"],
    "学位": ["学位要求", "是否要求学位", "学位条件"],
    "户籍": ["户籍要求", "生源地", "户口所在地", "户籍所在地"],
    "年龄": ["年龄要求", "年龄限制", "年龄条件", "岁"],
    "政治面貌": ["政治面貌要求", "政治面目", "党团员"],
    "服务单位": ["用人单位", "招录机关", "单位名称", "工作单位"],
    "岗位类型": ["岗位名称", "职位", "职务", "职级"],
    "招募人数": ["招录人数", "计划人数", "人数", "名额"],
    "联系方式": ["联系电话", "咨询电话", "电话"],
}

def detect_columns(df: pd.DataFrame, header_row: int = 0) -> dict[str, int]:
    """
    自动检测列名对应关系
    返回: {"专业": 2, "学历": 3, "服务单位": 1, ...}
    """
```

**识别策略**：
1. 遍历前N行，找到包含关键词的列
2. 用识别出的列解析2-3行，验证数据合理性
3. 返回置信度最高的映射结果

### 5.2 匹配器设计

```python
class BaseMatcher(ABC):
    @abstractmethod
    def match(self, job: Job, profile: UserProfile) -> tuple[bool, str]:
        """返回 (是否匹配, 原因说明)"""

class MajorMatcher(BaseMatcher):
    """专业匹配器 - 支持大类/代码/模糊匹配"""

class EducationMatcher(BaseMatcher):
    """学历匹配器 - 支持向下兼容"""

class PoliticalMatcher(BaseMatcher):
    """政治面貌匹配器"""

class AgeMatcher(BaseMatcher):
    """年龄匹配器"""

class GrassrootsMatcher(BaseMatcher):
    """基层工作经验匹配器"""

class CompositeMatcher:
    """组合匹配器 - 协调多个匹配器"""

    def __init__(self, matchers: list[BaseMatcher], weights: dict):
        self.matchers = matchers
        self.weights = weights

    def match(self, job: Job, profile: UserProfile) -> MatchResult:
        # 依次调用各匹配器
        # 计算加权总分
        # 返回综合结果
```

### 5.3 推荐系统设计

```python
class TierRecommender:
    """
    冲/稳/保 推荐逻辑

    冲刺: 专业完全匹配 + 竞争比<30 + 历史分数接近用户预估
    稳妥: 专业匹配 + 竞争比30-80 + 难度稳定
    保底: 专业部分匹配/不限 + 竞争比<20
    """

    def recommend(self, jobs: list[Job], profile: UserProfile) -> dict:
        for job in jobs:
            job.recommendation_tier = self._classify(job, profile)
            job.pass_probability = self._calc_probability(job, profile)

        return {
            "冲刺": [j for j in jobs if j.recommendation_tier == "冲刺"],
            "稳妥": [j for j in jobs if j.recommendation_tier == "稳妥"],
            "保底": [j for j in jobs if j.recommendation_tier == "保底"],
        }

    def _classify(self, job: Job, profile: UserProfile) -> str:
        # 实现分层逻辑
        pass

    def _calc_probability(self, job: Job, profile: UserProfile) -> float:
        """计算上岸概率"""
        # 基于竞争比和分数预测的贝叶斯模型
        base_prob = 1 / (1 + job.competition_ratio)

        if job.predicted_score and profile.estimated_score:
            score_diff = profile.estimated_score - job.predicted_score
            base_prob *= (1 + score_diff / 100)

        return min(max(base_prob, 0.0), 0.95)
```

### 5.4 平台适配器设计

```python
class PlatformAdapter(ABC):
    """岗位平台适配器基类"""

    @abstractmethod
    def get_column_mapping(self) -> dict[str, list[str]]:
        """获取该平台的列名映射"""
        pass

    @abstractmethod
    def parse_job(self, row: pd.Series) -> Job:
        """解析单行数据为Job"""
        pass

    @abstractmethod
    def validate_file(self, file_path: str) -> bool:
        """验证文件格式"""
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        """获取平台名称"""
        pass


class SanzhiyifuAdapter(PlatformAdapter):
    """三支一扶适配器"""

    def get_column_mapping(self) -> dict[str, list[str]]:
        return {
            "unit": ["服务单位", "服务单位名称"],
            "major": ["专业要求", "专业", "Unnamed: 7"],
            "education": ["学历要求", "服务岗位要求"],
            # ...
        }


class GongwuyuanAdapter(PlatformAdapter):
    """公务员适配器（国考/省考）"""

    def get_column_mapping(self) -> dict[str, list[str]]:
        return {
            "unit": ["招录机关", "用人单位"],
            "major": ["专业", "所学专业"],
            "education": ["学历", "文化程度"],
            # ...
        }
```

---

## 六、API设计

### 6.1 接口列表

| 接口 | 方法 | 说明 | 优先级 |
|-----|------|------|-------|
| `/api/auth/login` | POST | 微信登录 | P0 |
| `/api/jobs/upload` | POST | 上传Excel | P0 |
| `/api/jobs/search` | GET | 搜索岗位 | P0 |
| `/api/jobs/filter` | POST | 条件筛选 | P0 |
| `/api/jobs/recommend` | POST | 智能推荐 | P1 |
| `/api/jobs/{id}` | GET | 岗位详情 | P0 |
| `/api/jobs/compare` | POST | 岗位对比 | P2 |
| `/api/favorites` | GET/POST/DELETE | 收藏管理 | P1 |
| `/api/profile` | GET/PUT | 用户画像 | P1 |
| `/api/history` | GET | 筛选历史 | P2 |
| `/api/export` | POST | 导出结果 | P2 |

### 6.2 主要接口详情

#### POST /api/jobs/filter

**请求**：
```json
{
  "profile": {
    "major": "经济学",
    "education": "本科",
    "gender": "女",
    "household": "山西",
    "party_status": "群众",
    "target_cities": ["太原市", "吕梁市"]
  },
  "platform": "sanzhiyifu",
  "filters": {
    "max_competition_ratio": 100,
    "min_recruit_count": 1
  },
  "sort_by": "competition_ratio",
  "order": "asc"
}
```

**响应**：
```json
{
  "total": 43,
  "jobs": [
    {
      "id": 1,
      "city": "太原市",
      "unit": "太原市古交市特殊教育学校",
      "job_type": "专技1",
      "major": "不限",
      "education": "本科及以上",
      "recruit_count": 2,
      "competition_ratio": 3.0,
      "match_level": "perfect",
      "match_score": 85,
      "recommendation_tier": "稳妥"
    }
  ]
}
```

---

## 七、实施计划

### 7.1 阶段划分

| 阶段 | 内容 | 工期 | 目标 |
|-----|------|------|------|
| 阶段1 | 后端核心 + 小程序前端 | 4-6周 | 可用的筛选工具 |
| 阶段2 | 智能推荐 + 历史分析 | 2-3周 | 智能推荐能力 |
| 阶段3 | 多平台 + 完善功能 | 2-3周 | 多类型岗位支持 |

**预计总工期**：8-12周

### 7.2 详细计划

#### 阶段1：后端核心 + 小程序前端（第1-6周）

| 周次 | 任务 | 产出 |
|-----|------|------|
| 第1周 | 通用列名映射器 `column_mapper.py` | 可识别多种列名格式 |
| 第2周 | 扩展数据模型（Job, UserProfile） | 支持政治面貌/年龄等 |
| 第3周 | 政治面貌/年龄匹配器 | 新维度匹配能力 |
| 第4周 | FastAPI后端 + 数据库Schema | 完整的API服务 |
| 第5周 | 微信小程序首页+筛选页 | 用户可填写条件 |
| 第6周 | 微信小程序结果页+详情页 | 可查看匹配结果 |

#### 阶段2：智能推荐 + 历史分析（第7-9周）

| 周次 | 任务 | 产出 |
|-----|------|------|
| 第7周 | 冲/稳/保推荐器 | 分层推荐能力 |
| 第8周 | 历史数据分析器 | 历年分数线分析 |
| 第9周 | 推荐标签组件 + 可视化 | 小程序推荐展示 |

#### 阶段3：多平台支持 + 完善功能（第10-12周）

| 周次 | 任务 | 产出 |
|-----|------|------|
| 第10周 | 平台适配器（三支一扶/公务员/事业编） | 多类型支持 |
| 第11周 | 收藏功能 + 岗位对比 | 用户收藏对比 |
| 第12周 | 报名倒计时 + 消息推送 | 完整功能上线 |

---

## 八、验证方案

### 8.1 单元测试

| 模块 | 测试用例 |
|-----|---------|
| column_mapper | 用三支一扶Excel验证识别正确率 > 95% |
| major_matcher | 专业完全匹配、部分匹配、不匹配场景 |
| tier_recommender | 冲/稳/保分类正确性 |

### 8.2 集成测试

| 测试 | 验证点 |
|-----|-------|
| Excel上传解析 | 不同格式Excel都能正确解析 |
| 筛选结果 | 新增字段（政治面貌/年龄）正确匹配 |
| API接口 | 各接口返回正确数据 |
| 小程序端到端 | 上传→筛选→查看结果 完整流程 |

### 8.3 对比验证

| 对比项 | 验证方法 |
|-----|---------|
| 识别准确率 | 与华图/中公工具对比相同Excel的筛选结果 |
| 推荐合理性 | 专家评估冲/稳/保分层是否合理 |

---

## 九、可复用现有组件

| 组件 | 位置 | 复用方式 |
|-----|------|---------|
| Job/MatchLevel | `job_matcher.py` | 直接迁移 |
| MajorMatcher | `job_matcher.py` | 直接迁移 |
| EducationMatcher | `job_matcher.py` | 直接迁移 |
| GenderMatcher | `job_matcher.py` | 直接迁移 |
| HouseholdMatcher | `job_matcher.py` | 直接迁移 |
| ExcelExporter | `excel_exporter.py` | 颜色标记逻辑迁移 |
| FastAPI后端模式 | `app_full.py` | 路由模式参考 |

---

## 十、技术选型

| 技术 | 选择 | 理由 |
|-----|------|------|
| 后端框架 | FastAPI | 高性能、自动文档、类型安全 |
| 数据库 | MySQL | 成熟稳定、适合关系数据 |
| 小程序框架 | 原生小程序 | 性能最优、官方支持 |
| ORM | SQLAlchemy | 功能强大、灵活 |
| Excel处理 | pandas + openpyxl | 现有技术栈 |

---

## 十一、注意事项

### 11.1 微信登录限制

- 个人账号无法使用微信登录API
- 需要**企业认证**的小程序账号才能获取用户openid
- 临时测试可使用模拟登录

### 11.2 后端部署

- 可选择云开发（免服务器）或自建服务器
- 推荐：阿里云/腾讯云 + Nginx + Gunicorn

### 11.3 数据安全

- Excel文件建议先上传到云存储，避免直接存数据库
- 用户敏感信息需要加密存储

---

## 附录

### A. 数据库Schema（简化版）

```sql
CREATE TABLE jobs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    platform VARCHAR(50) NOT NULL,        -- 三支一扶/公务员等
    city VARCHAR(50),                     -- 地市
    unit VARCHAR(200),                    -- 服务单位
    job_type VARCHAR(50),                -- 岗位类型
    education VARCHAR(50),                -- 学历要求
    major VARCHAR(200),                   -- 专业要求
    political_requirement VARCHAR(50),   -- 政治面貌要求
    age_limit VARCHAR(50),                -- 年龄要求
    recruit_count INT,                    -- 招募人数
    applicants INT DEFAULT 0,              -- 报名人数
    competition_ratio FLOAT,              -- 竞争比
    raw_data JSON,                        -- 原始JSON数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    openid VARCHAR(100) UNIQUE,           -- 微信openid
    major VARCHAR(100),                   -- 专业
    education VARCHAR(50),                -- 学历
    gender VARCHAR(10),                   -- 性别
    household VARCHAR(100),               -- 户籍
    party_status VARCHAR(50),              -- 政治面貌
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE favorites (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    job_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

### B. 关键文件清单

| 文件 | 说明 | 优先级 |
|-----|------|-------|
| `server/data/excel/column_mapper.py` | 列名映射器 | P0 |
| `server/data/excel/universal_parser.py` | 通用解析器 | P0 |
| `server/core/models/job.py` | Job模型 | P0 |
| `server/core/models/user_profile.py` | 用户模型 | P0 |
| `server/core/matchers/political_matcher.py` | 政治面貌匹配 | P1 |
| `server/core/matchers/age_matcher.py` | 年龄匹配 | P1 |
| `server/core/recommenders/tier_recommender.py` | 冲/稳/保推荐 | P1 |
| `miniprogram/pages/filter/` | 筛选页 | P0 |
| `miniprogram/pages/results/` | 结果页 | P0 |
