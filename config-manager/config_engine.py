"""
统一配置管理引擎
支持CLI和Web UI共享同一套配置系统
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger('ConfigManager')


@dataclass
class ConfigField:
    """配置字段定义"""
    name: str
    type: str  # string, number, boolean, list, object
    default: Any = None
    required: bool = False
    description: str = ""
    options: List[str] = None  # 可选值
    min_value: Any = None
    max_value: Any = None
    pattern: str = None  # 正则表达式验证


@dataclass
class ConfigSection:
    """配置分组"""
    id: str
    title: str
    description: str
    fields: List[ConfigField]
    icon: str = "settings"


class ConfigEngine:
    """配置管理引擎"""

    def __init__(self, config_dir: str = '.'):
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Any] = {}
        self.schemas: Dict[str, ConfigSection] = {}
        self.history: List[Dict] = []
        self.snapshots: List[Dict] = []  # 配置快照（用于回滚）

        # 加载所有配置
        self._load_all_configs()

        # 注册配置schema
        self._register_schemas()

        # 创建初始快照
        self._create_snapshot("初始状态")

    def _load_all_configs(self):
        """加载所有配置文件"""
        # 1. 加载 .env
        env_file = self.config_dir / '.env'
        if env_file.exists():
            self.configs['env'] = self._parse_env_file(env_file)

        # 2. 加载插件配置
        plugins_config = self.config_dir / 'plugins' / 'plugins_config.json'
        if plugins_config.exists():
            with open(plugins_config, 'r', encoding='utf-8') as f:
                self.configs['plugins'] = json.load(f)

        # 3. 加载同步配置
        sync_config = self.config_dir / 'obsidian-sync-config.json'
        if sync_config.exists():
            with open(sync_config, 'r', encoding='utf-8') as f:
                self.configs['sync'] = json.load(f)

        # 4. 加载Docker Compose配置
        compose_file = self.config_dir / 'docker-compose.yml'
        if compose_file.exists():
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    self.configs['docker'] = yaml.safe_load(f)
            except:
                logger.warning("无法解析docker-compose.yml")

    def _parse_env_file(self, file_path: Path) -> Dict[str, str]:
        """解析.env文件"""
        env_vars = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        return env_vars

    def _register_schemas(self):
        """注册配置schema"""

        # 1. 环境变量配置
        self.schemas['env'] = ConfigSection(
            id='env',
            title='环境变量',
            description='系统核心配置，包括数据库、API密钥等',
            icon='key',
            fields=[
                ConfigField(
                    name='POSTGRES_PASSWORD',
                    type='string',
                    required=True,
                    description='数据库密码',
                    pattern=r'^.{8,}$'
                ),
                ConfigField(
                    name='OPENAI_API_KEY',
                    type='string',
                    description='OpenAI API密钥（用于AI功能）',
                    pattern=r'^sk-'
                ),
                ConfigField(
                    name='WIKI_API_TOKEN',
                    type='string',
                    description='Wiki.js API Token',
                ),
                ConfigField(
                    name='GIT_SYNC_ENABLED',
                    type='boolean',
                    default=False,
                    description='启用Git同步'
                ),
                ConfigField(
                    name='GIT_REPO_URL',
                    type='string',
                    description='Git仓库地址',
                ),
            ]
        )

        # 2. 插件配置
        self.schemas['plugins'] = ConfigSection(
            id='plugins',
            title='插件管理',
            description='启用/禁用插件，配置插件参数',
            icon='puzzle',
            fields=[
                ConfigField(
                    name='rss-reader.enabled',
                    type='boolean',
                    default=True,
                    description='RSS阅读器插件'
                ),
                ConfigField(
                    name='daily-digest.enabled',
                    type='boolean',
                    default=False,
                    description='每日信息汇总插件'
                ),
                ConfigField(
                    name='web-scraper.enabled',
                    type='boolean',
                    default=False,
                    description='网页爬虫插件'
                ),
            ]
        )

        # 3. 同步配置
        self.schemas['sync'] = ConfigSection(
            id='sync',
            title='Obsidian同步',
            description='配置本地与Wiki的双向同步',
            icon='sync',
            fields=[
                ConfigField(
                    name='local_folder',
                    type='string',
                    default='./obsidian-vault',
                    description='Obsidian本地文件夹路径'
                ),
                ConfigField(
                    name='default_sync_strategy',
                    type='string',
                    default='auto_confirm',
                    options=['immediate', 'auto_confirm', 'manual', 'disabled'],
                    description='默认同步策略'
                ),
                ConfigField(
                    name='file_type_filters.allowed_types',
                    type='list',
                    default=['.md'],
                    description='允许同步的文件类型'
                ),
            ]
        )

    def get_config(self, section: str, key: str = None) -> Any:
        """获取配置值"""
        if section not in self.configs:
            return None

        config = self.configs[section]

        if key is None:
            return config

        # 支持嵌套键，如 'file_type_filters.allowed_types'
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None

        return value

    def set_config(self, section: str, key: str, value: Any) -> bool:
        """设置配置值"""
        if section not in self.configs:
            self.configs[section] = {}

        # 验证配置
        if not self._validate_config(section, key, value):
            return False

        # 设置值
        keys = key.split('.')
        config = self.configs[section]

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        old_value = config.get(keys[-1])
        config[keys[-1]] = value

        # 记录历史
        self._record_change(section, key, old_value, value)

        # 保存到文件
        self._save_config(section)

        logger.info(f"配置已更新: {section}.{key} = {value}")
        return True

    def _validate_config(self, section: str, key: str, value: Any) -> bool:
        """验证配置值"""
        if section not in self.schemas:
            return True

        schema = self.schemas[section]
        for field in schema.fields:
            if field.name == key:
                # 类型检查
                if field.type == 'boolean' and not isinstance(value, bool):
                    logger.error(f"配置类型错误: {key} 应该是布尔值")
                    return False

                if field.type == 'number' and not isinstance(value, (int, float)):
                    logger.error(f"配置类型错误: {key} 应该是数字")
                    return False

                # 范围检查
                if field.min_value is not None and value < field.min_value:
                    logger.error(f"配置值过小: {key} >= {field.min_value}")
                    return False

                if field.max_value is not None and value > field.max_value:
                    logger.error(f"配置值过大: {key} <= {field.max_value}")
                    return False

                # 选项检查
                if field.options and value not in field.options:
                    logger.error(f"配置值不在选项中: {key} in {field.options}")
                    return False

                return True

        return True

    def _record_change(self, section: str, key: str, old_value: Any, new_value: Any):
        """记录配置变更历史"""
        change = {
            'timestamp': datetime.now().isoformat(),
            'section': section,
            'key': key,
            'old_value': old_value,
            'new_value': new_value
        }
        self.history.append(change)

        # 只保留最近100条
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def _save_config(self, section: str):
        """保存配置到文件"""
        if section == 'env':
            self._save_env_file()
        elif section == 'plugins':
            self._save_plugins_config()
        elif section == 'sync':
            self._save_sync_config()

    def _save_env_file(self):
        """保存.env文件"""
        env_file = self.config_dir / '.env'
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# 环境变量配置\n")
            f.write(f"# 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for key, value in self.configs['env'].items():
                f.write(f"{key}={value}\n")

    def _save_plugins_config(self):
        """保存插件配置"""
        plugins_config = self.config_dir / 'plugins' / 'plugins_config.json'
        plugins_config.parent.mkdir(parents=True, exist_ok=True)

        with open(plugins_config, 'w', encoding='utf-8') as f:
            json.dump(self.configs['plugins'], f, indent=2, ensure_ascii=False)

    def _save_sync_config(self):
        """保存同步配置"""
        sync_config = self.config_dir / 'obsidian-sync-config.json'

        with open(sync_config, 'w', encoding='utf-8') as f:
            json.dump(self.configs['sync'], f, indent=2, ensure_ascii=False)

    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.configs

    def get_schema(self, section: str) -> Optional[ConfigSection]:
        """获取配置schema"""
        return self.schemas.get(section)

    def get_all_schemas(self) -> Dict[str, ConfigSection]:
        """获取所有schema"""
        return self.schemas

    def get_history(self, limit: int = 20) -> List[Dict]:
        """获取配置变更历史"""
        return self.history[-limit:]

    def reset_config(self, section: str, key: str) -> bool:
        """重置配置为默认值"""
        if section not in self.schemas:
            return False

        schema = self.schemas[section]
        for field in schema.fields:
            if field.name == key:
                return self.set_config(section, key, field.default)

        return False

    def export_config(self, format: str = 'json') -> str:
        """导出配置"""
        if format == 'json':
            return json.dumps(self.configs, indent=2, ensure_ascii=False)
        elif format == 'yaml':
            return yaml.dump(self.configs, allow_unicode=True)
        else:
            raise ValueError(f"不支持的格式: {format}")

    def import_config(self, data: str, format: str = 'json') -> bool:
        """导入配置"""
        try:
            if format == 'json':
                imported = json.loads(data)
            elif format == 'yaml':
                imported = yaml.safe_load(data)
            else:
                raise ValueError(f"不支持的格式: {format}")

            # 合并配置
            for section, values in imported.items():
                if section in self.configs:
                    self.configs[section].update(values)
                    self._save_config(section)

            return True

        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False

    # ==========================================
    # 模板功能
    # ==========================================

    def list_templates(self) -> List[Dict]:
        """列出所有可用模板"""
        templates_dir = self.config_dir / 'config-manager' / 'templates'
        templates = []

        if templates_dir.exists():
            for template_file in templates_dir.glob('*.json'):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                        templates.append({
                            'id': template_file.stem,
                            'name': template.get('name', template_file.stem),
                            'description': template.get('description', ''),
                            'version': template.get('version', '1.0')
                        })
                except Exception as e:
                    logger.error(f"读取模板失败 {template_file}: {e}")

        return templates

    def apply_template(self, template_id: str) -> bool:
        """应用配置模板"""
        templates_dir = self.config_dir / 'config-manager' / 'templates'
        template_file = templates_dir / f"{template_id}.json"

        if not template_file.exists():
            logger.error(f"模板不存在: {template_id}")
            return False

        try:
            # 创建快照（回滚点）
            self._create_snapshot(f"应用模板前: {template_id}")

            with open(template_file, 'r', encoding='utf-8') as f:
                template = json.load(f)

            # 应用配置
            configs = template.get('configs', {})
            for section, values in configs.items():
                if section in self.configs:
                    self._deep_merge(self.configs[section], values)
                    self._save_config(section)

            # 创建应用后快照
            self._create_snapshot(f"已应用模板: {template_id}")

            logger.info(f"模板已应用: {template_id}")
            return True

        except Exception as e:
            logger.error(f"应用模板失败: {e}")
            return False

    def _deep_merge(self, base: Dict, update: Dict):
        """深度合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    # ==========================================
    # 配置回滚功能
    # ==========================================

    def _create_snapshot(self, description: str = ""):
        """创建配置快照"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'configs': json.loads(json.dumps(self.configs))  # 深拷贝
        }
        self.snapshots.append(snapshot)

        # 只保留最近20个快照
        if len(self.snapshots) > 20:
            self.snapshots = self.snapshots[-20:]

        logger.info(f"配置快照已创建: {description}")

    def list_snapshots(self) -> List[Dict]:
        """列出所有快照"""
        return [
            {
                'index': i,
                'timestamp': s['timestamp'],
                'description': s['description']
            }
            for i, s in enumerate(self.snapshots)
        ]

    def rollback_to_snapshot(self, snapshot_index: int) -> bool:
        """回滚到指定快照"""
        if snapshot_index < 0 or snapshot_index >= len(self.snapshots):
            logger.error(f"无效的快照索引: {snapshot_index}")
            return False

        snapshot = self.snapshots[snapshot_index]

        try:
            # 创建回滚前快照
            self._create_snapshot(f"回滚前: {snapshot['description']}")

            # 恢复配置
            self.configs = json.loads(json.dumps(snapshot['configs']))

            # 保存所有配置
            for section in self.configs:
                self._save_config(section)

            # 创建回滚后快照
            self._create_snapshot(f"已回滚到: {snapshot['description']}")

            logger.info(f"配置已回滚到: {snapshot['description']}")
            return True

        except Exception as e:
            logger.error(f"回滚失败: {e}")
            return False

    def rollback_last_change(self) -> bool:
        """回滚最后一次变更"""
        if len(self.history) < 1:
            logger.warning("没有可回滚的变更")
            return False

        last_change = self.history[-1]
        section = last_change['section']
        key = last_change['key']
        old_value = last_change['old_value']

        # 恢复旧值
        return self.set_config(section, key, old_value)


# 全局配置引擎实例
_config_engine = None


def get_config_engine(config_dir: str = '.') -> ConfigEngine:
    """获取全局配置引擎实例"""
    global _config_engine

    if _config_engine is None:
        _config_engine = ConfigEngine(config_dir)

    return _config_engine
