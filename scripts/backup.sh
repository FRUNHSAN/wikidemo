#!/bin/bash

# ==========================================
# Wiki.js 自动备份脚本
# 支持本地备份 + Git同步 + 云存储（可选）
# ==========================================

set -e

# 配置变量
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
COMPRESS_BACKUP="${COMPRESS_BACKUP:-true}"
GIT_BACKUP_ENABLED="${GIT_BACKUP_ENABLED:-false}"
CLOUD_STORAGE_ENABLED="${CLOUD_STORAGE_ENABLED:-false}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 创建备份目录
create_backup_dir() {
    log_step "创建备份目录..."
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$BACKUP_DIR/database"
    mkdir -p "$BACKUP_DIR/files"
    mkdir -p "$BACKUP_DIR/config"
}

# 备份数据库
backup_database() {
    log_step "备份PostgreSQL数据库..."

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local db_backup_file="$BACKUP_DIR/database/wiki_db_${timestamp}.sql"

    docker compose exec -T db pg_dump -U ${POSTGRES_USER:-wikiuser} ${POSTGRES_DB:-wikidb} > "$db_backup_file"

    if [ $? -eq 0 ]; then
        log_info "✓ 数据库备份完成: $db_backup_file"

        # 压缩备份
        if [ "$COMPRESS_BACKUP" = "true" ]; then
            gzip "$db_backup_file"
            log_info "✓ 数据库备份已压缩: ${db_backup_file}.gz"
        fi
    else
        log_error "✗ 数据库备份失败"
        return 1
    fi
}

# 备份Wiki文件
backup_files() {
    log_step "备份Wiki文件和数据..."

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local files_backup_dir="$BACKUP_DIR/files/wiki_files_${timestamp}"

    mkdir -p "$files_backup_dir"

    # 复制Docker卷数据
    docker cp wiki-js:/wiki/data "$files_backup_dir/data" 2>/dev/null || true
    docker cp wiki-js:/wiki/assets "$files_backup_dir/assets" 2>/dev/null || true

    if [ $? -eq 0 ]; then
        log_info "✓ Wiki文件备份完成: $files_backup_dir"

        # 压缩备份
        if [ "$COMPRESS_BACKUP" = "true" ]; then
            tar -czf "${files_backup_dir}.tar.gz" -C "$BACKUP_DIR/files" "wiki_files_${timestamp}"
            rm -rf "$files_backup_dir"
            log_info "✓ Wiki文件备份已压缩: ${files_backup_dir}.tar.gz"
        fi
    else
        log_warn "⚠ Wiki文件备份部分失败（可能为空）"
    fi
}

# 备份配置文件
backup_config() {
    log_step "备份配置文件..."

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local config_backup_dir="$BACKUP_DIR/config/wiki_config_${timestamp}"

    mkdir -p "$config_backup_dir"

    # 复制配置文件
    cp docker-compose.yml "$config_backup_dir/" 2>/dev/null || true
    cp .env "$config_backup_dir/" 2>/dev/null || true
    cp -r nginx "$config_backup_dir/" 2>/dev/null || true

    if [ $? -eq 0 ]; then
        log_info "✓ 配置文件备份完成: $config_backup_dir"
    else
        log_warn "⚠ 配置文件备份部分失败"
    fi
}

# Git同步备份
git_backup() {
    if [ "$GIT_BACKUP_ENABLED" != "true" ]; then
        return 0
    fi

    log_step "同步备份到Git仓库..."

    cd "$BACKUP_DIR"

    # 初始化Git仓库（如果不存在）
    if [ ! -d ".git" ]; then
        git init
        git remote add origin ${GIT_REPO_URL}
    fi

    # 添加并提交
    git add .
    git commit -m "Auto backup: $(date '+%Y-%m-%d %H:%M:%S')" || true

    # 推送到远程
    git push origin main || git push origin master || log_warn "⚠ Git推送失败"

    cd - > /dev/null

    log_info "✓ Git同步完成"
}

# 清理旧备份
cleanup_old_backups() {
    log_step "清理${RETENTION_DAYS}天前的旧备份..."

    find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "$BACKUP_DIR" -type d -empty -delete 2>/dev/null || true

    log_info "✓ 旧备份清理完成"
}

# 显示备份统计
show_backup_stats() {
    log_step "备份统计信息:"

    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    local backup_count=$(find "$BACKUP_DIR" -type f | wc -l)
    local db_backups=$(find "$BACKUP_DIR/database" -type f 2>/dev/null | wc -l)
    local file_backups=$(find "$BACKUP_DIR/files" -type f 2>/dev/null | wc -l)

    echo "  总大小: $total_size"
    echo "  备份文件数: $backup_count"
    echo "  数据库备份: $db_backups"
    echo "  文件备份: $file_backups"
}

# 主函数
main() {
    log_info "=========================================="
    log_info "  Wiki.js 自动备份开始"
    log_info "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "=========================================="

    # 检查Docker是否运行
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker未运行，请先启动Docker"
        exit 1
    fi

    create_backup_dir
    backup_database
    backup_files
    backup_config
    git_backup
    cleanup_old_backups
    show_backup_stats

    log_info "=========================================="
    log_info "  ✓ 备份完成！"
    log_info "  备份位置: $BACKUP_DIR"
    log_info "=========================================="
}

# 执行主函数
main "$@"
