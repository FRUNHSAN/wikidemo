@echo off
REM Wiki.js 部署脚本 - Windows版本（支持IPv6）
REM 使用方法: deploy.bat [start|stop|restart|logs|status]

setlocal enabledelayedexpansion

set COMPOSE_FILE=docker-compose.yml
set PROJECT_NAME=wiki-js-ipv6

echo.
echo ========================================
echo   Wiki.js IPv6 部署工具
echo ========================================
echo.

REM 检查Docker是否安装
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

docker compose version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose未安装，请确保使用Docker Desktop最新版
    pause
    exit /b 1
)

echo [INFO] Docker版本:
docker --version
echo.

REM 创建必要的目录
if not exist "nginx\conf.d" mkdir nginx\conf.d
if not exist "data\postgres" mkdir data\postgres
if not exist "data\wiki" mkdir data\wiki
if not exist "logs\nginx" mkdir logs\nginx

REM 检查.env文件
if not exist ".env" (
    echo [WARN] .env文件不存在，将使用默认配置
    echo [WARN] 建议复制 .env.example 为 .env 并修改配置
    echo.
)

if "%1"=="" goto start
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="backup" goto backup
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help

echo [ERROR] 未知命令: %1
goto help

:start
echo [INFO] 启动Wiki.js服务（支持IPv6）...
echo.
docker compose -p %PROJECT_NAME% up -d

echo.
echo [INFO] 等待服务启动...
timeout /t 5 /nobreak >nul

echo.
echo [INFO] 服务状态:
docker compose -p %PROJECT_NAME% ps

echo.
echo ==========================================
echo   Wiki.js 部署完成！
echo ==========================================
echo.
echo 访问地址:
echo   - IPv4: http://localhost
echo   - IPv6: http://[::1]
echo   - 本机IP: http://[你的IPv6地址]
echo.
echo 初始管理员账号:
echo   - 邮箱: admin@example.com
echo   - 密码: changeme123
echo.
echo 请尽快登录并修改密码！
echo ==========================================
echo.
pause
exit /b 0

:stop
echo [INFO] 停止Wiki.js服务...
docker compose -p %PROJECT_NAME% down
echo [INFO] 服务已停止
pause
exit /b 0

:restart
echo [INFO] 重启Wiki.js服务...
call :stop
timeout /t 2 /nobreak >nul
call :start
exit /b 0

:logs
echo [INFO] 查看服务日志...
if "%2"=="" (
    docker compose -p %PROJECT_NAME% logs -f
) else (
    docker compose -p %PROJECT_NAME% logs -f %2
)
exit /b 0

:status
echo [INFO] 服务状态:
docker compose -p %PROJECT_NAME% ps
echo.
echo [INFO] 网络信息:
docker network inspect %PROJECT_NAME%_wiki-network 2>nul | findstr "IPv6" || echo 无法获取网络信息
pause
exit /b 0

:backup
set BACKUP_DIR=backups\%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

echo [INFO] 备份数据到 %BACKUP_DIR% ...

if not exist "%BACKUP_DIR%" mkdir %BACKUP_DIR%

REM 备份数据库
docker compose -p %PROJECT_NAME% exec -T db pg_dump -U wikiuser wikidb > "%BACKUP_DIR%\database.sql"

REM 备份配置文件
copy docker-compose.yml %BACKUP_DIR%\ >nul
xcopy /E /I nginx %BACKUP_DIR%\nginx\ >nul 2>&1

echo [INFO] 备份完成: %BACKUP_DIR%
pause
exit /b 0

:help
echo Wiki.js IPv6 部署脚本
echo.
echo 使用方法: deploy.bat [command]
echo.
echo 命令:
echo   start       启动服务
echo   stop        停止服务
echo   restart     重启服务
echo   logs        查看日志 ^(可指定服务名: wiki, nginx, db^)
echo   status      查看服务状态
echo   backup      备份数据
echo   help        显示此帮助信息
echo.
echo 示例:
echo   deploy.bat start
echo   deploy.bat logs wiki
echo   deploy.bat backup
echo.
pause
exit /b 0
