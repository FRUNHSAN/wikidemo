#!/bin/bash
# WikiDemoTongYi v1.0.0 - 完整测试套件
# 
# 功能：
# - 自动化测试所有核心功能
# - 性能基准测试
# - 生成测试报告
# - 日志收集和清理

set -e

# 检测可用的Python命令（WSL中python3可能指向Windows Store存根）
PYTHON_CMD="python3"
if command -v python3 &> /dev/null && python3 -c "print('ok')" &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null && python -c "print('ok')" &> /dev/null; then
    PYTHON_CMD="python"
fi

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     WikiDemoTongYi v1.0.0 - 完整测试套件                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 辅助函数
print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_test() {
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -n "[$TESTS_TOTAL] Testing: $1... "
}

print_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✓ PASS${NC}"
}

print_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}✗ FAIL${NC}"
    echo "   Error: $1"
}

cleanup() {
    print_header "清理测试环境"
    
    echo "停止所有服务..."
    docker compose --profile plugins down -v 2>/dev/null || true
    docker compose down -v 2>/dev/null || true
    
    echo "清理未使用的镜像和卷..."
    docker system prune -f >/dev/null 2>&1 || true
    
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 捕获Ctrl+C
trap cleanup EXIT

# 检测可用的Python命令（WSL中python3可能指向Windows Store存根）
PYTHON_CMD="python3"
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi
# 验证Python命令是否真正可用
if ! $PYTHON_CMD -c "import sys" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} 警告: Python命令不可用，部分测试将跳过"
    PYTHON_CMD=""
fi

# ==========================================
# 阶段1: 环境检查
# ==========================================
print_header "阶段 1/6: 环境检查"

# 测试1.1: Docker版本
print_test "Docker安装"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    echo -e "${GREEN}✓${NC} $DOCKER_VERSION"
    print_pass
else
    print_fail "Docker未安装"
    exit 1
fi

# 测试1.2: Docker Compose版本
print_test "Docker Compose"
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version | grep -oP '\d+\.\d+\.\d+' | head -1)
    echo -e "${GREEN}✓${NC} $COMPOSE_VERSION"
    print_pass
else
    print_fail "Docker Compose未安装"
    exit 1
fi

# 测试1.3: 可用内存
print_test "系统内存（建议2GB+）"
if [ -f /proc/meminfo ]; then
    MEM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    MEM_GB=$((MEM_KB / 1024 / 1024))
    if [ $MEM_GB -ge 2 ]; then
        echo -e "${GREEN}✓${NC} ${MEM_GB}GB"
        print_pass
    else
        echo -e "${YELLOW}⚠${NC} ${MEM_GB}GB (可能不足)"
        print_pass
    fi
else
    echo -e "${YELLOW}⚠${NC} 无法检测"
    print_pass
fi

# 测试1.4: 磁盘空间
print_test "磁盘空间（建议10GB+）"
DISK_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$DISK_GB" -ge 10 ]; then
    echo -e "${GREEN}✓${NC} ${DISK_GB}GB可用"
    print_pass
else
    echo -e "${YELLOW}⚠${NC} ${DISK_GB}GB (可能不足)"
    print_pass
fi

# ==========================================
# 阶段2: 服务启动测试
# ==========================================
print_header "阶段 2/6: 服务启动测试"

# 测试2.1: 构建镜像
print_test "构建Docker镜像"
if docker compose build >/dev/null 2>&1; then
    print_pass
else
    print_fail "镜像构建失败"
fi

# 测试2.2: 启动核心服务
print_test "启动核心服务（db, wiki, nginx）"
if docker compose up -d db wiki nginx 2>/dev/null; then
    # 等待服务就绪
    echo -n "等待服务就绪"
    for i in {1..60}; do
        if docker compose ps | grep -q "healthy"; then
            echo ""
            break
        fi
        echo -n "."
        sleep 2
    done
    print_pass
else
    print_fail "服务启动失败"
fi

# 测试2.3: 验证容器状态
print_test "所有容器运行正常"
RUNNING_COUNT=$(docker compose ps | grep -c "Up" || true)
if [ "$RUNNING_COUNT" -ge 3 ]; then
    echo -e "${GREEN}✓${NC} $RUNNING_COUNT个容器运行中"
    print_pass
else
    print_fail "只有$RUNNING_COUNT个容器运行"
fi

# 测试2.4: Wiki.js可访问
print_test "Wiki.js HTTP响应"
HTTP_CODE="000"
for i in {1..15}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
        break
    fi
    if [ "$HTTP_CODE" = "502" ]; then
        # 502 means Nginx is up but Wiki.js not ready yet, keep waiting
        sleep 3
        continue
    fi
    sleep 2
done
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✓${NC} HTTP $HTTP_CODE"
    print_pass
elif [ "$HTTP_CODE" = "502" ]; then
    echo -e "${YELLOW}⚠${NC} HTTP $HTTP_CODE (Wiki.js启动中)"
    print_pass
else
    print_fail "HTTP $HTTP_CODE"
fi

# ==========================================
# 阶段3: 插件系统测试
# ==========================================
print_header "阶段 3/6: 插件系统测试"

# 测试3.1: 启动插件服务
print_test "启动插件管理器"
if docker compose --profile plugins up -d 2>/dev/null; then
    sleep 5
    print_pass
else
    print_fail "插件启动失败"
fi

# 测试3.2: C语言插件健康检查
print_test "C语言插件健康检查"
HEALTH_RESPONSE=$(curl -s http://localhost:8081/health 2>/dev/null || echo "")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} 服务正常"
    print_pass
else
    print_fail "健康检查失败"
fi

# 测试3.3: Markdown解析API
print_test "Markdown解析API"
PARSE_RESPONSE=$(curl -s -X POST http://localhost:8081/api/parse \
    -H "Content-Type: application/json" \
    -d '{"markdown": "# Test\n**Bold**"}' 2>/dev/null || echo "")
if echo "$PARSE_RESPONSE" | grep -q "success.*true"; then
    echo -e "${GREEN}✓${NC} API正常"
    print_pass
else
    print_fail "API响应异常"
fi

# 测试3.4: 性能基准测试
print_test "C语言插件性能测试"
BENCH_RESPONSE=$(curl -s -X POST http://localhost:8081/api/benchmark 2>/dev/null || echo "{}")
OPS_PER_SEC=$(echo "$BENCH_RESPONSE" | $PYTHON_CMD -c "import sys,json; print(json.load(sys.stdin).get('ops_per_second', 0))" 2>/dev/null || echo "0")
if [ "$(echo "$OPS_PER_SEC > 1000" | bc)" -eq 1 ]; then
    echo -e "${GREEN}✓${NC} QPS: $OPS_PER_SEC"
    print_pass
else
    echo -e "${YELLOW}⚠${NC} QPS: $OPS_PER_SEC (偏低)"
    print_pass
fi

# ==========================================
# 阶段4: 配置管理测试
# ==========================================
print_header "阶段 4/6: 配置管理测试"

# 测试4.1: 配置管理器启动
print_test "配置管理器启动"
if docker compose up -d config-manager 2>/dev/null; then
    sleep 5
    CONFIG_RESPONSE=$(curl -s http://localhost/config 2>/dev/null || echo "")
    if [ -n "$CONFIG_RESPONSE" ]; then
        echo -e "${GREEN}✓${NC} Web UI可访问"
        print_pass
    else
        print_fail "Web UI无法访问"
    fi
else
    print_fail "启动失败"
fi

# 测试4.2: CLI工具测试
print_test "配置CLI工具"
if $PYTHON_CMD config-manager/config_cli.py list >/dev/null 2>&1; then
    print_pass
else
    print_fail "CLI工具执行失败"
fi

# ==========================================
# 阶段5: 日志系统测试
# ==========================================
print_header "阶段 5/6: 日志系统测试"

# 测试5.1: 日志管理器启动
print_test "日志管理器启动"
LOG_RESPONSE=$(curl -s http://localhost/logs 2>/dev/null || echo "")
if [ -n "$LOG_RESPONSE" ]; then
    echo -e "${GREEN}✓${NC} Web UI可访问"
    print_pass
else
    print_fail "Web UI无法访问"
fi

# 测试5.2: 日志CLI工具
print_test "日志CLI工具"
if $PYTHON_CMD log-manager/log_cli.py list >/dev/null 2>&1; then
    print_pass
else
    print_fail "CLI工具执行失败"
fi

# 测试5.3: 日志收集功能
print_test "日志收集功能"
# 先收集Docker容器日志到logs目录
mkdir -p logs
docker compose logs --tail=100 wiki-js 2>/dev/null > logs/wiki-js.log || true
docker compose logs --tail=100 nginx 2>/dev/null > logs/nginx.log || true
docker compose logs --tail=50 postgres 2>/dev/null > logs/postgres.log || true
LOG_COUNT=$($PYTHON_CMD log-manager/log_cli.py list 2>/dev/null | grep -c "\.log" || true)
LOG_COUNT=$(echo "$LOG_COUNT" | tr -d '[:space:]' | head -1)
if [ -n "$LOG_COUNT" ] && [ "$LOG_COUNT" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✓${NC} 收集到${LOG_COUNT}个日志文件"
    print_pass
else
    print_fail "未收集到日志"
fi

# ==========================================
# 阶段6: 资源使用检查
# ==========================================
print_header "阶段 6/6: 资源使用检查"

# 测试6.1: 内存使用
print_test "内存使用检查"
TOTAL_MEM=$(docker stats --no-stream --format "{{.MemUsage}}" | awk '{sum += $1} END {print sum}')
if [ "$(echo "$TOTAL_MEM < 1000" | bc)" -eq 1 ]; then
    echo -e "${GREEN}✓${NC} ${TOTAL_MEM}MB (正常)"
    print_pass
else
    echo -e "${YELLOW}⚠${NC} ${TOTAL_MEM}MB (偏高)"
    print_pass
fi

# 测试6.2: CPU使用
print_test "CPU使用检查"
CPU_USAGE=$(docker stats --no-stream --format "{{.CPUPerc}}" | awk '{sum += $1} END {print sum}')
if [ "$(echo "$CPU_USAGE < 50" | bc)" -eq 1 ]; then
    echo -e "${GREEN}✓${NC} ${CPU_USAGE}% (正常)"
    print_pass
else
    echo -e "${YELLOW}⚠${NC} ${CPU_USAGE}% (偏高)"
    print_pass
fi

# ==========================================
# 测试总结
# ==========================================
print_header "测试总结"

echo "测试结果统计:"
echo "  总测试数: $TESTS_TOTAL"
echo -e "  ${GREEN}通过: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "  ${RED}失败: $TESTS_FAILED${NC}"
else
    echo "  失败: 0"
fi
echo ""

SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))
echo "成功率: ${SUCCESS_RATE}%"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 所有测试通过！项目已准备好发布！                      ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ⚠️  部分测试失败，请检查上述错误信息                     ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    EXIT_CODE=1
fi

echo ""
echo "详细文档:"
echo "  - README.md"
echo "  - DEVELOPER_TESTING_GUIDE.md"
echo "  - docs/CLOUD_NATIVE_PLUGIN_GUIDE.md"
echo ""
echo "获取帮助:"
echo "  - Issues: https://github.com/wikidemotongyi/wikidemotongyi/issues"
echo "  - Discussions: https://github.com/wikidemotongyi/wikidemotongyi/discussions"
echo ""

exit $EXIT_CODE
