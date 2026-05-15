#!/bin/bash

# IPv6支持检查脚本

echo "======================================"
echo "  IPv6 支持检查工具"
echo "======================================"
echo ""

# 检查系统IPv6支持
echo "1. 检查系统IPv6支持"
echo "--------------------------------------"

if [ -f /proc/net/if_inet6 ]; then
    echo "✓ 系统内核支持IPv6"
    echo ""
    echo "网络接口IPv6地址:"
    ip -6 addr show 2>/dev/null | grep "inet6" || echo "  未找到IPv6地址"
else
    echo "✗ 系统可能不支持IPv6"
    echo "  请检查内核配置或联系系统管理员"
fi

echo ""

# 检查Docker IPv6支持
echo "2. 检查Docker IPv6支持"
echo "--------------------------------------"

if command -v docker &> /dev/null; then
    echo "✓ Docker已安装: $(docker --version)"
    echo ""

    if docker info 2>/dev/null | grep -q "IPv6"; then
        echo "✓ Docker支持IPv6"
        echo ""
        echo "Docker网络信息:"
        docker network ls 2>/dev/null
    else
        echo "✗ Docker可能未启用IPv6支持"
        echo ""
        echo "建议在 /etc/docker/daemon.json 中添加:"
        echo "{"
        echo '  "ipv6": true,'
        echo '  "fixed-cidr-v6": "fd00::/80"'
        echo "}"
        echo ""
        echo "然后重启Docker: sudo systemctl restart docker"
    fi
else
    echo "✗ Docker未安装"
    echo "  请先安装Docker: https://docs.docker.com/get-docker/"
fi

echo ""

# 检查端口占用
echo "3. 检查端口占用情况"
echo "--------------------------------------"

if command -v netstat &> /dev/null; then
    echo "端口80 (HTTP):"
    netstat -tlnp 2>/dev/null | grep ":80 " || echo "  端口80未被占用 ✓"
    echo ""
    echo "端口443 (HTTPS):"
    netstat -tlnp 2>/dev/null | grep ":443 " || echo "  端口443未被占用 ✓"
elif command -v ss &> /dev/null; then
    echo "端口80 (HTTP):"
    ss -tlnp 2>/dev/null | grep ":80 " || echo "  端口80未被占用 ✓"
    echo ""
    echo "端口443 (HTTPS):"
    ss -tlnp 2>/dev/null | grep ":443 " || echo "  端口443未被占用 ✓"
else
    echo "⚠ 无法检查端口（netstat和ss都不可用）"
fi

echo ""

# 测试本地IPv6连接
echo "4. 测试本地IPv6连接"
echo "--------------------------------------"

if command -v curl &> /dev/null; then
    echo "测试连接到 [::1] (localhost IPv6)..."
    if curl -g -s --connect-timeout 2 http://[::1] > /dev/null 2>&1; then
        echo "✓ 可以连接到 [::1]"
    else
        echo "✗ 无法连接到 [::1]（可能是正常的，如果服务未启动）"
    fi
else
    echo "⚠ curl未安装，跳过测试"
fi

echo ""

# 检查防火墙
echo "5. 检查防火墙状态"
echo "--------------------------------------"

if command -v ufw &> /dev/null; then
    echo "UFW防火墙状态:"
    ufw status 2>/dev/null || echo "  UFW未激活"
elif command -v firewall-cmd &> /dev/null; then
    echo "Firewalld状态:"
    firewall-cmd --state 2>/dev/null || echo "  Firewalld未运行"
else
    echo "⚠ 未检测到常见防火墙（ufw/firewalld）"
fi

echo ""
echo "======================================"
echo "  检查完成"
echo "======================================"
echo ""
echo "建议:"
echo "  1. 确保系统启用了IPv6"
echo "  2. 确保Docker配置了IPv6支持"
echo "  3. 确保防火墙允许80和443端口"
echo "  4. 运行 ./deploy.sh start 启动Wiki.js"
echo ""
