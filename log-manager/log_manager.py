"""
日志管理系统
提供日志收集、存储、查看、轮转和清理功能
"""

import os
import json
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import glob


@dataclass
class LogFileInfo:
    """日志文件信息"""
    filename: str
    size_bytes: int
    size_human: str
    created_at: str
    modified_at: str
    line_count: int
    is_compressed: bool


class LogManager:
    """日志管理器"""

    def __init__(self, log_dir: str = 'logs', max_size_mb: int = 10, backup_count: int = 5):
        self.log_dir = Path(log_dir)
        self.max_size = max_size_mb * 1024 * 1024  # 转换为字节
        self.backup_count = backup_count

        # 创建日志目录
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 创建子目录
        (self.log_dir / 'archive').mkdir(exist_ok=True)  # 归档日志
        (self.log_dir / 'temp').mkdir(exist_ok=True)      # 临时日志

    def setup_logger(self, name: str, level=logging.INFO) -> logging.Logger:
        """
        配置日志记录器

        Args:
            name: 日志记录器名称
            level: 日志级别

        Returns:
            配置好的Logger实例
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # 避免重复添加handler
        if logger.handlers:
            return logger

        # 控制台Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # 文件Handler（按大小轮转）
        log_file = self.log_dir / f'{name}.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_size,
            backupCount=self.backup_count
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 错误日志单独文件
        error_file = self.log_dir / f'{name}_error.log'
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=self.max_size,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)

        return logger

    def get_log_files(self, pattern: str = '*.log') -> List[LogFileInfo]:
        """
        获取日志文件列表

        Args:
            pattern: 文件匹配模式

        Returns:
            日志文件信息列表
        """
        files = []

        # 查找当前日志
        for log_file in self.log_dir.glob(pattern):
            if log_file.is_file():
                info = self._get_file_info(log_file)
                files.append(info)

        # 查找归档日志
        for log_file in (self.log_dir / 'archive').glob(f'{pattern}*'):
            if log_file.is_file():
                info = self._get_file_info(log_file)
                info.is_compressed = log_file.suffix == '.gz'
                files.append(info)

        # 按修改时间排序（最新的在前）
        files.sort(key=lambda x: x.modified_at, reverse=True)

        return files

    def _get_file_info(self, file_path: Path) -> LogFileInfo:
        """获取文件信息"""
        stat = file_path.stat()

        # 计算行数
        line_count = 0
        try:
            if file_path.suffix == '.gz':
                with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
        except:
            pass

        return LogFileInfo(
            filename=file_path.name,
            size_bytes=stat.st_size,
            size_human=self._format_size(stat.st_size),
            created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
            modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            line_count=line_count,
            is_compressed=False
        )

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def read_log(self, filename: str, lines: int = 100, offset: int = 0) -> Dict:
        """
        读取日志内容

        Args:
            filename: 日志文件名
            lines: 读取行数
            offset: 偏移量（从第几行开始）

        Returns:
            包含日志内容的字典
        """
        file_path = self.log_dir / filename
        archive_path = self.log_dir / 'archive' / filename

        if not file_path.exists() and not archive_path.exists():
            return {'success': False, 'error': '文件不存在'}

        target_path = file_path if file_path.exists() else archive_path

        try:
            all_lines = []

            if target_path.suffix == '.gz':
                with gzip.open(target_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    all_lines = f.readlines()
            else:
                with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
                    all_lines = f.readlines()

            total_lines = len(all_lines)

            # 应用偏移和限制
            start = offset
            end = min(offset + lines, total_lines)
            selected_lines = all_lines[start:end]

            return {
                'success': True,
                'filename': filename,
                'total_lines': total_lines,
                'returned_lines': len(selected_lines),
                'offset': offset,
                'lines': selected_lines,
                'has_more': end < total_lines
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_logs(self, keyword: str, case_sensitive: bool = False,
                   max_results: int = 100) -> List[Dict]:
        """
        搜索日志内容

        Args:
            keyword: 搜索关键词
            case_sensitive: 是否区分大小写
            max_results: 最大结果数

        Returns:
            匹配的日志行列表
        """
        results = []
        log_files = self.get_log_files()

        for log_file in log_files[:10]:  # 只搜索最近10个文件
            if log_file.is_compressed:
                continue

            try:
                file_path = self.log_dir / log_file.filename
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if case_sensitive:
                            match = keyword in line
                        else:
                            match = keyword.lower() in line.lower()

                        if match:
                            results.append({
                                'filename': log_file.filename,
                                'line_num': line_num,
                                'content': line.strip(),
                                'timestamp': self._extract_timestamp(line)
                            })

                            if len(results) >= max_results:
                                return results

            except Exception as e:
                continue

        return results

    def _extract_timestamp(self, line: str) -> Optional[str]:
        """从日志行提取时间戳"""
        try:
            # 尝试匹配常见的时间格式
            import re
            patterns = [
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
                r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
            ]

            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1)
        except:
            pass

        return None

    def rotate_logs(self, dry_run: bool = False) -> Dict:
        """
        轮转日志（压缩旧日志）

        Args:
            dry_run: 是否仅预览，不实际执行

        Returns:
            轮转结果
        """
        rotated = []
        skipped = []

        log_files = self.get_log_files('*.log')

        for log_file in log_files:
            file_path = self.log_dir / log_file.filename

            # 跳过小文件
            if log_file.size_bytes < 1024 * 1024:  # 小于1MB
                skipped.append(log_file.filename)
                continue

            # 生成归档文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = log_file.filename.replace('.log', '')
            archive_name = f"{base_name}_{timestamp}.log.gz"
            archive_path = self.log_dir / 'archive' / archive_name

            if dry_run:
                rotated.append({
                    'filename': log_file.filename,
                    'archive_name': archive_name,
                    'size': log_file.size_human,
                    'action': 'would_rotate'
                })
            else:
                try:
                    # 压缩并归档
                    with open(file_path, 'rb') as f_in:
                        with gzip.open(archive_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    # 清空原文件
                    with open(file_path, 'w') as f:
                        f.write(f"# Log rotated at {datetime.now().isoformat()}\n")

                    rotated.append({
                        'filename': log_file.filename,
                        'archive_name': archive_name,
                        'size': log_file.size_human,
                        'action': 'rotated'
                    })

                except Exception as e:
                    skipped.append(f"{log_file.filename}: {str(e)}")

        return {
            'rotated': rotated,
            'skipped': skipped,
            'dry_run': dry_run
        }

    def cleanup_logs(self, days: int = 30, dry_run: bool = False) -> Dict:
        """
        清理旧日志

        Args:
            days: 保留天数
            dry_run: 是否仅预览

        Returns:
            清理结果
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = []
        total_size_freed = 0

        archive_dir = self.log_dir / 'archive'

        for log_file in archive_dir.glob('*.gz'):
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

            if mtime < cutoff_date:
                size = log_file.stat().st_size

                if not dry_run:
                    log_file.unlink()

                deleted.append({
                    'filename': log_file.name,
                    'size': self._format_size(size),
                    'age_days': (datetime.now() - mtime).days
                })
                total_size_freed += size

        return {
            'deleted': deleted,
            'count': len(deleted),
            'total_size_freed': self._format_size(total_size_freed),
            'dry_run': dry_run
        }

    def get_log_stats(self) -> Dict:
        """获取日志统计信息"""
        current_files = self.get_log_files('*.log')
        archive_files = self.get_log_files('*.gz')

        current_size = sum(f.size_bytes for f in current_files)
        archive_size = sum(f.size_bytes for f in archive_files)

        return {
            'current_logs': {
                'count': len(current_files),
                'total_size': self._format_size(current_size),
                'files': [asdict(f) for f in current_files[:5]]
            },
            'archived_logs': {
                'count': len(archive_files),
                'total_size': self._format_size(archive_size),
                'files': [asdict(f) for f in archive_files[:5]]
            },
            'total_size': self._format_size(current_size + archive_size)
        }

    def tail_log(self, filename: str, lines: int = 20, follow: bool = False) -> Dict:
        """
        查看日志末尾（类似tail命令）

        Args:
            filename: 日志文件名
            lines: 行数
            follow: 是否持续跟踪（暂不支持）

        Returns:
            日志内容
        """
        result = self.read_log(filename, lines=lines, offset=-lines)

        if result['success']:
            # 如果是负数offset，重新计算
            if result['total_lines'] > lines:
                result = self.read_log(filename, lines=lines,
                                     offset=result['total_lines'] - lines)

        return result


# 全局日志管理器实例
_log_manager = None


def get_log_manager(log_dir: str = 'logs') -> LogManager:
    """获取全局日志管理器实例"""
    global _log_manager

    if _log_manager is None:
        _log_manager = LogManager(log_dir)

    return _log_manager
