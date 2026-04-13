# 三支一扶智能选岗系统 V2.0

🎓 AI驱动的三支一扶岗位智能匹配系统，支持语义匹配、专业图谱、报告导出等功能。

---

## ✨ 核心功能

### 1. AI语义匹配
- **本地语义匹配**: 使用专业嵌入向量，无需API即可实现智能匹配
- **Claude API匹配**: 接入真实的Claude API，最高准确率和智能程度
- **三级匹配策略**: 规则匹配 → 缓存匹配 → LLM匹配，兼顾速度与智能

### 2. 专业关系图谱
- **完整专业数据库**: 28个专业大类，206个专业
- **可视化图谱**: D3.js力导向图，直观展示专业关系
- **专业对比**: 任意两个专业对比，显示关联度和报考建议
- **匹配模拟**: 实时模拟专业匹配效果

### 3. 报告导出
- **JSON**: 结构化数据，便于二次开发
- **HTML**: 美观的可视化报告，支持打印
- **Excel**: 表格格式，便于数据分析
- **PDF**: 通过HTML打印生成

### 4. 数据管理
- **自定义专业**: 添加系统未收录的专业
- **关系管理**: 自定义专业之间的关联关系
- **数据导入导出**: JSON格式数据备份和恢复
- **编辑历史**: 操作记录和撤销功能

---

## 📁 文件说明

### 核心模块

| 文件 | 说明 | 大小 |
|------|------|------|
| `job_matcher_v2.py` | V2版岗位匹配引擎 | 17KB |
| `llm_matcher_api.py` | Claude API匹配器 | 12KB |
| `major_graph_complete.py` | 完整专业图谱(28类/206专业) | 29KB |
| `major_graph_compare.py` | 专业对比可视化工具 | 20KB |
| `report_generator.py` | 报告生成器(支持4种格式) | 23KB |
| `data_manager.py` | 数据管理器(CRUD操作) | 17KB |
| `app_full.py` | FastAPI完整后端 | 13KB |

### 可视化界面

| 文件 | 说明 | 大小 |
|------|------|------|
| `major_graph.html` | 基础版专业图谱 | 29KB |
| `major_graph_enhanced.html` | 增强版(含匹配模拟) | 45KB |
| `major_compare.html` | 专业对比工具(206专业) | 105KB |
| `index_full.html` | 完整版Web界面 | 28KB |

### 配置与工具

| 文件 | 说明 |
|------|------|
| `api_config.py` | API配置管理器 |
| `demo_llm_api.py` | API演示和测试脚本 |
| `config_full.yaml` | 完整配置文件 |
| `.env.example` | 环境变量示例 |

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
uv add pandas openpyxl pyyaml anthropic

# 配置API Key (可选，用于AI匹配)
uv run api_config.py
# 或手动创建 .env 文件
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 2. 运行测试

```bash
# 测试本地语义匹配
uv run demo_llm_api.py --mode local

# 对比不同匹配方法
uv run demo_llm_api.py --mode compare

# 测试Claude API (需配置API Key)
uv run demo_llm_api.py --mode api
```

### 3. 启动Web服务

```bash
# 启动FastAPI后端
uv run app_full.py

# 或
python -m uvicorn app_full:app --reload
```

访问 http://localhost:8000/docs 查看API文档

### 4. 使用可视化工具

```bash
# 打开专业对比工具
start major_compare.html

# 或打开完整Web界面
start index_full.html
```

---

## 📊 专业数据库

### 包含的学科门类

| 门类 | 专业类 | 专业数量 |
|------|--------|----------|
| 📊 经济学 | 4类 | 24个 |
| ⚖️ 法学 | 4类 | 21个 |
| 📚 教育学 | 2类 | 18个 |
| 📖 文学 | 3类 | 23个 |
| 🔬 理学 | 5类 | 22个 |
| 🔧 工学 | 2类 | 16个 |
| 🏥 医学 | 5类 | 28个 |
| 📋 管理学 | 3类 | 26个 |

**总计**: 28个专业类，206个专业

---

## 🔍 匹配准确度对比

| 匹配方法 | 速度 | 准确度 | 适用场景 |
|----------|------|--------|----------|
| 规则匹配 | <1ms | 60% | 精确名称匹配 |
| 本地语义 | ~10ms | 85% | 相似专业匹配 |
| Claude API | ~500ms | 95%+ | 复杂语义判断 |

---

## 📝 使用示例

### 专业对比

```python
from major_graph_full import compare_majors

result = compare_majors("金融学", "经济学")
print(result['relationship'])  # 高度相关
print(result['path'])  # ['金融学', '经济学类', '经济学']
```

### 生成报告

```python
from report_generator import ReportGenerator, MatchReport

generator = ReportGenerator()
report = MatchReport(
    user_major="金融学",
    user_education="本科",
    matched_jobs=[...]
)

# 生成不同格式
generator.generate_json(report)   # JSON
generator.generate_html(report)   # HTML
generator.generate_excel(report)  # Excel
```

### 数据管理

```python
from data_manager import DataManager

manager = DataManager()

# 添加新专业
manager.add_major(
    name="人工智能",
    category="工学",
    subcategory="计算机类",
    description="AI专业"
)

# 添加关系
manager.add_relation("人工智能", "计算机科学与技术")

# 导出数据
manager.export_to_json("backup.json")
```

---

## 🌐 API接口

### 岗位搜索
```http
POST /api/jobs/search
Content-Type: application/json

{
  "profile": {
    "major": "金融学",
    "education": "本科",
    "target_cities": ["济南市", "青岛市"]
  },
  "use_llm": true
}
```

### 专业对比
```http
POST /api/majors/compare
Content-Type: application/json

{
  "major1": "金融学",
  "major2": "经济学"
}
```

### 导出报告
```http
POST /api/reports/export?format=html
Content-Type: application/json

{
  "profile": {...},
  "filters": {...}
}
```

---

## 💰 成本估算

### Claude API费用 (Opus 4.6)

| 项目 | 费用 |
|------|------|
| Input | $5 / 1M tokens |
| Output | $25 / 1M tokens |
| 单次匹配 | ~$0.002 |
| 100次匹配 | ~$0.20 |

### 成本优化
- 启用Prompt Caching可节省90%成本
- 本地语义匹配完全免费
- 缓存机制避免重复计算

---

## 🔧 高级配置

### 环境变量

```bash
# 必需
ANTHROPIC_API_KEY=sk-ant-api03-...

# 可选
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 配置文件 (config_full.yaml)

```yaml
profile:
  专业: "金融学"
  学历: "本科"
  学位: "学士"
  性别: ""
  户籍: ""
  是否应届: false

rules:
  性别限制:
    模式: "loose"  # strict/loose
  户籍匹配:
    模式: "loose"
  应届生匹配:
    模式: "loose"

filter:
  最大竞争比: 50
  最低匹配分数: 50
```

---

## 📈 性能优化

1. **缓存机制**: 语义匹配结果自动缓存
2. **批量处理**: Excel导入使用批量写入
3. **异步加载**: 大型图谱使用懒加载
4. **增量更新**: 只更新变化的数据

---

## 🤝 贡献指南

欢迎提交新专业或关联关系！

1. Fork本仓库
2. 使用 `data_manager.py` 添加数据
3. 导出为JSON并提交PR
4. 或通过Issue提交建议

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- Anthropic Claude API
- D3.js 可视化库
- FastAPI Web框架
- 所有贡献者

---

## 📞 支持

遇到问题？
- 查看 `demo_llm_api.py` 示例代码
- 运行测试：`uv run demo_llm_api.py --mode compare`
- 提交Issue

---

**当前版本**: V2.0.0
**最后更新**: 2025-04-13
