# Docker镜像加速器配置指南

本文档帮助你解决在中国大陆访问Docker Hub时的网络连接问题。

## 问题现象

运行测试脚本时出现以下错误：

```
failed to resolve reference "docker.io/library/postgres:15-alpine":
dialing registry-1.docker.io:443: connectex: A connection attempt failed
because the connected party did not properly respond after a period of time
```

## 快速解决方案

### 方案A：使用自动化脚本（推荐）

#### Windows用户（WSL环境）

在**Windows PowerShell**中运行：

```powershell
.\scripts\setup-docker-mirror.ps1
```

脚本会自动：
1. 检测Docker Desktop安装
2. 创建/更新配置文件
3. 添加国内镜像源
4. 提示重启Docker Desktop

#### Linux/WSL用户

在终端中运行：

```bash
sudo ./scripts/setup-docker-mirror.sh
```

### 方案B：手动配置

#### Windows (Docker Desktop)

1. **打开Docker Desktop设置**
   - 右键点击系统托盘中的Docker图标
   - 选择 **Settings** (⚙️)

2. **编辑Docker Engine配置**
   - 左侧菜单选择 **Docker Engine**
   - 在JSON编辑器中添加以下内容：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://huecker.io",
    "https://dockerhub.timeweb.cloud"
  ]
}
```

3. **应用并重启**
   - 点击右下角 **Apply & restart**
   - 等待Docker Desktop完全重启（约60秒）

4. **验证配置**
   ```bash
   # 在WSL或PowerShell中运行
   docker info | Select-String "Registry Mirrors"
   ```

   应该看到类似输出：
   ```
   Registry Mirrors:
     https://docker.m.daocloud.io/
     https://huecker.io/
     https://dockerhub.timeweb.cloud/
   ```

#### Linux (Ubuntu/Debian)

1. **创建配置文件**

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://huecker.io",
    "https://dockerhub.timeweb.cloud"
  ]
}
EOF
```

2. **重启Docker服务**

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

3. **验证配置**

```bash
docker info | grep -A 3 "Registry Mirrors"
```

#### macOS (Docker Desktop)

配置步骤与Windows类似：

1. 打开Docker Desktop
2. 菜单栏 **Docker** → **Settings**
3. 选择 **Docker Engine**
4. 添加相同的 `registry-mirrors` 配置
5. 点击 **Apply & restart**

## 可用的镜像源列表

以下是经过验证的国内Docker镜像源（按推荐顺序）：

| 镜像源 | 地址 | 稳定性 | 速度 |
|--------|------|--------|------|
| DaoCloud | `https://docker.m.daocloud.io` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Huecker | `https://huecker.io` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| TimeWeb | `https://dockerhub.timeweb.cloud` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 阿里云（需登录） | `https://<your-id>.mirror.aliyuncs.com` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**注意**: 建议同时配置多个镜像源，Docker会自动选择最快的一个。

## 验证配置

### 1. 检查Docker信息

```bash
docker info
```

查找 `Registry Mirrors` 部分，确认镜像源已列出。

### 2. 测试拉取镜像

```bash
# 拉取一个小镜像进行测试
docker pull hello-world

# 如果成功，尝试拉取项目所需的镜像
docker pull postgres:15-alpine
docker pull nginx:alpine
docker pull python:3.11-slim
```

### 3. 运行项目测试

```bash
# WSL环境
./scripts/run-all-tests.sh

# 或者分步测试
docker compose up -d db wiki nginx
```

## 故障排查

### 问题1：配置后仍然无法连接

**可能原因**：
- Docker Desktop未完全重启
- 配置文件格式错误
- 镜像源暂时不可用

**解决方法**：

```bash
# 1. 完全重启Docker Desktop
# Windows: 右键托盘图标 → Quit Docker Desktop → 重新启动

# 2. 检查配置文件语法
# Windows: %USERPROFILE%\.docker\daemon.json
# Linux: /etc/docker/daemon.json

# 使用JSON验证工具检查
python -m json.tool ~/.docker/daemon.json

# 3. 尝试其他镜像源
# 编辑配置文件，更换registry-mirrors列表
```

### 问题2：Docker Desktop启动失败

**可能原因**：
- 配置文件JSON格式错误
- 端口冲突
- WSL集成问题

**解决方法**：

```bash
# 1. 恢复备份配置
# Windows PowerShell
Copy-Item $env:USERPROFILE\.docker\daemon.json.backup.* $env:USERPROFILE\.docker\daemon.json

# Linux
sudo cp /etc/docker/daemon.json.backup.* /etc/docker/daemon.json

# 2. 重置Docker Desktop
# Settings → Troubleshoot → Reset to factory defaults
```

### 问题3：镜像拉取速度慢

**可能原因**：
- 当前镜像源负载高
- 网络波动

**解决方法**：

```bash
# 1. 更换镜像源顺序
# 将最快的镜像源放在列表第一位

# 2. 清理Docker缓存
docker system prune -a

# 3. 测试不同镜像源的速度
time docker pull alpine:latest
```

### 问题4：WSL中无法连接Docker Desktop

**可能原因**：
- WSL集成未启用
- Docker Desktop未在Windows中运行

**解决方法**：

```bash
# 1. 检查Docker Desktop是否在运行
# Windows任务管理器中查看Docker Desktop进程

# 2. 启用WSL集成
# Docker Desktop → Settings → Resources → WSL Integration
# 勾选你的WSL发行版

# 3. 在WSL中测试
docker ps
docker --version
```

## 高级配置

### 配置代理（如果有科学上网）

如果你已有代理工具，可以配置Docker使用代理：

#### Windows (Docker Desktop)

1. Settings → Resources → Proxies
2. 配置HTTP/HTTPS代理：
   ```
   HTTP Proxy: http://127.0.0.1:7890
   HTTPS Proxy: http://127.0.0.1:7890
   No Proxy: localhost,127.0.0.1,.docker.internal
   ```
3. Apply & restart

#### Linux

编辑 `/etc/systemd/system/docker.service.d/http-proxy.conf`：

```ini
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:7890"
Environment="HTTPS_PROXY=http://127.0.0.1:7890"
Environment="NO_PROXY=localhost,127.0.0.1,.docker.internal"
```

然后重启Docker：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 私有镜像仓库

如果你有私有镜像仓库，可以添加到配置中：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://huecker.io"
  ],
  "insecure-registries": [
    "my-registry.example.com:5000"
  ]
}
```

## 最佳实践

1. **定期更新镜像源列表**
   - 镜像源可能会失效或变慢
   - 保持2-3个备用镜像源

2. **监控Docker Hub访问状态**
   - 关注Docker官方状态页面
   - 加入Docker用户社区获取最新信息

3. **本地缓存常用镜像**
   ```bash
   # 定期拉取常用基础镜像
   docker pull postgres:15-alpine
   docker pull nginx:alpine
   docker pull python:3.11-slim

   # 导出备份
   docker save postgres:15-alpine > postgres-15-alpine.tar
   ```

4. **使用多阶段构建减少镜像大小**
   - 参考项目的Dockerfile最佳实践
   - 使用`.dockerignore`排除不必要文件

## 相关资源

- [Docker官方文档 - 镜像加速器](https://docs.docker.com/registry/recipes/mirror/)
- [DaoCloud镜像服务](https://www.daocloud.io/mirror)
- [Docker Hub状态](https://www.dockerstatus.com/)
- [项目README](../README.md)
- [开发者测试指南](../DEVELOPER_TESTING_GUIDE.md)

## 反馈与支持

如果遇到问题，请：

1. 查看本文档的故障排查部分
2. 检查Docker日志：
   - Windows: `%USERPROFILE%\AppData\Local\Docker\log.txt`
   - Linux: `journalctl -u docker.service`
   - macOS: `~/Library/Containers/com.docker.docker/Data/log/`
3. 在项目GitHub Issues中提问

---

**最后更新**: 2026-05-16
**适用版本**: WikiDemoTongYi v1.0.0+
