# 故障排查速查表

快速解决常见问题。

## Docker Hub连接失败

### 症状
```
dialing registry-1.docker.io:443: connectex: A connection attempt failed
```

### 解决方案

**Windows PowerShell:**
```powershell
.\scripts\setup-docker-mirror.ps1
```

**Linux/WSL:**
```bash
sudo ./scripts/setup-docker-mirror.sh
```

**详细指南**: [docs/DOCKER_MIRROR_SETUP.md](docs/DOCKER_MIRROR_SETUP.md)

---

## WSL无法连接Docker Desktop

### 症状
```
failed to connect to the docker API at unix:///var/run/docker.sock
```

### 解决方案

1. **确认Docker Desktop正在运行**
   - Windows任务管理器中查看进程

2. **启用WSL集成**
   - Docker Desktop → Settings → Resources → WSL Integration
   - 勾选你的WSL发行版
   - Apply & Restart

3. **在WSL中测试**
   ```bash
   docker ps
   docker --version
   ```

---

## 服务启动失败

### 检查容器状态
```bash
docker compose ps
docker compose logs db      # 数据库日志
docker compose logs wiki    # Wiki.js日志
docker compose logs nginx   # Nginx日志
```

### 常见错误

#### 端口被占用
```
Error starting userland proxy: Bind for 0.0.0.0:80 failed: port is already allocated
```

**解决**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :80     # Windows
lsof -i :80                     # Linux/macOS

# 停止占用进程或修改端口
# 编辑 docker-compose.yml 修改端口映射
```

#### 数据库连接失败
```
Error: connect ECONNREFUSED db:5432
```

**解决**:
```bash
# 等待数据库完全启动
docker compose logs db | grep "ready to accept connections"

# 重启Wiki.js服务
docker compose restart wiki
```

---

## C语言插件编译失败

### 症状
```
gcc: command not found
```

### 解决方案

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential gcc make
```

**CentOS/RHEL:**
```bash
sudo yum groupinstall "Development Tools"
```

**macOS:**
```bash
xcode-select --install
```

---

## 性能问题

### WSL中/mnt/f路径慢

**症状**: 文件操作极慢，测试脚本执行时间长

**解决**: 迁移到WSL文件系统
```bash
# 在WSL中执行
mkdir -p ~/projects
cd ~/projects
git clone <repository-url>
cd wikidemotongyi
./scripts/run-all-tests.sh
```

### Docker镜像拉取慢

**解决**: 配置镜像加速器（见上文）

---

## 日志查看

### 实时查看所有服务日志
```bash
docker compose logs -f
```

### 查看特定服务日志
```bash
docker compose logs -f wiki
docker compose logs -f db
docker compose logs -f nginx
```

### 查看最近100行
```bash
docker compose logs --tail=100 wiki
```

### 查看C语言插件日志
```bash
docker compose logs -f markdown-optimizer
```

---

## 重置环境

### 清理所有容器和数据
```bash
# 警告：这将删除所有数据！
docker compose down -v
docker system prune -a
```

### 重新开始
```bash
docker compose up -d
```

---

## 获取帮助

1. 查看详细文档：
   - [README.md](README.md)
   - [DEVELOPER_TESTING_GUIDE.md](DEVELOPER_TESTING_GUIDE.md)
   - [docs/DOCKER_MIRROR_SETUP.md](docs/DOCKER_MIRROR_SETUP.md)

2. 查看Docker日志：
   - Windows: `%USERPROFILE%\AppData\Local\Docker\log.txt`
   - Linux: `journalctl -u docker.service`

3. 提交Issue：
   - GitHub Issues页面

---

**最后更新**: 2026-05-16
