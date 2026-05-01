# JobMatch 智能选岗系统

> 三支一扶智能选岗系统 - AI驱动的考公考编岗位智能匹配工具

---

## 项目概述

| 项目 | 说明 |
|-----|------|
| 版本 | v3.0 |
| 更新时间 | 2026-05-01 |
| 技术栈 | Python 3.11+ / FastAPI / Vue 3 |

支持语义匹配、专业图谱、历年分析和报告导出。

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
├── docs/                     # 详细文档
├── data/                     # 数据目录
├── reports/                  # 报告输出
├── pyproject.toml            # 依赖管理
├── config.yaml               # 基础配置
├── start.py                  # 快速启动脚本
└── demo_full_pipeline.py     # 完整流程演示
```

---

## 已完成功能

### 核心匹配
- [x] 专业匹配（支持大类/代码/模糊）
- [x] 学历匹配（支持向下兼容）
- [x] 学位匹配
- [x] 性别匹配
- [x] 户籍匹配
- [x] 政治面貌匹配
- [x] 年龄匹配
- [x] 基层工作经验匹配
- [x] 语义匹配（支持模糊表达）

### 历年分析
- [x] 历史数据分析
- [x] 竞争趋势预测
- [x] 进面分数预测
- [x] 上岸概率计算

### 平台适配
- [x] 三支一扶
- [x] 公务员
- [x] 事业单位
- [x] 教师招聘

### 用户体验
- [x] 颜色标记（绿/黄/红）
- [x] 竞争比显示
- [x] 结果导出（Excel/HTML/JSON）
- [x] 收藏功能

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

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

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

## 详细文档

| 文档 | 说明 |
|-----|------|
| `docs/ARCHITECTURE.md` | 架构设计详解 |
| `docs/IMPLEMENTATION_STATUS.md` | 实施进度详情 |

---

## 许可证

MIT License
