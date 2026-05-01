# 三支一扶智能选岗系统

AI驱动的考公考编岗位智能匹配系统，支持语义匹配、专业图谱、历年分析和报告导出。

---

## 项目结构

```
JobMatch/
├── server/                    # FastAPI 后端
│   ├── app.py                # 主入口
│   ├── core/                 # 核心业务逻辑
│   │   ├── models/          # 数据模型
│   │   ├── matchers/        # 匹配器
│   │   ├── recommenders/    # 推荐系统
│   │   └── analyzers/       # 分析器
│   ├── data/                # 数据处理
│   │   ├── excel/           # Excel 解析
│   │   └── database/        # 数据库
│   ├── platforms/           # 平台适配层
│   └── utils/               # 工具函数
├── webapp/                   # Web 应用（Vue3）
├── miniprogram/              # 微信小程序
├── shared/api/               # 统一 API 服务
├── tests/                    # 测试
├── docs/                     # 文档
├── data/                     # 数据目录
├── reports/                  # 报告输出
├── archive/                  # 归档旧文件
├── pyproject.toml            # 依赖管理
├── config.yaml               # 基础配置
├── start.py                  # 快速启动脚本
└── demo_full_pipeline.py     # 完整流程演示
```

---

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入必要的 API Key
```

### 3. 启动后端服务

```bash
uv run uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 启动前端开发服务器

```bash
cd webapp/frontend
npm install
npm run dev
```

### 5. 访问应用

前端：http://localhost:3000
后端 API：http://localhost:8000
API 文档：http://localhost:8000/docs

---

## 核心功能

### 智能匹配
- **专业匹配**：支持大类匹配（经济学类包含经济学）、专业代码匹配
- **学历兼容**：本科可报大专及以上
- **多维度筛选**：性别、户籍、政治面貌、年龄、基层经验等

### 历年分析
- 历史数据分析与趋势预测
- 竞争比趋势预测
- 进面分数预测

### 报告导出
- Excel：带颜色标记的筛选结果
- HTML：可视化报告
- JSON：结构化数据

---

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy
- pandas / openpyxl
- Anthropic Claude API（可选）

### 前端
- Vue 3
- Element Plus
- Vite
- Lucide 图标

---

## 主要模块

| 模块 | 说明 |
|-----|------|
| `server/core/matchers/` | 匹配器（专业/学历/政治面貌等） |
| `server/core/recommenders/` | 推荐系统（冲/稳/保分层） |
| `server/core/analyzers/` | 历史数据分析 |
| `server/data/excel/` | Excel 解析 |
| `server/data/database/` | 数据库访问 |
| `server/platforms/` | 平台适配层 |

---

## 命令行使用

```bash
# 运行完整流程演示
uv run python demo_full_pipeline.py

# 快速启动（交互式）
uv run python start.py
```

---

## 配置文件

| 文件 | 说明 |
|-----|------|
| `config.yaml` | 基础配置 |
| `config_full.yaml` | 完整配置 |
| `.env` | 环境变量 |
| `.env.example` | 环境变量示例 |

---

## 许可证

MIT License
