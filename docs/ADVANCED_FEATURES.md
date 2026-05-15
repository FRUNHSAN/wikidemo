# 高级功能使用指南

## 目录

1. [Git同步配置](#git同步配置)
2. [插件系统使用](#插件系统使用)
3. [AI集成功能](#ai集成功能)
4. [自动化任务](#自动化任务)
5. [性能优化](#性能优化)

---

## Git同步配置

### 快速配置步骤

1. **创建GitHub仓库**
   ```bash
   # 在GitHub上创建新仓库（私有推荐）
   # 记录仓库地址，例如: https://github.com/username/wiki-notes.git
   ```

2. **生成Personal Access Token**
   - GitHub: https://github.com/settings/tokens
   - 权限选择: `repo` (Full control)
   - 复制生成的Token

3. **编辑.env文件**
   ```bash
   cp .env.example .env
   vim .env
   ```

   修改以下配置：
   ```env
   GIT_SYNC_ENABLED=true
   GIT_REPO_URL=https://github.com/username/wiki-notes.git
   GIT_USERNAME=your-username
   GIT_TOKEN=ghp_xxxxxxxxxxxx
   GIT_BRANCH=main
   GIT_SYNC_INTERVAL=30
   ```

4. **重启服务**
   ```bash
   ./deploy.sh restart
   ```

5. **验证同步**
   - 登录Wiki管理后台
   - 进入"存储" → "Git"
   - 查看同步状态

---

## 插件系统使用

### 启用插件管理器

```bash
# 启动时包含plugins profile
docker compose --profile plugins up -d

# 查看插件状态
docker compose logs plugin-manager
```

### 已提供的示例插件

#### 1. 每日信息汇总 (daily-digest)

**功能**: 自动抓取Hacker News、GitHub Trending等网站，使用AI整理成日报

**配置**:
```json
// plugins/daily-digest/plugin.json
{
  "config": {
    "sources": [
      {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com",
        "type": "news"
      }
    ],
    "ai_enabled": true,
    "schedule": "0 8 * * *"
  }
}
```

**启用**:
```bash
# 编辑 plugins/plugins_config.json
{
  "plugins": {
    "daily-digest": {
      "enabled": true
    }
  }
}

# 重启插件管理器
docker compose --profile plugins restart plugin-manager
```

#### 2. 通用网页爬虫 (web-scraper)

**功能**: 可配置的网页爬虫，支持自定义URL和提取规则

**配置示例**:
```json
{
  "targets": [
    {
      "name": "技术博客",
      "url": "https://example.com/blog",
      "selector": "article.post",
      "interval": "6h"
    }
  ]
}
```

### 开发自己的插件

参考: [插件开发指南](PLUGIN_DEVELOPMENT_GUIDE.md)

**快速模板**:
```bash
mkdir plugins/my-plugin
cp plugins/daily-digest/plugin.json plugins/my-plugin/
cp plugins/daily-digest/plugin.py plugins/my-plugin/

# 编辑配置文件和代码
vim plugins/my-plugin/plugin.json
vim plugins/my-plugin/plugin.py
```

---

## AI集成功能

### 配置OpenAI

1. **获取API Key**
   - 访问: https://platform.openai.com/api-keys
   - 创建新的API Key

2. **配置环境变量**
   ```bash
   # 编辑 .env
   OPENAI_API_KEY=sk-your-api-key-here
   ```

3. **重启服务**
   ```bash
   docker compose --profile plugins up -d
   ```

### 使用AI功能

#### 在插件中使用

```python
from plugins.core.ai_client import get_ai_client

# 获取AI客户端
ai = get_ai_client('openai')

# 生成内容
summary = ai.summarize(long_text)
keywords = ai.extract_keywords(text)
translation = ai.translate(text, "中文")
```

#### 支持的AI操作

1. **文本总结**
   ```python
   summary = ai.summarize(text, max_words=200)
   ```

2. **关键词提取**
   ```python
   keywords = ai.extract_keywords(text, max_keywords=10)
   ```

3. **内容分类**
   ```python
   category = ai.classify_content(text, ["技术", "新闻", "教程"])
   ```

4. **翻译**
   ```python
   translated = ai.translate(text, "英文")
   ```

5. **自由生成**
   ```python
   result = ai.generate("写一篇关于Python的文章")
   ```

### 成本优化建议

- 使用`gpt-3.5-turbo`而非`gpt-4`降低成本
- 设置合理的`max_tokens`限制
- 缓存常用结果
- 批量处理请求

---

## 自动化任务

### 定时备份

#### Linux/macOS

```bash
# 设置定时备份
chmod +x scripts/setup-cron.sh
./scripts/setup-cron.sh

# 选择备份频率:
# 1. 每天凌晨2点
# 2. 每6小时
# 3. 每周日
# 4. 自定义
```

#### Windows

使用任务计划程序：
1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器: 每天2:00
4. 操作: 运行程序
   - 程序: `f:\wikidemotongyi\scripts\backup.bat`

### 手动备份

```bash
# Linux/macOS
./deploy.sh backup

# Windows
deploy.bat backup
```

### 恢复备份

```bash
# 查看可用备份
ls backups/

# 恢复指定备份
./deploy.sh restore backups/20260514_120000
```

---

## 性能优化

### Nginx优化

编辑 `nginx/nginx.conf`:

```nginx
worker_processes auto;  # 自动检测CPU核心数

events {
    worker_connections 2048;  # 增加连接数
}

http {
    # 启用Gzip压缩
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript;

    # 缓存静态文件
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 数据库优化

PostgreSQL已配置基本优化，如需进一步优化：

```sql
-- 连接到数据库
docker compose exec db psql -U wikiuser wikidb

-- 分析表性能
ANALYZE;

-- 重建索引
REINDEX DATABASE wikidb;
```

### Docker资源限制

编辑 `docker-compose.yml`:

```yaml
services:
  wiki:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 512M

  db:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### CDN加速（可选）

对于公开访问的Wiki，可以配置CDN：
- Cloudflare（免费）
- 阿里云CDN
- 腾讯云CDN

---

## 监控和告警

### 健康检查

```bash
# 检查所有服务状态
./deploy.sh status

# 查看资源使用
docker stats

# 查看日志
docker compose logs -f
```

### 日志管理

```bash
# 清理旧日志
find logs/ -name "*.log" -mtime +30 -delete

# 日志轮转（安装logrotate）
sudo apt install logrotate
```

### 简单的监控脚本

创建 `scripts/monitor.sh`:

```bash
#!/bin/bash

# 检查服务是否运行
if ! docker compose ps | grep -q "Up"; then
    echo "警告: Wiki.js服务异常" | mail -s "Wiki监控告警" admin@example.com
fi

# 检查磁盘空间
usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $usage -gt 90 ]; then
    echo "警告: 磁盘使用率 ${usage}%" | mail -s "磁盘空间告警" admin@example.com
fi
```

添加到crontab:
```cron
*/30 * * * * /path/to/monitor.sh
```

---

## 安全加固

### 1. 修改默认密码

首次登录后立即修改管理员密码。

### 2. 启用HTTPS

使用Let's Encrypt免费证书：

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d wiki.yourdomain.com
```

### 3. 配置防火墙

```bash
# 只允许必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. IP白名单（内网访问）

编辑 `nginx/conf.d/wiki.conf`:

```nginx
# 只允许特定IP段访问
allow 192.168.1.0/24;
allow 10.0.0.0/8;
deny all;
```

### 5. 定期更新

```bash
# 更新Docker镜像
docker compose pull
docker compose up -d

# 清理旧镜像
docker image prune -f
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 查看详细日志
docker compose logs

# 检查端口占用
netstat -tlnp | grep -E '80|443'
```

#### 2. 插件不工作

```bash
# 查看插件日志
docker compose logs plugin-manager

# 检查配置
cat plugins/plugins_config.json
```

#### 3. Git同步失败

```bash
# 检查Git配置
docker compose exec wiki env | grep GIT

# 测试Git连接
docker compose exec wiki git ls-remote
```

#### 4. 数据库连接错误

```bash
# 检查数据库状态
docker compose ps db

# 查看数据库日志
docker compose logs db
```

### 重置系统

如果遇到问题需要重置：

```bash
# 停止服务
./deploy.sh stop

# 删除数据（谨慎操作！）
docker compose down -v

# 重新启动
./deploy.sh start
```

---

## 扩展阅读

- [README.md](../README.md) - 基础使用文档
- [QUICKSTART.md](../QUICKSTART.md) - 快速开始
- [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md) - 插件开发
- [GIT_SYNC_GUIDE.md](GIT_SYNC_GUIDE.md) - Git同步详解

---

**提示**: 定期查阅文档和更新系统，保持最佳性能和安全性。
