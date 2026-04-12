# 三支一扶岗位筛选系统 - Web版

## 项目结构

```
webapp/
├── backend/           # FastAPI后端
│   ├── app.py        # 主API
│   └── requirements.txt
├── frontend/          # Vue3前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── FilterPanel.vue   # 筛选面板
│   │   │   └── ResultPanel.vue   # 结果展示
│   │   ├── App.vue               # 主应用
│   │   └── main.js               # 入口
│   ├── package.json
│   └── vite.config.js
└── README.md         # 本文件
```

## 快速开始

### 1. 安装依赖

**后端依赖（在项目根目录）：**
```bash
cd ..
uv add fastapi uvicorn python-multipart
```

**前端依赖：**
```bash
cd frontend
npm install
```

### 2. 启动服务

**启动后端（端口8000）：**
```bash
cd ..
uv run python webapp/backend/app.py
```

**启动前端（端口3000）：**
```bash
cd frontend
npm run dev
```

### 3. 访问应用

打开浏览器访问：`http://localhost:3000`

## 功能特点

1. **拖拽上传**：支持拖拽上传Excel文件
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
6. **结果导出**：支持下载Excel文件

## 部署

### 本地部署
按照"快速开始"步骤执行即可

### 服务器部署

**使用Docker（推荐）：**
```bash
# 构建镜像
docker build -t jobmatch .

# 运行
docker run -p 8000:8000 jobmatch
```

**手动部署：**
1. 将代码上传到服务器
2. 安装Python依赖：`uv sync`
3. 构建前端：`cd frontend && npm run build`
4. 使用Nginx代理前端静态文件
5. 使用PM2运行后端：`pm2 start webapp/backend/app.py`

## 技术栈

- **后端**：Python + FastAPI
- **前端**：Vue3 + Element Plus
- **Excel处理**：pandas + openpyxl
- **构建工具**：Vite
