#!/usr/bin/env python3
"""
日志管理CLI工具
提供命令行日志查看和管理功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from log_manager import get_log_manager
import json


class LogCLI:
    """日志CLI交互器"""

    def __init__(self):
        self.manager = get_log_manager()

    def run(self, args):
        """运行CLI命令"""
        if not args:
            self.show_help()
            return

        command = args[0]

        commands = {
            'list': self.cmd_list,
            'view': self.cmd_view,
            'tail': self.cmd_tail,
            'search': self.cmd_search,
            'stats': self.cmd_stats,
            'rotate': self.cmd_rotate,
            'cleanup': self.cmd_cleanup,
            'help': self.cmd_help,
        }

        if command in commands:
            commands[command](args[1:])
        else:
            print(f"未知命令: {command}")
            print("使用 'log help' 查看帮助")

    def cmd_list(self, args):
        """列出日志文件"""
        files = self.manager.get_log_files()

        if not files:
            print("暂无日志文件")
            return

        print(f"\n找到 {len(files)} 个日志文件:\n")
        print(f"{'文件名':<40} {'大小':<12} {'行数':<10} {'更新时间'}")
        print("-" * 100)

        for f in files:
            print(f"{f.filename:<40} {f.size_human:<12} {f.line_count:<10} {f.modified_at[:19]}")

        print()

    def cmd_view(self, args):
        """查看日志内容"""
        if not args:
            print("用法: log view <filename> [lines] [offset]")
            return

        filename = args[0]
        lines = int(args[1]) if len(args) > 1 else 100
        offset = int(args[2]) if len(args) > 2 else 0

        result = self.manager.read_log(filename, lines=lines, offset=offset)

        if result['success']:
            print(f"\n--- {filename} (显示 {result['returned_lines']}/{result['total_lines']} 行) ---\n")
            for line in result['lines']:
                print(line, end='')
            print()

            if result['has_more']:
                print(f"\n... 还有更多行，使用 offset={offset + lines} 继续查看 ...")
        else:
            print(f"错误: {result['error']}")

    def cmd_tail(self, args):
        """查看日志末尾"""
        if not args:
            print("用法: log tail <filename> [lines]")
            return

        filename = args[0]
        lines = int(args[1]) if len(args) > 1 else 50

        result = self.manager.tail_log(filename, lines=lines)

        if result['success']:
            print(f"\n--- {filename} (最后 {len(result['lines'])} 行) ---\n")
            for line in result['lines']:
                print(line, end='')
            print()
        else:
            print(f"错误: {result['error']}")

    def cmd_search(self, args):
        """搜索日志"""
        if not args:
            print("用法: log search <keyword> [max_results]")
            return

        keyword = args[0]
        max_results = int(args[1]) if len(args) > 1 else 50

        print(f"\n搜索关键词: '{keyword}'\n")
        results = self.manager.search_logs(keyword, max_results=max_results)

        if results:
            print(f"找到 {len(results)} 条结果:\n")
            for r in results:
                print(f"[{r['filename']}] 第 {r['line_num']} 行:")
                print(f"  {r['content'][:200]}")
                print()
        else:
            print("未找到匹配结果")

        print()

    def cmd_stats(self, args):
        """查看日志统计"""
        stats = self.manager.get_log_stats()

        print("\n=== 日志统计 ===\n")
        print(f"当前日志:")
        print(f"  文件数: {stats['current_logs']['count']}")
        print(f"  总大小: {stats['current_logs']['total_size']}")
        print()
        print(f"归档日志:")
        print(f"  文件数: {stats['archived_logs']['count']}")
        print(f"  总大小: {stats['archived_logs']['total_size']}")
        print()
        print(f"总计: {stats['total_size']}")
        print()

    def cmd_rotate(self, args):
        """轮转日志"""
        dry_run = '--dry-run' in args or '-n' in args

        print(f"\n{'预览' if dry_run else '执行'}日志轮转...\n")
        result = self.manager.rotate_logs(dry_run=dry_run)

        if result['rotated']:
            print(f"轮转的文件:")
            for r in result['rotated']:
                print(f"  ✓ {r['filename']} -> {r['archive_name']} ({r['size']})")
        else:
            print("没有需要轮转的文件")

        if result['skipped']:
            print(f"\n跳过的文件:")
            for s in result['skipped']:
                print(f"  - {s}")

        print()

    def cmd_cleanup(self, args):
        """清理旧日志"""
        days = 30
        dry_run = False

        i = 0
        while i < len(args):
            if args[i].isdigit():
                days = int(args[i])
            elif args[i] in ['--dry-run', '-n']:
                dry_run = True
            i += 1

        print(f"\n{'预览' if dry_run else '执行'}清理 {days} 天前的日志...\n")
        result = self.manager.cleanup_logs(days=days, dry_run=dry_run)

        if result['deleted']:
            print(f"删除的文件:")
            for d in result['deleted']:
                print(f"  ✗ {d['filename']} ({d['size']}, {d['age_days']} 天前)")
            print(f"\n共删除 {result['count']} 个文件，释放 {result['total_size_freed']} 空间")
        else:
            print("没有需要清理的文件")

        print()

    def cmd_help(self, args):
        """显示帮助"""
        print("""
日志管理CLI工具

用法: log <command> [options]

命令:
  list                  列出所有日志文件
  view <file> [n] [off] 查看日志内容（n=行数，off=偏移）
  tail <file> [n]       查看日志末尾n行
  search <keyword> [n]  搜索日志内容
  stats                 查看日志统计
  rotate [-n]           轮转日志（-n=预览）
  cleanup <days> [-n]   清理旧日志（-n=预览）
  help                  显示此帮助

示例:
  log list
  log view app.log 50
  log tail error.log 20
  log search "ERROR" 100
  log stats
  log rotate -n
  log cleanup 30
""")

    def show_help(self):
        """显示简要帮助"""
        self.cmd_help([])


def main():
    """主函数"""
    cli = LogCLI()
    cli.run(sys.argv[1:])


if __name__ == '__main__':
    main()
