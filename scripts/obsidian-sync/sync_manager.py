"""
Obsidian双向同步管理器
支持智能冲突处理、细粒度同步策略、文件类型过滤
"""

import os
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/obsidian-sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ObsidianSync')


class SyncStrategy(Enum):
    """同步策略"""
    IMMEDIATE = "immediate"          # 立即同步（无需确认）
    AUTO_WITH_CONFIRM = "auto_confirm"  # 自动检测，需要确认
    MANUAL = "manual"                # 手动触发
    DISABLED = "disabled"            # 不同步


class ConflictResolution(Enum):
    """冲突解决策略"""
    WIKI_WINS = "wiki_wins"         # Wiki版本优先
    LOCAL_WINS = "local_wins"       # 本地版本优先
    KEEP_BOTH = "keep_both"         # 保留两个版本
    DRAFT_MERGE = "draft_merge"     # 合并到草稿箱


@dataclass
class FileMetadata:
    """文件元数据"""
    path: str                       # 文件路径
    wiki_id: Optional[int] = None   # Wiki页面ID
    local_hash: Optional[str] = None  # 本地文件哈希
    wiki_hash: Optional[str] = None   # Wiki版本哈希
    last_sync_time: Optional[str] = None  # 最后同步时间
    sync_strategy: str = "auto_confirm"  # 同步策略
    conflict_status: str = "none"   # 冲突状态: none/pending/resolved
    file_types: List[str] = None    # 允许同步的文件类型

    def __post_init__(self):
        if self.file_types is None:
            self.file_types = ['.md']


@dataclass
class SyncConflict:
    """同步冲突记录"""
    file_path: str
    conflict_type: str              # modified_both/deleted_conflict/etc
    local_version: Dict             # 本地版本信息
    wiki_version: Dict              # Wiki版本信息
    draft_content: Optional[str] = None  # 草稿内容
    created_at: str = ""
    status: str = "pending"         # pending/resolved/ignored

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class SyncConfig:
    """同步配置管理器"""

    def __init__(self, config_file: str = 'obsidian-sync-config.json'):
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 默认配置
        return {
            "local_folder": "./obsidian-vault",
            "wiki_base_url": "http://localhost",
            "wiki_api_token": "",
            "default_sync_strategy": "auto_confirm",
            "default_conflict_resolution": "draft_merge",
            "file_type_filters": {
                "enabled": True,
                "allowed_types": [".md"],
                "max_file_size_mb": 10
            },
            "sync_rules": [],       # 针对特定路径的规则
            "excluded_paths": []    # 排除的路径
        }

    def save(self):
        """保存配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_local_folder(self) -> Path:
        return Path(self.config['local_folder'])

    def get_sync_strategy_for_path(self, path: str) -> SyncStrategy:
        """获取指定路径的同步策略"""
        # 检查是否有特定规则
        for rule in self.config.get('sync_rules', []):
            if path.startswith(rule.get('path_pattern', '')):
                return SyncStrategy(rule.get('strategy', 'auto_confirm'))

        # 返回默认策略
        return SyncStrategy(self.config.get('default_sync_strategy', 'auto_confirm'))

    def should_sync_file(self, file_path: Path) -> bool:
        """检查文件是否应该同步"""
        # 检查排除列表
        rel_path = str(file_path.relative_to(self.get_local_folder()))
        for excluded in self.config.get('excluded_paths', []):
            if rel_path.startswith(excluded):
                return False

        # 检查文件类型
        if self.config['file_type_filters']['enabled']:
            allowed = self.config['file_type_filters']['allowed_types']
            if file_path.suffix not in allowed:
                return False

            # 检查文件大小
            max_size = self.config['file_type_filters']['max_file_size_mb'] * 1024 * 1024
            if file_path.exists() and file_path.stat().st_size > max_size:
                logger.warning(f"文件过大，跳过: {file_path}")
                return False

        return True


class WikiAPIClient:
    """Wiki.js API客户端（增强版）"""

    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.session = None

    def _get_headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

    def get_page_by_path(self, path: str) -> Optional[Dict]:
        """根据路径获取页面"""
        try:
            import requests
            response = requests.get(
                f'{self.base_url}/api/pages/path/{path}',
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"API错误: {response.status_code}")

        except Exception as e:
            logger.error(f"获取页面失败: {e}")
            return None

    def create_or_update_page(self, path: str, title: str, content: str, tags: List[str] = None) -> Dict:
        """创建或更新页面"""
        try:
            import requests

            # 先检查页面是否存在
            existing = self.get_page_by_path(path)

            if existing:
                # 更新
                response = requests.put(
                    f'{self.base_url}/api/pages/{existing["id"]}',
                    headers=self._get_headers(),
                    json={
                        'content': content,
                        'title': title,
                        'tags': tags or []
                    }
                )
            else:
                # 创建
                response = requests.post(
                    f'{self.base_url}/api/pages',
                    headers=self._get_headers(),
                    json={
                        'path': path,
                        'title': title,
                        'content': content,
                        'isPublished': True,
                        'tags': tags or []
                    }
                )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise Exception(f"API错误: {response.text}")

        except Exception as e:
            logger.error(f"创建/更新页面失败: {e}")
            raise

    def delete_page(self, page_id: int) -> bool:
        """删除页面"""
        try:
            import requests
            response = requests.delete(
                f'{self.base_url}/api/pages/{page_id}',
                headers=self._get_headers()
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"删除页面失败: {e}")
            return False


class FileWatcher:
    """文件监听器 - 检测本地文件变化"""

    def __init__(self, folder: Path):
        self.folder = folder
        self.file_hashes: Dict[str, str] = {}

    def scan_files(self) -> Dict[str, str]:
        """扫描文件夹，计算文件哈希"""
        current_hashes = {}

        for md_file in self.folder.rglob('*.md'):
            if md_file.is_file():
                file_hash = self._calculate_hash(md_file)
                rel_path = str(md_file.relative_to(self.folder))
                current_hashes[rel_path] = file_hash

        return current_hashes

    def detect_changes(self) -> Dict[str, List[str]]:
        """检测文件变化"""
        new_hashes = self.scan_files()

        changes = {
            'added': [],
            'modified': [],
            'deleted': []
        }

        # 检测新增和修改
        for path, hash_val in new_hashes.items():
            if path not in self.file_hashes:
                changes['added'].append(path)
            elif self.file_hashes[path] != hash_val:
                changes['modified'].append(path)

        # 检测删除
        for path in self.file_hashes:
            if path not in new_hashes:
                changes['deleted'].append(path)

        # 更新哈希表
        self.file_hashes = new_hashes

        return changes

    def _calculate_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()


class ConflictManager:
    """冲突管理器 - 处理同步冲突"""

    def __init__(self, conflicts_file: str = 'sync-conflicts.json'):
        self.conflicts_file = Path(conflicts_file)
        self.conflicts: List[SyncConflict] = self._load_conflicts()

    def _load_conflicts(self) -> List[SyncConflict]:
        """加载冲突记录"""
        if self.conflicts_file.exists():
            with open(self.conflicts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [SyncConflict(**c) for c in data]
        return []

    def save_conflicts(self):
        """保存冲突记录"""
        with open(self.conflicts_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(c) for c in self.conflicts], f, indent=2, ensure_ascii=False)

    def add_conflict(self, conflict: SyncConflict):
        """添加冲突记录"""
        self.conflicts.append(conflict)
        self.save_conflicts()
        logger.info(f"检测到冲突: {conflict.file_path}")

    def get_pending_conflicts(self) -> List[SyncConflict]:
        """获取待处理的冲突"""
        return [c for c in self.conflicts if c.status == 'pending']

    def resolve_conflict(self, file_path: str, resolution: str, merged_content: str = None):
        """
        解决冲突

        Args:
            file_path: 文件路径
            resolution: 解决方案 (wiki_wins/local_wins/merge)
            merged_content: 合并后的内容（如果是merge方案）
        """
        for conflict in self.conflicts:
            if conflict.file_path == file_path and conflict.status == 'pending':
                conflict.status = 'resolved'

                if resolution == 'merge' and merged_content:
                    conflict.draft_content = merged_content

                self.save_conflicts()
                logger.info(f"冲突已解决: {file_path} ({resolution})")
                return conflict

        raise ValueError(f"未找到待处理的冲突: {file_path}")

    def create_draft_from_conflict(self, conflict: SyncConflict) -> str:
        """从冲突创建草稿"""
        draft_path = f"drafts/{conflict.file_path}"
        Path(draft_path).parent.mkdir(parents=True, exist_ok=True)

        # 合并两个版本（简单策略：用分隔符标记）
        draft_content = f"""<!-- 冲突草稿 - {conflict.created_at} -->

<!-- ===== 本地版本 ===== -->
{conflict.local_version.get('content', '')}

<!-- ===== Wiki版本 ===== -->
{conflict.wiki_version.get('content', '')}

<!-- ===== 请在此处编辑合并后的内容 ===== -->
"""

        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(draft_content)

        conflict.draft_content = draft_path
        self.save_conflicts()

        return draft_path


class ObsidianSyncManager:
    """Obsidian同步管理器 - 主类"""

    def __init__(self, config_file: str = 'obsidian-sync-config.json'):
        self.config = SyncConfig(config_file)
        self.wiki_api = None
        self.file_watcher = FileWatcher(self.config.get_local_folder())
        self.conflict_manager = ConflictManager()
        self.metadata_file = Path('sync-metadata.json')
        self.file_metadata: Dict[str, FileMetadata] = {}

        # 初始化Wiki API
        wiki_token = self.config.config.get('wiki_api_token', '')
        wiki_url = self.config.config.get('wiki_base_url', 'http://localhost')
        if wiki_token:
            self.wiki_api = WikiAPIClient(wiki_url, wiki_token)

        # 加载元数据
        self._load_metadata()

    def _load_metadata(self):
        """加载文件元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.file_metadata = {k: FileMetadata(**v) for k, v in data.items()}

    def _save_metadata(self):
        """保存文件元数据"""
        data = {k: asdict(v) for k, v in self.file_metadata.items()}
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def sync_all(self):
        """执行全量同步"""
        logger.info("=" * 50)
        logger.info("开始Obsidian双向同步")
        logger.info("=" * 50)

        try:
            # 1. 检测本地变化
            local_changes = self.file_watcher.detect_changes()
            logger.info(f"本地变化: +{len(local_changes['added'])} ~{len(local_changes['modified'])} -{len(local_changes['deleted'])}")

            # 2. 处理新增文件
            for path in local_changes['added']:
                self._sync_new_file(path)

            # 3. 处理修改文件
            for path in local_changes['modified']:
                self._sync_modified_file(path)

            # 4. 处理删除文件
            for path in local_changes['deleted']:
                self._sync_deleted_file(path)

            # 5. 检查Wiki端的变化（反向同步）
            self._sync_from_wiki()

            logger.info("同步完成")

        except Exception as e:
            logger.error(f"同步失败: {e}", exc_info=True)
            raise

    def _sync_new_file(self, rel_path: str):
        """同步新文件到Wiki"""
        local_file = self.config.get_local_folder() / rel_path

        if not self.config.should_sync_file(local_file):
            logger.info(f"跳过文件: {rel_path}")
            return

        strategy = self.config.get_sync_strategy_for_path(rel_path)

        if strategy == SyncStrategy.DISABLED:
            return

        try:
            # 读取文件内容
            content = local_file.read_text(encoding='utf-8')

            # 生成Wiki路径（保持目录结构）
            wiki_path = rel_path.replace('\\', '/')

            # 提取标题（从第一个heading或文件名）
            title = self._extract_title(content, local_file.stem)

            # 上传到Wiki
            if self.wiki_api:
                result = self.wiki_api.create_or_update_page(wiki_path, title, content)

                # 记录元数据
                self.file_metadata[rel_path] = FileMetadata(
                    path=rel_path,
                    wiki_id=result.get('id'),
                    local_hash=self.file_watcher._calculate_hash(local_file),
                    wiki_hash=result.get('hash'),
                    last_sync_time=datetime.now().isoformat(),
                    sync_strategy=strategy.value
                )
                self._save_metadata()

                logger.info(f"✓ 新文件已同步: {rel_path}")
            else:
                logger.warning("Wiki API未配置，跳过上传")

        except Exception as e:
            logger.error(f"同步新文件失败 {rel_path}: {e}")

    def _sync_modified_file(self, rel_path: str):
        """同步修改的文件"""
        local_file = self.config.get_local_folder() / rel_path

        if not self.config.should_sync_file(local_file):
            return

        strategy = self.config.get_sync_strategy_for_path(rel_path)

        if strategy == SyncStrategy.DISABLED:
            return

        # 检查是否有冲突
        metadata = self.file_metadata.get(rel_path)
        if metadata and metadata.conflict_status == 'pending':
            logger.info(f"文件有未解决的冲突，跳过: {rel_path}")
            return

        try:
            content = local_file.read_text(encoding='utf-8')
            wiki_path = rel_path.replace('\\', '/')
            title = self._extract_title(content, local_file.stem)

            # 检查Wiki端是否也有修改
            if metadata and self.wiki_api:
                wiki_page = self.wiki_api.get_page_by_path(wiki_path)

                if wiki_page:
                    wiki_hash = self._calculate_content_hash(wiki_page.get('content', ''))

                    if wiki_hash != metadata.wiki_hash:
                        # 检测到冲突！
                        logger.warning(f"检测到冲突: {rel_path}")
                        self._handle_conflict(rel_path, content, wiki_page)
                        return

            # 无冲突，直接同步
            if self.wiki_api:
                self.wiki_api.create_or_update_page(wiki_path, title, content)

                # 更新元数据
                if metadata:
                    metadata.local_hash = self.file_watcher._calculate_hash(local_file)
                    metadata.last_sync_time = datetime.now().isoformat()
                    self._save_metadata()

                logger.info(f"✓ 文件已同步: {rel_path}")

        except Exception as e:
            logger.error(f"同步修改文件失败 {rel_path}: {e}")

    def _handle_conflict(self, rel_path: str, local_content: str, wiki_page: Dict):
        """处理冲突"""
        conflict = SyncConflict(
            file_path=rel_path,
            conflict_type='modified_both',
            local_version={
                'content': local_content,
                'modified_time': datetime.now().isoformat()
            },
            wiki_version={
                'content': wiki_page.get('content', ''),
                'modified_time': wiki_page.get('updatedAt', '')
            }
        )

        self.conflict_manager.add_conflict(conflict)

        # 创建草稿
        draft_path = self.conflict_manager.create_draft_from_conflict(conflict)
        logger.info(f"已创建冲突草稿: {draft_path}")

    def _sync_deleted_file(self, rel_path: str):
        """处理删除的文件"""
        metadata = self.file_metadata.get(rel_path)
        if not metadata or not metadata.wiki_id:
            return

        # 根据策略决定是否删除Wiki页面
        # 这里暂时只记录，不实际删除（安全考虑）
        logger.info(f"本地文件已删除: {rel_path} (Wiki页面保留)")

    def _sync_from_wiki(self):
        """从Wiki同步到本地（反向同步）"""
        if not self.wiki_api:
            return

        # TODO: 实现Wiki端变化检测
        # 这需要调用Wiki API列出所有页面并比较
        logger.info("Wiki→本地同步暂未实现（需要完整页面列表API）")

    def _extract_title(self, content: str, default: str) -> str:
        """从Markdown内容提取标题"""
        lines = content.split('\n')
        for line in lines[:10]:  # 只检查前10行
            if line.startswith('# '):
                return line[2:].strip()
        return default

    def _calculate_content_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def get_sync_status(self) -> Dict:
        """获取同步状态"""
        pending_conflicts = self.conflict_manager.get_pending_conflicts()

        return {
            'total_files': len(self.file_metadata),
            'pending_conflicts': len(pending_conflicts),
            'last_sync': datetime.now().isoformat(),
            'conflicts': [asdict(c) for c in pending_conflicts]
        }


def main():
    """主函数"""
    # 创建必要的目录
    Path('logs').mkdir(exist_ok=True)
    Path('drafts').mkdir(exist_ok=True)

    # 创建同步管理器
    manager = ObsidianSyncManager()

    try:
        # 执行同步
        manager.sync_all()

        # 显示状态
        status = manager.get_sync_status()
        print(f"\n同步状态:")
        print(f"  总文件数: {status['total_files']}")
        print(f"  待处理冲突: {status['pending_conflicts']}")

    except Exception as e:
        logger.error(f"同步失败: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
