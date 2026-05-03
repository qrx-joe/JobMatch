@echo off
chcp 65001 >nul
echo ========================================
echo 三支一扶岗位筛选系统 - 启动脚本
echo ========================================
echo.

:: 检查是否已有服务在运行
netstat -ano | findstr ":8000" >nul && (
    echo [警告] 端口8000已被占用，请先关闭其他实例
    pause
    exit /b 1
)

netstat -ano | findstr ":3000" >nul && (
    echo [警告] 端口3000已被占用，请先关闭其他实例
    pause
    exit /b 1
)

echo [1/3] 启动后端服务 (端口: 8000)...
start "Backend" cmd /k "cd .. && uv run python webapp/backend/app.py"

timeout /t 3 /nobreak >nul

echo [2/3] 启动前端服务 (端口: 3000)...
start "Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo [3/3] 启动浏览器...
start http://localhost:3000

echo.
echo ========================================
echo 服务已启动！
echo 前端: http://localhost:3000
echo 后端: http://localhost:8000
echo ========================================
echo.
echo 按任意键关闭所有服务...
pause >nul

taskkill /FI "WindowTitle eq Backend*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend*" /F >nul 2>&1

echo 服务已关闭
