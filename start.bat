@echo off
echo ========================================
echo AI Test Platform - 启动脚本
echo ========================================
echo.

echo [1/3] 检查Docker是否安装...
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未安装Docker，请先安装Docker Desktop
    pause
    exit /b 1
)
echo Docker已安装

echo.
echo [2/3] 检查Docker Compose是否安装...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未安装Docker Compose，请先安装Docker Compose
    pause
    exit /b 1
)
echo Docker Compose已安装

echo.
echo [3/3] 启动服务...
echo 正在启动AI Test Platform...
echo.

docker-compose up -d

if errorlevel 1 (
    echo.
    echo 错误: 启动失败，请检查Docker是否正常运行
    pause
    exit /b 1
)

echo.
echo ========================================
echo AI Test Platform 启动成功!
echo ========================================
echo.
echo 前端地址: http://localhost:5173
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 默认管理员账号:
echo 用户名: admin
echo 密码: admin123
echo.
echo 按任意键打开浏览器...
pause >nul

start http://localhost:5173