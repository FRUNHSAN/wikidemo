# 跨平台开发环境设置指南

## 🎯 问题说明

在Windows环境下使用Docker开发时，面临以下选择：

| 方案 | 优点 | 缺点 |
|------|------|------|
| **PowerShell + Docker Desktop** | 无需额外配置 | bash脚本无法直接运行 |
| **WSL + Windows文件系统** | 可用Linux命令 | I/O性能极差（/mnt/f） |
| **WSL + WSL文件系统** | 最佳性能 | Windows工具无法访问 |

---

## ✅ 推荐方案

### 方案A: 双版本脚本（最简单 ⭐⭐⭐⭐⭐）

**适用场景**: 不想迁移项目位置

**步骤：**

1. **Windows用户** - 使用PowerShell脚本
   ```powershell
   # 在项目根目录执行
   .\scripts\run-all-tests.ps1
   ```

2. **WSL/Linux用户** - 使用Bash脚本
   ```bash
   chmod +x scripts/run-all-tests.sh
   ./scripts/run-all-tests.sh
   ```

**优点：**
- ✅ 无需移动项目
- ✅ 两种环境都支持
- ✅ 维护成本低

**缺点：**
- ⚠️ Windows文件系统性能略低
- ⚠️ 需要维护两套脚本

---

### 方案B: 迁移到WSL文件系统（最佳性能 ⭐⭐⭐⭐⭐）

**适用场景**: 追求最佳性能，长期使用

#### 步骤1: 迁移项目到WSL

```bash
# 在WSL中执行

# 1. 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 2. 克隆项目（或从Windows复制）
git clone https://github.com/wikidemotongyi/wikidemotongyi.git

# 或者从Windows复制（首次）
cp -r /mnt/f/wikidemotongyi ~/projects/
```

#### 步骤2: 在WSL中运行

```bash
cd ~/projects/wikidemotongyi

# 赋予执行权限
chmod +x scripts/run-all-tests.sh
chmod +x deploy.sh

# 运行测试
./scripts/run-all-tests.sh

# 或直接启动
./deploy.sh start
```

#### 步骤3: 从Windows访问（可选）

如果需要从Windows编辑器访问WSL文件：

```
\\wsl$\Ubuntu\home\your-username\projects\wikidemotongyi
```

在VSCode中：
1. 安装 "Remote - WSL" 扩展
2. Ctrl+Shift+P → "Remote-WSL: Open Folder in WSL"
3. 选择 `~/projects/wikidemotongyi`

**优点：**
- ✅ 最佳I/O性能（比/mnt/f快10倍+）
- ✅ 完整的Linux环境
- ✅ 无兼容性问题

**缺点：**
- ⚠️ 需要学习WSL基本操作
- ⚠️ Windows资源管理器访问稍慢

---

### 方案C: Docker Dev Containers（最专业 ⭐⭐⭐⭐）

**适用场景**: 团队协作，统一开发环境

#### 步骤1: 添加Dev Container配置

创建 `.devcontainer/devcontainer.json`:

```json
{
  "name": "WikiDemoTongYi",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "wiki",
  "workspaceFolder": "/workspace",
  "mounts": [
    "source=${localWorkspaceFolder},target=/workspace,type=bind"
  ],
  "extensions": [
    "ms-python.python",
    "ms-vscode.docker"
  ],
  "settings": {
    "terminal.integrated.defaultProfile.linux": "bash"
  },
  "forwardPorts": [80, 443, 3000, 5000, 8080]
}
```

#### 步骤2: 在VSCode中打开

1. 安装 "Dev Containers" 扩展
2. Ctrl+Shift+P → "Dev Containers: Reopen in Container"
3. VSCode会自动连接到容器内部

**优点：**
- ✅ 完全隔离的开发环境
- ✅ 团队成员环境一致
- ✅ 无需本地安装依赖

**缺点：**
- ⚠️ 需要VSCode
- ⚠️ 学习曲线较陡

---

## 📊 性能对比

### 文件系统性能测试

```bash
# 测试写入速度
time dd if=/dev/zero of=test bs=1M count=100 oflag=direct

# Windows (/mnt/f): ~50 MB/s
# WSL (~/): ~500 MB/s
# 差异: 10倍
```

### Docker启动速度

| 位置 | 首次启动 | 后续启动 |
|------|---------|---------|
| Windows (/mnt/f) | 3-5分钟 | 1-2分钟 |
| WSL (~/) | 2-3分钟 | 30-60秒 |

---

## 🔧 常见问题

### Q1: 我应该选择哪个方案？

**决策树：**

```
是否追求最佳性能？
├─ 是 → 方案B (迁移到WSL)
└─ 否 → 是否长期使用？
         ├─ 是 → 方案B (迁移到WSL)
         └─ 否 → 方案A (双版本脚本)
```

### Q2: 如何从Windows迁移到WSL？

```bash
# 方法1: Git克隆（推荐）
cd ~
git clone https://github.com/wikidemotongyi/wikidemotongyi.git

# 方法2: 直接复制
cp -r /mnt/f/wikidemotongyi ~/

# 验证迁移
cd ~/wikidemotongyi
ls -la
```

### Q3: WSL中如何使用Docker？

```bash
# 确保Docker Desktop已安装并启用WSL 2集成

# 在WSL中检查Docker
docker --version
docker compose version

# 如果找不到Docker，添加到PATH
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
source ~/.bashrc
```

### Q4: 如何在两个环境间同步代码？

**推荐：使用Git**

```bash
# 在任一环境中修改后
git add .
git commit -m "Update feature"
git push

# 在另一环境中拉取
git pull
```

**不推荐：直接文件复制**（可能导致权限问题）

---

## 🎯 我的建议

### 对于个人开发

**推荐：方案B (迁移到WSL)**

理由：
1. ✅ 性能提升显著（10倍+）
2. ✅ 长期来看节省时间
3. ✅ 更接近生产环境（Linux）
4. ✅ 避免跨平台兼容性问题

迁移成本：
- ⏱️ 初次设置：30分钟
- 📚 学习WSL基础：1-2小时
- 💾 磁盘空间：~5GB

### 对于团队开发

**推荐：方案C (Dev Containers)**

理由：
1. ✅ 环境完全一致
2. ✅ 新人上手快
3. ✅ 减少"在我机器上能跑"问题

---

## 📝 快速开始指南

### Windows PowerShell用户

```powershell
# 1. 克隆项目
git clone https://github.com/wikidemotongyi/wikidemotongyi.git
cd wikidemotongyi

# 2. 运行测试（PowerShell版本）
.\scripts\run-all-tests.ps1

# 3. 启动服务
.\deploy.bat start
```

### WSL/Linux用户

```bash
# 1. 克隆项目（推荐放在WSL文件系统）
cd ~
git clone https://github.com/wikidemotongyi/wikidemotongyi.git
cd wikidemotongyi

# 2. 运行测试（Bash版本）
chmod +x scripts/run-all-tests.sh
./scripts/run-all-tests.sh

# 3. 启动服务
./deploy.sh start
```

---

## 🔗 相关资源

- [WSL官方文档](https://docs.microsoft.com/en-us/windows/wsl/)
- [Docker Desktop WSL 2 backend](https://docs.docker.com/desktop/wsl/)
- [VSCode Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)
- [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)

---

**总结：**

- **短期/临时使用**: 方案A (双版本脚本) - 立即可用
- **长期/高性能需求**: 方案B (迁移到WSL) - 最佳体验
- **团队/标准化**: 方案C (Dev Containers) - 最专业的选择

根据你的实际情况选择合适的方案！🚀
