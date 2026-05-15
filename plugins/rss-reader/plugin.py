"""
技术资讯RSS阅读器插件
自动抓取技术RSS源，AI生成摘要，发布到Wiki
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import feedparser
import time

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from plugins.core.plugin_manager import PluginBase, PluginMetadata
from plugins.core.ai_client import get_ai_client


class RSSFetcher:
    """RSS抓取器"""

    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    def fetch(self, url: str, max_items: int = 10) -> List[Dict]:
        """
        抓取RSS源

        Args:
            url: RSS源URL
            max_items: 最大条目数

        Returns:
            条目列表
        """
        try:
            # 解析RSS
            feed = feedparser.parse(url)

            if not feed.entries:
                print(f"警告: 未获取到内容 - {url}")
                return []

            items = []
            for entry in feed.entries[:max_items]:
                item = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'tags': [tag.term for tag in entry.get('tags', [])] if hasattr(entry, 'tags') else []
                }

                # 清理HTML标签
                item['summary'] = self._clean_html(item['summary'])
                item['title'] = self._clean_html(item['title'])

                items.append(item)

            print(f"成功抓取 {len(items)} 条: {feed.feed.get('title', url)}")
            return items

        except Exception as e:
            print(f"抓取失败 {url}: {e}")
            return []

    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        if not text:
            return ""

        # 简单去除HTML标签
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        # 去除多余空白
        clean = ' '.join(clean.split())
        return clean.strip()


class AISummarizer:
    """AI摘要生成器"""

    def __init__(self, enabled: bool = True, provider: str = "openai", max_tokens: int = 150):
        self.enabled = enabled
        self.max_tokens = max_tokens
        self.ai_client = None

        if enabled:
            try:
                self.ai_client = get_ai_client(provider)
                print(f"AI摘要功能已启用 ({provider})")
            except Exception as e:
                print(f"AI初始化失败，将使用原始摘要: {e}")
                self.enabled = False

    def summarize(self, title: str, content: str) -> str:
        """
        生成智能摘要

        Args:
            title: 文章标题
            content: 文章内容

        Returns:
            AI生成的摘要
        """
        if not self.enabled or not self.ai_client:
            # 降级：返回原始摘要的前200字符
            return content[:200] + "..." if len(content) > 200 else content

        try:
            prompt = f"""请用一句话总结以下技术文章（50字以内），突出核心价值：

标题：{title}
内容：{content[:500]}

总结："""

            summary = self.ai_client.generate(
                prompt,
                max_tokens=self.max_tokens,
                temperature=0.5
            )

            return summary.strip()

        except Exception as e:
            print(f"AI摘要生成失败: {e}")
            return content[:200] + "..."


class WikiPublisher:
    """Wiki发布器"""

    def __init__(self, wiki_api=None):
        self.wiki_api = wiki_api

    def publish_daily_digest(self, date_str: str, items_by_category: Dict[str, List[Dict]]) -> bool:
        """
        发布每日RSS摘要到Wiki

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)
            items_by_category: 按分类组织的内容

        Returns:
            是否成功
        """
        # 生成Markdown内容
        markdown = self._generate_markdown(date_str, items_by_category)

        # 如果未配置Wiki API，保存到文件
        if not self.wiki_api:
            filename = f"rss-digest-{date_str}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"内容已保存到: {filename}")
            return True

        try:
            path = f"rss-digest/{date_str}"
            title = f"技术资讯日报 - {date_str}"

            # 尝试更新现有页面
            try:
                page = self.wiki_api.get_page(path)
                self.wiki_api.update_page(page['id'], markdown)
                print(f"页面已更新: {path}")
            except:
                # 创建新页面
                self.wiki_api.create_page(path, title, markdown, tags=['rss', 'daily-digest', 'tech-news'])
                print(f"页面已创建: {path}")

            return True

        except Exception as e:
            print(f"发布到Wiki失败: {e}")
            # 降级保存
            filename = f"rss-digest-{date_str}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"降级保存到: {filename}")
            return False

    def _generate_markdown(self, date_str: str, items_by_category: Dict[str, List[Dict]]) -> str:
        """生成Markdown格式的内容"""

        # 中文星期
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        weekday = weekdays[dt.weekday()]

        markdown = f"""# 📰 技术资讯日报

**日期**: {date_str} ({weekday})
**更新时间**: {datetime.now().strftime('%H:%M:%S')}
**数据来源**: Hacker News, GitHub Trending, Reddit Programming, Lobsters

---

"""

        # 分类名称映射
        category_names = {
            'tech': '🔧 技术动态',
            'opensource': '⭐ GitHub趋势',
            'community': '💬 社区讨论',
            'news': '📢 行业新闻'
        }

        # 按分类输出
        total_items = 0
        for category, items in items_by_category.items():
            if not items:
                continue

            category_name = category_names.get(category, category)
            markdown += f"\n## {category_name}\n\n"

            for i, item in enumerate(items, 1):
                markdown += f"### {i}. [{item['title']}]({item['link']})\n\n"

                if item.get('ai_summary'):
                    markdown += f"**摘要**: {item['ai_summary']}\n\n"
                elif item.get('summary'):
                    # 显示原始摘要的前150字符
                    summary_preview = item['summary'][:150]
                    if len(item['summary']) > 150:
                        summary_preview += "..."
                    markdown += f"{summary_preview}\n\n"

                # 元信息
                meta = []
                if item.get('author'):
                    meta.append(f"作者: {item['author']}")
                if item.get('published'):
                    # 格式化时间
                    try:
                        pub_time = datetime.strptime(item['published'][:19], '%Y-%m-%dT%H:%M:%S')
                        meta.append(f"发布: {pub_time.strftime('%m-%d %H:%M')}")
                    except:
                        pass
                if item.get('tags'):
                    tags_str = ', '.join(item['tags'][:3])
                    meta.append(f"标签: {tags_str}")

                if meta:
                    markdown += f"*{' | '.join(meta)}*\n\n"

                total_items += 1

            markdown += "---\n"

        # 底部统计
        markdown += f"\n**今日共收录 {total_items} 条资讯**\n\n"
        markdown += "*此内容由RSS阅读器自动生成，每小时更新*\n"

        return markdown


class Plugin(PluginBase):
    """RSS阅读器插件"""

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.fetcher = RSSFetcher()

        # 初始化AI摘要器
        config = metadata.config
        self.summarizer = AISummarizer(
            enabled=config.get('ai_summary_enabled', True),
            provider=config.get('ai_provider', 'openai'),
            max_tokens=config.get('max_tokens_per_summary', 150)
        )

        # 初始化发布器
        self.publisher = WikiPublisher(self.wiki_api)

    def on_initialize(self):
        """初始化插件"""
        self.logger.info("技术资讯RSS阅读器插件初始化")

        sources = self.metadata.config.get('rss_sources', [])
        self.logger.info(f"已配置 {len(sources)} 个RSS源")

    def execute(self, **kwargs):
        """执行RSS抓取和发布任务"""
        self.logger.info("开始执行RSS更新任务...")

        try:
            # 1. 抓取所有RSS源
            all_items = self.fetch_all_sources()

            if not all_items:
                self.logger.warning("未抓取到任何内容")
                return {'success': False, 'message': 'No content fetched'}

            # 2. 生成AI摘要
            if self.metadata.config.get('ai_summary_enabled', True):
                self.generate_summaries(all_items)

            # 3. 按分类组织
            items_by_category = self.organize_by_category(all_items)

            # 4. 发布到Wiki
            date_str = datetime.now().strftime('%Y-%m-%d')
            success = self.publisher.publish_daily_digest(date_str, items_by_category)

            total_count = sum(len(items) for items in items_by_category.values())

            result = {
                'success': success,
                'total_items': total_count,
                'categories': len(items_by_category),
                'timestamp': datetime.now().isoformat()
            }

            self.logger.info(f"RSS更新完成: {total_count}条内容")
            return result

        except Exception as e:
            self.logger.error(f"执行RSS任务失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def fetch_all_sources(self) -> List[Dict]:
        """抓取所有RSS源"""
        sources = self.metadata.config.get('rss_sources', [])
        all_items = []

        for source in sources:
            name = source.get('name', 'Unknown')
            url = source.get('url', '')
            max_items = source.get('max_items', 10)
            category = source.get('category', 'general')

            if not url:
                continue

            self.logger.info(f"抓取: {name}")

            try:
                items = self.fetcher.fetch(url, max_items)

                # 为每个条目添加元信息
                for item in items:
                    item['source'] = name
                    item['category'] = category

                all_items.extend(items)

                # 礼貌间隔，避免请求过快
                time.sleep(1)

            except Exception as e:
                self.logger.error(f"抓取 {name} 失败: {e}")

        self.logger.info(f"共抓取 {len(all_items)} 条内容")
        return all_items

    def generate_summaries(self, items: List[Dict]):
        """为所有条目生成AI摘要"""
        if not self.summarizer.enabled:
            return

        self.logger.info(f"开始生成AI摘要 ({len(items)}条)...")

        for i, item in enumerate(items, 1):
            try:
                summary = self.summarizer.summarize(item['title'], item['summary'])
                item['ai_summary'] = summary

                # 每5条显示进度
                if i % 5 == 0:
                    self.logger.info(f"摘要进度: {i}/{len(items)}")

                # 避免API限流
                time.sleep(0.5)

            except Exception as e:
                self.logger.warning(f"生成摘要失败: {item['title'][:50]} - {e}")
                item['ai_summary'] = item['summary'][:150]

        self.logger.info("AI摘要生成完成")

    def organize_by_category(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """按分类组织内容"""
        categorized = {}

        for item in items:
            category = item.get('category', 'general')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(item)

        return categorized

    def cleanup_old_pages(self):
        """清理过期的RSS页面"""
        keep_days = self.metadata.config.get('keep_days', 30)
        cutoff_date = datetime.now() - timedelta(days=keep_days)

        if not self.wiki_api:
            return

        try:
            pages = self.wiki_api.list_pages()

            for page in pages:
                path = page.get('path', '')
                if not path.startswith('rss-digest/'):
                    continue

                # 提取日期
                try:
                    date_str = path.replace('rss-digest/', '')
                    page_date = datetime.strptime(date_str, '%Y-%m-%d')

                    if page_date < cutoff_date:
                        # 删除过期页面（需要Wiki.js API支持）
                        self.logger.info(f"过期页面: {path}")
                except:
                    pass

        except Exception as e:
            self.logger.error(f"清理过期页面失败: {e}")

    def on_shutdown(self):
        """关闭插件"""
        self.logger.info("RSS阅读器插件已关闭")


if __name__ == '__main__':
    # 测试运行
    from plugins.core.plugin_manager import PluginMetadata

    config = {
        'name': '技术资讯RSS阅读器',
        'version': '1.0.0',
        'description': 'Test',
        'enabled': True,
        'config': {
            'rss_sources': [
                {
                    'name': 'Hacker News',
                    'url': 'https://hnrss.org/frontpage',
                    'category': 'tech',
                    'max_items': 5
                }
            ],
            'ai_summary_enabled': False,  # 测试时禁用AI
            'update_interval': '1h'
        }
    }

    metadata = PluginMetadata(config)
    plugin = Plugin(metadata)
    plugin.initialize()
    result = plugin.execute()
    print(f"\n执行结果: {result}")
