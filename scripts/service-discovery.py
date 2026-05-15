#!/usr/bin/env python3
"""
Wiki.js 插件服务发现与API网关

功能：
- 自动发现运行中的插件容器
- 维护插件服务注册表
- 提供统一的API网关
- 负载均衡和健康检查

使用方法：
    python service_discovery.py start
    python service_discovery.py list
    python service_discovery.py health-check
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class ServiceDiscovery:
    """插件服务发现管理器"""
    
    def __init__(self):
        self.registry_file = Path("plugins/service_registry.json")
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """加载服务注册表"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "services": {}
        }
    
    def _save_registry(self):
        """保存服务注册表"""
        self.registry["last_updated"] = datetime.now().isoformat()
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def discover_plugins(self) -> List[Dict]:
        """通过Docker标签自动发现插件"""
        try:
            # 查询带有wiki.plugin标签的容器
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'label=wiki.plugin=true', 
                 '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                check=True
            )
            
            plugins = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    container = json.loads(line)
                    plugin_info = self._extract_plugin_info(container)
                    if plugin_info:
                        plugins.append(plugin_info)
            
            return plugins
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker命令执行失败: {e}")
            return []
    
    def _extract_plugin_info(self, container: Dict) -> Optional[Dict]:
        """从容器信息提取插件元数据"""
        labels = container.get('Labels', '')
        
        # 解析标签
        plugin_name = None
        plugin_version = None
        
        for label in labels.split(','):
            if 'wiki.plugin.name=' in label:
                plugin_name = label.split('=')[1]
            elif 'wiki.plugin.version=' in label:
                plugin_version = label.split('=')[1]
        
        if not plugin_name:
            return None
        
        return {
            "id": plugin_name,
            "name": plugin_name,
            "version": plugin_version or "unknown",
            "container_id": container.get('ID', '')[:12],
            "image": container.get('Image', ''),
            "status": container.get('State', ''),
            "ports": container.get('Ports', ''),
            "created": container.get('CreatedAt', ''),
            "discovered_at": datetime.now().isoformat()
        }
    
    def register_service(self, plugin_id: str, service_info: Dict):
        """注册插件服务"""
        self.registry["services"][plugin_id] = {
            **service_info,
            "registered_at": datetime.now().isoformat(),
            "last_health_check": None,
            "health_status": "unknown"
        }
        self._save_registry()
    
    def unregister_service(self, plugin_id: str):
        """注销插件服务"""
        if plugin_id in self.registry["services"]:
            del self.registry["services"][plugin_id]
            self._save_registry()
    
    def health_check(self, plugin_id: str) -> bool:
        """健康检查"""
        service = self.registry["services"].get(plugin_id)
        if not service:
            return False
        
        # TODO: 实现实际的健康检查逻辑
        # 例如：HTTP请求、TCP连接等
        
        service["last_health_check"] = datetime.now().isoformat()
        service["health_status"] = "healthy"
        self._save_registry()
        
        return True
    
    def list_services(self) -> List[Dict]:
        """列出所有已注册的服务"""
        services = []
        for plugin_id, info in self.registry["services"].items():
            services.append({
                "id": plugin_id,
                **info
            })
        return services
    
    def get_api_gateway_config(self) -> Dict:
        """生成API网关配置（Nginx）"""
        config = {
            "upstreams": [],
            "locations": []
        }
        
        for plugin_id, service in self.registry["services"].items():
            if service.get("health_status") == "healthy":
                # 添加upstream
                config["upstreams"].append({
                    "name": f"plugin_{plugin_id}",
                    "server": f"{plugin_id}:8080"  # 假设插件监听8080端口
                })
                
                # 添加location
                config["locations"].append({
                    "path": f"/api/plugins/{plugin_id}",
                    "proxy_pass": f"http://plugin_{plugin_id}"
                })
        
        return config
    
    def sync_with_docker(self):
        """与Docker同步服务状态"""
        print("🔄 正在同步Docker容器状态...")
        
        # 发现运行中的插件
        discovered = self.discover_plugins()
        discovered_ids = {p['id'] for p in discovered}
        
        # 注册新发现的插件
        for plugin in discovered:
            if plugin['id'] not in self.registry["services"]:
                print(f"  ➕ 发现新插件: {plugin['id']}")
                self.register_service(plugin['id'], plugin)
            else:
                # 更新现有插件状态
                self.registry["services"][plugin['id']].update({
                    "status": plugin['status'],
                    "container_id": plugin['container_id']
                })
        
        # 移除已停止的插件
        registered_ids = set(self.registry["services"].keys())
        stopped = registered_ids - discovered_ids
        for plugin_id in stopped:
            print(f"  ➖ 插件已停止: {plugin_id}")
            self.unregister_service(plugin_id)
        
        self._save_registry()
        print(f"✅ 同步完成: {len(discovered)} 个插件运行中")
    
    def start_monitoring(self, interval: int = 30):
        """启动服务监控"""
        print(f"👀 开始监控插件服务 (间隔: {interval}s)")
        
        try:
            while True:
                self.sync_with_docker()
                
                # 健康检查
                for plugin_id in list(self.registry["services"].keys()):
                    self.health_check(plugin_id)
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n⏹️  监控已停止")


def main():
    """主函数"""
    discovery = ServiceDiscovery()
    
    if len(sys.argv) < 2:
        print("用法: python service_discovery.py <command>")
        print("\n可用命令:")
        print("  start          - 启动服务监控")
        print("  sync           - 同步Docker状态")
        print("  list           - 列出服务")
        print("  health-check   - 执行健康检查")
        print("  gateway-config - 生成API网关配置")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'start':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        discovery.start_monitoring(interval)
    
    elif command == 'sync':
        discovery.sync_with_docker()
    
    elif command == 'list':
        services = discovery.list_services()
        print(f"\n已注册服务 ({len(services)} 个):\n")
        for service in services:
            status_icon = "✅" if service.get('health_status') == 'healthy' else "❓"
            print(f"{status_icon} {service['id']} v{service.get('version', '?')}")
            print(f"   状态: {service.get('status', 'unknown')}")
            print(f"   镜像: {service.get('image', 'N/A')}")
            print()
    
    elif command == 'health-check':
        services = discovery.list_services()
        for service in services:
            healthy = discovery.health_check(service['id'])
            status = "✅ healthy" if healthy else "❌ unhealthy"
            print(f"{service['id']}: {status}")
    
    elif command == 'gateway-config':
        config = discovery.get_api_gateway_config()
        print(json.dumps(config, indent=2))
    
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
