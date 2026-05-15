# 插件开发指南

## 概述

Wiki.js插件系统是一个可扩展的框架，允许你添加自定义功能，如AI集成、自动化任务、数据爬虫等。

## 架构设计

```
plugins/
├── core/                    # 核心模块
│   ├── plugin_manager.py   # 插件管理器
│   └── ai_client.py        # AI客户端
├── daily-digest/           # 示例：每日信息汇总
├── web-scraper/            # 示例：网页爬虫
└── your-plugin/            # 你的插件
    ├── plugin.json         # 插件配置
    └── plugin.py           # 插件代码
```

## 快速开始

### 1. 创建插件目录

```bash
mkdir plugins/my-plugin
cd plugins/my-plugin
```

### 2. 创建plugin.json配置文件

```json
{
  "name": "我的插件",
  "version": "1.0.0",
  "description": "插件描述",
  "author": "你的名字",
  "enabled": true,
  "dependencies": ["requests"],
  "config": {
    "your_config_key": "value"
  },
  "tasks": [
    {
      "id": "my_task",
      "interval": "1h",
      "method": "execute"
    }
  ]
}
```

### 3. 创建plugin.py主文件

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from plugins.core.plugin_manager import PluginBase, PluginMetadata


class Plugin(PluginBase):
    """我的插件"""

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)

    def on_initialize(self):
        """初始化逻辑"""
        self.logger.info("插件初始化")

    def execute(self, **kwargs):
        """执行主逻辑"""
        self.logger.info("执行插件任务")

        # 你的代码
        result = "Hello World"

        return {
            'success': True,
            'result': result
        }

    def on_shutdown(self):
        """关闭逻辑"""
        self.logger.info("插件关闭")
```

### 4. 启用插件

编辑 `plugins/plugins_config.json`：

```json
{
  "plugins": {
    "my-plugin": {
      "enabled": true,
      "config": {}
    }
  }
}
```

### 5. 重启服务

```bash
docker compose --profile plugins up -d
```

## 插件API参考

### PluginBase基类方法

#### `on_initialize()`
插件初始化时调用，用于设置资源、连接等。

#### `execute(**kwargs)`
插件的主要执行逻辑，返回任意数据。

#### `on_shutdown()`
插件关闭时调用，用于清理资源。

### 可用属性

- `self.metadata`: 插件元数据（名称、版本、配置等）
- `self.logger`: 日志记录器
- `self.wiki_api`: Wiki.js API客户端（如果配置了token）
- `self.is_initialized`: 初始化状态

### Wiki API使用

```python
# 创建页面
self.wiki_api.create_page(
    path='my-page',
    title='我的页面',
    content='# Hello',
    tags=['tag1', 'tag2']
)

# 更新页面
self.wiki_api.update_page(page_id=123, content='New content')

# 获取页面
page = self.wiki_api.get_page('my-page')

# 列出所有页面
pages = self.wiki_api.list_pages()
```

### AI客户端使用

```python
from plugins.core.ai_client import get_ai_client

# 获取AI客户端
ai = get_ai_client('openai')

# 生成文本
result = ai.generate("写一首关于编程的诗")

# 总结文本
summary = ai.summarize(long_text)

# 提取关键词
keywords = ai.extract_keywords(text, max_keywords=5)

# 分类内容
category = ai.classify_content(text, ["技术", "新闻"])

# 翻译
translated = ai.translate(text, "英文")
```

## 定时任务配置

在`plugin.json`中配置：

```json
{
  "tasks": [
    {
      "id": "hourly_task",
      "interval": "1h",    // 支持: Xm, Xh, Xd
      "method": "execute"  // 调用的方法名
    },
    {
      "id": "daily_task",
      "interval": "24h",
      "method": "run_daily"
    }
  ]
}
```

## 完整示例：RSS阅读器插件

### plugin.json

```json
{
  "name": "RSS阅读器",
  "version": "1.0.0",
  "description": "订阅RSS源并发布到Wiki",
  "author": "Your Name",
  "enabled": true,
  "dependencies": ["feedparser"],
  "config": {
    "feeds": [
      {
        "name": "Tech News",
        "url": "https://example.com/rss"
      }
    ],
    "update_interval": "2h"
  },
  "tasks": [
    {
      "id": "update_feeds",
      "interval": "2h",
      "method": "update_feeds"
    }
  ]
}
```

### plugin.py

```python
import sys
import os
import feedparser
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from plugins.core.plugin_manager import PluginBase, PluginMetadata


class Plugin(PluginBase):
    """RSS阅读器插件"""

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)

    def on_initialize(self):
        self.logger.info("RSS阅读器插件初始化")

    def update_feeds(self):
        """更新RSS源"""
        feeds = self.metadata.config.get('feeds', [])

        for feed_config in feeds:
            name = feed_config['name']
            url = feed_config['url']

            self.logger.info(f"更新RSS源: {name}")

            try:
                feed = feedparser.parse(url)

                # 生成Markdown
                markdown = f"# {name}\n\n"
                markdown += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

                for entry in feed.entries[:10]:
                    markdown += f"## [{entry.title}]({entry.link})\n\n"
                    if hasattr(entry, 'summary'):
                        markdown += f"{entry.summary[:500]}...\n\n"

                # 发布到Wiki
                path = f"rss/{name.lower().replace(' ', '-')}"
                self.wiki_api.create_page(path, name, markdown)

            except Exception as e:
                self.logger.error(f"更新失败 {name}: {e}")

        return {'success': True}

    def execute(self, **kwargs):
        return self.update_feeds()

    def on_shutdown(self):
        self.logger.info("RSS阅读器插件关闭")
```

## 最佳实践

### 1. 错误处理

```python
def execute(self, **kwargs):
    try:
        # 你的逻辑
        result = self.do_something()
        return {'success': True, 'result': result}
    except Exception as e:
        self.logger.error(f"执行失败: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}
```

### 2. 日志记录

```python
self.logger.info("正常信息")
self.logger.warning("警告信息")
self.logger.error("错误信息")
```

### 3. 配置验证

```python
def on_initialize(self):
    required_config = ['api_key', 'url']
    for key in required_config:
        if key not in self.metadata.config:
            raise ValueError(f"缺少必需配置: {key}")
```

### 4. 资源清理

```python
def on_shutdown(self):
    # 关闭连接、释放资源
    if hasattr(self, 'connection'):
        self.connection.close()
```

## 调试技巧

### 本地测试插件

```python
if __name__ == '__main__':
    from plugins.core.plugin_manager import PluginMetadata

    config = {
        'name': 'Test Plugin',
        'version': '1.0.0',
        'description': 'Test',
        'enabled': True,
        'config': {}
    }

    metadata = PluginMetadata(config)
    plugin = Plugin(metadata)
    plugin.initialize()
    result = plugin.execute()
    print(result)
```

### 查看日志

```bash
# 插件管理器日志
docker compose logs plugin-manager

# 实时日志
docker compose logs -f plugin-manager
```

## 插件发布

1. 确保插件经过充分测试
2. 编写清晰的README文档
3. 在`plugin.json`中填写完整信息
4. 提交到GitHub或分享

## 常见问题

### Q: 插件无法加载？

检查：
- `plugin.json`格式是否正确
- `plugin.py`中是否有`Plugin`类
- 依赖是否安装

### Q: 如何安装依赖？

在Docker中自动安装，或在`plugin.json`的`dependencies`中声明。

### Q: 如何访问环境变量？

```python
import os
api_key = os.getenv('MY_API_KEY')
```

## 更多资源

- 示例插件: `plugins/daily-digest/`
- 示例插件: `plugins/web-scraper/`
- Wiki.js API文档: https://docs.requarks.io/api

---

**祝你开发愉快！** 🚀
