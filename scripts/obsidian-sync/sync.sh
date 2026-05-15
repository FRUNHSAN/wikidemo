#!/bin/bash

# Obsidian同步快捷脚本 - Linux/macOS版本

echo ""
echo "========================================"
echo "  Obsidian 双向同步工具"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3未安装，请先安装Python 3.8+"
    exit 1
fi

# 检查配置文件
if [ ! -f "obsidian-sync-config.json" ]; then
    echo "[WARN] 配置文件不存在，正在创建..."
    cp obsidian-sync-config.example.json obsidian-sync-config.json
    echo ""
    echo "请编辑 obsidian-sync-config.json 配置以下内容:"
    echo "  - local_folder: Obsidian仓库路径"
    echo "  - wiki_api_token: Wiki API Token"
    echo ""
    read -p "按回车继续..."
fi

# 解析命令
case "${1:-sync}" in
    sync)
        echo "[INFO] 开始同步..."
        echo ""
        python3 scripts/obsidian-sync/sync_manager.py
        echo ""
        echo "[OK] 同步完成"
        ;;
    status)
        echo "[INFO] 同步状态:"
        echo ""
        python3 scripts/obsidian-sync/sync_manager.py --status
        ;;
    conflicts)
        echo "[INFO] 待处理冲突:"
        echo ""
        python3 scripts/obsidian-sync/sync_manager.py --conflicts
        ;;
    help|--help|-h)
        echo "用法: ./sync.sh [command]"
        echo ""
        echo "命令:"
        echo "  sync        执行同步（默认）"
        echo "  status      查看同步状态"
        echo "  conflicts   查看待处理冲突"
        echo "  help        显示此帮助信息"
        echo ""
        echo "示例:"
        echo "  ./sync.sh"
        echo "  ./sync.sh status"
        echo "  ./sync.sh conflicts"
        ;;
    *)
        echo "[ERROR] 未知命令: $1"
        echo "使用 ./sync.sh help 查看帮助"
        exit 1
        ;;
esac
