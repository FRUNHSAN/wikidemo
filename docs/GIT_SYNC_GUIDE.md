# Git同步配置指南

## 为什么需要Git同步？

- ✅ **数据备份**：笔记自动同步到云端，永不丢失
- ✅ **版本控制**：可查看和恢复历史版本
- ✅ **多设备同步**：在不同设备上访问笔记
- ✅ **离线可用**：本地Git仓库可离线使用

## 配置步骤

### 1. 创建Git仓库

#### GitHub方式
1. 访问 https://github.com/new
2. 创建私有仓库（推荐）或公开仓库
3. 记录仓库地址，例如：`https://github.com/username/wiki-notes.git`

#### Gitee方式（国内更快）
1. 访问 https://gitee.com/projects/new
2. 创建私有仓库
3. 记录仓库地址，例如：`https://gitee.com/username/wiki-notes.git`

### 2. 生成Access Token

#### GitHub Token
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：`repo` (Full control of private repositories)
4. 生成并复制Token

#### Gitee Token
1. 访问 https://gitee.com/profile/personal_access_tokens
2. 点击 "生成新令牌"
3. 选择权限：`projects` (项目)
4. 生成并复制Token

### 3. 配置环境变量

编辑 `.env` 文件：

```bash
# 启用Git同步
GIT_SYNC_ENABLED=true

# Git仓库地址
GIT_REPO_URL=https://github.com/username/wiki-notes.git

# Git分支
GIT_BRANCH=main

# Git用户名
GIT_USERNAME=your-username

# Git Token
GIT_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 同步间隔（分钟）
GIT_SYNC_INTERVAL=30
```

### 4. 启动服务

```bash
./deploy.sh restart
```

### 5. 验证同步

1. 登录Wiki.js管理后台
2. 进入 "存储" → "Git"
3. 查看同步状态
4. 手动触发一次同步测试

## 常见问题

### Q: 同步失败怎么办？

检查日志：
```bash
docker compose logs wiki | grep -i git
```

常见原因：
- Token权限不足
- 仓库地址错误
- 网络连接问题

### Q: 如何查看同步历史？

在Wiki.js管理后台：
- 存储 → Git → 同步历史

### Q: 可以双向同步吗？

Wiki.js支持：
- **推送到Git**：Wiki内容 → Git仓库
- **从Git拉取**：Git仓库 → Wiki内容

建议在管理后台配置同步方向。

### Q: 首次同步很慢？

正常现象，特别是笔记较多时。后续增量同步会很快。

## 高级配置

### 忽略某些页面

在仓库根目录创建 `.gitignore`：

```gitignore
# 忽略临时页面
drafts/*
temp/*

# 忽略特定分类
private/*
```

### 自定义提交信息

Wiki.js会自动生成提交信息，格式：
```
[Wiki.js] Auto-sync: <页面标题>
```

### 使用SSH而非HTTPS

如果使用SSH密钥：

```bash
GIT_REPO_URL=git@github.com:username/wiki-notes.git
```

需要在容器中配置SSH密钥（较复杂，推荐使用Token）。

## 最佳实践

1. ✅ 使用私有仓库保护隐私
2. ✅ 定期备份Token
3. ✅ 设置合理的同步间隔（建议30-60分钟）
4. ✅ 监控同步状态
5. ✅ 保留Git历史记录

---

**提示：** 如果暂时不想配置Git同步，可以跳过此步骤，稍后随时启用。
