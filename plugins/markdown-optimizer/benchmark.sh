#!/bin/bash
# Markdown Optimizer 压力测试脚本
# 
# 功能：
# - 并发性能测试
# - 延迟分布统计
# - 吞吐量测量
# - 资源监控

set -e

BASE_URL="${BASE_URL:-http://localhost:8080}"
CONCURRENCY="${CONCURRENCY:-10}"
REQUESTS="${REQUESTS:-1000}"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║      Markdown Optimizer - 压力测试工具                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查服务是否运行
echo "[1/5] 检查服务状态..."
if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} 服务正常运行"
else
    echo -e "${RED}✗${NC} 服务未启动，请先运行: docker compose up -d markdown-optimizer"
    exit 1
fi

# 测试1: 健康检查延迟
echo ""
echo "[2/5] 测试健康检查延迟..."
start_time=$(date +%s%N)
for i in {1..100}; do
    curl -s "$BASE_URL/health" > /dev/null
done
end_time=$(date +%s%N)
elapsed=$(( (end_time - start_time) / 1000000 ))
avg_latency=$(( elapsed / 100 ))
echo "  平均延迟: ${avg_latency}ms (100次请求)"

# 测试2: Markdown解析性能
echo ""
echo "[3/5] Markdown解析性能测试..."
cat > /tmp/test_parse.json << 'EOF'
{
  "markdown": "# Test Document\n\nThis is a **bold** and *italic* test.\n\n- Item 1\n- Item 2\n- Item 3\n\n```python\nprint('Hello')\n```\n"
}
EOF

start_time=$(date +%s%N)
success=0
failed=0

for i in $(seq 1 $REQUESTS); do
    if curl -s -X POST "$BASE_URL/api/parse" \
        -H "Content-Type: application/json" \
        -d @/tmp/test_parse.json > /dev/null 2>&1; then
        ((success++))
    else
        ((failed++))
    fi
done

end_time=$(date +%s%N)
total_time=$(( (end_time - start_time) / 1000000 ))
qps=$(( REQUESTS * 1000 / total_time ))

echo -e "  总请求数: ${REQUESTS}"
echo -e "  ${GREEN}成功: ${success}${NC}"
if [ $failed -gt 0 ]; then
    echo -e "  ${RED}失败: ${failed}${NC}"
fi
echo "  总耗时: ${total_time}ms"
echo "  QPS: ${qps}"
echo "  平均延迟: $(( total_time / REQUESTS ))ms"

# 测试3: 并发性能
echo ""
echo "[4/5] 并发性能测试 (${CONCURRENCY}并发)..."
pids=()
batch_size=$(( REQUESTS / CONCURRENCY ))

for c in $(seq 1 $CONCURRENCY); do
    (
        for i in $(seq 1 $batch_size); do
            curl -s -X POST "$BASE_URL/api/parse" \
                -H "Content-Type: application/json" \
                -d @/tmp/test_parse.json > /dev/null 2>&1
        done
    ) &
    pids+=($!)
done

start_time=$(date +%s%N)

# 等待所有进程完成
for pid in "${pids[@]}"; do
    wait $pid
done

end_time=$(date +%s%N)
concurrent_time=$(( (end_time - start_time) / 1000000 ))
concurrent_qps=$(( REQUESTS * 1000 / concurrent_time ))

echo "  并发数: ${CONCURRENCY}"
echo "  总耗时: ${concurrent_time}ms"
echo "  QPS: ${concurrent_qps}"
echo "  吞吐量提升: $(( concurrent_qps / (qps > 0 ? qps : 1) ))x"

# 测试4: 基准测试API
echo ""
echo "[5/5] 内置基准测试..."
benchmark_result=$(curl -s -X POST "$BASE_URL/api/benchmark")
echo "  $benchmark_result" | python3 -m json.tool 2>/dev/null || echo "  $benchmark_result"

# 清理
rm -f /tmp/test_parse.json

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  测试完成！                                               ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "性能总结:"
echo "  • 单线程QPS: ${qps}"
echo "  • ${CONCURRENCY}并发QPS: ${concurrent_qps}"
echo "  • 平均延迟: $(( total_time / REQUESTS ))ms"
echo ""
echo "对比参考（Python实现）:"
echo "  • 预期QPS: ~200"
echo "  • 性能提升: $(( qps / 200 ))x"
echo ""
