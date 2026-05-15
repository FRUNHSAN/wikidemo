# 云原生架构迁移指南

## 🚀 快速开始

你的项目已经完成云原生改造！现在可以按照以下步骤启用新功能。

---

## ✅ 新增功能清单

### 1. 插件标准化模板
- 📁 `plugins/TEMPLATE/` - 复制即可开发新插件
- 🐳 支持Python、Node.js、Go、Rust、Java
- 🔒 多阶段构建，安全高效

### 2. 插件市场系统
- 📦 `plugins/registry.json` - 插件注册表
- 🛠️ `scripts/plugin-marketplace.py` - CLI管理工具

### 3. CI/CD流水线
- ⚙️ `.github/workflows/ci.yml` - GitHub Actions
- 🧪 自动测试、linting、镜像构建
- 📦 自动发布到GHCR

### 4. Kubernetes支持
- ☸️ `k8s/base/` - Kustomize配置
- 📊 `helm/wikidemotongyi/` - Helm Chart
- 🔄 零代码修改迁移

### 5. 服务发现
- 🔍 `scripts/service-discovery.py` - 自动发现插件
- 🌐 API网关配置生成
- 💚 健康检查

---

## 📋 使用指南

### 开发新插件（3步）

```bash
# 1. 复制模板
cp -r plugins/TEMPLATE plugins/my-new-plugin
cd plugins/my-new-plugin

# 2. 修改配置
vim plugin.json  # 填写插件信息
vim src/main.py  # 实现业务逻辑

# 3. 构建测试
docker build -t wikidemotongyi/plugin-my-new-plugin:latest .
docker run -p 8080:8080 wikidemotongyi/plugin-my-new-plugin:latest
```

### 管理插件市场

```bash
# 列出所有插件
python scripts/plugin-marketplace.py list

# 搜索AI相关插件
python scripts/plugin-marketplace.py search ai

# 安装插件
python scripts/plugin-marketplace.py install rss-reader

# 查看插件详情
python scripts/plugin-marketplace.py info rss-reader
```

### 使用CI/CD

```bash
# 提交代码触发CI
git add .
git commit -m "Add new feature"
git push

# 创建版本标签触发发布
git tag v1.0.0
git push origin v1.0.0
```

### 部署到Kubernetes

```bash
# 方式1: Kustomize
kubectl apply -k k8s/base

# 方式2: Helm
helm install wiki ./helm/wikidemotongyi

# 自定义配置
helm install wiki ./helm/wikidemotongyi \
  --set wiki.replicaCount=3
```

### 服务发现

```bash
# 同步Docker状态
python scripts/service-discovery.py sync

# 查看运行中的插件
python scripts/service-discovery.py list

# 启动监控
python scripts/service-discovery.py start 30
```

---

## 🔄 迁移现有插件

### RSS阅读器改造示例

**步骤1: 添加标准化文件**

```bash
cd plugins/rss-reader

# 创建Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine
RUN apk add --no-cache curl tini && \
    addgroup -g 1001 -S plugin && \
    adduser -u 1001 -S plugin -G plugin

WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=plugin:plugin . .

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

USER plugin
EXPOSE 8080
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python", "plugin.py"]
EOF

# 创建.dockerignore
cat > .dockerignore << 'EOF'
__pycache__
*.pyc
.git
tests
EOF
```

**步骤2: 更新plugin.json**

```json
{
  "id": "rss-reader",
  "name": "RSS Reader",
  "version": "1.0.0",
  "description": "自动抓取技术资讯并生成AI摘要",
  "author": "WikiDemoTongYi Team",
  "repository": "https://github.com/wikidemotongyi/plugin-rss-reader",
  "category": "content",
  "tags": ["rss", "ai", "automation"],
  "ports": [8080],
  "resources": {
    "cpu_limit": "0.5",
    "memory_limit": "256M"
  }
}
```

**步骤3: 构建和推送**

```bash
docker build -t wikidemotongyi/plugin-rss-reader:1.0.0 .
docker build -t wikidemotongyi/plugin-rss-reader:latest .
docker push wikidemotongyi/plugin-rss-reader:1.0.0
docker push wikidemotongyi/plugin-rss-reader:latest
```

---

## 🎯 推荐行动顺序

### 第1周：熟悉和测试

- [ ] 阅读 `docs/CLOUD_NATIVE_PLUGIN_GUIDE.md`
- [ ] 阅读 `docs/CLOUD_NATIVE_ARCHITECTURE.md`
- [ ] 测试插件模板：`cp -r plugins/TEMPLATE plugins/test-plugin`
- [ ] 测试plugin-marketplace.py CLI工具
- [ ] 测试service-discovery.py

### 第2周：CI/CD集成

- [ ] 在GitHub启用Actions
- [ ] 提交代码触发CI
- [ ] 观察流水线执行
- [ ] 修复任何问题

### 第3周：插件改造

- [ ] 改造RSS阅读器为标准化插件
- [ ] 改造Obsidian同步为标准化插件
- [ ] 更新plugins/registry.json
- [ ] 测试插件市场安装流程

### 第4周：K8s测试

- [ ] 安装minikube或kind
- [ ] 测试Helm部署
- [ ] 验证所有功能正常
- [ ] 记录问题和改进点

### 第5周：准备发布

- [ ] 更新README.md，添加云原生说明
- [ ] 创建v2.0.0版本标签
- [ ] 编写发布公告
- [ ] 推送到GitHub

---

## 📚 文档索引

### 核心文档
- [CLOUD_NATIVE_PLUGIN_GUIDE.md](docs/CLOUD_NATIVE_PLUGIN_GUIDE.md) - 插件开发指南 ⭐
- [CLOUD_NATIVE_ARCHITECTURE.md](docs/CLOUD_NATIVE_ARCHITECTURE.md) - 架构设计详解
- [CLOUD_NATIVE_SUMMARY.md](docs/CLOUD_NATIVE_SUMMARY.md) - 改造总结

### 参考文件
- [plugins/TEMPLATE/Dockerfile](plugins/TEMPLATE/Dockerfile) - 多语言Dockerfile模板
- [plugins/TEMPLATE/docker-compose.plugin.yml](plugins/TEMPLATE/docker-compose.plugin.yml) - 插件Compose模板
- [plugins/registry.json](plugins/registry.json) - 插件注册表示例
- [.github/workflows/ci.yml](.github/workflows/ci.yml) - CI/CD配置
- [helm/wikidemotongyi/values.yaml](helm/wikidemotongyi/values.yaml) - Helm配置值

---

## 🐛 常见问题

### Q: 我的现有插件需要重写吗？

A: 不需要！现有插件仍然可以工作。标准化模板是为了方便未来开发新插件。你可以逐步迁移现有插件。

### Q: Kubernetes是必须的吗？

A: 不是！Docker Compose仍然是主要的部署方式。Kubernetes是为未来扩展预留的选项。

### Q: CI/CD会减慢开发速度吗？

A: 不会！CI/CD只在PR和Push时运行，本地开发不受影响。反而能提前发现问题，提高开发效率。

### Q: 如何回滚到之前的架构？

A: 所有新文件都是附加的，没有修改现有核心文件。只需删除新增的文件即可回滚：
```bash
rm -rf plugins/TEMPLATE
rm -rf k8s/
rm -rf helm/
rm -rf .github/
rm scripts/plugin-marketplace.py
rm scripts/service-discovery.py
```

---

## 💡 最佳实践

### 1. 版本管理

```bash
# 使用语义化版本
git tag v1.0.0    # 主版本.次版本.修订版本
git tag v1.1.0    # 新功能
git tag v1.0.1    # Bug修复
```

### 2. 插件命名

```
✅ 推荐: rss-reader, obsidian-sync, daily-digest
❌ 避免: MyPlugin, Plugin1, test
```

### 3. 提交信息

```bash
# 使用约定式提交
git commit -m "feat: add RSS reader plugin"
git commit -m "fix: resolve sync conflict issue"
git commit -m "docs: update plugin development guide"
```

### 4. 分支策略

```
main          - 稳定版本
develop       - 开发分支
feature/*     - 功能分支
hotfix/*      - 紧急修复
```

---

## 🎉 恭喜你！

现在你的项目已经具备：

✅ **企业级架构** - 云原生、可扩展、高可用  
✅ **开发者友好** - 简单模板、完整文档、自动化CI/CD  
✅ **社区就绪** - 插件市场、贡献指南、质量保证  
✅ **未来证明** - Kubernetes支持、多语言、零成本迁移  

**准备好迎接社区贡献者了吗？** 🚀

---

**最后更新**: 2026-05-15  
**版本**: v2.0.0 (Cloud-Native)
