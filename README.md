# Wiki.js 个人知识管理系统 - 增强版 v1.0.0

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](RELEASE_v1.0.0.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-compose-blue?logo=docker)](https://docs.docker.com/compose/)
[![Wiki.js](https://img.shields.io/badge/wiki.js-2.5+-green)](https://wiki.js.org/)
[![Python](https://img.shields.io/badge/python-3.11-yellow)](https://www.python.org/)
[![C](https://img.shields.io/badge/C-Performance-orange)](plugins/markdown-optimizer/README.md)

基于 [Wiki.js](https://wiki.js.org/) 构建的**功能增强型个人知识库系统**，支持IPv4/IPv6双栈访问，集成RSS阅读器、Obsidian双向同步、配置管理、日志管理等高级功能。**v1.0.0** 版本新增C语言高性能插件支持和完整的云原生架构！

## ✨ 核心特性

### 🏗️ 基础架构
- ✅ **IPv4/IPv6双栈支持** - 完全兼容现代网络环境
- ✅ **Docker容器化部署** - 一键启动，隔离运行
- ✅ **Nginx反向代理** - 高性能HTTP服务
- ✅ **PostgreSQL数据库** - 可靠的数据存储
- ✅ **Git自动备份** - 版本控制与数据恢复

### 🔌 插件系统
- ✅ **可扩展插件框架** - 独立容器运行，不影响主系统
- ✅ **RSS阅读器插件** - 自动抓取技术资讯，AI生成摘要
- ✅ **任务调度引擎** - Cron表达式定时执行
- ✅ **AI集成能力** - OpenAI API支持

### 📝 笔记同步
- ✅ **Obsidian双向同步** - 本地与Wiki智能同步
- ✅ **冲突检测与解决** - 草稿箱机制，手动合并
- ✅ **增量同步** - 基于哈希追踪，只同步变更文件
- ✅ **选择性同步** - 按文件夹/标签过滤

### ⚙️ 配置管理
- ✅ **CLI + Web UI双模** - 满足不同用户群体
- ✅ **配置模板** - 预设个人Wiki、团队协作等场景
- ✅ **配置回滚** - 快照机制，随时恢复到历史状态
- ✅ **REST API** - 可编程配置管理

### 📊 日志系统
- ✅ **集中式日志收集** - 所有服务日志统一管理
- ✅ **Web日志查看器** - 实时浏览、搜索日志
- ✅ **日志轮转** - 自动压缩归档，节省空间
- ✅ **日志清理** - 定期删除过期日志
- ✅ **关键词搜索** - 跨文件快速定位问题

## 📋 系统要求

- **Docker**: 20.10+
- **Docker Compose**: V2
- **操作系统**: Linux / Windows / macOS
- **内存**: 建议 2GB+
- **磁盘**: 建议 10GB+ (含数据备份)
- **IPv6**: 可选，但推荐启用

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/wikidemotongyi.git
cd wikidemotongyi
```

### 2. 配置环境变量（可选）

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑配置文件
vim .env  # Linux/macOS
notepad .env  # Windows
```

主要配置项：
- `POSTGRES_PASSWORD` - 数据库密码（建议修改）
- `GIT_REPO_URL` - Git仓库地址（用于自动备份）
- `OPENAI_API_KEY` - OpenAI API密钥（用于AI摘要）

### 3. 运行测试（推荐）

```bash
# 赋予执行权限
chmod +x scripts/run-all-tests.sh

# 运行完整测试套件（约5-10分钟）
./scripts/run-all-tests.sh
```

**测试内容：**
- ✅ Docker环境检查
- ✅ 服务启动测试
- ✅ Wiki.js功能测试
- ✅ 插件系统测试（含C语言插件）
- ✅ 配置管理测试
- ✅ 日志系统测试
- ✅ 性能基准测试

详见 [DEVELOPER_TESTING_GUIDE.md](DEVELOPER_TESTING_GUIDE.md)

### 4. 启动服务

**Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh start
```

**Windows:**
```bash
deploy.bat start
```

首次启动会自动下载镜像并初始化，约需2-5分钟。

### 4. 访问Wiki

服务启动后，通过以下地址访问：

- **IPv4**: http://localhost
- **IPv6**: http://[::1]
- **局域网**: http://你的IP地址

**初始登录凭证:**
- 邮箱: `admin@example.com`
- 密码: `changeme123`

⚠️ **重要：** 首次登录后请立即修改密码！

## 📖 功能使用指南

### RSS阅读器插件

自动抓取技术资讯并生成AI摘要，每小时执行一次。

**快速开始:**
```bash
# 查看RSS插件状态
docker compose logs rss-reader

# 手动触发执行
docker compose exec rss-reader python /app/plugins/rss-reader/plugin.py --run-now
```

详细文档: [RSS_READER_GUIDE.md](docs/RSS_READER_GUIDE.md) | [快速入门](RSS_QUICKSTART.md)

---

### Obsidian双向同步

实现本地Obsidian与Wiki.js的智能同步，支持冲突处理。

**配置步骤:**
1. 复制配置模板: `cp obsidian-sync-config.example.json obsidian-sync-config.json`
2. 编辑配置，指定同步目录和策略
3. 运行同步: `python scripts/obsidian-sync/sync_manager.py sync`

**冲突处理:**
当检测到冲突时，会在 `drafts/` 目录生成交替版本，手动合并后标记解决。

详细文档: [OBSIDIAN_SYNC_GUIDE.md](docs/OBSIDIAN_SYNC_GUIDE.md) | [快速入门](OBSIDIAN_SYNC_QUICKSTART.md)

---

### 配置管理系统

提供CLI和Web UI两种方式管理Wiki配置。

**CLI方式:**
```bash
# 查看当前配置
python config-manager/config_cli.py list

# 应用配置模板
python config-manager/config_cli.py apply personal-wiki

# 创建配置快照
python config-manager/config_cli.py snapshot "更新前备份"

# 回滚到快照
python config-manager/config_cli.py rollback 0
```

**Web UI方式:**
访问 http://localhost/config 打开配置管理界面。

详细文档: [CONFIG_MANAGER_GUIDE.md](docs/CONFIG_MANAGER_GUIDE.md)

---

### 日志管理系统

集中管理所有服务的日志文件。

**CLI方式:**
```bash
# 查看日志列表
python log-manager/log_cli.py list

# 查看Wiki.js日志末尾100行
python log-manager/log_cli.py tail wiki-js.log 100

# 搜索包含"error"的日志
python log-manager/log_cli.py search error

# 轮转日志（压缩大于1MB的文件）
python log-manager/log_cli.py rotate

# 清理30天前的归档日志
python log-manager/log_cli.py cleanup 30
```

**Web UI方式:**
访问 http://localhost/logs 打开日志查看器。

详细文档: [LOG_MANAGEMENT_GUIDE.md](docs/LOG_MANAGEMENT_GUIDE.md)

## 📁 项目结构

```
wikidemotongyi/
├── docker-compose.yml          # Docker编排文件
├── .env.example                # 环境配置模板
├── .gitignore                  # Git忽略规则
├── requirements.txt            # Python依赖
├── deploy.sh                   # Linux/macOS部署脚本
├── deploy.bat                  # Windows部署脚本
│
├── nginx/                      # Nginx配置
│   ├── nginx.conf              # 主配置（IPv6支持）
│   └── conf.d/
│       └── wiki.conf           # Wiki.js反向代理
│
├── plugins/                    # 插件系统
│   ├── core/
│   │   ├── plugin_manager.py   # 插件管理器
│   │   └── task_scheduler.py   # 任务调度器
│   └── rss-reader/             # RSS阅读器插件
│       ├── plugin.py
│       ├── plugin.json
│       └── README.md
│
├── scripts/                    # 工具脚本
│   └── obsidian-sync/          # Obsidian同步工具
│       ├── sync_manager.py
│       ├── conflict_resolver.py
│       └── README.md
│
├── config-manager/             # 配置管理系统
│   ├── config_engine.py        # 配置引擎
│   ├── config_cli.py           # CLI工具
│   ├── web_server.py           # Web服务器
│   ├── web_ui.html             # Web界面
│   └── templates/              # 配置模板
│       ├── personal-wiki.json
│       ├── team-collab.json
│       └── ai-powered.json
│
├── log-manager/                # 日志管理系统
│   ├── log_manager.py          # 日志管理器
│   ├── log_cli.py              # CLI工具
│   └── log_viewer.html         # Web查看器
│
├── docs/                       # 完整文档
│   ├── PROJECT_OVERVIEW.md     # 项目总览
│   ├── GIT_SYNC_GUIDE.md       # Git同步指南
│   ├── PLUGIN_DEVELOPMENT_GUIDE.md  # 插件开发指南
│   ├── ADVANCED_FEATURES.md    # 高级功能
│   ├── RSS_READER_GUIDE.md     # RSS阅读器指南
│   ├── OBSIDIAN_SYNC_GUIDE.md  # Obsidian同步指南
│   ├── CONFIG_MANAGER_GUIDE.md # 配置管理指南
│   ├── LOG_MANAGEMENT_GUIDE.md # 日志管理指南
│   └── ...
│
├── data/                       # 数据目录（运行时创建）
│   ├── postgres/               # PostgreSQL数据
│   └── wiki/                   # Wiki.js数据
│
└── logs/                       # 日志目录（运行时创建）
    ├── nginx/                  # Nginx日志
    ├── wiki-js/                # Wiki.js日志
    ├── config-manager/         # 配置管理日志
    └── log-manager/            # 日志管理自身日志
```

## 🔧 常用命令

### 服务管理

```bash
# 启动服务
./deploy.sh start              # Linux/macOS
deploy.bat start               # Windows

# 停止服务
./deploy.sh stop
deploy.bat stop

# 重启服务
./deploy.sh restart
deploy.bat restart

# 查看状态
./deploy.sh status
deploy.bat status

# 查看日志
./deploy.sh logs wiki          # Wiki.js日志
./deploy.sh logs nginx         # Nginx日志
./deploy.sh logs db            # 数据库日志
./deploy.sh logs rss-reader    # RSS插件日志
```

### 数据备份

```bash
# 自动备份（Git推送）
./deploy.sh backup

# 手动备份数据库
docker compose exec db pg_dump -U wikiuser wikidb > backup.sql

# 恢复数据库
cat backup.sql | docker compose exec -T db psql -U wikiuser wikidb
```

### 插件管理

```bash
# 查看已安装插件
docker compose exec plugin-manager python /app/plugins/core/plugin_manager.py list

# 启用/禁用插件
docker compose exec plugin-manager python /app/plugins/core/plugin_manager.py enable rss-reader
docker compose exec plugin-manager python /app/plugins/core/plugin_manager.py disable rss-reader

# 查看插件日志
docker compose logs rss-reader
```

### 同步管理

```bash
# 执行Obsidian同步
python scripts/obsidian-sync/sync_manager.py sync

# 查看同步状态
python scripts/obsidian-sync/sync_manager.py status

# 解决冲突
python scripts/obsidian-sync/sync_manager.py resolve-conflict <conflict_id>
```

## 🌐 IPv6配置说明

### 检查IPv6支持

**Linux:**
```bash
ip -6 addr show
curl -g http://[::1]
```

**Windows:**
```powershell
ipconfig | findstr "IPv6"
Test-NetConnection -ComputerName ::1 -Port 80
```

### Docker IPv6配置

如果Docker未启用IPv6，编辑 `/etc/docker/daemon.json`:

```json
{
  "ipv6": true,
  "fixed-cidr-v6": "fd00::/80"
}
```

重启Docker:
```bash
sudo systemctl restart docker
```

## 🔒 安全建议

1. ⚠️ **立即修改默认密码** - 首次登录后修改管理员密码
2. 🔒 **启用HTTPS** - 生产环境使用SSL证书
3. 🛡️ **配置防火墙** - 仅开放必要端口
4. 🔑 **定期更新** - 保持Docker镜像为最新版本
5. 💾 **定期备份** - 使用Git自动备份或手动备份
6. 👥 **限制访问** - 使用Nginx IP白名单或认证

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker compose logs

# 检查端口占用
netstat -tlnp | grep -E '80|443'  # Linux
netstat -ano | findstr "80"        # Windows
```

### 无法通过IPv6访问

1. 确认系统支持IPv6
2. 确认Docker启用了IPv6
3. 检查防火墙设置
4. 测试本地连接: `curl -g http://[::1]`

### 数据库连接失败

```bash
# 检查数据库状态
docker compose ps db
docker compose logs db

# 重置数据库（警告：会丢失数据）
docker compose down -v
docker compose up -d db
```

### 插件不工作

```bash
# 查看插件日志
docker compose logs rss-reader

# 重启插件容器
docker compose restart rss-reader

# 检查插件配置
docker compose exec rss-reader cat /app/plugins/rss-reader/plugin.json
```

### 同步冲突

```bash
# 查看冲突列表
python scripts/obsidian-sync/sync_manager.py list-conflicts

# 查看冲突详情
cat drafts/<conflict_id>.md

# 解决冲突后标记完成
python scripts/obsidian-sync/sync_manager.py resolve-conflict <conflict_id>
```

## 📚 完整文档

- [项目总览](docs/PROJECT_OVERVIEW.md) - 架构设计和技术栈
- [Git同步指南](docs/GIT_SYNC_GUIDE.md) - 自动备份配置
- [插件开发指南](docs/PLUGIN_DEVELOPMENT_GUIDE.md) - 开发自定义插件
- [高级功能](docs/ADVANCED_FEATURES.md) - 性能优化和扩展
- [RSS阅读器指南](docs/RSS_READER_GUIDE.md) - 配置和使用
- [Obsidian同步指南](docs/OBSIDIAN_SYNC_GUIDE.md) - 双向同步详解
- [配置管理指南](docs/CONFIG_MANAGER_GUIDE.md) - 配置模板和回滚
- [日志管理指南](docs/LOG_MANAGEMENT_GUIDE.md) - 日志查看和清理
- [修复和优化记录](docs/FIXES_AND_OPTIMIZATIONS.md) - 已知问题和解决方案

## 🔄 更新升级

```bash
# 拉取最新代码
git pull

# 更新Docker镜像
docker compose pull

# 重启服务
docker compose up -d

# 清理旧镜像
docker image prune -f
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

## 📄 License

本项目使用的组件：
- **Wiki.js**: AGPL-3.0
- **PostgreSQL**: PostgreSQL License
- **Nginx**: BSD-like license
- **部署脚本和配置**: MIT License

## 🙏 致谢

- [Wiki.js](https://wiki.js.org/) - 强大的开源Wiki引擎
- [Obsidian](https://obsidian.md/) - 优秀的本地知识管理工具
- [OpenAI](https://openai.com/) - 提供AI摘要生成能力

---

**注意：** 本部署方案专为IPv6网络环境设计，同时也完全兼容IPv4网络。

**最后更新:** 2026-05-15
