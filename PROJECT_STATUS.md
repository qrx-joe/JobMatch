# JobMatch 智能选岗系统 - 项目状态

> 更新日期: 2026-05-01
> 版本: v2.0 → v3.0

## 项目概述

三支一扶智能选岗系统是一个 AI 驱动的考公考编岗位智能匹配工具，支持语义匹配、专业图谱、历年分析和报告导出。

---

## 项目结构

```
JobMatch/
├── 核心模块 (根目录)
│   ├── job_matcher.py           # 基础匹配引擎
│   ├── job_matcher_v2.py        # 增强版匹配引擎
│   ├── job_matcher_v3.py        # 第三版匹配引擎
│   ├── semantic_matcher.py      # 语义匹配器
│   ├── excel_reader_v2.py       # Excel 读取器
│   ├── excel_exporter.py       # Excel 导出器
│   ├── report_generator.py      # 报告生成器
│   └── data_manager.py          # 数据管理器
│
├── server/                      # FastAPI 后端
│   ├── app.py                   # 主入口
│   ├── core/                    # 核心业务逻辑
│   │   ├── models/              # 数据模型
│   │   ├── matchers/            # 匹配器
│   │   ├── recommenders/       # 推荐系统
│   │   └── analyzers/          # 分析器
│   ├── data/                    # 数据处理
│   │   ├── excel/               # Excel 解析
│   │   └── database/            # 数据库
│   └── platforms/              # 平台适配层
│
├── webapp/                      # Web 应用 (Vue3)
│   ├── backend/                 # 后端入口
│   └── frontend/               # Vue3 前端
│
├── shared/api/                  # 统一 API 服务
├── miniprogram/                # 微信小程序
├── tests/                       # 测试
└── docs/                        # 文档
```

---

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy
- pandas / openpyxl
- Anthropic Claude API (可选)

### 前端
- Vue 3
- Element Plus
- Vite
- Lucide 图标

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
- [x] 结果导出（Excel/HTML/JSON/PDF）
- [x] 收藏功能

---

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 启动后端
uv run uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload

# 3. 启动前端
cd webapp/frontend
npm install
npm run dev
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

## 下一步计划

1. 完善微信小程序界面
2. 添加更多匹配维度
3. 优化推荐算法
4. 添加数据可视化
5. 实现岗位对比功能
