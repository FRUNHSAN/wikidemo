"""
每日信息汇总插件
自动抓取网站内容，使用AI整理成每日汇总
"""

import sys
import os
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from plugins.core.plugin_manager import PluginBase, PluginMetadata
from plugins.core.ai_client import get_ai_client


class WebScraper:
    """网页爬虫工具类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_page(self, url: str) -> str:
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"获取页面失败 {url}: {e}")
            return ""

    def extract_links(self, html: str, selector: str) -> List[Dict[str, str]]:
        """提取链接"""
        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        elements = soup.select(selector)

        results = []
        for elem in elements[:10]:  # 限制数量
            title = elem.get_text(strip=True)
            href = elem.get('href', '')

            if href and not href.startswith('http'):
                href = f"https://news.ycombinator.com/{href}"

            if title:
                results.append({
                    'title': title,
                    'url': href
                })

        return results

    def scrape_hacker_news(self) -> List[Dict[str, str]]:
        """抓取Hacker News"""
        html = self.fetch_page("https://news.ycombinator.com")
        return self.extract_links(html, ".titleline > a")

    def scrape_github_trending(self) -> List[Dict[str, str]]:
        """抓取GitHub Trending"""
        html = self.fetch_page("https://github.com/trending")
        return self.extract_links(html, "h2.h3.lh-condensed a")


class Plugin(PluginBase):
    """每日信息汇总插件"""

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.scraper = WebScraper()
        self.ai_client = None

    def on_initialize(self):
        """初始化插件"""
        self.logger.info("初始化每日信息汇总插件")

        # 初始化AI客户端
        if self.metadata.config.get('ai_enabled', False):
            try:
                provider = self.metadata.config.get('ai_provider', 'openai')
                self.ai_client = get_ai_client(provider)
                self.logger.info(f"AI客户端已初始化: {provider}")
            except Exception as e:
                self.logger.warning(f"AI客户端初始化失败: {e}")

    def execute(self, **kwargs):
        """执行每日汇总任务"""
        self.logger.info("开始执行每日信息汇总...")

        try:
            # 1. 抓取数据
            news_data = self.collect_data()

            # 2. 使用AI整理
            if self.ai_client:
                summary = self.generate_summary(news_data)
            else:
                summary = self.generate_simple_summary(news_data)

            # 3. 发布到Wiki
            self.publish_to_wiki(summary)

            self.logger.info("每日信息汇总完成")
            return {
                'success': True,
                'items_count': len(news_data),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"执行每日汇总失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def collect_data(self) -> Dict[str, List]:
        """收集数据"""
        data = {
            'hacker_news': [],
            'github_trending': [],
            'timestamp': datetime.now().isoformat()
        }

        sources = self.metadata.config.get('sources', [])

        for source in sources:
            source_type = source.get('type', '')
            url = source.get('url', '')

            if 'hackernews' in url or source_type == 'news':
                data['hacker_news'] = self.scraper.scrape_hacker_news()
            elif 'github' in url or source_type == 'tech':
                data['github_trending'] = self.scraper.scrape_github_trending()

        self.logger.info(f"数据收集完成: HN={len(data['hacker_news'])}, GitHub={len(data['github_trending'])}")
        return data

    def generate_summary(self, data: Dict) -> str:
        """使用AI生成摘要"""
        hn_items = "\n".join([f"- {item['title']} ({item['url']})" for item in data['hacker_news'][:5]])
        gh_items = "\n".join([f"- {item['title']} ({item['url']})" for item in data['github_trending'][:5]])

        prompt = f"""请根据以下信息生成一份简洁的每日技术资讯汇总（使用Markdown格式）：

## Hacker News热门话题
{hn_items if hn_items else "暂无数据"}

## GitHub趋势项目
{gh_items if gh_items else "暂无数据"}

要求：
1. 用中文撰写
2. 包含日期标题
3. 对每个项目进行简要说明
4. 添加总结和建议
5. 使用清晰的Markdown格式
"""

        summary = self.ai_client.generate(prompt, max_tokens=2000, temperature=0.7)
        return summary

    def generate_simple_summary(self, data: Dict) -> str:
        """生成简单摘要（无AI）"""
        date_str = datetime.now().strftime('%Y年%m月%d日')

        markdown = f"""# 每日信息汇总 - {date_str}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Hacker News热门

"""

        for i, item in enumerate(data['hacker_news'][:10], 1):
            markdown += f"{i}. [{item['title']}]({item['url']})\n"

        markdown += "\n## GitHub趋势项目\n\n"

        for i, item in enumerate(data['github_trending'][:10], 1):
            markdown += f"{i}. [{item['title']}]({item['url']})\n"

        return markdown

    def publish_to_wiki(self, content: str):
        """发布到Wiki.js"""
        if not self.wiki_api:
            self.logger.warning("Wiki API未配置，跳过发布")
            # 保存到本地文件
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"daily-digest-{date_str}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"内容已保存到: {filename}")
            return

        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            path = f"daily-digest/{date_str}"
            title = f"每日汇总 - {date_str}"

            # 检查页面是否存在
            try:
                page = self.wiki_api.get_page(path)
                # 更新现有页面
                self.wiki_api.update_page(page['id'], content)
                self.logger.info(f"页面已更新: {path}")
            except:
                # 创建新页面
                self.wiki_api.create_page(path, title, content)
                self.logger.info(f"页面已创建: {path}")

        except Exception as e:
            self.logger.error(f"发布到Wiki失败: {e}")
            # 降级：保存到文件
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"daily-digest-{date_str}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"内容已保存到: {filename}")

    def on_shutdown(self):
        """关闭插件"""
        self.logger.info("每日信息汇总插件已关闭")


if __name__ == '__main__':
    # 测试运行
    from plugins.core.plugin_manager import PluginMetadata

    config = {
        'name': '每日信息汇总',
        'version': '1.0.0',
        'description': '测试',
        'enabled': True,
        'config': {
            'ai_enabled': False,
            'sources': [
                {'url': 'https://news.ycombinator.com', 'type': 'news'},
                {'url': 'https://github.com/trending', 'type': 'tech'}
            ]
        }
    }

    metadata = PluginMetadata(config)
    plugin = Plugin(metadata)
    plugin.initialize()
    result = plugin.execute()
    print(f"执行结果: {result}")
