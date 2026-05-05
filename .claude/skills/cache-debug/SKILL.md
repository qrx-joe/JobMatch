---
description: Debug cache/state persistence issues systematically
---

## 缓存盲区诊断协议

当用户报告"修了代码但问题还在"或"刷新后数据不对"时，按此协议执行。

### Step 1: 识别症状（判断是否是缓存问题）

| 症状 | 大概率是缓存问题 |
|------|-----------------|
| 代码已改，但浏览器显示旧行为 | ✅ |
| 表单默认值改了，但页面还是旧值 | ✅ localStorage |
| 同样的 bug，别人复现不了 | ✅ 浏览器缓存 |
| 重启电脑后 bug 消失 | ✅ 内存/进程状态 |
| Docker 容器里行为不一致 | ✅ 镜像层缓存 |
| 数据看起来是对的，但计算结果错 | ❌ 可能是逻辑 bug |

### Step 2: 分层清除（从快到慢）

**Layer 1 — 页面级（5秒）**
- 硬刷新：`Ctrl + F5`
- 或 DevTools → Network → Disable cache → 刷新

**Layer 2 — Storage 级（30秒）**
- DevTools → Application → Local Storage → 右键 Clear
- DevTools → Application → Session Storage → 右键 Clear
- DevTools → Application → Cookies → 清除相关域名
- JobMatch 特定：`localStorage.removeItem('jobmatch_profile')`
- JobMatch 特定：`localStorage.removeItem('jobmatch_result')`

**Layer 3 — 浏览器级（1分钟）**
- 无痕/隐私窗口打开
- 或 Settings → Privacy → Clear browsing data → Cached images and files

**Layer 4 — 服务级（2分钟）**
- 重启 dev server (`Ctrl+C`, `npm run dev`)
- Vite 有时缓存：`rm -rf node_modules/.vite`

**Layer 5 — 系统级（5分钟）**
- Docker: `docker system prune -a` (谨慎)
- Docker volume: `docker volume rm <name>`
- 重装 node_modules: `rm -rf node_modules && npm install`

### Step 3: 验证修复

清除后必须做：
1. 重新打开页面（不是刷新，是新标签页）
2. 复现用户的操作路径
3. 确认问题消失
4. 如果还在 → 不是缓存问题，继续代码级 debug

### Step 4: 防复发

- 修改数据结构时，同时修改 localStorage key（加版本号）
- 或每次启动时检查 schema 版本，不匹配则自动清除

### 禁忌

- 不要一上来就清 Layer 5（重装依赖）
- 不要清完缓存不验证就宣布修复
- 不要假设"用户肯定已经刷新过了"
