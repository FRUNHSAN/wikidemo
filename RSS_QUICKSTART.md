# RSS阅读器插件 - 5分钟快速启动

## 🎯 已完成的功能

✅ **技术资讯RSS阅读器插件**已创建完成！

### 功能特性
- 自动抓取4个技术RSS源（Hacker News、GitHub等）
- AI智能摘要生成
- 每小时自动更新
- 按日期归档到Wiki
- 分类整理（技术/开源/社区）

---

## 🚀 立即启用（3步）

### 步骤1: 配置OpenAI API（可选）

如果你想使用AI摘要功能：

```bash
# 编辑 .env 文件
vim .env

# 添加这一行
OPENAI_API_KEY=sk-your-openai-key-here
```

**如果不想用AI？** 没关系，插件仍然可以工作，只是显示原始摘要。

### 步骤2: 启动插件系统

```bash
# Windows
docker compose --profile plugins up -d

# Linux/macOS
docker compose --profile plugins up -d
```

### 步骤3: 验证运行

```bash
# 查看日志
docker compose logs -f plugin-manager

# 应该看到类似输出:
# [INFO] 技术资讯RSS阅读器插件初始化
# [INFO] 已配置 4 个RSS源
# [INFO] RSS更新完成: 34条内容
```

---

## 📰 查看生成的内容

### 等待第一次更新

插件会**每小时自动执行**，你可以：

**选项A**: 等待1小时自动更新

**选项B**: 手动触发测试（立即看到效果）

```bash
# 进入插件容器
docker compose exec plugin-manager bash

# 在容器内执行
cd /app
python plugins/rss-reader/plugin.py
```

### 访问生成的页面

```
http://localhost/rss-digest/2026-05-14
```

替换为今天的日期。

---

## 📊 你会看到什么？

生成的页面类似这样：

```
📰 技术资讯日报

日期: 2026-05-14 (星期二)
更新时间: 14:30:00

━━━━━━━━━━━━━━━━━━━━━━

🔧 技术动态

1. Show HN: A new tool for...
   摘要: 一个用于XXX的新工具，可以...
   作者: xxx | 发布: 05-14 10:30

2. Understanding Rust ownership...
   摘要: 深入讲解Rust所有权机制...

━━━━━━━━━━━━━━━━━━━━━━

⭐ GitHub趋势

1. awesome-project - 10k stars
   ...
```

---

## ⚙️ 自定义RSS源

想添加自己喜欢的网站？

编辑 `plugins/rss-reader/plugin.json`：

```json
{
  "config": {
    "rss_sources": [
      // 现有源...

      // 添加你的源
      {
        "name": "我的博客",
        "url": "https://your-blog.com/rss",
        "category": "tech",
        "max_items": 5
      }
    ]
  }
}
```

然后重启：

```bash
docker compose --profile plugins restart plugin-manager
```

---

## 🔧 常见问题

### Q: 如何知道插件是否在运行？

```bash
# 查看状态
docker compose ps

# 应该看到 plugin-manager 状态为 Up
```

### Q: 多久更新一次？

默认**每小时**更新一次。

想修改频率？编辑 `plugin.json`：

```json
{
  "tasks": [{
    "interval": "2h"  // 改为每2小时
  }]
}
```

### Q: AI费用贵吗？

每次更新约34条摘要，消耗约：
- GPT-3.5: ~$0.02/次
- 每天约$0.5（如果每小时更新）

**省钱技巧**:
- 降低更新频率（每4小时）
- 减少条目数量
- 或禁用AI（仍然可用）

### Q: 内容保存在哪里？

- **主要**: Wiki页面 `rss-digest/YYYY-MM-DD`
- **备份**: 本地文件 `rss-digest-2026-05-14.md`

---

## 🎉 完成！

现在你有了：
- ✅ 自动化技术资讯流
- ✅ AI智能摘要
- ✅ 历史归档
- ✅ 分类整理

**下一步**:
1. 浏览生成的内容
2. 根据需要调整配置
3. 享受自动化资讯！

---

**有问题？** 查看完整文档: [docs/RSS_READER_GUIDE.md](docs/RSS_READER_GUIDE.md)
