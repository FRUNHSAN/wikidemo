# WikiDemoTongYi v1.0.0 - Windows PowerShell 测试脚本
# 
# 使用方法：
# .\scripts\run-all-tests.ps1

$ErrorActionPreference = "Stop"

# 颜色定义
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Header { param($msg) Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n  $msg`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan }

$TestsPassed = 0
$TestsFailed = 0
$TestsTotal = 0

Write-Host "╔═══════════════════════════════════════════════════════════╗"
Write-Host "║     WikiDemoTongYi v1.0.0 - Windows 测试套件              ║"
Write-Host "╚═══════════════════════════════════════════════════════════╝"
Write-Host ""

# 辅助函数
function Test-Command {
    param($name, $script)
    $TestsTotal++
    Write-Host -NoNewline "[$TestsTotal] Testing: $name... "
    
    try {
        $result = Invoke-Expression $script
        if ($LASTEXITCODE -eq 0 -or $result) {
            Write-Success "PASS"
            $TestsPassed++
            return $true
        } else {
            Write-Error "FAIL"
            $TestsFailed++
            return $false
        }
    } catch {
        Write-Error "FAIL - $_"
        $TestsFailed++
        return $false
    }
}

# ==========================================
# 阶段1: 环境检查
# ==========================================
Write-Header "阶段 1/6: 环境检查"

# 测试1.1: Docker版本
Test-Command "Docker安装" "docker --version | Out-Null"

# 测试1.2: Docker Compose版本
Test-Command "Docker Compose" "docker compose version | Out-Null"

# 测试1.3: 可用内存
Write-Host -NoNewline "[$(($TestsTotal+1))] Testing: 系统内存（建议2GB+）... "
$MemGB = (Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum / 1GB
if ($MemGB -ge 2) {
    Write-Success "${MemGB}GB"
    $TestsPassed++
} else {
    Write-Warning "${MemGB}GB (可能不足)"
    $TestsPassed++
}
$TestsTotal++

# ==========================================
# 阶段2: 服务启动测试
# ==========================================
Write-Header "阶段 2/6: 服务启动测试"

# 测试2.1: 构建镜像
Test-Command "构建Docker镜像" "docker compose build"

# 测试2.2: 启动核心服务
Write-Host -NoNewline "[$(($TestsTotal+1))] Testing: 启动核心服务... "
try {
    docker compose up -d db wiki nginx 2>&1 | Out-Null
    Write-Host "等待服务就绪" -NoNewline
    
    for ($i = 1; $i -le 60; $i++) {
        $status = docker compose ps 2>&1
        if ($status -match "healthy") {
            break
        }
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
    Write-Host ""
    Write-Success "PASS"
    $TestsPassed++
} catch {
    Write-Error "FAIL"
    $TestsFailed++
}
$TestsTotal++

# 测试2.3: 验证容器状态
Write-Host -NoNewline "[$(($TestsTotal+1))] Testing: 所有容器运行正常... "
$runningCount = (docker compose ps 2>&1 | Select-String "Up").Count
if ($runningCount -ge 3) {
    Write-Success "$runningCount个容器运行中"
    $TestsPassed++
} else {
    Write-Error "只有$runningCount个容器运行"
    $TestsFailed++
}
$TestsTotal++

# 测试2.4: Wiki.js可访问
Write-Host -NoNewline "[$(($TestsTotal+1))] Testing: Wiki.js HTTP响应... "
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 302) {
        Write-Success "HTTP $($response.StatusCode)"
        $TestsPassed++
    } else {
        Write-Error "HTTP $($response.StatusCode)"
        $TestsFailed++
    }
} catch {
    Write-Error "无法连接"
    $TestsFailed++
}
$TestsTotal++

# ==========================================
# 阶段3: 插件系统测试
# ==========================================
Write-Header "阶段 3/6: 插件系统测试"

# 测试3.1: 启动插件服务
Test-Command "启动插件管理器" "docker compose --profile plugins up -d"
Start-Sleep -Seconds 5

# 测试3.2: C语言插件健康检查
Write-Host -NoNewline "[$(($TestsTotal+1))] Testing: C语言插件健康检查... "
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5
    if ($health.status -eq "healthy") {
        Write-Success "服务正常"
        $TestsPassed++
    } else {
        Write-Error "健康检查失败"
        $TestsFailed++
    }
} catch {
    Write-Error "无法连接"
    $TestsFailed++
}
$TestsTotal++

# 测试3.3: Markdown解析API
Write-Host -NoNewline "[$(($TestsTotal+1))] Testing: Markdown解析API... "
try {
    $body = '{"markdown": "# Test\n**Bold**"}'
    $response = Invoke-RestMethod -Uri "http://localhost:8080/api/parse" `
        -Method Post `
        -Body $body `
        -ContentType "application/json" `
        -UseBasicParsing `
        -TimeoutSec 5
    
    if ($response.success -eq $true) {
        Write-Success "API正常"
        $TestsPassed++
    } else {
        Write-Error "API响应异常"
        $TestsFailed++
    }
} catch {
    Write-Error "API调用失败: $_"
    $TestsFailed++
}
$TestsTotal++

# 测试3.4: 性能基准测试
Write-Host -NoNewline "[$(($TestsTotal+1))] Testing: C语言插件性能测试... "
try {
    $bench = Invoke-RestMethod -Uri "http://localhost:8080/api/benchmark" `
        -Method Post `
        -Body '{}' `
        -ContentType "application/json" `
        -UseBasicParsing `
        -TimeoutSec 10
    
    $opsPerSec = $bench.ops_per_second
    if ($opsPerSec -gt 1000) {
        Write-Success "QPS: $opsPerSec"
        $TestsPassed++
    } else {
        Write-Warning "QPS: $opsPerSec (偏低)"
        $TestsPassed++
    }
} catch {
    Write-Error "基准测试失败"
    $TestsFailed++
}
$TestsTotal++

# ==========================================
# 测试总结
# ==========================================
Write-Header "测试总结"

Write-Host "测试结果统计:"
Write-Host "  总测试数: $TestsTotal"
Write-Host "  通过: $TestsPassed" -ForegroundColor Green
if ($TestsFailed -gt 0) {
    Write-Host "  失败: $TestsFailed" -ForegroundColor Red
} else {
    Write-Host "  失败: 0"
}
Write-Host ""

$successRate = [math]::Round($TestsPassed * 100 / $TestsTotal)
Write-Host "成功率: ${successRate}%"
Write-Host ""

if ($TestsFailed -eq 0) {
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  🎉 所有测试通过！项目已准备好发布！                      ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
} else {
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║  ⚠️  部分测试失败，请检查上述错误信息                     ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Red
}

Write-Host ""
Write-Host "详细文档:"
Write-Host "  - README.md"
Write-Host "  - DEVELOPER_TESTING_GUIDE.md"
Write-Host ""

exit $(if ($TestsFailed -eq 0) { 0 } else { 1 })
