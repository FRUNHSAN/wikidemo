@echo off
REM Obsidian同步快捷脚本 - Windows版本

echo.
echo ========================================
echo   Obsidian 双向同步工具
echo ========================================
echo.

REM 检查Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查配置文件
if not exist "obsidian-sync-config.json" (
    echo [WARN] 配置文件不存在，正在创建...
    copy obsidian-sync-config.example.json obsidian-sync-config.json
    echo.
    echo 请编辑 obsidian-sync-config.json 配置以下内容:
    echo   - local_folder: Obsidian仓库路径
    echo   - wiki_api_token: Wiki API Token
    echo.
    pause
)

REM 解析命令
if "%1"=="" goto sync
if "%1"=="sync" goto sync
if "%1"=="status" goto status
if "%1"=="conflicts" goto conflicts
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help

echo [ERROR] 未知命令: %1
goto help

:sync
echo [INFO] 开始同步...
echo.
python scripts\obsidian-sync\sync_manager.py
echo.
echo [OK] 同步完成
pause
exit /b 0

:status
echo [INFO] 同步状态:
echo.
python scripts\obsidian-sync\sync_manager.py --status
pause
exit /b 0

:conflicts
echo [INFO] 待处理冲突:
echo.
python scripts\obsidian-sync\sync_manager.py --conflicts
pause
exit /b 0

:help
echo 用法: sync.bat [command]
echo.
echo 命令:
echo   sync        执行同步（默认）
echo   status      查看同步状态
echo   conflicts   查看待处理冲突
echo   help        显示此帮助信息
echo.
echo 示例:
echo   sync.bat
echo   sync.bat status
echo   sync.bat conflicts
echo.
pause
exit /b 0
