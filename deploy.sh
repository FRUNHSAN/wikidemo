#!/bin/bash

# Wiki.js 部署脚本 - 支持IPv6
# 使用方法: ./deploy.sh [start|stop|restart|logs|status]

set -e

COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="wiki-js-ipv6"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo_error "Docker未安装，请先安装Docker"
        exit 1
    fi

    if ! command -v docker compose &> /dev/null; then
        echo_error "Docker Compose未安装，请先安装Docker Compose V2"
        exit 1
    fi

    echo_info "Docker版本: $(docker --version)"
    echo_info "Docker Compose版本: $(docker compose version)"
}

# 检查IPv6支持
check_ipv6() {
    echo_info "检查系统IPv6支持..."

    if [ -f /proc/net/if_inet6 ]; then
        echo_info "系统内核支持IPv6"
    else
        echo_warn "系统可能不支持IPv6，请检查内核配置"
    fi

    # 检查Docker IPv6支持
    if docker info 2>/dev/null | grep -q "IPv6"; then
        echo_info "Docker支持IPv6"
    else
        echo_warn "Docker可能需要启用IPv6支持"
        echo_warn "请在 /etc/docker/daemon.json 中添加:"
        echo_warn '{'
        echo_warn '  "ipv6": true,'
        echo_warn '  "fixed-cidr-v6": "fd00::/80"'
        echo_warn '}'
    fi
}

# 创建必要的目录
create_dirs() {
    echo_info "创建必要的目录..."
    mkdir -p nginx/conf.d
    mkdir -p data/postgres
    mkdir -p data/wiki
    mkdir -p logs/nginx
}

# 启动服务
start() {
    echo_info "启动Wiki.js服务（支持IPv6）..."

    # 检查.env文件
    if [ ! -f .env ]; then
        echo_warn ".env文件不存在，使用默认配置"
        echo_warn "建议复制 .env.example 为 .env 并修改配置"
    fi

    docker compose -p $PROJECT_NAME up -d

    echo_info "等待服务启动..."
    sleep 5

    # 检查服务状态
    docker compose -p $PROJECT_NAME ps

    echo_info ""
    echo_info "=========================================="
    echo_info "Wiki.js 部署完成！"
    echo_info "=========================================="
    echo_info "访问地址:"
    echo_info "  - IPv4: http://localhost"
    echo_info "  - IPv6: http://[::1]"
    echo_info ""
    echo_info "初始管理员账号:"
    echo_info "  - 邮箱: admin@example.com"
    echo_info "  - 密码: changeme123"
    echo_info ""
    echo_info "请尽快登录并修改密码！"
    echo_info "=========================================="
}

# 停止服务
stop() {
    echo_info "停止Wiki.js服务..."
    docker compose -p $PROJECT_NAME down
    echo_info "服务已停止"
}

# 重启服务
restart() {
    echo_info "重启Wiki.js服务..."
    stop
    sleep 2
    start
}

# 查看日志
logs() {
    echo_info "查看服务日志..."
    docker compose -p $PROJECT_NAME logs -f ${1:-}
}

# 查看状态
status() {
    echo_info "服务状态:"
    docker compose -p $PROJECT_NAME ps
    echo_info ""
    echo_info "网络信息:"
    docker network inspect ${PROJECT_NAME}_wiki-network 2>/dev/null | grep -A 5 "IPv6" || echo "无法获取网络信息"
}

# 备份数据
backup() {
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    echo_info "备份数据到 $BACKUP_DIR ..."

    mkdir -p $BACKUP_DIR

    # 备份数据库
    docker compose -p $PROJECT_NAME exec -T db pg_dump -U wikiuser wikidb > "$BACKUP_DIR/database.sql"

    # 备份配置文件
    cp docker-compose.yml $BACKUP_DIR/
    cp -r nginx $BACKUP_DIR/ 2>/dev/null || true

    echo_info "备份完成: $BACKUP_DIR"
}

# 恢复数据
restore() {
    if [ -z "$1" ]; then
        echo_error "请指定备份目录"
        echo_info "可用的备份:"
        ls -d backups/*/ 2>/dev/null || echo "没有可用的备份"
        exit 1
    fi

    BACKUP_DIR="$1"
    echo_info "从 $BACKUP_DIR 恢复数据..."

    if [ ! -f "$BACKUP_DIR/database.sql" ]; then
        echo_error "备份文件不存在: $BACKUP_DIR/database.sql"
        exit 1
    fi

    # 恢复数据库
    cat "$BACKUP_DIR/database.sql" | docker compose -p $PROJECT_NAME exec -T db psql -U wikiuser wikidb

    echo_info "数据恢复完成，请重启服务"
}

# 显示帮助
show_help() {
    echo "Wiki.js IPv6 部署脚本"
    echo ""
    echo "使用方法: $0 [command]"
    echo ""
    echo "命令:"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  logs        查看日志 (可指定服务名: wiki, nginx, db)"
    echo "  status      查看服务状态"
    echo "  backup      备份数据"
    echo "  restore     恢复数据 (需指定备份目录)"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start"
    echo "  $0 logs wiki"
    echo "  $0 backup"
    echo "  $0 restore backups/20260514_120000"
}

# 主函数
main() {
    check_docker

    case "${1:-start}" in
        start)
            create_dirs
            check_ipv6
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs "$2"
            ;;
        status)
            status
            ;;
        backup)
            backup
            ;;
        restore)
            restore "$2"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
