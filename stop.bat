@echo off
echo ========================================
echo AI Test Platform - 停止脚本
echo ========================================
echo.

echo 正在停止AI Test Platform服务...
echo.

docker-compose down

if errorlevel 1 (
    echo.
    echo 错误: 停止失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo AI Test Platform 已停止
echo ========================================
echo.
pause