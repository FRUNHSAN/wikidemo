# WikiDemoTongYi v1.0.0 快速参考卡片

## 🚀 一键启动

```bash
# 克隆项目
git clone https://github.com/wikidemotongyi/wikidemotongyi.git
cd wikidemotongyi

# 运行测试（推荐）
chmod +x scripts/run-all-tests.sh
./scripts/run-all-tests.sh

# 或直接启动
./deploy.sh start
```

---

## 📋 常用命令速查

### 服务管理

```bash
# 启动/停止/重启
./deploy.sh start/stop/restart

# 查看状态
docker compose ps
docker stats

# 查看日志
docker compose logs -f [service]
docker compose logs --tail=100 wiki

# 进入容器
docker compose exec wiki sh
docker compose exec markdown-optimizer sh
```

### 插件管理

```bash
# 列出插件
python scripts/plugin-marketplace.py list

# 安装插件
python scripts/plugin-marketplace.py install rss-reader

# 搜索插件
python scripts/plugin-marketplace.py search ai
```

### 配置管理

```bash
# CLI方式
python config-manager/config_cli.py list
python config-manager/config_cli.py apply personal-wiki
python config-manager/config_cli.py snapshot "backup"
python config-manager/config_cli.py rollback 0

# Web UI
open http://localhost/config
```

### 日志管理

```bash
# CLI方式
python log-manager/log_cli.py list
python log-manager/log_cli.py tail wiki-js.log 100
python log-manager/log_cli.py search error
python log-manager/log_cli.py rotate
python log-manager/log_cli.py cleanup 30

# Web UI
open http://localhost/logs
```

---

## 🌐 访问地址

| 服务 | URL | 说明 |
|------|-----|------|
| **Wiki.js** | http://localhost | 主应用 |
| **配置管理** | http://localhost/config | Web UI |
| **日志查看** | http://localhost/logs | Web UI |
| **C插件API** | http://localhost:8080 | REST API |
| **健康检查** | http://localhost:8080/health | 插件状态 |

**初始登录：**
- 邮箱: `admin@example.com`
- 密码: `changeme123`

---

## 🔍 日志查看命令

### 快速查看

```bash
# 所有服务
docker compose logs

# 特定服务
docker compose logs wiki        # Wiki.js
docker compose logs db          # PostgreSQL
docker compose logs nginx       # Nginx
docker compose logs rss-reader  # RSS插件
docker compose logs markdown-optimizer  # C插件

# 实时跟踪
docker compose logs -f wiki

# 最近100行
docker compose logs --tail=100 wiki
```

### 高级过滤

```bash
# 搜索错误
docker compose logs | grep -i error

# 搜索关键词
docker compose logs | grep "plugin"

# 导出日志
docker compose logs wiki > wiki.log

# 带时间戳
docker compose logs -t wiki
```

---

## 🧪 性能测试

### C语言插件基准测试

```bash
# 快速测试
curl -X POST http://localhost:8080/api/benchmark | python3 -m json.tool

# 完整测试
cd plugins/markdown-optimizer
./benchmark.sh

# ab压力测试
ab -n 10000 -c 100 \
   -p test.json \
   -T "application/json" \
   http://localhost:8080/api/parse
```

### 预期性能

| 指标 | 目标值 |
|------|--------|
| QPS | 5000+ |
| 平均延迟 | <1ms |
| P99延迟 | <5ms |
| 内存占用 | <128MB |

---

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细错误
docker compose logs

# 检查端口占用
netstat -tlnp | grep 80

# 重启服务
docker compose restart
```

### Wiki无法访问

```bash
# 检查容器状态
docker compose ps wiki

# 测试内部连接
docker compose exec wiki curl http://localhost:3000

# 查看Nginx配置
docker compose exec nginx nginx -t
```

### 插件不工作

```bash
# 查看插件日志
docker compose logs markdown-optimizer

# 检查健康状态
curl http://localhost:8080/health

# 重启插件
docker compose restart markdown-optimizer
```

---

## 📁 项目结构速览

```
wikidemotongyi/
├── 📄 核心文件
│   ├── docker-compose.yml      # Docker编排
│   ├── .env.example            # 环境模板
│   └── requirements.txt        # Python依赖
│
├── 🚀 脚本
│   ├── deploy.sh/bat           # 部署脚本
│   └── scripts/run-all-tests.sh # 测试套件
│
├── 🔌 插件
│   ├── rss-reader/             # RSS插件
│   └── markdown-optimizer/     # C语言插件 ⭐
│
├── ⚙️ 工具
│   ├── config-manager/         # 配置管理
│   ├── log-manager/            # 日志管理
│   └── obsidian-sync/          # Obsidian同步
│
└── 📚 文档
    ├── README.md               # 主文档
    ├── DEVELOPER_TESTING_GUIDE.md  # 测试指南 ⭐
    └── docs/                   # 详细文档
```

---

## 🎯 开发新插件（3步）

```bash
# 1. 复制模板
cp -r plugins/TEMPLATE plugins/my-plugin

# 2. 修改配置
cd plugins/my-plugin
vim plugin.json
vim src/main.c  # 或其他语言

# 3. 构建测试
docker build -t my-plugin .
docker run -p 8080:8080 my-plugin
```

详见 [docs/CLOUD_NATIVE_PLUGIN_GUIDE.md](docs/CLOUD_NATIVE_PLUGIN_GUIDE.md)

---

## 📊 资源限制

### 默认限制

| 服务 | CPU | 内存 |
|------|-----|------|
| Wiki.js | 1.0 | 1GB |
| PostgreSQL | 0.5 | 512MB |
| Nginx | 0.2 | 128MB |
| C插件 | 1.0 | 128MB |
| Python插件 | 0.5 | 256MB |

### 调整限制

编辑 `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 512M
```

---

## 🔒 安全提示

- ✅ 首次登录后立即修改密码
- ✅ 生产环境启用HTTPS
- ✅ 不要提交 `.env` 文件
- ✅ 定期更新Docker镜像
- ✅ 使用强密码策略

---

## 📞 获取帮助

- 📖 完整文档: `docs/` 目录
- 🐛 报告问题: [GitHub Issues](https://github.com/wikidemotongyi/wikidemotongyi/issues)
- 💬 讨论交流: [Discussions](https://github.com/wikidemotongyi/wikidemotongyi/discussions)
- 📧 邮件联系: team@wikidemotongyi.com

---

**版本**: v1.0.0  
**最后更新**: 2026-05-15
