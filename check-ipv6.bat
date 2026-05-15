@echo off
REM IPv6支持检查脚本 - Windows版本

echo.
echo ======================================
echo   IPv6 支持检查工具 (Windows)
echo ======================================
echo.

REM 检查系统IPv6支持
echo 1. 检查系统IPv6支持
echo --------------------------------------
ipconfig | findstr "IPv6" >nul
if %errorlevel% equ 0 (
    echo [OK] 系统支持IPv6
    echo.
    echo IPv6地址列表:
    ipconfig | findstr "IPv6"
) else (
    echo [ERROR] 未检测到IPv6地址
    echo   可能需要在网络适配器中启用IPv6
)

echo.

REM 检查Docker
echo 2. 检查Docker支持
echo --------------------------------------
where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Docker已安装
    docker --version
    echo.

    docker info 2>nul | findstr "IPv6" >nul
    if %errorlevel% equ 0 (
        echo [OK] Docker支持IPv6
    ) else (
        echo [WARN] Docker可能未完全启用IPv6
        echo   Docker Desktop通常默认支持IPv6
    )
) else (
    echo [ERROR] Docker未安装
    echo   请下载安装 Docker Desktop:
    echo   https://www.docker.com/products/docker-desktop/
)

echo.

REM 检查端口占用
echo 3. 检查端口占用情况
echo --------------------------------------
netstat -ano | findstr ":80 " | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [WARN] 端口80已被占用
    netstat -ano | findstr ":80 " | findstr "LISTENING"
) else (
    echo [OK] 端口80未被占用
)

echo.

netstat -ano | findstr ":443 " | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [WARN] 端口443已被占用
    netstat -ano | findstr ":443 " | findstr "LISTENING"
) else (
    echo [OK] 端口443未被占用
)

echo.

REM 测试本地连接
echo 4. 测试本地IPv6连接
echo --------------------------------------
echo 测试连接到 [::1] (localhost IPv6)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://[::1]' -TimeoutSec 2 -UseBasicParsing; Write-Host '[OK] 可以连接到 [::1]' } catch { Write-Host '[INFO] 无法连接到 [::1] (可能是正常的，如果服务未启动)' }"

echo.
echo ======================================
echo   检查完成
echo ======================================
echo.
echo 建议:
echo   1. 确保系统启用了IPv6
echo   2. 确保Docker Desktop正在运行
echo   3. 确保防火墙允许80和443端口
echo   4. 运行 deploy.bat start 启动Wiki.js
echo.
pause
