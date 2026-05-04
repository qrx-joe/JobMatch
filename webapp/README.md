# JobMatch 前端应用

> Vue3 + Vite + Element Plus 构建的纯前端岗位筛选工具。
> Excel 在浏览器内解析，无后端服务。

---

## 项目结构

```
webapp/frontend/
├── src/
│   ├── App.vue              # 主应用入口
│   ├── main.js              # 应用初始化
│   ├── components/          # 页面组件
│   │   ├── FilterPanel.vue  # 筛选条件面板（文件上传 + 表单）
│   │   └── ResultPanel.vue  # 结果展示面板（统计 + 表格）
│   ├── engine/              # 核心筛选引擎
│   │   ├── excel.js         # Excel 解析、智能列识别
│   │   ├── matcher.js       # 多条件匹配引擎
│   │   ├── joiner.js        # 岗位表与统计表关联
│   │   └── parseOther.js    # "其他要求"文本解析
│   └── services/
│       └── api.js           # 业务接口层（纯函数，无网络请求）
├── index.html
├── package.json
└── vite.config.js
```

---

## 快速开始

### 安装依赖

```bash
cd webapp/frontend
npm install
```

### 本地开发

```bash
npm run dev
```

默认端口 `3000`，访问 `http://localhost:3000`。

### 生产构建

```bash
npm run build
```

输出目录：`dist/`

### 预览构建产物

```bash
npm run preview
```

---

## 技术栈

| 依赖 | 用途 |
|-----|------|
| Vue 3 | 前端框架 |
| Vite | 构建工具 |
| Element Plus | UI 组件库 |
| SheetJS (xlsx) | Excel 读写（浏览器内） |
| fuse.js | 模糊匹配（专业、列名识别） |
| Lucide Vue Next | 图标 |

---

## 核心模块说明

### engine/excel.js
- 读取 `.xls` / `.xlsx` 文件
- 智能列头识别：通过同义词映射自动识别"专业要求"、"学历要求"等列
- 数据清洗：去除空行、标准化字段名

### engine/matcher.js
- 根据用户画像对岗位列表进行多条件匹配
- 支持学历向下兼容、专业大类包含、性别/户籍严格/宽松模式
- 输出匹配等级：完全符合 / 可能符合 / 不符合

### engine/joiner.js
- 读取报名统计表
- 按"岗位代码 + 岗位名称"与岗位表关联
- 处理格式漂移（前导零、空格、全半角）

---

## 部署

本项目通过 **Vercel** 自动部署：

- **在线访问**：https://frontend-gamma-seven-37.vercel.app
- 触发条件：`main` 分支推送
- 构建命令：`npm run build`
- 输出目录：`dist/`

Vercel 会自动识别 Vite 项目并完成构建，无需额外配置。

---

## 浏览器兼容性

- Chrome / Edge / Firefox / Safari 最新两个主版本
- 依赖 `FileReader` 和 `localStorage`，IE 不支持
