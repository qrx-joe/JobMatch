# 三支一扶智能选岗系统 - Web 应用

Vue3 + FastAPI 构建的 Web 版岗位筛选工具。

---

## 项目结构

```
webapp/
├── backend/           # FastAPI 后端
│   └── app.py        # 主 API
├── frontend/          # Vue3 前端
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── App.vue      # 主应用
│   │   └── main.js     # 入口
│   ├── package.json
│   └── vite.config.js
└── README.md          # 本文件
```

---

## 快速开始

### 1. 安装依赖

**后端依赖（在项目根目录）：**
```bash
uv sync
```

**前端依赖：**
```bash
cd webapp/frontend
npm install
```

### 2. 启动服务

**启动后端（端口 8000）：**
```bash
uv run uvicorn webapp.backend.app:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端（端口 3000）：**
```bash
cd webapp/frontend
npm run dev
```

### 3. 访问应用

打开浏览器访问：`http://localhost:3000`

---

## 功能特点

1. **拖拽上传**：支持拖拽上传 Excel 文件
2. **实时筛选**：所有筛选条件即时生效
3. **智能匹配**：
   - 专业大类匹配（经济学类包含经济学）
   - 学历向下兼容（本科可报大专及以上）
   - 性别/户籍/应届/政治面貌等条件
4. **竞争分析**：显示缴费人数和竞争比
5. **颜色标记**：
   - 绿色 = 完全符合
   - 黄色 = 可能符合
   - 红色 = 不符合
6. **结果导出**：支持下载 Excel 文件

---

## API 接口

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/jobs/upload` | POST | 上传 Excel |
| `/api/jobs/filter` | POST | 条件筛选 |
| `/api/jobs/recommend` | POST | 智能推荐 |
| `/api/jobs/{id}` | GET | 岗位详情 |
| `/api/cities` | GET | 城市列表 |

---

## 技术栈

- **后端**：Python + FastAPI
- **前端**：Vue 3 + Element Plus + Vite
- **Excel 处理**：pandas + openpyxl
- **图标**：Lucide Vue Next
