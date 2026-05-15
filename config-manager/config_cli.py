#!/usr/bin/env python3
"""
增强型CLI配置工具
提供交互式配置管理界面
"""

import sys
import os

# 设置UTF-8输出编码（解决Windows下GBK编码问题）
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config_engine import get_config_engine
from typing import List
import json


class ConfigCLI:
    """配置CLI交互器"""

    def __init__(self):
        self.engine = get_config_engine()
        self.commands = {
            'list': self.cmd_list,
            'get': self.cmd_get,
            'set': self.cmd_set,
            'reset': self.cmd_reset,
            'history': self.cmd_history,
            'export': self.cmd_export,
            'import': self.cmd_import,
            'help': self.cmd_help,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
        }

    def run(self):
        """运行交互式CLI"""
        print("=" * 60)
        print("  Wiki.js 配置管理工具")
        print("=" * 60)
        print()
        print("输入 'help' 查看帮助，'quit' 退出")
        print()

        while True:
            try:
                command = input("config> ").strip()

                if not command:
                    continue

                # 解析命令
                parts = command.split()
                cmd_name = parts[0].lower()
                args = parts[1:]

                if cmd_name in self.commands:
                    self.commands[cmd_name](args)
                else:
                    print(f"未知命令: {cmd_name}")
                    print("输入 'help' 查看可用命令")

            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")

    def cmd_list(self, args: List[str]):
        """列出所有配置分组"""
        print("\n可用配置分组:")
        print("-" * 60)

        schemas = self.engine.get_all_schemas()
        for section_id, schema in schemas.items():
            current = self.engine.get_config(section_id)
            status = "✓" if current else "✗"

            print(f"\n[{section_id}] {schema.title} {status}")
            print(f"  {schema.description}")

            if current and isinstance(current, dict):
                keys = list(current.keys())[:5]
                print(f"  配置项: {', '.join(keys)}")

        print()

    def cmd_get(self, args: List[str]):
        """获取配置值"""
        if len(args) < 2:
            print("用法: get <section> <key>")
            return

        section = args[0]
        key = args[1]

        value = self.engine.get_config(section, key)

        if value is not None:
            print(f"\n{section}.{key} = {json.dumps(value, ensure_ascii=False)}")
        else:
            print(f"配置不存在: {section}.{key}")

    def cmd_set(self, args: List[str]):
        """设置配置值"""
        if len(args) < 3:
            print("用法: set <section> <key> <value>")
            print("示例: set env OPENAI_API_KEY sk-xxx")
            return

        section = args[0]
        key = args[1]
        value_str = ' '.join(args[2:])

        # 尝试解析值类型
        value = self._parse_value(value_str)

        success = self.engine.set_config(section, key, value)

        if success:
            print(f"✓ 配置已更新: {section}.{key} = {value}")
        else:
            print(f"✗ 配置更新失败，请检查值是否正确")

    def cmd_reset(self, args: List[str]):
        """重置配置"""
        if len(args) < 2:
            print("用法: reset <section> <key>")
            return

        section = args[0]
        key = args[1]

        success = self.engine.reset_config(section, key)

        if success:
            print(f"✓ 配置已重置: {section}.{key}")
        else:
            print(f"✗ 重置失败")

    def cmd_history(self, args: List[str]):
        """查看配置历史"""
        limit = int(args[0]) if args else 20

        history = self.engine.get_history(limit)

        if not history:
            print("暂无历史记录")
            return

        print(f"\n最近 {len(history)} 条配置变更:")
        print("-" * 60)

        for change in reversed(history):
            print(f"[{change['timestamp']}]")
            print(f"  {change['section']}.{change['key']}")
            print(f"  {change['old_value']} → {change['new_value']}")
            print()

    def cmd_export(self, args: List[str]):
        """导出配置"""
        format = args[0] if args else 'json'
        output_file = args[1] if len(args) > 1 else f'config-export.{format}'

        try:
            data = self.engine.export_config(format)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(data)

            print(f"✓ 配置已导出到: {output_file}")

        except Exception as e:
            print(f"✗ 导出失败: {e}")

    def cmd_import(self, args: List[str]):
        """导入配置"""
        if not args:
            print("用法: import <file>")
            return

        input_file = args[0]

        if not os.path.exists(input_file):
            print(f"文件不存在: {input_file}")
            return

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = f.read()

            format = 'yaml' if input_file.endswith('.yml') or input_file.endswith('.yaml') else 'json'
            success = self.engine.import_config(data, format)

            if success:
                print(f"✓ 配置已导入: {input_file}")
            else:
                print(f"✗ 导入失败")

        except Exception as e:
            print(f"✗ 导入失败: {e}")

    def cmd_help(self, args: List[str]):
        """显示帮助"""
        print("\n可用命令:")
        print("-" * 60)
        print("  list                  - 列出所有配置分组")
        print("  get <section> <key>   - 获取配置值")
        print("  set <s> <k> <value>   - 设置配置值")
        print("  reset <section> <key> - 重置为默认值")
        print("  history [n]           - 查看变更历史")
        print("  export [fmt] [file]   - 导出配置 (json/yaml)")
        print("  import <file>         - 导入配置")
        print("  help                  - 显示此帮助")
        print("  quit/exit             - 退出")
        print()
        print("示例:")
        print("  set env OPENAI_API_KEY sk-xxx")
        print("  get plugins rss-reader.enabled")
        print("  export json backup.json")
        print()

    def cmd_quit(self, args: List[str]):
        """退出"""
        print("再见！")
        sys.exit(0)

    def _parse_value(self, value_str: str):
        """解析字符串值为适当类型"""
        # 布尔值
        if value_str.lower() in ['true', 'yes', 'on']:
            return True
        if value_str.lower() in ['false', 'no', 'off']:
            return False

        # 数字
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # JSON数组
        if value_str.startswith('[') and value_str.endswith(']'):
            try:
                import json
                return json.loads(value_str)
            except:
                pass

        # 字符串
        return value_str.strip('"').strip("'")


def main():
    """主函数"""
    cli = ConfigCLI()
    
    # 支持命令行参数直接执行命令
    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = sys.argv[2:]
        if command in cli.commands:
            try:
                cli.commands[command](args)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            sys.exit(1)
    else:
        cli.run()


if __name__ == '__main__':
    main()
