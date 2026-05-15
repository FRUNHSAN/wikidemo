# WikiDemoTongYi 使用说明

## 🚀 快速启动

### 1. 启动服务

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

### 2. 访问Wiki

打开浏览器访问: **http://localhost**

**初始登录:**
- 邮箱: `admin@example.com`
- 密码: `changeme123`

⚠️ **首次登录后请立即修改密码！**

---

## 📖 核心功能使用

### RSS阅读器插件

**查看状态:**
```bash
docker compose logs rss-reader
```

**手动触发执行:**
```bash
docker compose exec rss-reader python /app/plugins/rss-reader/plugin.py --run-now
```

**查看详细文档:** [RSS_QUICKSTART.md](RSS_QUICKSTART.md)

---

### Obsidian双向同步

**1. 配置同步:**
```bash
cp obsidian-sync-config.example.json obsidian-sync-config.json
# 编辑配置文件，指定你的Obsidian目录
```

**2. 执行同步:**
```bash
python scripts/obsidian-sync/sync_manager.py sync
```

**3. 查看冲突:**
```bash
python scripts/obsidian-sync/sync_manager.py list-conflicts
```

**查看详细文档:** [OBSIDIAN_SYNC_QUICKSTART.md](OBSIDIAN_SYNC_QUICKSTART.md)

---

### 配置管理系统

**CLI方式:**
```bash
# 查看当前配置
python config-manager/config_cli.py list

# 应用配置模板
python config-manager/config_cli.py apply personal-wiki

# 创建快照
python config-manager/config_cli.py snapshot "更新前备份"

# 回滚到快照
python config-manager/config_cli.py rollback 0
```

**Web UI方式:**
访问 http://localhost/config

**查看详细文档:** [docs/CONFIG_MANAGER_GUIDE.md](docs/CONFIG_MANAGER_GUIDE.md)

---

### 日志管理系统

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
访问 http://localhost/logs

**查看详细文档:** [docs/LOG_MANAGEMENT_GUIDE.md](docs/LOG_MANAGEMENT_GUIDE.md)

---

## 🔧 常用命令

### 服务管理

```bash
# 查看状态
./deploy.sh status              # Linux/macOS
deploy.bat status               # Windows

# 停止服务
./deploy.sh stop
deploy.bat stop

# 重启服务
./deploy.sh restart
deploy.bat restart

# 查看日志
./deploy.sh logs wiki           # Wiki.js日志
./deploy.sh logs nginx          # Nginx日志
./deploy.sh logs db             # 数据库日志
./deploy.sh logs rss-reader     # RSS插件日志
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

### Docker操作

```bash
# 查看所有容器
docker compose ps

# 查看实时日志
docker compose logs -f

# 重启特定服务
docker compose restart wiki-js

# 进入容器内部
docker compose exec wiki-js sh
```

---

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细错误
docker compose logs

# 检查端口占用
netstat -tlnp | grep 80        # Linux
netstat -ano | findstr "80"    # Windows
```

### 无法访问Wiki

1. 确认Docker容器正在运行: `docker compose ps`
2. 检查防火墙设置
3. 尝试访问 http://127.0.0.1

### 数据库连接失败

```bash
# 重启数据库
docker compose restart db

# 查看数据库日志
docker compose logs db

# 重置数据库（警告：会丢失数据）
docker compose down -v
docker compose up -d db
```

### RSS插件不工作

```bash
# 查看插件日志
docker compose logs rss-reader

# 检查配置
docker compose exec rss-reader cat /app/plugins/rss-reader/plugin.json

# 重启插件
docker compose restart rss-reader
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

---

## 📚 完整文档索引

### 快速入门
- [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始
- [RSS_QUICKSTART.md](RSS_QUICKSTART.md) - RSS快速入门
- [OBSIDIAN_SYNC_QUICKSTART.md](OBSIDIAN_SYNC_QUICKSTART.md) - Obsidian同步快速入门

### 详细指南
- [README.md](README.md) - 完整项目说明
- [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) - 项目总览
- [docs/GIT_SYNC_GUIDE.md](docs/GIT_SYNC_GUIDE.md) - Git同步配置
- [docs/PLUGIN_DEVELOPMENT_GUIDE.md](docs/PLUGIN_DEVELOPMENT_GUIDE.md) - 插件开发
- [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md) - 高级功能
- [docs/RSS_READER_GUIDE.md](docs/RSS_READER_GUIDE.md) - RSS阅读器详解
- [docs/OBSIDIAN_SYNC_GUIDE.md](docs/OBSIDIAN_SYNC_GUIDE.md) - Obsidian同步详解
- [docs/CONFIG_MANAGER_GUIDE.md](docs/CONFIG_MANAGER_GUIDE.md) - 配置管理
- [docs/LOG_MANAGEMENT_GUIDE.md](docs/LOG_MANAGEMENT_GUIDE.md) - 日志管理
- [docs/FIXES_AND_OPTIMIZATIONS.md](docs/FIXES_AND_OPTIMIZATIONS.md) - 问题修复

### 其他
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
- [CHANGELOG.md](CHANGELOG.md) - 更新日志
- [CHEATSHEET.md](CHEATSHEET.md) - 速查表
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结
- [GITHUB_CHECKLIST.md](GITHUB_CHECKLIST.md) - GitHub上传清单
- [README_GITHUB.md](README_GITHUB.md) - GitHub上传指南

---

## 💡 使用技巧

### 1. IPv6访问

如果你的网络支持IPv6：
```bash
# 本地IPv6访问
curl -g http://[::1]

# 获取本机IPv6地址
ip -6 addr show          # Linux
ipconfig | findstr IPv6  # Windows
```

### 2. 性能优化

**调整Nginx worker数量:**
编辑 `nginx/nginx.conf`:
```nginx
worker_processes auto;
```

**增加PostgreSQL缓存:**
编辑 `docker-compose.yml` 中的db服务环境变量。

### 3. 自定义域名

编辑 `nginx/conf.d/wiki.conf`:
```nginx
server_name wiki.yourdomain.com;
```

### 4. 启用HTTPS

使用Let's Encrypt:
```bash
docker compose exec certbot certbot --nginx -d wiki.yourdomain.com
```

---

## 🎯 下一步建议

1. ✅ **修改默认密码** - 首次登录后立即修改
2. 🔒 **配置HTTPS** - 生产环境必须启用
3. 💾 **设置自动备份** - 配置Git同步或定时备份
4. 📊 **安装监控** - 可选Prometheus + Grafana
5. 🔌 **开发插件** - 根据需求扩展功能

---

## 📞 获取帮助

- 📖 查看完整文档: [README.md](README.md)
- 🐛 报告问题: [GitHub Issues](https://github.com/your-username/wikidemotongyi/issues)
- 💬 讨论交流: [GitHub Discussions](https://github.com/your-username/wikidemotongyi/discussions)

---

**祝你使用愉快！** 🎉

**版本**: v1.0.0  
**最后更新**: 2026-05-15
