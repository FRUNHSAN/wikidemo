# 开发者快速测试指南 v1.0.0

## 📋 目录

1. [环境准备](#环境准备)
2. [完整测试链条](#完整测试链条)
3. [分步测试指南](#分步测试指南)
4. [日志查看命令](#日志查看命令)
5. [故障排查](#故障排查)
6. [性能基准测试](#性能基准测试)

---

## ⚠️ Windows用户重要提示

**本项目推荐使用WSL（Windows Subsystem for Linux）环境运行**

### 为什么？

- ✅ **性能**: WSL文件系统比/mnt/f快10倍+
- ✅ **兼容性**: Bash脚本100%兼容
- ✅ **Docker**: 集成更稳定

### 快速设置

```bash
# 1. 打开WSL
wsl

# 2. 迁移项目到WSL文件系统
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/wikidemotongyi/wikidemotongyi.git
cd wikidemotongyi

# 3. 运行测试
chmod +x scripts/run-all-tests.sh
./scripts/run-all-tests.sh
```

### 从Windows访问WSL文件

在VSCode中安装"Remote - WSL"扩展，或通过文件资源管理器访问：
```
\\wsl$\Ubuntu\home\你的用户名\projects\wikidemotongyi
```

---

## 🛠️ 环境准备

### 系统要求

```bash
# 检查Docker版本（需要20.10+）
docker --version
docker compose version

# 检查可用内存（建议2GB+）
free -h          # Linux
systeminfo | findstr "Physical Memory"  # Windows

# 检查磁盘空间（建议10GB+）
df -h            # Linux/macOS
dir              # Windows
```

### 克隆项目

```bash
git clone https://github.com/wikidemotongyi/wikidemotongyi.git
cd wikidemotongyi
```

### 配置Docker镜像加速器（中国大陆用户必选）

**重要**: 在中国大陆访问Docker Hub可能遇到网络超时问题，需要先配置镜像加速器。

#### 自动配置（推荐）

**Windows PowerShell:**
```powershell
.\scripts\setup-docker-mirror.ps1
```

**Linux/WSL:**
```bash
sudo ./scripts/setup-docker-mirror.sh
```

#### 手动配置

1. **Windows Docker Desktop**:
   - Settings → Docker Engine
   - 添加配置：
   ```json
   {
     "registry-mirrors": [
       "https://docker.m.daocloud.io",
       "https://huecker.io",
       "https://dockerhub.timeweb.cloud"
     ]
   }
   ```
   - Apply & restart

2. **Linux**:
   ```bash
   sudo tee /etc/docker/daemon.json <<'EOF'
   {
     "registry-mirrors": [
       "https://docker.m.daocloud.io",
       "https://huecker.io",
       "https://dockerhub.timeweb.cloud"
     ]
   }
   EOF
   sudo systemctl restart docker
   ```

3. **验证配置**:
   ```bash
   docker info | grep -A 3 "Registry Mirrors"
   ```

详细配置指南：[docs/DOCKER_MIRROR_SETUP.md](docs/DOCKER_MIRROR_SETUP.md)

---

### 配置环境变量（可选）

```bash
cp .env.example .env
# 编辑 .env 文件，修改数据库密码等
vim .env  # Linux/WSL
notepad .env  # Windows
```

---

## 🚀 完整测试链条

### 一键测试脚本（推荐 ⭐）

```bash
# 赋予执行权限
chmod +x scripts/run-all-tests.sh

# 运行完整测试套件（约5-10分钟）
./scripts/run-all-tests.sh
```

**测试内容：****
1. ✅ Docker环境检查
2. ✅ 服务启动测试
3. ✅ Wiki.js功能测试
4. ✅ 插件系统测试
5. ✅ C语言插件性能测试
6. ✅ 配置管理测试
7. ✅ 日志系统测试
8. ✅ 清理和总结

---

## 📝 分步测试指南

### 阶段1: 基础服务启动

#### 步骤1.1: 启动核心服务

```bash
# 启动Wiki.js、PostgreSQL、Nginx
./deploy.sh start

# 或使用docker compose
docker compose up -d db wiki nginx
```

**预期输出：**
```
✅ Starting WikiDemoTongYi services...
✅ Database started
✅ Wiki.js started
✅ Nginx started
🎉 All services running!
```

#### 步骤1.2: 验证服务状态

```bash
# 查看所有容器状态
docker compose ps

# 预期输出:
# NAME                STATUS         PORTS
# wiki-db             Up (healthy)   5432/tcp
# wiki-js             Up (healthy)   3000/tcp
# wiki-nginx          Up             0.0.0.0:80->80/tcp
```

#### 步骤1.3: 访问Wiki.js

```bash
# 浏览器访问
open http://localhost        # macOS
xdg-open http://localhost    # Linux
start http://localhost       # Windows

# 或使用curl测试
curl -I http://localhost

# 预期响应: HTTP/1.1 200 OK
```

**初始登录凭证：**
- 邮箱: `admin@example.com`
- 密码: `changeme123`

---

### 阶段2: 插件系统测试

#### 步骤2.1: 启动插件管理器

```bash
# 启动插件相关服务
docker compose --profile plugins up -d

# 查看插件容器
docker compose ps | grep plugin
```

#### 步骤2.2: 测试RSS阅读器插件

```bash
# 查看RSS插件日志
docker compose logs rss-reader

# 手动触发RSS抓取
docker compose exec rss-reader \
  python /app/plugins/rss-reader/plugin.py --run-now

# 预期输出:
# [INFO] Fetching RSS feeds...
# [INFO] Fetched 10 articles from Hacker News
# [INFO] Generated AI summaries
# [INFO] Published to Wiki.js
```

#### 步骤2.3: 测试C语言Markdown优化器

```bash
# 启动C语言插件
docker compose --profile benchmark up -d markdown-optimizer

# 健康检查
curl http://localhost:8080/health

# 预期响应:
# {"status":"healthy","service":"markdown-optimizer"}

# Markdown解析测试
curl -X POST http://localhost:8080/api/parse \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello\nThis is **bold** text"}'

# 预期响应:
# {"success":true,"html":"<h1>Hello</h1>\nThis is <strong>bold</strong> text","processing_time_ms":2}

# 性能基准测试
curl -X POST http://localhost:8080/api/benchmark | python3 -m json.tool
```

---

### 阶段3: 高级功能测试

#### 步骤3.1: 配置管理系统测试

```bash
# 启动配置管理器
docker compose up -d config-manager

# CLI方式测试
python config-manager/config_cli.py list

# 应用配置模板
python config-manager/config_cli.py apply personal-wiki

# Web UI访问
open http://localhost/config
```

#### 步骤3.2: 日志管理系统测试

```bash
# 查看日志列表
python log-manager/log_cli.py list

# 搜索错误日志
python log-manager/log_cli.py search error

# Web UI访问
open http://localhost/logs

# 轮转日志
python log-manager/log_cli.py rotate --dry-run
```

#### 步骤3.3: Obsidian同步测试

```bash
# 配置同步
cp obsidian-sync-config.example.json obsidian-sync-config.json
vim obsidian-sync-config.json  # 配置你的Obsidian目录

# 执行同步
python scripts/obsidian-sync/sync_manager.py sync

# 查看同步状态
python scripts/obsidian-sync/sync_manager.py status
```

---

## 📊 日志查看命令

### 通用日志查看

```bash
# 查看所有服务日志
docker compose logs

# 查看特定服务日志
docker compose logs wiki        # Wiki.js
docker compose logs db          # PostgreSQL
docker compose logs nginx       # Nginx
docker compose logs rss-reader  # RSS插件
docker compose logs markdown-optimizer  # C语言插件

# 实时跟踪日志
docker compose logs -f wiki

# 查看最近100行
docker compose logs --tail=100 wiki

# 带时间戳
docker compose logs -t wiki
```

### 日志过滤和搜索

```bash
# 搜索错误日志
docker compose logs wiki | grep -i error

# 搜索特定关键词
docker compose logs | grep "plugin"

# 只查看stderr
docker compose logs wiki 2>&1 | grep ERROR

# 导出日志到文件
docker compose logs wiki > wiki-logs.txt
```

### 容器内部日志

```bash
# 进入容器查看日志文件
docker compose exec wiki sh
ls -la /wiki/logs/
cat /wiki/logs/app.log

# C语言插件日志
docker compose exec markdown-optimizer sh
cat /app/logs/app.log
```

### 系统日志

```bash
# Docker daemon日志
sudo journalctl -u docker.service -f    # Linux

# Nginx访问日志
docker compose exec nginx cat /var/log/nginx/access.log

# PostgreSQL日志
docker compose exec db cat /var/lib/postgresql/data/log/*.log
```

---

## 🧪 性能基准测试

### 测试1: C语言插件性能

```bash
cd plugins/markdown-optimizer

# 运行自动化测试脚本
./benchmark.sh

# 预期输出:
# QPS: 5000+
# 平均延迟: <1ms
# 性能提升: 25x (vs Python)
```

### 测试2: 使用ab工具

```bash
# 安装ab
sudo apt-get install apache2-utils  # Ubuntu

# 准备测试数据
echo '{"markdown": "# Test\n**Bold** text"}' > /tmp/test.json

# 执行压力测试
ab -n 10000 -c 100 \
   -p /tmp/test.json \
   -T "application/json" \
   http://localhost:8080/api/parse

# 关键指标:
# Requests per second: 5000+
# Time per request: <1ms
```

### 测试3: 并发性能

```bash
# 测试不同并发级别
for concurrency in 1 10 50 100; do
  echo "Testing $concurrency concurrent connections..."
  
  ab -n 1000 -c $concurrency \
     -p /tmp/test.json \
     -T "application/json" \
     http://localhost:8080/api/parse \
     2>&1 | grep "Requests per second"
done
```

---

## 🔍 故障排查

### 问题1: 服务无法启动

```bash
# 查看详细错误
docker compose logs

# 检查端口占用
netstat -tlnp | grep 80      # Linux
netstat -ano | findstr "80"  # Windows

# 检查Docker资源
docker stats

# 重启服务
docker compose restart
```

### 问题2: Wiki.js无法访问

```bash
# 检查容器状态
docker compose ps wiki

# 查看Wiki.js日志
docker compose logs wiki

# 测试内部连接
docker compose exec wiki curl http://localhost:3000

# 检查Nginx配置
docker compose exec nginx nginx -t
```

### 问题3: 数据库连接失败

```bash
# 检查数据库状态
docker compose ps db
docker compose logs db

# 测试数据库连接
docker compose exec db pg_isready -U wikiuser -d wikidb

# 重置数据库（警告：丢失数据）
docker compose down -v db
docker compose up -d db
```

### 问题4: 插件不工作

```bash
# 查看插件日志
docker compose logs rss-reader
docker compose logs markdown-optimizer

# 检查插件配置
docker compose exec rss-reader cat /app/plugins/rss-reader/plugin.json

# 重启插件
docker compose restart rss-reader

# 检查网络连接
docker compose exec rss-reader ping wiki
```

### 问题5: 性能不佳

```bash
# 检查资源使用
docker stats

# 检查CPU限制
docker inspect wiki-plugin-markdown-optimizer | grep -A 5 CpuQuota

# 检查内存限制
docker inspect wiki-plugin-markdown-optimizer | grep -A 5 Memory

# 调整资源限制（docker-compose.yml）
# deploy.resources.limits.cpus: '2.0'
# deploy.resources.limits.memory: 256M
```

---

## ✅ 测试检查清单

### 基础功能
- [ ] Docker服务正常启动
- [ ] Wiki.js可访问
- [ ] 可以登录并创建页面
- [ ] Nginx反向代理正常工作
- [ ] 数据库持久化正常

### 插件系统
- [ ] 插件管理器启动成功
- [ ] RSS插件可以抓取内容
- [ ] C语言插件响应正常
- [ ] 插件间网络通信正常
- [ ] 资源限制生效

### 高级功能
- [ ] 配置管理CLI可用
- [ ] 配置管理Web UI可访问
- [ ] 日志系统正常收集
- [ ] 日志搜索功能正常
- [ ] Obsidian同步工具可用

### 性能测试
- [ ] C语言插件QPS > 3000
- [ ] 平均延迟 < 2ms
- [ ] P99延迟 < 10ms
- [ ] 内存占用 < 128MB（C插件）
- [ ] 并发测试通过

### 文档和工具
- [ ] 所有文档可访问
- [ ] 测试脚本正常运行
- [ ] Makefile编译成功
- [ ] Docker镜像构建成功
- [ ] Helm Chart可用

---

## 📈 测试报告模板

完成测试后，填写以下报告：

```markdown
# 测试报告 - WikiDemoTongYi v1.0.0

## 测试环境
- 操作系统: ____________
- Docker版本: ____________
- 内存: ____________
- CPU: ____________

## 测试结果

### 基础功能
- Wiki.js启动: ✅/❌
- 数据库连接: ✅/❌
- Nginx代理: ✅/❌

### 插件系统
- RSS插件: ✅/❌ (QPS: _____)
- C语言插件: ✅/❌ (QPS: _____)
- 配置管理: ✅/❌
- 日志系统: ✅/❌

### 性能指标
- C插件QPS: ____________
- 平均延迟: ____________
- P99延迟: ____________
- 内存占用: ____________

## 遇到的问题
1. ____________
2. ____________

## 建议改进
1. ____________
2. ____________

测试人: ____________
测试日期: ____________
```

---

## 🎯 快速参考卡片

### 常用命令速查

```bash
# 启动/停止
./deploy.sh start/stop/restart

# 查看状态
docker compose ps
docker stats

# 查看日志
docker compose logs -f [service]

# 进入容器
docker compose exec [service] sh

# 重启服务
docker compose restart [service]

# 清理
docker compose down -v
docker system prune -af
```

### 端口映射

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|---------|---------|------|
| Nginx | 80 | 80 | HTTP |
| Nginx | 443 | 443 | HTTPS |
| Wiki.js | 3000 | - | 内部 |
| Config Manager | 5000 | - | 内部 |
| Markdown Optimizer | 8080 | - | 内部 |

### 访问地址

- Wiki.js: http://localhost
- 配置管理: http://localhost/config
- 日志查看: http://localhost/logs
- C插件API: http://localhost:8080

---

## 📞 获取帮助

遇到问题？

1. 📖 查看完整文档: `docs/` 目录
2. 🔍 搜索Issues: https://github.com/wikidemotongyi/wikidemotongyi/issues
3. 💬 提问讨论: https://github.com/wikidemotongyi/wikidemotongyi/discussions
4. 📧 邮件联系: team@wikidemotongyi.com

---

**祝你测试顺利！** 🚀

**版本**: v1.0.0  
**最后更新**: 2026-05-15
