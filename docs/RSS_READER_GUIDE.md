# RSS阅读器插件使用指南

## 📰 功能概述

RSS阅读器插件会自动抓取技术资讯网站的RSS源，使用AI生成智能摘要，并按日期归档发布到Wiki。

### 核心特性

- ✅ **自动抓取** - 每小时自动更新
- ✅ **多源聚合** - Hacker News、GitHub Trending等
- ✅ **AI摘要** - 智能生成文章摘要
- ✅ **分类整理** - 按技术、开源、社区分类
- ✅ **日期归档** - 每天一个独立页面
- ✅ **自动清理** - 保留30天内容

---

## 🚀 快速启用

### 1. 配置OpenAI API（可选但推荐）

编辑 `.env` 文件：

```bash
OPENAI_API_KEY=sk-your-openai-key-here
```

如果不配置AI，插件会使用原始摘要（仍然可用）。

### 2. 启动插件系统

```bash
# 启动时包含plugins profile
docker compose --profile plugins up -d

# 查看插件日志
docker compose logs -f plugin-manager
```

### 3. 验证运行

等待1小时后，访问Wiki查看生成的内容：

```
http://localhost/rss-digest/2026-05-14
```

或手动触发测试：

```bash
# 进入插件管理器容器
docker compose exec plugin-manager bash

# 运行测试
python /app/plugins/rss-reader/plugin.py
```

---

## 📊 数据来源

当前配置的RSS源：

| 来源 | 类型 | 更新频率 | 数量 |
|------|------|----------|------|
| Hacker News | 技术动态 | 实时 | 10条 |
| GitHub Trending | 开源项目 | 每日 | 8条 |
| Reddit Programming | 社区讨论 | 实时 | 8条 |
| Lobsters | 技术新闻 | 实时 | 8条 |

**总计**: 每次更新约34条资讯

---

## ⚙️ 自定义配置

### 添加/删除RSS源

编辑 `plugins/rss-reader/plugin.json`：

```json
{
  "config": {
    "rss_sources": [
      {
        "name": "我的自定义源",
        "url": "https://example.com/rss",
        "category": "tech",
        "max_items": 10
      }
    ]
  }
}
```

### 可用的分类

- `tech` - 技术动态
- `opensource` - 开源项目
- `community` - 社区讨论
- `news` - 行业新闻
- `general` - 通用

### 修改更新频率

```json
{
  "tasks": [
    {
      "id": "hourly_update",
      "interval": "2h",  // 改为每2小时
      "method": "execute"
    }
  ]
}
```

支持的间隔格式：
- `30m` - 30分钟
- `1h` - 1小时
- `6h` - 6小时
- `1d` - 1天

### 调整AI摘要长度

```json
{
  "config": {
    "max_tokens_per_summary": 200  // 增加摘要长度
  }
}
```

### 修改保留天数

```json
{
  "config": {
    "keep_days": 60  // 保留60天
  }
}
```

---

## 📖 查看内容

### 方式1：直接访问URL

```
http://localhost/rss-digest/YYYY-MM-DD
例如: http://localhost/rss-digest/2026-05-14
```

### 方式2：Wiki导航

1. 登录Wiki
2. 浏览页面树
3. 找到 `rss-digest` 文件夹
4. 选择日期查看

### 方式3：搜索

在Wiki搜索框输入：
```
rss-digest
```

---

## 🎨 内容格式示例

生成的页面格式：

```markdown
# 📰 技术资讯日报

**日期**: 2026-05-14 (星期二)
**更新时间**: 14:30:00

---

## 🔧 技术动态

### 1. [文章标题](链接)

**摘要**: AI生成的简洁摘要...

*作者: xxx | 发布: 05-14 10:30 | 标签: python, ai*

---

## ⭐ GitHub趋势

...
```

---

## 🔧 故障排查

### 问题1: 插件未运行

**检查日志**:
```bash
docker compose logs plugin-manager
```

**可能原因**:
- 插件未启用
- 依赖未安装
- 配置文件错误

**解决**:
```bash
# 检查配置
cat plugins/plugins_config.json

# 重启插件
docker compose --profile plugins restart plugin-manager
```

### 问题2: 没有抓取到内容

**检查**:
```bash
# 测试RSS源是否可访问
curl https://hnrss.org/frontpage

# 查看插件日志
docker compose logs plugin-manager | grep rss
```

**可能原因**:
- 网络连接问题
- RSS源暂时不可用
- 防火墙阻止

### 问题3: AI摘要未生成

**检查**:
```bash
# 确认API Key已配置
docker compose exec plugin-manager env | grep OPENAI

# 测试API连接
docker compose exec plugin-manager python -c "import openai; print('OK')"
```

**解决**:
- 确认 `.env` 中配置了 `OPENAI_API_KEY`
- 检查API配额是否充足
- 查看OpenAI状态页面

### 问题4: 内容未发布到Wiki

**检查**:
```bash
# 确认Wiki API Token已配置
docker compose exec plugin-manager env | grep WIKI_API

# 查看是否有保存的文件
ls -la rss-digest-*.md
```

**解决**:
- 在Wiki管理后台生成API Token
- 配置到 `.env` 的 `WIKI_API_TOKEN`
- 重启插件管理器

---

## 💡 高级用法

### 手动触发更新

```bash
# 进入容器
docker compose exec plugin-manager bash

# 执行Python脚本
cd /app
python -c "
from plugins.rss_reader.plugin import Plugin
from plugins.core.plugin_manager import PluginMetadata
import json

with open('plugins/rss-reader/plugin.json') as f:
    config = json.load(f)

metadata = PluginMetadata(config)
plugin = Plugin(metadata)
plugin.initialize()
result = plugin.execute()
print(result)
"
```

### 导出为PDF

1. 访问RSS日报页面
2. 浏览器打印功能 (Ctrl+P)
3. 选择"另存为PDF"

### 订阅特定主题

可以创建多个RSS阅读器实例，每个关注不同主题：

```bash
mkdir plugins/rss-ai
mkdir plugins/rss-webdev
# 分别配置不同的RSS源
```

---

## 📈 性能优化

### 减少API调用成本

如果担心OpenAI费用：

1. **降低更新频率**
   ```json
   "interval": "4h"  // 每4小时
   ```

2. **禁用AI摘要**
   ```json
   "ai_summary_enabled": false
   ```

3. **减少条目数量**
   ```json
   "max_items": 5  // 每个源只取5条
   ```

### 提高抓取速度

```json
{
  "config": {
    "parallel_fetch": true  // 并行抓取（需修改代码实现）
  }
}
```

---

## 🔐 隐私和安全

### API Key保护

- ✅ OpenAI API Key存储在环境变量
- ✅ 不会提交到Git仓库
- ✅ 容器内隔离运行

### 数据保留

- 默认保留30天
- 可配置自动清理
- 本地文件备份

---

## 🆘 常见问题FAQ

### Q: 可以自定义RSS源吗？

A: 可以！编辑 `plugin.json` 中的 `rss_sources` 数组，添加你喜欢的RSS链接。

### Q: AI摘要是中文还是英文？

A: 默认使用中文摘要。可以在代码中修改prompt来改变语言。

### Q: 如何查看历史内容？

A: 所有历史内容都保存在Wiki的 `rss-digest` 目录下，可以按日期浏览。

### Q: 会重复抓取相同内容吗？

A: 每次都是最新内容，不会去重。如需去重功能，可以扩展插件代码。

### Q: 能否推送到手机？

A: 可以通过以下方式：
- 配置邮件通知
- 使用IFTTT集成
- 开启Wiki的PWA功能

---

## 🎯 下一步

1. ✅ 启用插件
2. ⭕ 配置自定义RSS源
3. ⭕ 调整更新频率
4. ⭕ 探索历史内容
5. ⭕ 开发增强功能

---

**享受你的自动化技术资讯流！** 📰✨
