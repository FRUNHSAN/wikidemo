"""
Wiki.js 插件管理器核心
提供插件加载、生命周期管理、API接口等功能
"""

import os
import sys
import json
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import schedule
import time
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/plugin_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('PluginManager')


class PluginMetadata:
    """插件元数据"""

    def __init__(self, config: dict):
        self.name = config.get('name', 'Unknown')
        self.version = config.get('version', '1.0.0')
        self.description = config.get('description', '')
        self.author = config.get('author', '')
        self.enabled = config.get('enabled', True)
        self.dependencies = config.get('dependencies', [])
        self.config = config.get('config', {})
        self.triggers = config.get('triggers', [])  # 触发器配置


class PluginBase:
    """插件基类 - 所有插件必须继承此类"""

    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.is_initialized = False
        self.logger = logging.getLogger(f'Plugin.{metadata.name}')

    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.on_initialize()
            self.is_initialized = True
            self.logger.info(f"插件 '{self.metadata.name}' 初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"插件 '{self.metadata.name}' 初始化失败: {e}")
            return False

    def on_initialize(self):
        """插件初始化逻辑（子类实现）"""
        pass

    def shutdown(self):
        """关闭插件"""
        try:
            self.on_shutdown()
            self.is_initialized = False
            self.logger.info(f"插件 '{self.metadata.name}' 已关闭")
        except Exception as e:
            self.logger.error(f"插件 '{self.metadata.name}' 关闭失败: {e}")

    def on_shutdown(self):
        """插件关闭逻辑（子类实现）"""
        pass

    def execute(self, **kwargs) -> Any:
        """执行插件主逻辑（子类实现）"""
        raise NotImplementedError("子类必须实现execute方法")


class TaskScheduler:
    """任务调度器 - 管理定时任务"""

    def __init__(self):
        self.tasks = {}
        self.scheduler_thread = None
        self.is_running = False

    def add_task(self, task_id: str, interval: str, func: callable, **kwargs):
        """
        添加定时任务

        Args:
            task_id: 任务ID
            interval: 时间间隔 (例如: '1h', '30m', '1d')
            func: 要执行的函数
            **kwargs: 传递给函数的参数
        """
        # 解析时间间隔
        if interval.endswith('h'):
            hours = int(interval[:-1])
            schedule.every(hours).hours.do(func, **kwargs)
        elif interval.endswith('m'):
            minutes = int(interval[:-1])
            schedule.every(minutes).minutes.do(func, **kwargs)
        elif interval.endswith('d'):
            days = int(interval[:-1])
            schedule.every(days).days.do(func, **kwargs)
        else:
            raise ValueError(f"不支持的时间间隔格式: {interval}")

        self.tasks[task_id] = {
            'interval': interval,
            'func': func,
            'last_run': None,
            'run_count': 0
        }

        logger.info(f"任务已添加: {task_id} (每{interval})")

    def remove_task(self, task_id: str):
        """移除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            schedule.clear()
            logger.info(f"任务已移除: {task_id}")

    def start(self):
        """启动调度器"""
        if self.is_running:
            return

        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("任务调度器已启动")

    def stop(self):
        """停止调度器"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("任务调度器已停止")

    def _run_scheduler(self):
        """运行调度循环"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)


class WikiAPI:
    """Wiki.js API 客户端"""

    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.session = None

    def _get_headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

    def create_page(self, path: str, title: str, content: str, tags: List[str] = None) -> dict:
        """创建页面"""
        import requests

        data = {
            'path': path,
            'title': title,
            'content': content,
            'isPublished': True
        }

        if tags:
            data['tags'] = tags

        response = requests.post(
            f'{self.api_url}/pages',
            headers=self._get_headers(),
            json=data
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"创建页面失败: {response.text}")

    def update_page(self, page_id: int, content: str) -> dict:
        """更新页面"""
        import requests

        response = requests.put(
            f'{self.api_url}/pages/{page_id}',
            headers=self._get_headers(),
            json={'content': content}
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"更新页面失败: {response.text}")

    def get_page(self, path: str) -> dict:
        """获取页面"""
        import requests

        response = requests.get(
            f'{self.api_url}/pages/path/{path}',
            headers=self._get_headers()
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取页面失败: {response.text}")

    def list_pages(self) -> List[dict]:
        """列出所有页面"""
        import requests

        response = requests.get(
            f'{self.api_url}/pages',
            headers=self._get_headers()
        )

        if response.status_code == 200:
            return response.json().get('pages', [])
        else:
            raise Exception(f"获取页面列表失败: {response.text}")


class PluginManager:
    """插件管理器 - 核心管理类"""

    def __init__(self, plugins_dir: str = './plugins', config_file: str = './plugins/plugins_config.json'):
        self.plugins_dir = Path(plugins_dir)
        self.config_file = Path(config_file)
        self.plugins: Dict[str, PluginBase] = {}
        self.metadata: Dict[str, PluginMetadata] = {}
        self.scheduler = TaskScheduler()
        self.wiki_api = None

        # 初始化Wiki API
        wiki_api_url = os.getenv('WIKI_API_URL', 'http://wiki:3000/api')
        wiki_api_token = os.getenv('WIKI_API_TOKEN', '')
        if wiki_api_token:
            self.wiki_api = WikiAPI(wiki_api_url, wiki_api_token)

    def load_config(self) -> dict:
        """加载插件配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_config(self, config: dict):
        """保存插件配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def discover_plugins(self) -> List[str]:
        """发现所有可用插件"""
        plugins = []

        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('_'):
                plugin_config = plugin_dir / 'plugin.json'
                if plugin_config.exists():
                    plugins.append(plugin_dir.name)

        return plugins

    def load_plugin(self, plugin_name: str) -> bool:
        """加载单个插件"""
        try:
            plugin_dir = self.plugins_dir / plugin_name
            plugin_config_file = plugin_dir / 'plugin.json'

            # 读取插件配置
            with open(plugin_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            metadata = PluginMetadata(config)

            # 检查是否启用
            if not metadata.enabled:
                logger.info(f"插件 '{plugin_name}' 已禁用，跳过加载")
                return False

            # 导入插件模块
            plugin_module_path = plugin_dir / 'plugin.py'
            if not plugin_module_path.exists():
                logger.error(f"插件 '{plugin_name}' 缺少 plugin.py 文件")
                return False

            # 动态导入
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}.plugin",
                plugin_module_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugins.{plugin_name}"] = module
            spec.loader.exec_module(module)

            # 实例化插件
            plugin_class = getattr(module, 'Plugin', None)
            if not plugin_class:
                logger.error(f"插件 '{plugin_name}' 未找到 Plugin 类")
                return False

            plugin_instance = plugin_class(metadata)

            # 初始化插件
            if plugin_instance.initialize():
                self.plugins[plugin_name] = plugin_instance
                self.metadata[plugin_name] = metadata

                # 注册定时任务
                self._register_plugin_tasks(plugin_name, plugin_instance, config)

                logger.info(f"✓ 插件 '{plugin_name}' v{metadata.version} 加载成功")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"加载插件 '{plugin_name}' 失败: {e}", exc_info=True)
            return False

    def _register_plugin_tasks(self, plugin_name: str, plugin: PluginBase, config: dict):
        """注册插件的定时任务"""
        tasks = config.get('tasks', [])

        for task in tasks:
            task_id = f"{plugin_name}_{task.get('id', 'task')}"
            interval = task.get('interval', '1h')
            method_name = task.get('method', 'execute')

            # 获取插件方法
            method = getattr(plugin, method_name, None)
            if method:
                self.scheduler.add_task(task_id, interval, method)
            else:
                logger.warning(f"插件 '{plugin_name}' 未找到方法: {method_name}")

    def load_all_plugins(self):
        """加载所有插件"""
        logger.info("开始加载插件...")

        discovered = self.discover_plugins()
        logger.info(f"发现 {len(discovered)} 个插件: {', '.join(discovered)}")

        success_count = 0
        for plugin_name in discovered:
            if self.load_plugin(plugin_name):
                success_count += 1

        logger.info(f"插件加载完成: {success_count}/{len(discovered)} 成功")

    def unload_plugin(self, plugin_name: str):
        """卸载插件"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.shutdown()
            del self.plugins[plugin_name]
            del self.metadata[plugin_name]
            logger.info(f"插件 '{plugin_name}' 已卸载")

    def reload_plugin(self, plugin_name: str):
        """重新加载插件"""
        self.unload_plugin(plugin_name)
        time.sleep(1)
        self.load_plugin(plugin_name)

    def execute_plugin(self, plugin_name: str, **kwargs) -> Any:
        """执行插件"""
        if plugin_name not in self.plugins:
            raise Exception(f"插件 '{plugin_name}' 未加载")

        plugin = self.plugins[plugin_name]
        return plugin.execute(**kwargs)

    def get_plugin_status(self) -> dict:
        """获取所有插件状态"""
        status = {}

        for name, plugin in self.plugins.items():
            status[name] = {
                'name': plugin.metadata.name,
                'version': plugin.metadata.version,
                'enabled': plugin.metadata.enabled,
                'initialized': plugin.is_initialized,
                'description': plugin.metadata.description
            }

        return status

    def start(self):
        """启动插件管理器"""
        logger.info("=" * 50)
        logger.info("Wiki.js 插件管理器启动中...")
        logger.info("=" * 50)

        # 加载所有插件
        self.load_all_plugins()

        # 启动任务调度器
        self.scheduler.start()

        logger.info("插件管理器启动完成")

    def stop(self):
        """停止插件管理器"""
        logger.info("插件管理器正在关闭...")

        # 停止调度器
        self.scheduler.stop()

        # 卸载所有插件
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)

        logger.info("插件管理器已关闭")


def main():
    """主函数"""
    # 创建日志目录
    Path('logs').mkdir(exist_ok=True)

    # 创建插件管理器
    manager = PluginManager(
        plugins_dir='./plugins',
        config_file='./plugins/plugins_config.json'
    )

    try:
        # 启动管理器
        manager.start()

        # 保持运行
        while True:
            time.sleep(60)

            # 每小时输出一次状态
            status = manager.get_plugin_status()
            logger.info(f"当前加载的插件: {len(status)} 个")

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
        manager.stop()
    except Exception as e:
        logger.error(f"插件管理器运行错误: {e}", exc_info=True)
        manager.stop()
        sys.exit(1)


if __name__ == '__main__':
    main()
