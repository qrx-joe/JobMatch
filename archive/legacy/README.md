# 归档说明

归档时间：2026-05-03

本次归档的是 V1 探索阶段的所有 Python 后端代码和旧前端，原因是：
- 产品架构已锁定为**纯前端**（Vue 3 + SheetJS + fuse.js），不再依赖任何后端服务
- 旧后端存在已知的 import bug（webapp/backend/app.py 的 sys.path 错误）
- 旧 HTML 页面、miniprogram、server/ MySQL 后端均已明确从 V1 砍掉

## 目录结构

- `backend-python/` — 所有 Python 脚本、后端服务、测试、数据库初始化
  - `server/` — 旧 MySQL 后端（已废弃）
  - `webapp/backend/` — 旧 FastAPI 后端（已废弃）
  - `miniprogram/` — 微信小程序（V1 明确不做）
  - `database/` — 数据库 schema 和迁移
  - `shared/` — 旧共享模块
  - `tests/` — Python 单元测试
  - `*.py` — 各版本 matcher、reader、exporter
  - `pyproject.toml`, `uv.lock`, `ruff.toml`, `mypy.ini` — Python 工具链
- `configs/` — `config.yaml`, `config_full.yaml`
- `docs-old/` — 旧架构文档和实现计划
- `old-html/` — 旧 HTML 前端页面
- `output-artifacts/` — 历次运行生成的报告、Excel、txt

## 恢复方式

如需查看旧代码：
```bash
git log --all --oneline --grep="archive"   # 查找归档前提交
git checkout <commit> -- <path>            # 恢复特定文件
```
