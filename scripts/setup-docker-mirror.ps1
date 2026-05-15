# Docker镜像加速器配置脚本 (PowerShell版本)
# 用于解决中国大陆访问Docker Hub网络问题
# 在Windows PowerShell中运行此脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Docker镜像加速器配置工具 (PowerShell)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker Desktop是否安装
$dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (-not (Test-Path $dockerDesktopPath)) {
    Write-Host "错误: 未检测到Docker Desktop" -ForegroundColor Red
    Write-Host "请先安装Docker Desktop for Windows" -ForegroundColor Yellow
    Write-Host "下载地址: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Docker配置文件路径
$dockerConfigPath = "$env:USERPROFILE\.docker\daemon.json"

Write-Host "Docker配置文件位置: $dockerConfigPath" -ForegroundColor Green
Write-Host ""

# 创建或读取现有配置
if (Test-Path $dockerConfigPath) {
    Write-Host "发现现有配置文件，将添加镜像加速器..." -ForegroundColor Yellow
    try {
        $config = Get-Content $dockerConfigPath | ConvertFrom-Json
    } catch {
        Write-Host "警告: 现有配置文件格式可能不正确，将创建新配置" -ForegroundColor Yellow
        $config = @{}
    }
} else {
    Write-Host "未找到配置文件，将创建新配置..." -ForegroundColor Yellow
    $config = @{}
}

# 备份现有配置
if (Test-Path $dockerConfigPath) {
    $backupPath = "$dockerConfigPath.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
    Copy-Item $dockerConfigPath $backupPath
    Write-Host "已备份现有配置到: $backupPath" -ForegroundColor Green
}

# 添加镜像加速器
$mirrors = @(
    "https://docker.m.daocloud.io",
    "https://huecker.io",
    "https://dockerhub.timeweb.cloud"
)

$config.'registry-mirrors' = $mirrors

# 确保其他必要配置存在
if (-not $config.'builder') {
    $config.'builder' = @{
        'gc' = @{
            'defaultKeepStorage' = '20GB'
            'enabled' = $true
        }
    }
}

if (-not $config.'experimental') {
    $config.'experimental' = $false
}

# 保存配置
try {
    # 创建目录（如果不存在）
    $configDir = Split-Path $dockerConfigPath -Parent
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }

    # 保存JSON配置
    $jsonContent = $config | ConvertTo-Json -Depth 10
    Set-Content $dockerConfigPath $jsonContent -Encoding UTF8

    Write-Host ""
    Write-Host "✓ 配置已成功保存到: $dockerConfigPath" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "✗ 保存配置失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请尝试以管理员身份运行此脚本" -ForegroundColor Yellow
    exit 1
}

# 显示配置内容
Write-Host "配置内容:" -ForegroundColor Cyan
Write-Host "----------------------------------------"
Get-Content $dockerConfigPath | Write-Host
Write-Host "----------------------------------------"
Write-Host ""

# 提示重启Docker Desktop
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "下一步操作" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 重启Docker Desktop使配置生效" -ForegroundColor White
Write-Host "   - 右键点击系统托盘中的Docker图标" -ForegroundColor Gray
Write-Host "   - 选择 'Quit Docker Desktop'" -ForegroundColor Gray
Write-Host "   - 重新打开Docker Desktop" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 等待Docker完全启动（约30-60秒）" -ForegroundColor White
Write-Host ""
Write-Host "3. 验证配置是否生效:" -ForegroundColor White
Write-Host "   打开WSL或PowerShell，运行:" -ForegroundColor Gray
Write-Host "   docker info | Select-String 'Registry Mirrors'" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 测试拉取镜像:" -ForegroundColor White
Write-Host "   docker pull hello-world" -ForegroundColor Gray
Write-Host ""
Write-Host "5. 运行项目测试脚本:" -ForegroundColor White
Write-Host "   wsl ./scripts/run-all-tests.sh" -ForegroundColor Gray
Write-Host ""

# 询问是否立即重启Docker Desktop
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "是否立即重启Docker Desktop?" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "注意: 这将关闭所有正在运行的容器" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "输入 Y 立即重启，或 N 稍后手动重启 (Y/N)"

if ($choice -eq 'Y' -or $choice -eq 'y') {
    Write-Host ""
    Write-Host "正在重启Docker Desktop..." -ForegroundColor Yellow

    # 停止Docker Desktop
    Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5

    # 启动Docker Desktop
    Start-Process $dockerDesktopPath

    Write-Host ""
    Write-Host "✓ Docker Desktop正在重启..." -ForegroundColor Green
    Write-Host ""
    Write-Host "请等待60秒左右让Docker完全启动" -ForegroundColor Yellow
    Write-Host "然后运行: wsl ./scripts/run-all-tests.sh" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "请记得手动重启Docker Desktop以使配置生效" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "故障排查" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "如果重启后仍然无法连接Docker Hub:" -ForegroundColor White
Write-Host ""
Write-Host "1. 检查Docker Desktop状态" -ForegroundColor White
Write-Host "   - 确保Docker Desktop完全启动" -ForegroundColor Gray
Write-Host "   - 查看系统托盘图标是否正常" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 检查网络连接" -ForegroundColor White
Write-Host "   ping registry-1.docker.io" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 尝试其他镜像源" -ForegroundColor White
Write-Host "   编辑 $dockerConfigPath" -ForegroundColor Gray
Write-Host "   修改 registry-mirrors 列表" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 查看Docker日志" -ForegroundColor White
Write-Host "   位置: %USERPROFILE%\AppData\Local\Docker\log.txt" -ForegroundColor Gray
Write-Host ""
Write-Host "5. 重置Docker Desktop（最后手段）" -ForegroundColor White
Write-Host "   Settings → Troubleshoot → Reset to factory defaults" -ForegroundColor Gray
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "配置完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
