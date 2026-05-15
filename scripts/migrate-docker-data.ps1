# Docker Desktop 数据迁移脚本
# 将 Docker Desktop 的镜像和容器数据从 C 盘迁移到其他盘
# 解决 C 盘空间不足导致的 read-only file system 错误

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Docker Desktop 数据迁移工具" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 显示各磁盘空间
Write-Host "磁盘空间情况:" -ForegroundColor Yellow
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -gt 1GB } | ForEach-Object {
    $freeGB = [math]::Round($_.Free / 1GB, 2)
    $usedGB = [math]::Round($_.Used / 1GB, 2)
    Write-Host "  $($_.Name):\ - 已用: ${usedGB} GB, 可用: ${freeGB} GB" -ForegroundColor White
}
Write-Host ""

# 显示Docker当前占用C盘空间
$dockerPath = "$env:LOCALAPPDATA\Docker"
if (Test-Path $dockerPath) {
    $dockerSize = (Get-ChildItem $dockerPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "Docker Desktop 当前占用 C 盘空间: $([math]::Round($dockerSize, 2)) GB" -ForegroundColor Yellow
}
Write-Host ""

# 目标盘选择
Write-Host "请选择目标磁盘（必须有足够空间）:" -ForegroundColor Cyan
$targetDrive = Read-Host "输入目标磁盘盘符 (D/E/F)"

if (-not ($targetDrive -match "^[DEFdef]$")) {
    Write-Host "错误: 无效的盘符，脚本退出" -ForegroundColor Red
    exit 1
}

$targetDrive = $targetDrive.ToUpper()
$targetPath = "${targetDrive}:\DockerData"
$dockerPath = "$env:LOCALAPPDATA\Docker"

Write-Host ""
Write-Host "源路径: $dockerPath" -ForegroundColor Yellow
Write-Host "目标路径: $targetPath" -ForegroundColor Green
Write-Host ""

$confirm = Read-Host "确认迁移? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit 0
}

# 步骤 1: 停止 Docker Desktop
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "步骤 1/4: 停止 Docker Desktop" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "正在停止 Docker Desktop..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -like "*Docker*" -or $_.ProcessName -like "*com.docker*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
Write-Host "Docker Desktop 已停止" -ForegroundColor Green
Write-Host ""

# 步骤 2: 复制数据
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "步骤 2/4: 复制数据（这可能需要几分钟）" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if (-not (Test-Path $targetPath)) {
    New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
}

Write-Host "正在复制数据..." -ForegroundColor Yellow
robocopy "$dockerPath" "$targetPath" /E /COPYALL /XJ /R:3 /W:5 /NFL /NDL

if ($LASTEXITCODE -le 7) {
    Write-Host "数据复制完成" -ForegroundColor Green
} else {
    Write-Host "复制过程中出现错误 (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 步骤 3: 备份原始目录并创建符号链接
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "步骤 3/4: 创建符号链接" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$backupPath = "$dockerPath.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
Write-Host "备份原始目录到: $backupPath" -ForegroundColor Yellow

Rename-Item "$dockerPath" $backupPath
Write-Host "原始目录已备份" -ForegroundColor Green

New-Item -ItemType Junction -Path "$dockerPath" -Target "$targetPath" -Force | Out-Null
Write-Host "符号链接已创建: $dockerPath -> $targetPath" -ForegroundColor Green
Write-Host ""

# 步骤 4: 重启 Docker Desktop
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "步骤 4/4: 重启 Docker Desktop" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Write-Host "Docker Desktop 正在启动..." -ForegroundColor Yellow
Write-Host "请等待 60 秒左右让 Docker 完全启动" -ForegroundColor Yellow
Write-Host ""

# 等待 Docker 启动
Start-Sleep -Seconds 10

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "迁移完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Docker 数据已迁移到: $targetPath" -ForegroundColor Green
Write-Host "原始数据已备份到: $backupPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "验证步骤:" -ForegroundColor Cyan
Write-Host "1. 等待 Docker Desktop 完全启动（托盘图标稳定）" -ForegroundColor White
Write-Host "2. 运行: docker ps" -ForegroundColor White
Write-Host "3. 运行项目测试: ./scripts/run-all-tests.sh" -ForegroundColor White
Write-Host ""
Write-Host "确认一切正常后，可以删除备份目录释放空间:" -ForegroundColor Yellow
Write-Host "  Remove-Item -Recurse -Force '$backupPath'" -ForegroundColor White
Write-Host ""
