# IPv6 公网地址快速检测脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   IPv6 公网地址检测工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查IPv6配置
Write-Host "[1] 检查IPv6配置..." -ForegroundColor Yellow
$ipv6Addresses = Get-NetIPAddress -AddressFamily IPv6 | Where-Object { $_.PrefixOrigin -eq "RouterAdvertisement" -or $_.PrefixOrigin -eq "Manual" }
if ($ipv6Addresses) {
    Write-Host "检测到IPv6地址:" -ForegroundColor Green
    $ipv6Addresses | ForEach-Object {
        Write-Host "  $($_.IPAddress)" -ForegroundColor White
    }
} else {
    Write-Host "未检测到IPv6地址" -ForegroundColor Red
}
Write-Host ""

# 2. 测试IPv6网络连接
Write-Host "[2] 测试IPv6网络连接..." -ForegroundColor Yellow
try {
    $testResult = Test-Connection -ComputerName ipv6.google.com -Count 2 -Quiet -ErrorAction Stop
    if ($testResult) {
        Write-Host "IPv6网络连接正常" -ForegroundColor Green
    } else {
        Write-Host "IPv6网络不可达" -ForegroundColor Red
    }
} catch {
    Write-Host "IPv6网络不可达" -ForegroundColor Red
}
Write-Host ""

# 3. 获取公网IPv6地址
Write-Host "[3] 检测公网IPv6地址..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://api64.ipify.org?format=json" -TimeoutSec 5
    Write-Host "你的公网IPv6地址: $($response.ip)" -ForegroundColor Green
} catch {
    Write-Host "无法获取公网IPv6地址" -ForegroundColor Red
    Write-Host "请访问 https://test-ipv6.com 手动查看" -ForegroundColor Yellow
}
Write-Host ""

# 4. 检查端口状态
Write-Host "[4] 检查关键端口..." -ForegroundColor Yellow
$ports = @(80, 443)
foreach ($port in $ports) {
    $tcpConnection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    if ($tcpConnection.TcpTestSucceeded) {
        Write-Host "端口 $port 已开放" -ForegroundColor Green
    } else {
        Write-Host "端口 $port 未开放" -ForegroundColor Red
    }
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "下一步操作指南:" -ForegroundColor Yellow
Write-Host "1. 如果检测到公网IPv6地址，继续配置防火墙" -ForegroundColor White
Write-Host "2. 如果没有公网IPv6地址，需要联系ISP开通" -ForegroundColor White
Write-Host "3. 访问 https://test-ipv6.com 进行完整测试" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan