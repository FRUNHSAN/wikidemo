# 快速开始指南

## 🚀 5分钟快速部署

### 前置要求

- Docker 20.10+
- Docker Compose V2
- 2GB+ 可用内存
- 10GB+ 磁盘空间

### 步骤1: 克隆项目

```bash
git clone https://github.com/your-username/wikidemotongyi.git
cd wikidemotongyi
```

### 步骤2: 配置环境（可选）

```bash
cp .env.example .env
# 编辑 .env 文件，修改数据库密码等
```

### 步骤3: 启动服务

**Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh start
```

**Windows:**
```bash
deploy.bat start
```

等待2-5分钟，直到所有服务启动完成。

### 步骤4: 访问Wiki

打开浏览器访问: http://localhost

**初始登录:**
- 邮箱: `admin@example.com`
- 密码: `changeme123`

⚠️ **首次登录后请立即修改密码！**

---

## 📖 常用操作

### 查看服务状态

```bash
./deploy.sh status        # Linux/macOS
deploy.bat status         # Windows
```

### 查看日志

```bash
./deploy.sh logs wiki     # Wiki.js日志
./deploy.sh logs nginx    # Nginx日志
./deploy.sh logs db       # 数据库日志
```

### 停止服务

```bash
./deploy.sh stop          # Linux/macOS
deploy.bat stop           # Windows
```

### 重启服务

```bash
./deploy.sh restart       # Linux/macOS
deploy.bat restart        # Windows
```

---

## 🔌 启用高级功能

### RSS阅读器插件

RSS插件默认已安装，每小时自动执行。

**手动触发:**
```bash
docker compose exec rss-reader python /app/plugins/rss-reader/plugin.py --run-now
```

**查看详细文档:** [RSS_QUICKSTART.md](RSS_QUICKSTART.md)

---

### Obsidian同步

**1. 配置同步:**
```bash
cp obsidian-sync-config.example.json obsidian-sync-config.json
# 编辑配置文件，指定Obsidian目录
```

**2. 执行同步:**
```bash
python scripts/obsidian-sync/sync_manager.py sync
```

**查看详细文档:** [OBSIDIAN_SYNC_QUICKSTART.md](OBSIDIAN_SYNC_QUICKSTART.md)

---

### 配置管理

**CLI方式:**
```bash
# 查看配置
python config-manager/config_cli.py list

# 应用模板
python config-manager/config_cli.py apply personal-wiki
```

**Web UI方式:**
访问 http://localhost/config

**查看详细文档:** [docs/CONFIG_MANAGER_GUIDE.md](docs/CONFIG_MANAGER_GUIDE.md)

---

### 日志管理

**CLI方式:**
```bash
# 查看日志列表
python log-manager/log_cli.py list

# 搜索错误
python log-manager/log_cli.py search error
```

**Web UI方式:**
访问 http://localhost/logs

**查看详细文档:** [docs/LOG_MANAGEMENT_GUIDE.md](docs/LOG_MANAGEMENT_GUIDE.md)

---

## 🐛 常见问题

### 服务启动失败

```bash
# 查看详细错误
docker compose logs

# 检查端口占用
netstat -tlnp | grep 80
```

### 无法访问Wiki

1. 确认Docker容器正在运行: `docker compose ps`
2. 检查防火墙设置
3. 尝试访问 http://127.0.0.1

### 数据库连接错误

```bash
# 重启数据库
docker compose restart db

# 查看数据库日志
docker compose logs db
```

---

## 📚 更多资源

- [完整README](README.md)
- [项目总览](docs/PROJECT_OVERVIEW.md)
- [故障排查](README.md#-故障排查)
- [GitHub Issues](https://github.com/your-username/wikidemotongyi/issues)

---

**祝你使用愉快！** 🎉
