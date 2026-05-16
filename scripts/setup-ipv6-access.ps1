# ========================================
# Wiki.js IPv6 公网访问配置脚本
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Wiki.js IPv6 公网访问配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 获取公网IPv6地址
Write-Host "[步骤 1/5] 获取你的公网IPv6地址..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://api64.ipify.org?format=json" -TimeoutSec 5
    $publicIPv6 = $response.ip
    Write-Host "你的公网IPv6地址: $publicIPv6" -ForegroundColor Green
} catch {
    Write-Host "错误：无法获取公网IPv6地址" -ForegroundColor Red
    Write-Host "请确保你的网络支持IPv6" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# 2. 检查当前Wiki.js服务状态
Write-Host "[步骤 2/5] 检查Wiki.js服务状态..." -ForegroundColor Yellow
$containerStatus = docker compose ps --format json 2>$null | ConvertFrom-Json
if ($containerStatus) {
    Write-Host "当前运行的服务:" -ForegroundColor Green
    $containerStatus | ForEach-Object {
        Write-Host "  - $($_.Name): $($_.Status)" -ForegroundColor White
    }
} else {
    Write-Host "警告：未检测到运行的服务" -ForegroundColor Yellow
    Write-Host "请先运行: docker compose up -d" -ForegroundColor Yellow
}
Write-Host ""

# 3. 配置Windows防火墙
Write-Host "[步骤 3/5] 配置Windows防火墙..." -ForegroundColor Yellow
Write-Host "需要开放以下端口：" -ForegroundColor White
Write-Host "  - 80 (HTTP)" -ForegroundColor White
Write-Host "  - 443 (HTTPS)" -ForegroundColor White
Write-Host ""

$firewallRules = @(
    @{Name="Wiki-HTTP-In"; DisplayName="Wiki.js HTTP入站"; Protocol="TCP"; LocalPort=80},
    @{Name="Wiki-HTTPS-In"; DisplayName="Wiki.js HTTPS入站"; Protocol="TCP"; LocalPort=443}
)

foreach ($rule in $firewallRules) {
    $existingRule = Get-NetFirewallRule -Name $rule.Name -ErrorAction SilentlyContinue
    if ($existingRule) {
        Write-Host "防火墙规则已存在: $($rule.DisplayName)" -ForegroundColor Green
    } else {
        Write-Host "创建防火墙规则: $($rule.DisplayName)..." -ForegroundColor Yellow
        New-NetFirewallRule -Name $rule.Name `
                           -DisplayName $rule.DisplayName `
                           -Direction Inbound `
                           -Protocol $rule.Protocol `
                           -LocalPort $rule.LocalPort `
                           -Action Allow `
                           -Profile Any `
                           -Enabled True | Out-Null
        Write-Host "✓ 防火墙规则已创建" -ForegroundColor Green
    }
}
Write-Host ""

# 4. 生成访问URL
Write-Host "[步骤 4/5] 生成访问URL..." -ForegroundColor Yellow
$httpURL = "http://[$publicIPv6]"
$httpsURL = "https://[$publicIPv6]"

Write-Host "HTTP访问地址:" -ForegroundColor Green
Write-Host "  $httpURL" -ForegroundColor White
Write-Host ""
Write-Host "HTTPS访问地址（推荐）:" -ForegroundColor Green
Write-Host "  $httpsURL" -ForegroundColor White
Write-Host ""

# 5. 测试端口可达性
Write-Host "[步骤 5/5] 测试端口可达性..." -ForegroundColor Yellow
$testPorts = @(80, 443)
foreach ($port in $testPorts) {
    Write-Host "测试端口 $port..." -ForegroundColor White
    $tcpTest = Test-NetConnection -ComputerName $publicIPv6 -Port $port -WarningAction SilentlyContinue
    if ($tcpTest.TcpTestSucceeded) {
        Write-Host "✓ 端口 $port 可从公网访问" -ForegroundColor Green
    } else {
        Write-Host " 端口 $port 无法从公网访问" -ForegroundColor Red
        Write-Host "  可能原因：" -ForegroundColor Yellow
        Write-Host "  1. 路由器未开放IPv6端口转发" -ForegroundColor Yellow
        Write-Host "  2. 运营商阻止了该端口" -ForegroundColor Yellow
        Write-Host "  3. 防火墙规则未生效" -ForegroundColor Yellow
    }
}
Write-Host ""

# 6. 输出配置总结
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "你的Wiki.js现在可以通过以下地址访问：" -ForegroundColor White
Write-Host "  $httpURL" -ForegroundColor Cyan
Write-Host "  $httpsURL（需配置SSL证书）" -ForegroundColor Cyan
Write-Host ""
Write-Host "重要提示：" -ForegroundColor Yellow
Write-Host "  1. 首次访问会显示不安全的警告（正常）" -ForegroundColor White
Write-Host "  2. 建议配置HTTPS和SSL证书" -ForegroundColor White
Write-Host "  3. 记得修改默认管理员密码" -ForegroundColor White
Write-Host "  4. 定期更新Docker镜像" -ForegroundColor White
Write-Host ""
Write-Host "下一步建议：" -ForegroundColor Yellow
Write-Host "  1. 配置域名和DDNS（可选）" -ForegroundColor White
Write-Host "  2. 安装Let's Encrypt SSL证书" -ForegroundColor White
Write-Host "  3. 配置备份策略" -ForegroundColor White
Write-Host "  4. 设置监控告警" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# 保存配置到文件
$configFile = "ipv6-config.txt"
@"
Wiki.js IPv6 公网访问配置
生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
公网IPv6地址: $publicIPv6
HTTP访问地址: $httpURL
HTTPS访问地址: $httpsURL
"@ | Out-File -FilePath $configFile -Encoding UTF8

Write-Host "配置信息已保存到: $configFile" -ForegroundColor Green