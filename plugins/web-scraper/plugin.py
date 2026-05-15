"""
通用网页爬虫插件
支持自定义URL和提取规则
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from plugins.core.plugin_manager import PluginBase, PluginMetadata


class ConfigurableScraper:
    """可配置的网页爬虫"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape(self, url: str, selector: str = None) -> Dict:
        """
        抓取网页并提取内容

        Args:
            url: 目标URL
            selector: CSS选择器（可选）

        Returns:
            提取的数据字典
        """
        try:
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'lxml')

            # 提取标题
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ""

            # 提取主要内容
            content = ""
            if selector:
                elements = soup.select(selector)
                content = "\n".join([elem.get_text(strip=True) for elem in elements[:5]])
            else:
                # 尝试自动提取文章主体
                article = soup.find('article') or soup.find('main') or soup.find('body')
                if article:
                    content = article.get_text(strip=True)[:2000]  # 限制长度

            return {
                'url': url,
                'title': title_text,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"抓取失败 {url}: {e}")
            return {
                'url': url,
                'title': '',
                'content': f'错误: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }


class Plugin(PluginBase):
    """通用网页爬虫插件"""

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.scraper = ConfigurableScraper()

    def on_initialize(self):
        """初始化"""
        self.logger.info("初始化通用网页爬虫插件")

    def execute(self, **kwargs):
        """执行爬虫任务"""
        self.logger.info("开始执行网页爬虫任务...")

        targets = self.metadata.config.get('targets', [])
        results = []

        for target in targets:
            name = target.get('name', 'Unknown')
            url = target.get('url', '')
            selector = target.get('selector')

            if not url:
                continue

            self.logger.info(f"抓取: {name} - {url}")

            try:
                data = self.scraper.scrape(url, selector)
                results.append(data)

                # 保存到Wiki
                if self.metadata.config.get('save_to_wiki', True):
                    self.save_to_wiki(name, data)

            except Exception as e:
                self.logger.error(f"抓取失败 {name}: {e}")

        self.logger.info(f"爬虫任务完成，共处理 {len(results)} 个目标")
        return {
            'success': True,
            'count': len(results),
            'results': results
        }

    def save_to_wiki(self, name: str, data: Dict):
        """保存数据到Wiki"""
        if not self.wiki_api:
            self.logger.warning("Wiki API未配置，跳过保存")
            return

        try:
            # 生成Markdown内容
            markdown = f"""# {data['title']}

**来源:** [{name}]({data['url']})
**抓取时间:** {datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}

---

## 内容摘要

{data['content'][:1000]}

---

*此内容由网页爬虫自动生成*
"""

            # 生成路径
            path = f"scraped/{name.lower().replace(' ', '-')}"

            # 创建或更新页面
            try:
                page = self.wiki_api.get_page(path)
                self.wiki_api.update_page(page['id'], markdown)
                self.logger.info(f"页面已更新: {path}")
            except:
                self.wiki_api.create_page(path, data['title'], markdown)
                self.logger.info(f"页面已创建: {path}")

        except Exception as e:
            self.logger.error(f"保存到Wiki失败: {e}")

    def on_shutdown(self):
        """关闭"""
        self.logger.info("通用网页爬虫插件已关闭")
