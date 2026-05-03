# 岗位筛选工具 - 完整架构设计

## 数据现状分析

### 1. 岗位表（附件1...xlsx）
- **结构**: 12个Sheet（11个地市 + 省林草局）
- **表头**: 第2-3行为合并表头
- **关键字段**:
  - 服务单位、岗位类型、服务类别
  - 学历、学位、专业、相关资格、其他
  - 招募人数、联系电话

### 2. 统计表（P020260410598205300172.xls）
- **结构**: 单Sheet，692行
- **关键字段**:
  - 服务单位（格式：城市-区县-单位）
  - 岗位类型
  - 招募人数、填报信息人数、初审通过人数、缴费人数

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        微信小程序                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   条件录入    │  │   结果展示    │  │   收藏/导出功能      │  │
│  │  (表单页面)   │  │  (列表+筛选)  │  │                     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS
┌───────────────────────────▼─────────────────────────────────────┐
│                        后端API (Python/FastAPI)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  岗位筛选服务 │  │  竞争数据分析 │  │   用户/收藏管理      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                        数据处理层                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Excel解析器  │  岗位匹配引擎  │  竞争数据关联器         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心模块设计

### 1. 配置层 (config.yaml)

```yaml
# 个人条件配置
profile:
  专业: "经济学"
  学历: "本科"  # 可选: 大专、本科、研究生
  学位: "学士"  # 可选: 无要求、学士、硕士、博士
  性别: "男"    # 用于性别限制判断
  户籍: ""      # 如"吕梁市"，用于户籍限制
  资格证书: []  # 如["教师资格证", "法律职业资格证"]

# 意向设置
preference:
  意向城市: ["吕梁市", "太原市"]  # 空数组表示全省
  服务类别: []  # 支农/支医/支教/帮扶乡村振兴
  排除关键词: []  # 如["限女性"]（如果你是男性）

# 匹配规则
rules:
  专业匹配模式: "智能"  # 精确/包含/智能
  学历匹配: "向下兼容"  # 本科可以报"大专及以上"
  竞争比阈值: 50  # 高于此值标红警示

# 输出设置
output:
  排序方式: "竞争比升序"
  显示字段:
    - 服务单位
    - 岗位类型
    - 专业
    - 学历
    - 招募人数
    - 缴费人数
    - 竞争比
    - 匹配度
```

### 2. 数据模型

```python
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class MatchLevel(Enum):
    PERFECT = "完全符合"      # 绿色
    PARTIAL = "可能符合"      # 黄色
    MISMATCH = "不符合"       # 红色

@dataclass
class Job:
    # 基本信息
    city: str                    # 所属地市
    unit: str                    # 服务单位
    job_type: str               # 岗位类型
    service_category: str       # 服务类别
    recruit_count: int          # 招募人数

    # 要求
    education: str              # 学历要求
    degree: str                 # 学位要求
    major: str                  # 专业要求
    qualifications: str         # 相关资格
    other: str                  # 其他要求（性别/户籍等）

    # 竞争数据（来自统计表）
    applicants: int = 0         # 填报信息人数
    approved: int = 0           # 初审通过人数
    paid: int = 0               # 缴费人数

    # 匹配结果
    match_level: MatchLevel = MatchLevel.MISMATCH
    match_reasons: List[str] = None
    competition_ratio: float = 0.0

@dataclass
class UserProfile:
    major: str
    education: str
    degree: str
    gender: str
    household: str = ""
    certificates: List[str] = None
    target_cities: List[str] = None
```

### 3. 匹配引擎

```python
class JobMatcher:
    def __init__(self, profile: UserProfile):
        self.profile = profile

    def match(self, job: Job) -> MatchResult:
        checks = {
            '城市': self._match_city(job),
            '专业': self._match_major(job.major),
            '学历': self._match_education(job.education),
            '学位': self._match_degree(job.degree),
            '性别': self._match_gender(job.other),
            '户籍': self._match_household(job.other),
        }

        # 判断匹配等级
        if all(checks.values()):
            level = MatchLevel.PERFECT
        elif checks['专业'] and checks['学历']:
            level = MatchLevel.PARTIAL
        else:
            level = MatchLevel.MISMATCH

        return MatchResult(
            level=level,
            checks=checks,
            competition_ratio=job.paid / job.recruit_count if job.recruit_count > 0 else 0
        )

    def _match_major(self, job_major: str) -> bool:
        job_major = str(job_major).strip()
        user_major = self.profile.major

        # 不限
        if '不限' in job_major:
            return True

        # 完全匹配
        if user_major == job_major:
            return True

        # 包含匹配（如"经济学、金融学"）
        if user_major in job_major:
            return True

        # 大类匹配（如"经济学类"包含"经济学"）
        if f"{user_major}类" in job_major:
            return True

        # 专业代码匹配（如"0201"是经济学类代码）
        major_codes = self._get_major_codes(user_major)
        for code in major_codes:
            if code in job_major:
                return True

        return False

    def _match_education(self, job_edu: str) -> bool:
        # 学历层级
        edu_levels = {'大专': 1, '本科': 2, '研究生': 3}
        job_level = 0
        user_level = edu_levels.get(self.profile.education, 0)

        for edu, level in edu_levels.items():
            if edu in job_edu:
                job_level = max(job_level, level)

        # 本科可以报"大专及以上"
        return user_level >= job_level
```

### 4. 竞争数据关联

```python
class StatsMatcher:
    """将岗位与统计表数据关联"""

    def __init__(self, stats_df: pd.DataFrame):
        self.stats = self._build_index(stats_df)

    def _build_index(self, df: pd.DataFrame) -> dict:
        """建立索引: (单位名, 岗位类型) -> 统计数据"""
        index = {}
        for _, row in df.iterrows():
            unit = str(row['服务单位']).strip()
            job_type = str(row['岗位类型']).strip()
            key = (unit, job_type)
            index[key] = {
                'applicants': row['填报信息人数'],
                'approved': row['初审通过人数'],
                'paid': row['缴费人数'],
            }
        return index

    def match_job(self, job: Job) -> Optional[dict]:
        # 构建完整的单位名：城市-区县-单位
        full_unit = f"{job.city}-{job.unit}"

        # 尝试精确匹配
        key = (full_unit, job.job_type)
        if key in self.stats:
            return self.stats[key]

        # 尝试模糊匹配
        return self._fuzzy_match(job)

    def _fuzzy_match(self, job: Job) -> Optional[dict]:
        """服务单位名称可能不完全一致，需要模糊匹配"""
        best_score = 0
        best_match = None

        for (unit, job_type), stats in self.stats.items():
            if job_type != job.job_type:
                continue

            score = self._calc_similarity(unit, job.unit)
            if score > best_score and score > 0.7:  # 阈值
                best_score = score
                best_match = stats

        return best_match
```

---

## API设计

### 1. 岗位筛选接口

```python
# POST /api/jobs/filter
@app.post("/api/jobs/filter")
async def filter_jobs(request: FilterRequest):
    """
    请求体:
    {
        "profile": {
            "major": "经济学",
            "education": "本科",
            "degree": "学士",
            "gender": "男",
            "target_cities": ["吕梁市", "太原市"]
        },
        "filters": {
            "max_competition_ratio": 100,
            "service_categories": []
        },
        "sort_by": "competition_ratio",
        "page": 1,
        "page_size": 20
    }

    响应:
    {
        "total": 150,
        "jobs": [
            {
                "id": "ty-001",
                "city": "太原市",
                "unit": "娄烦县社会普查中心",
                "job_type": "专技1",
                "major": "本科：经济学类（0201）、统计学类（0712）",
                "education": "本科及以上",
                "recruit_count": 1,
                "paid": 47,
                "competition_ratio": 47.0,
                "match_level": "完全符合",
                "match_details": {
                    "专业": true,
                    "学历": true,
                    "性别": true
                }
            }
        ],
        "summary": {
            "perfect_match": 20,
            "partial_match": 50,
            "mismatch": 80
        }
    }
    """
```

### 2. 导出Excel接口

```python
# POST /api/jobs/export
@app.post("/api/jobs/export")
async def export_jobs(request: FilterRequest):
    """
    生成带颜色标记的Excel文件

    颜色规则:
    - 绿色: 完全符合 + 竞争比<30
    - 黄色: 完全符合 + 竞争比30-100
    - 红色: 完全符合 + 竞争比>100 或 不符合
    """
    output_path = generate_excel(request)
    return FileResponse(output_path, filename="筛选结果.xlsx")
```

---

## 微信小程序设计

### 页面结构

```
pages/
├── index/              # 首页（条件录入）
│   └── index.wxml
├── result/             # 结果列表
│   └── result.wxml
├── detail/             # 岗位详情
│   └── detail.wxml
├── profile/            # 个人条件管理
│   └── profile.wxml
└── favorites/          # 收藏列表
    └── favorites.wxml
```

### 首页设计

```html
<!-- index.wxml -->
<view class="container">
  <view class="header">
    <text class="title">三支一扶岗位筛选</text>
    <text class="subtitle">山西省2026年度</text>
  </view>

  <!-- 个人条件卡片 -->
  <view class="card">
    <view class="card-title">个人条件</view>

    <view class="form-item">
      <text class="label">专业</text>
      <input placeholder="如：经济学" value="{{profile.major}}" bindinput="onMajorChange"/>
    </view>

    <view class="form-item">
      <text class="label">学历</text>
      <picker mode="selector" range="{{educationOptions}}" bindchange="onEducationChange">
        <view class="picker">{{profile.education || '请选择'}}</view>
      </picker>
    </view>

    <view class="form-item">
      <text class="label">性别</text>
      <radio-group bindchange="onGenderChange">
        <radio value="男" checked="{{profile.gender === '男'}}">男</radio>
        <radio value="女" checked="{{profile.gender === '女'}}">女</radio>
      </radio-group>
    </view>

    <view class="form-item">
      <text class="label">意向城市（可多选）</text>
      <checkbox-group bindchange="onCityChange">
        <label wx:for="{{cities}}" wx:key="*this">
          <checkbox value="{{item}}" checked="{{profile.target_cities.includes(item)}}"/>
          {{item}}
        </label>
      </checkbox-group>
    </view>
  </view>

  <!-- 筛选选项 -->
  <view class="card">
    <view class="card-title">筛选选项</view>

    <view class="form-item">
      <text class="label">最大竞争比</text>
      <slider min="0" max="500" value="{{filters.maxCompetition}}" show-value bindchange="onCompetitionChange"/>
    </view>

    <view class="form-item">
      <text class="label">排序方式</text>
      <picker mode="selector" range="{{sortOptions}}" bindchange="onSortChange">
        <view class="picker">{{filters.sortBy}}</view>
      </picker>
    </view>
  </view>

  <button class="btn-primary" bindtap="onFilter">开始筛选</button>
</view>
```

### 结果页设计

```html
<!-- result.wxml -->
<view class="container">
  <!-- 统计栏 -->
  <view class="summary-bar">
    <view class="stat-item green">
      <text class="number">{{summary.perfect}}</text>
      <text class="label">完全符合</text>
    </view>
    <view class="stat-item yellow">
      <text class="number">{{summary.partial}}</text>
      <text class="label">可能符合</text>
    </view>
    <view class="stat-item red">
      <text class="number">{{summary.mismatch}}</text>
      <text class="label">不符合</text>
    </view>
  </view>

  <!-- 筛选标签 -->
  <view class="filter-tabs">
    <view class="tab {{activeTab === 'all' ? 'active' : ''}}" bindtap="switchTab" data-tab="all">
      全部({{summary.total}})
    </view>
    <view class="tab {{activeTab === 'perfect' ? 'active' : ''}}" bindtap="switchTab" data-tab="perfect">
      完全符合
    </view>
    <view class="tab {{activeTab === 'partial' ? 'active' : ''}}" bindtap="switchTab" data-tab="partial">
      可能符合
    </view>
  </view>

  <!-- 岗位列表 -->
  <scroll-view scroll-y class="job-list">
    <view wx:for="{{jobs}}" wx:key="id" class="job-card {{item.matchLevel}}">
      <view class="job-header">
        <text class="city">{{item.city}}</text>
        <text class="match-badge {{item.matchLevel}}">{{item.matchText}}</text>
      </view>

      <view class="job-title">{{item.unit}}</view>
      <view class="job-subtitle">{{item.jobType}} | {{item.serviceCategory}}</view>

      <view class="job-tags">
        <tag text="{{item.education}}" />
        <tag text="{{item.major}}" type="major" />
        <tag text="招{{item.recruitCount}}人" type="count" />
      </view>

      <view class="competition-bar">
        <text class="ratio">竞争比 {{item.competitionRatio}}:1</text>
        <progress percent="{{item.competitionPercent}}" color="{{item.ratioColor}}" />
      </view>

      <view class="job-footer">
        <text class="update-time">数据更新时间：{{updateTime}}</text>
        <view class="actions">
          <button size="mini" bindtap="viewDetail" data-id="{{item.id}}">详情</button>
          <button size="mini" type="primary" bindtap="toggleFavorite" data-id="{{item.id}}">
            {{item.isFavorite ? '已收藏' : '收藏'}}
          </button>
        </view>
      </view>
    </view>
  </scroll-view>

  <!-- 底部操作栏 -->
  <view class="bottom-bar">
    <button class="btn-export" bindtap="exportExcel">导出Excel</button>
  </view>
</view>
```

---

## 部署方案

### 方案A: 本地运行（个人使用）

```bash
# 1. 安装依赖
uv sync

# 2. 配置个人条件
cp config.example.yaml config.yaml
# 编辑 config.yaml

# 3. 运行
uv run python job_filter.py

# 4. 生成Excel
uv run python export.py --output result.xlsx
```

### 方案B: 云服务部署（分享使用）

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data  # Excel文件
    environment:
      - ENV=production

  frontend:
    build: ./frontend
    ports:
      - "80:80"
```

**推荐平台**:
- 后端：阿里云函数计算（FC）或 腾讯云云函数（SCF）
- 前端：微信小程序云开发（免费额度足够）

### 方案C: 微信小程序云开发

```javascript
// app.js
App({
  onLaunch() {
    // 初始化云开发
    wx.cloud.init({
      env: 'your-env-id',
      traceUser: true
    });

    // 云函数调用示例
    wx.cloud.callFunction({
      name: 'filterJobs',
      data: {
        profile: {
          major: '经济学',
          education: '本科',
          gender: '男'
        }
      }
    }).then(res => {
      console.log(res.result);
    });
  }
});
```

---

## 开发计划

### 阶段1: 核心功能（1-2天）
- [ ] Excel解析器（支持多Sheet、合并表头）
- [ ] 岗位匹配引擎（专业、学历、性别、户籍）
- [ ] 竞争数据关联
- [ ] 导出带颜色标记的Excel

### 阶段2: API服务（1天）
- [ ] FastAPI后端搭建
- [ ] 筛选接口
- [ ] 导出接口

### 阶段3: 小程序（2-3天）
- [ ] 首页（条件录入）
- [ ] 结果页（列表展示）
- [ ] 详情页
- [ ] 收藏功能

### 阶段4: 优化（1天）
- [ ] 专业词库完善
- [ ] 匹配算法优化
- [ ] UI美化

---

## 关键问题解答

### Q1: 如何处理专业匹配？
```python
# 专业大类映射（教育部专业目录）
MAJOR_CATEGORIES = {
    '经济学类': ['经济学', '经济统计学', '国民经济管理', ...],
    '财政学类': ['财政学', '税收学'],
    '金融学类': ['金融学', '金融工程', '保险学', ...],
}

# 专业代码映射
MAJOR_CODES = {
    '经济学': ['020101'],
    '经济学类': ['0201'],
}
```

### Q2: 如何关联岗位和竞争数据？
岗位表中的"服务单位"是"太原市杏花岭区杏花岭街道党群服务中心"，
统计表中是"太原市-杏花岭区-太原市杏花岭区杏花岭街道党群服务中心"。

关联策略：
1. 提取统计表中的城市前缀
2. 移除城市前缀后匹配单位名
3. 同时匹配岗位类型（管理1/专技1）

### Q3: 微信小程序限制？
- Excel导出：小程序无法直接生成Excel，需要：
  - 方案1: 后端生成后返回下载链接
  - 方案2: 生成后发送到用户邮箱
  - 方案3: 只展示，导出用PC端工具

---

## 下一步

你想从哪个阶段开始？我建议：

1. **先验证核心逻辑**：我帮你写Python脚本，你在本地跑通
2. **然后做后端API**：把脚本封装成服务
3. **最后做小程序**：调用API展示结果

你想先做哪个？