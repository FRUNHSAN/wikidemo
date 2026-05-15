@echo off
REM GitHub项目初始化脚本 (Windows版本)
REM 用于准备项目并上传到GitHub

echo =========================================
echo WikiDemoTongYi - GitHub项目初始化
echo =========================================
echo.

REM 检查是否在正确的目录
if not exist "docker-compose.yml" (
    echo X 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 1. 初始化Git仓库
echo [1/5] 初始化Git仓库...
if not exist ".git" (
    git init
    echo OK Git仓库已初始化
) else (
    echo ! Git仓库已存在，跳过
)
echo.

REM 2. 添加所有文件
echo [2/5] 添加文件到Git...
git add .
echo OK 文件已添加到暂存区
echo.

REM 3. 创建初始提交
echo [3/5] 创建初始提交...
git commit -m "Initial commit: Wiki.js个人知识管理系统增强版

Features:
- IPv4/IPv6双栈支持
- Docker容器化部署
- RSS阅读器插件（AI摘要）
- Obsidian双向同步
- 配置管理系统（CLI + Web UI）
- 日志管理系统
- Git自动备份
- 可扩展插件框架

Generated with Lingma"
echo OK 初始提交已创建
echo.

REM 4. 提示用户设置远程仓库
echo [4/5] 设置GitHub远程仓库
echo.
echo 请在GitHub上创建新仓库，然后运行以下命令：
echo.
echo   git remote add origin https://github.com/YOUR_USERNAME/wikidemotongyi.git
echo   git branch -M main
echo   git push -u origin main
echo.
pause
echo.

REM 5. 显示项目信息
echo [5/5] 项目信息
echo.
echo 项目名称: WikiDemoTongYi
echo 版本: 1.0.0
echo 许可证: MIT
echo.
echo 主要功能:
echo   ^> Wiki.js核心引擎
echo   ^> RSS阅读器插件
echo   ^> Obsidian双向同步
echo   ^> 配置管理系统
echo   ^> 日志管理系统
echo   ^> 插件开发框架
echo.
echo 文档:
echo   - README.md (主文档)
echo   - CONTRIBUTING.md (贡献指南)
echo   - docs/ (详细功能文档)
echo.

REM 显示下一步操作
echo =========================================
echo OK 初始化完成！
echo =========================================
echo.
echo 接下来请执行以下步骤：
echo.
echo 1. 在GitHub创建新仓库
echo    访问: https://github.com/new
echo.
echo 2. 设置远程仓库（替换YOUR_USERNAME）:
echo    git remote add origin https://github.com/YOUR_USERNAME/wikidemotongyi.git
echo.
echo 3. 推送到GitHub:
echo    git branch -M main
echo    git push -u origin main
echo.
echo 4. 更新README.md中的链接:
echo    - 替换 'your-username' 为你的GitHub用户名
echo    - 更新联系邮箱
echo.
echo 祝你好运！
echo.
pause
