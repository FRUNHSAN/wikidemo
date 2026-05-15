# 快速参考卡片 🚀

## 一键启动

```bash
# Windows
deploy.bat start

# Linux/macOS
./deploy.sh start
```

## 访问地址

- **本地**: http://localhost 或 http://[::1]
- **初始账号**: admin@example.com / changeme123

---

## 常用命令速查

### 服务管理

```bash
# 启动
./deploy.sh start

# 停止
./deploy.sh stop

# 重启
./deploy.sh restart

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs          # 所有日志
./deploy.sh logs wiki     # Wiki日志
./deploy.sh logs nginx    # Nginx日志
```

### 备份恢复

```bash
# 手动备份
./deploy.sh backup

# 恢复备份
./deploy.sh restore backups/20260514_120000

# 设置定时备份
./scripts/setup-cron.sh
```

### 插件系统

```bash
# 启动插件系统
docker compose --profile plugins up -d

# 查看插件日志
docker compose logs -f plugin-manager

# 重启插件
docker compose --profile plugins restart plugin-manager
```

---

## 配置文件位置

| 文件 | 用途 |
|------|------|
| `.env` | 环境变量（密码、API Key等） |
| `docker-compose.yml` | Docker配置 |
| `plugins/plugins_config.json` | 插件配置 |
| `nginx/conf.d/wiki.conf` | Nginx配置 |

---

## Git同步配置（3步）

```bash
# 1. 编辑.env
vim .env

# 修改以下配置：
GIT_SYNC_ENABLED=true
GIT_REPO_URL=https://github.com/username/wiki-notes.git
GIT_USERNAME=your-username
GIT_TOKEN=ghp_xxxxxxxxxxxx

# 2. 重启服务
./deploy.sh restart

# 3. 验证
# 登录Wiki后台 → 存储 → Git
```

---

## AI功能配置

```bash
# 1. 编辑.env
OPENAI_API_KEY=sk-your-key-here

# 2. 启动插件系统
docker compose --profile plugins up -d

# 3. 启用日报插件
# 编辑 plugins/plugins_config.json
# 设置 daily-digest.enabled = true
```

---

## 故障排查

### 服务无法启动
```bash
# 查看详细错误
docker compose logs

# 检查端口占用
netstat -tlnp | grep -E '80|443'
```

### 插件不工作
```bash
# 查看插件日志
docker compose logs plugin-manager

# 检查配置
cat plugins/plugins_config.json
```

### 数据备份
```bash
# 紧急备份
docker compose exec db pg_dump -U wikiuser wikidb > emergency_backup.sql
```

---

## 文档索引

- 📘 [完整文档](README.md)
- 🚀 [快速开始](QUICKSTART.md)
- 🔧 [高级功能](docs/ADVANCED_FEATURES.md)
- 🔌 [插件开发](docs/PLUGIN_DEVELOPMENT_GUIDE.md)
- 📦 [Git同步](docs/GIT_SYNC_GUIDE.md)
- 📊 [项目总览](docs/PROJECT_OVERVIEW.md)

---

## 快捷链接

- Wiki.js官方文档: https://docs.requarks.io/
- Docker文档: https://docs.docker.com/
- OpenAI API: https://platform.openai.com/docs

---

**提示**: 将此文件加入书签，方便快速查阅！
