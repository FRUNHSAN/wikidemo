#!/usr/bin/env python3
"""
Wiki.js 插件市场管理器

功能：
- 插件安装/卸载
- 版本管理
- 依赖检查
- 插件列表和搜索

使用方法：
    python plugin_marketplace.py install rss-reader
    python plugin_marketplace.py uninstall rss-reader
    python plugin_marketplace.py list
    python plugin_marketplace.py search ai
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class PluginMarketplace:
    """插件市场管理器"""
    
    def __init__(self, registry_path: str = "plugins/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
        self.compose_file = Path("docker-compose.yml")
    
    def _load_registry(self) -> Dict:
        """加载插件注册表"""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {self.registry_path}")
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_registry(self):
        """保存插件注册表"""
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def list_plugins(self, category: Optional[str] = None, status: Optional[str] = None):
        """列出所有插件"""
        plugins = self.registry.get('plugins', [])
        
        if category:
            plugins = [p for p in plugins if p.get('category') == category]
        
        if status:
            plugins = [p for p in plugins if p.get('status') == status]
        
        print(f"\n{'='*80}")
        print(f"插件列表 (共 {len(plugins)} 个)")
        print(f"{'='*80}\n")
        
        for plugin in plugins:
            status_icon = "✅" if plugin.get('status') == 'official' else "🔧"
            print(f"{status_icon} {plugin['id']} v{plugin['version']}")
            print(f"   名称: {plugin['name']}")
            print(f"   描述: {plugin['description']}")
            print(f"   作者: {plugin['author']}")
            print(f"   分类: {plugin['category']}")
            print(f"   标签: {', '.join(plugin.get('tags', []))}")
            print(f"   状态: {plugin.get('status', 'unknown')}")
            if plugin.get('repository'):
                print(f"   仓库: {plugin['repository']}")
            print()
    
    def search_plugins(self, keyword: str):
        """搜索插件"""
        plugins = self.registry.get('plugins', [])
        keyword_lower = keyword.lower()
        
        results = []
        for plugin in plugins:
            # 在ID、名称、描述、标签中搜索
            if (keyword_lower in plugin['id'].lower() or
                keyword_lower in plugin['name'].lower() or
                keyword_lower in plugin['description'].lower() or
                any(keyword_lower in tag.lower() for tag in plugin.get('tags', []))):
                results.append(plugin)
        
        print(f"\n搜索结果: '{keyword}' (找到 {len(results)} 个)\n")
        self._print_plugins(results)
    
    def install_plugin(self, plugin_id: str):
        """安装插件"""
        plugin = self._find_plugin(plugin_id)
        if not plugin:
            print(f"❌ 未找到插件: {plugin_id}")
            return False
        
        print(f"📦 正在安装插件: {plugin['name']} v{plugin['version']}")
        
        # 检查依赖
        if not self._check_dependencies(plugin):
            print("❌ 依赖检查失败")
            return False
        
        # 拉取Docker镜像
        if plugin.get('image'):
            print(f"⬇️  拉取镜像: {plugin['image']}")
            try:
                subprocess.run(
                    ['docker', 'pull', plugin['image']],
                    check=True,
                    capture_output=True
                )
                print("✅ 镜像拉取成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ 镜像拉取失败: {e.stderr.decode()}")
                return False
        
        # 添加到docker-compose
        self._add_to_compose(plugin)
        
        print(f"✅ 插件 {plugin['name']} 安装成功")
        print(f"💡 运行 'docker compose up -d {plugin_id}' 启动插件")
        return True
    
    def uninstall_plugin(self, plugin_id: str):
        """卸载插件"""
        plugin = self._find_plugin(plugin_id)
        if not plugin:
            print(f"❌ 未找到插件: {plugin_id}")
            return False
        
        print(f"🗑️  正在卸载插件: {plugin['name']}")
        
        # 停止容器
        try:
            subprocess.run(
                ['docker', 'compose', 'stop', plugin_id],
                check=False,
                capture_output=True
            )
        except Exception:
            pass
        
        # 从docker-compose移除
        self._remove_from_compose(plugin_id)
        
        print(f"✅ 插件 {plugin['name']} 已卸载")
        return True
    
    def update_plugin(self, plugin_id: str):
        """更新插件"""
        plugin = self._find_plugin(plugin_id)
        if not plugin:
            print(f"❌ 未找到插件: {plugin_id}")
            return False
        
        if not plugin.get('image'):
            print("❌ 插件没有Docker镜像，无法自动更新")
            return False
        
        print(f"⬆️  正在更新插件: {plugin['name']}")
        
        # 拉取最新镜像
        try:
            subprocess.run(
                ['docker', 'pull', plugin['image']],
                check=True,
                capture_output=True
            )
            print("✅ 镜像更新成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 镜像更新失败: {e.stderr.decode()}")
            return False
        
        # 重启容器
        try:
            subprocess.run(
                ['docker', 'compose', 'up', '-d', plugin_id],
                check=True,
                capture_output=True
            )
            print("✅ 插件重启成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 插件重启失败: {e.stderr.decode()}")
            return False
        
        return True
    
    def show_plugin_info(self, plugin_id: str):
        """显示插件详细信息"""
        plugin = self._find_plugin(plugin_id)
        if not plugin:
            print(f"❌ 未找到插件: {plugin_id}")
            return
        
        print(f"\n{'='*80}")
        print(f"插件详情: {plugin['name']}")
        print(f"{'='*80}\n")
        print(f"ID: {plugin['id']}")
        print(f"版本: {plugin['version']}")
        print(f"描述: {plugin['description']}")
        print(f"作者: {plugin['author']}")
        print(f"分类: {plugin['category']}")
        print(f"状态: {plugin.get('status', 'unknown')}")
        print(f"最低Wiki版本: {plugin.get('min_wiki_version', 'N/A')}")
        
        if plugin.get('repository'):
            print(f"仓库: {plugin['repository']}")
        
        if plugin.get('tags'):
            print(f"标签: {', '.join(plugin['tags'])}")
        
        if plugin.get('environment_vars'):
            print(f"\n环境变量:")
            for var in plugin['environment_vars']:
                required = "必需" if var.get('required') else "可选"
                print(f"  - {var['name']} ({required}): {var.get('description', '')}")
        
        if plugin.get('resources'):
            print(f"\n资源限制:")
            print(f"  CPU: {plugin['resources'].get('cpu_limit', 'N/A')}")
            print(f"  内存: {plugin['resources'].get('memory_limit', 'N/A')}")
        
        print()
    
    def _find_plugin(self, plugin_id: str) -> Optional[Dict]:
        """查找插件"""
        for plugin in self.registry.get('plugins', []):
            if plugin['id'] == plugin_id:
                return plugin
        return None
    
    def _check_dependencies(self, plugin: Dict) -> bool:
        """检查插件依赖"""
        # TODO: 实现依赖检查逻辑
        return True
    
    def _add_to_compose(self, plugin: Dict):
        """添加插件到docker-compose"""
        # TODO: 实现自动添加到docker-compose.yml
        print("⚠️  请手动将插件添加到 docker-compose.yml")
    
    def _remove_from_compose(self, plugin_id: str):
        """从docker-compose移除插件"""
        # TODO: 实现从docker-compose.yml移除
        print("⚠️  请手动从 docker-compose.yml 移除插件")
    
    def _print_plugins(self, plugins: List[Dict]):
        """打印插件列表"""
        for plugin in plugins:
            status_icon = "✅" if plugin.get('status') == 'official' else "🔧"
            print(f"{status_icon} {plugin['id']} v{plugin['version']} - {plugin['description']}")


def main():
    """主函数"""
    marketplace = PluginMarketplace()
    
    if len(sys.argv) < 2:
        print("用法: python plugin_marketplace.py <command> [args]")
        print("\n可用命令:")
        print("  list [category] [status]  - 列出插件")
        print("  search <keyword>          - 搜索插件")
        print("  install <plugin-id>       - 安装插件")
        print("  uninstall <plugin-id>     - 卸载插件")
        print("  update <plugin-id>        - 更新插件")
        print("  info <plugin-id>          - 查看插件详情")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        category = sys.argv[2] if len(sys.argv) > 2 else None
        status = sys.argv[3] if len(sys.argv) > 3 else None
        marketplace.list_plugins(category, status)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ 请提供搜索关键词")
            sys.exit(1)
        marketplace.search_plugins(sys.argv[2])
    
    elif command == 'install':
        if len(sys.argv) < 3:
            print("❌ 请提供插件ID")
            sys.exit(1)
        marketplace.install_plugin(sys.argv[2])
    
    elif command == 'uninstall':
        if len(sys.argv) < 3:
            print("❌ 请提供插件ID")
            sys.exit(1)
        marketplace.uninstall_plugin(sys.argv[2])
    
    elif command == 'update':
        if len(sys.argv) < 3:
            print("❌ 请提供插件ID")
            sys.exit(1)
        marketplace.update_plugin(sys.argv[2])
    
    elif command == 'info':
        if len(sys.argv) < 3:
            print("❌ 请提供插件ID")
            sys.exit(1)
        marketplace.show_plugin_info(sys.argv[2])
    
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
