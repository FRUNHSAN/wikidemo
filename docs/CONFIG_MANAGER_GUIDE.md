# 配置管理系统使用指南

## 🎯 功能概述

配置管理系统提供了**CLI + Web UI**双模式的配置管理方案，让你可以方便地管理所有Wiki.js相关配置。

### 核心特性

- ✅ **双模界面** - CLI和Web UI共享同一配置引擎
- ✅ **实时验证** - 配置值自动验证
- ✅ **历史记录** - 追踪所有配置变更
- ✅ **导入导出** - 备份和恢复配置
- ✅ **热重载** - 部分配置无需重启

---

## 🚀 快速开始

### 方式1: 使用CLI（推荐技术用户）

```bash
# Windows
python config-manager\config_cli.py

# Linux/macOS
python3 config-manager/config_cli.py
```

### 方式2: 使用Web UI（推荐普通用户）

```bash
# 启动Web服务器
python config-manager\web_server.py

# 浏览器访问
http://localhost:5000
```

---

## 💻 CLI使用指南

### 基本命令

```bash
# 进入交互模式
python config-manager\config_cli.py

# 列出所有配置分组
config> list

# 获取配置值
config> get env OPENAI_API_KEY

# 设置配置值
config> set env OPENAI_API_KEY sk-your-key-here

# 查看历史
config> history 10

# 导出配置
config> export json backup.json

# 导入配置
config> import backup.json
```

### 常用示例

```bash
# 启用RSS插件
config> set plugins plugins.rss-reader.enabled true

# 修改同步策略
config> set sync default_sync_strategy immediate

# 重置配置
config> reset env GIT_SYNC_ENABLED

# 退出
config> quit
```

---

## 🌐 Web UI使用指南

### 启动服务器

```bash
# 安装依赖（首次使用）
pip install flask pyyaml

# 启动
python config-manager\web_server.py
```

### 访问界面

打开浏览器访问: `http://localhost:5000`

### 功能标签页

#### 1. 🔑 环境变量
- 数据库密码
- OpenAI API Key
- Git同步配置

#### 2. 🔌 插件管理
- 启用/禁用插件
- 查看插件状态
- 重启插件

#### 3. 🔄 Obsidian同步
- 配置同步路径
- 设置同步策略
- 文件类型过滤

#### 4. 📜 历史记录
- 查看所有配置变更
- 时间戳和操作详情

---

## ⚙️ 配置项详解

### 环境变量 (env)

| 配置项 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| POSTGRES_PASSWORD | string | 数据库密码 | `wikipassword123` |
| OPENAI_API_KEY | string | OpenAI密钥 | `sk-xxx` |
| WIKI_API_TOKEN | string | Wiki API Token | `token-xxx` |
| GIT_SYNC_ENABLED | boolean | 启用Git同步 | `true/false` |
| GIT_REPO_URL | string | Git仓库地址 | `https://github.com/...` |

### 插件配置 (plugins)

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| rss-reader.enabled | boolean | RSS阅读器 | `true` |
| daily-digest.enabled | boolean | 每日汇总 | `false` |
| web-scraper.enabled | boolean | 网页爬虫 | `false` |

### 同步配置 (sync)

| 配置项 | 类型 | 说明 | 可选值 |
|--------|------|------|--------|
| local_folder | string | Obsidian路径 | `./obsidian-vault` |
| default_sync_strategy | string | 同步策略 | `immediate/auto_confirm/manual/disabled` |
| file_type_filters.allowed_types | list | 文件类型 | `[".md"]` |

---

## 🔧 REST API参考

### 获取配置

```bash
GET /api/config/<section>?key=<key>

# 示例
curl http://localhost:5000/api/config/env?key=OPENAI_API_KEY
```

### 设置配置

```bash
POST /api/config/<section>
Content-Type: application/json

{
  "key": "OPENAI_API_KEY",
  "value": "sk-xxx"
}
```

### 获取插件列表

```bash
GET /api/plugins

# 切换插件状态
POST /api/plugins/rss-reader/toggle
```

### 导出配置

```bash
GET /api/config/export?format=json
```

### 导入配置

```bash
POST /api/config/import?format=json
Content-Type: application/json

{配置数据}
```

---

## 💡 使用场景

### 场景1: 批量部署

```bash
# 1. 在一台机器上配置好
config> export json config-template.json

# 2. 复制到其他机器
scp config-template.json user@other-server:/path/to/wiki

# 3. 导入配置
config> import config-template.json
```

### 场景2: 配置版本控制

```bash
# 定期导出配置到Git
config> export yaml configs/backup-$(date +%Y%m%d).yaml

# 提交到Git
git add configs/
git commit -m "Backup config"
```

### 场景3: 快速切换配置

```bash
# 开发环境配置
config> import dev-config.json

# 生产环境配置
config> import prod-config.json
```

---

## 🔍 故障排查

### 问题1: CLI无法启动

**检查:**
```bash
# 确认Python版本
python --version  # 需要3.8+

# 检查文件是否存在
ls config-manager/config_cli.py
```

### 问题2: Web UI无法访问

**检查:**
```bash
# 安装Flask
pip install flask

# 检查端口占用
netstat -tlnp | grep 5000

# 查看错误日志
python config-manager/web_server.py
```

### 问题3: 配置未生效

**解决:**
```bash
# 大部分配置需要重启服务
./deploy.sh restart

# 或重启特定容器
docker compose restart wiki
```

---

## 🎯 最佳实践

### 1. 定期备份配置

```bash
# 每周备份
config> export json backups/config-$(date +%Y%m%d).json
```

### 2. 使用环境变量管理敏感信息

不要在配置文件中硬编码密码和API Key，使用`.env`文件。

### 3. 测试配置变更

在生产环境应用配置前，先在测试环境验证。

### 4. 记录配置变更原因

在修改配置时，添加注释说明原因。

---

## 📚 相关文档

- [RSS阅读器指南](RSS_READER_GUIDE.md)
- [Obsidian同步指南](OBSIDIAN_SYNC_GUIDE.md)
- [插件开发指南](PLUGIN_DEVELOPMENT_GUIDE.md)

---

**祝你配置愉快！** ⚙️✨
