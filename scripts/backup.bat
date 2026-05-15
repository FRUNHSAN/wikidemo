@echo off
REM ==========================================
REM Wiki.js 自动备份脚本 - Windows版本
REM ==========================================

setlocal enabledelayedexpansion

REM 配置变量
set BACKUP_DIR=%BACKUP_DIR%.\backups
set RETENTION_DAYS=%RETENTION_DAYS:30%
set COMPRESS_BACKUP=%COMPRESS_BACKUP:true%

echo.
echo ==========================================
echo   Wiki.js 自动备份开始
echo   时间: %date% %time%
echo ==========================================
echo.

REM 检查Docker
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)

REM 创建备份目录
echo [STEP] 创建备份目录...
if not exist "%BACKUP_DIR%\database" mkdir "%BACKUP_DIR%\database"
if not exist "%BACKUP_DIR%\files" mkdir "%BACKUP_DIR%\files"
if not exist "%BACKUP_DIR%\config" mkdir "%BACKUP_DIR%\config"

REM 生成时间戳
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

REM 备份数据库
echo [STEP] 备份PostgreSQL数据库...
docker compose exec -T db pg_dump -U wikiuser wikidb > "%BACKUP_DIR%\database\wiki_db_%TIMESTAMP%.sql"
if %errorlevel% equ 0 (
    echo [OK] 数据库备份完成
) else (
    echo [ERROR] 数据库备份失败
)

REM 备份配置文件
echo [STEP] 备份配置文件...
copy docker-compose.yml "%BACKUP_DIR%\config\" >nul 2>&1
if exist .env copy .env "%BACKUP_DIR%\config\" >nul 2>&1

echo [OK] 配置文件备份完成

REM 清理旧备份（简化版）
echo [STEP] 清理旧备份...
forfiles /p "%BACKUP_DIR%" /s /m *.sql /d -%RETENTION_DAYS% /c "cmd /c del @path" 2>nul

echo.
echo ==========================================
echo   [OK] 备份完成！
echo   备份位置: %BACKUP_DIR%
echo ==========================================
echo.
pause
