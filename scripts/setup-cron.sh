#!/bin/bash

# ==========================================
# 设置定时备份任务
# ==========================================

echo "=========================================="
echo "  设置Wiki.js定时备份任务"
echo "=========================================="
echo ""

# 获取脚本绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup.sh"

# 检查脚本是否存在
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "错误: 找不到 backup.sh 脚本"
    exit 1
fi

# 添加执行权限
chmod +x "$BACKUP_SCRIPT"

echo "选择备份频率:"
echo "1. 每天凌晨2点备份"
echo "2. 每6小时备份一次"
echo "3. 每周日凌晨3点备份"
echo "4. 自定义"
echo ""

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 2 * * *"
        echo "已选择: 每天凌晨2点备份"
        ;;
    2)
        CRON_SCHEDULE="0 */6 * * *"
        echo "已选择: 每6小时备份一次"
        ;;
    3)
        CRON_SCHEDULE="0 3 * * 0"
        echo "已选择: 每周日凌晨3点备份"
        ;;
    4)
        echo "请输入cron表达式 (例如: 0 2 * * *)"
        read -p "> " CRON_SCHEDULE
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "即将添加以下定时任务:"
echo "$CRON_SCHEDULE $BACKUP_SCRIPT >> $SCRIPT_DIR/../logs/backup.log 2>&1"
echo ""

read -p "确认添加? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    # 添加到crontab
    (crontab -l 2>/dev/null | grep -v "backup.sh"; echo "$CRON_SCHEDULE $BACKUP_SCRIPT >> $SCRIPT_DIR/../logs/backup.log 2>&1") | crontab -

    echo ""
    echo "✓ 定时任务已添加"
    echo ""
    echo "查看定时任务: crontab -l"
    echo "删除定时任务: crontab -e (手动删除对应行)"
else
    echo "已取消"
fi
