# 云原生插件开发指南

## 📋 目录

1. [概述](#概述)
2. [插件架构](#插件架构)
3. [快速开始](#快速开始)
4. [标准化模板](#标准化模板)
5. [多语言支持](#多语言支持)
6. [服务发现](#服务发现)
7. [最佳实践](#最佳实践)
8. [发布流程](#发布流程)

---

## 概述

WikiDemoTongYi采用**云原生架构**设计，每个插件都是独立的Docker容器，具有以下特点：

### ✨ 核心优势

- **完全隔离**: 插件运行在独立容器中，故障不影响主系统
- **语言无关**: 支持Python、Node.js、Go、Rust、Java等任何语言
- **自动发现**: 基于Docker标签的服务发现机制
- **资源限制**: 每个插件有CPU和内存限制
- **水平扩展**: 支持Kubernetes部署和自动扩缩容
- **版本管理**: 统一的插件注册表和版本控制

### 🏗️ 架构设计

```
┌─────────────────────────────────────────────┐
│              Nginx (API Gateway)             │
│         /api/plugins/{plugin-id}            │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┐
    │          │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Plugin1│ │Plugin2│ │Plugin3│ │PluginN│
│Python │ │Node.js│ │  Go   │ │ Rust  │
└───────┘ └───────┘ └───────┘ └───────┘
    │          │          │          │
    └──────────┴──────────┴──────────┘
               │
    ┌──────────▼──────────┐
    │   Service Discovery  │
    │  (Auto-registration) │
    └─────────────────────┘
```

---

## 插件架构

### 目录结构

```
your-plugin/
├── Dockerfile                    # 必需：多阶段构建
├── docker-compose.yml            # 可选：本地测试
├── plugin.json                   # 必需：插件元数据
├── README.md                     # 必需：插件文档
├── requirements.txt              # Python依赖（如需要）
├── package.json                  # Node.js依赖（如需要）
├── go.mod                        # Go依赖（如需要）
├── Cargo.toml                    # Rust依赖（如需要）
├── src/                          # 源代码
│   ├── main.py                   # 主入口文件
│   ├── handlers/                 # 请求处理器
│   ├── models/                   # 数据模型
│   └── utils/                    # 工具函数
├── tests/                        # 测试代码
│   ├── test_main.py
│   └── fixtures/
├── .dockerignore                 # Docker忽略文件
└── .github/workflows/            # CI/CD（可选）
    └── ci.yml
```

### plugin.json 规范

```json
{
  "id": "your-plugin-id",
  "name": "Your Plugin Name",
  "version": "1.0.0",
  "description": "简短描述插件功能",
  "author": "Your Name <email@example.com>",
  "license": "MIT",
  "repository": "https://github.com/username/your-plugin",
  "homepage": "https://your-plugin-docs.com",
  
  "category": "content",
  "tags": ["tag1", "tag2"],
  
  "min_wiki_version": "2.5.0",
  
  "entrypoint": "python src/main.py",
  
  "ports": [8080],
  
  "environment": [
    {
      "name": "API_KEY",
      "required": false,
      "default": "",
      "description": "API密钥"
    }
  ],
  
  "volumes": [
    "/app/data"
  ],
  
  "resources": {
    "cpu_limit": "0.5",
    "memory_limit": "256M"
  },
  
  "health_check": {
    "endpoint": "/health",
    "interval": 30,
    "timeout": 5
  }
}
```

---

## 快速开始

### 1. 使用模板创建插件

```bash
# 复制模板
cp -r plugins/TEMPLATE plugins/my-new-plugin
cd plugins/my-new-plugin

# 修改plugin.json
vim plugin.json
```

### 2. 实现插件逻辑

**Python示例 (src/main.py):**

```python
from flask import Flask, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/execute', methods=['POST'])
def execute():
    """插件主逻辑"""
    # TODO: 实现你的插件功能
    return jsonify({
        "success": True,
        "message": "Plugin executed successfully"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### 3. 构建Docker镜像

```bash
docker build -t wikidemotongyi/plugin-my-plugin:latest .
```

### 4. 本地测试

```bash
docker run -p 8080:8080 wikidemotongyi/plugin-my-plugin:latest
curl http://localhost:8080/health
```

### 5. 集成到系统

在根目录 `docker-compose.yml` 中添加：

```yaml
services:
  my-plugin:
    image: wikidemotongyi/plugin-my-plugin:latest
    container_name: wiki-plugin-my-plugin
    environment:
      - WIKI_API_URL=http://wiki:3000/api
      - WIKI_API_TOKEN=${WIKI_API_TOKEN}
    networks:
      - wiki-network
    labels:
      - "wiki.plugin=true"
      - "wiki.plugin.name=my-plugin"
      - "wiki.plugin.version=1.0.0"
```

---

## 标准化模板

### Python插件 Dockerfile

```dockerfile
# 构建阶段
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 运行阶段
FROM python:3.11-alpine
LABEL maintainer="Your Name"
LABEL description="Your Plugin Description"

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
CMD ["python", "src/main.py"]
```

### Node.js插件 Dockerfile

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /build
COPY package*.json ./
RUN npm ci --only=production

# 运行阶段
FROM node:18-alpine
LABEL maintainer="Your Name"

RUN apk add --no-cache curl tini && \
    addgroup -g 1001 -S plugin && \
    adduser -u 1001 -S plugin -G plugin

WORKDIR /app
COPY --from=builder /build/node_modules ./node_modules
COPY --chown=plugin:plugin . .

USER plugin
EXPOSE 8080
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "src/index.js"]
```

### Go插件 Dockerfile

```dockerfile
# 构建阶段
FROM golang:1.21-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o plugin-server .

# 运行阶段（极简）
FROM alpine:3.18
LABEL maintainer="Your Name"

RUN apk add --no-cache curl tini && \
    addgroup -g 1001 -S plugin && \
    adduser -u 1001 -S plugin -G plugin

WORKDIR /app
COPY --from=builder /build/plugin-server .
COPY --chown=plugin:plugin plugin.json .

USER plugin
EXPOSE 8080
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["./plugin-server"]
```

---

## 多语言支持

### 支持的语言

| 语言 | 基础镜像 | 优点 | 适用场景 |
|------|---------|------|---------|
| Python | python:3.11-alpine | 生态丰富，开发快速 | AI/ML、数据处理 |
| Node.js | node:18-alpine | 异步IO，高并发 | Web服务、实时应用 |
| Go | golang:1.21-alpine | 高性能，单二进制 | 系统工具、微服务 |
| Rust | rust:1.70-alpine | 内存安全，零成本抽象 | 高性能计算 |
| Java | openjdk:17-alpine | 企业级，成熟生态 | 大型企业应用 |

### 选择建议

- **快速原型**: Python
- **高并发Web服务**: Node.js或Go
- **性能敏感**: Go或Rust
- **企业集成**: Java

---

## 服务发现

### 自动注册

插件启动时会自动通过Docker标签被服务发现系统识别：

```yaml
labels:
  - "wiki.plugin=true"              # 必需：标记为插件
  - "wiki.plugin.name=my-plugin"    # 必需：插件ID
  - "wiki.plugin.version=1.0.0"     # 推荐：版本号
  - "wiki.plugin.author=username"   # 可选：作者
```

### API通信

插件与Wiki.js通过REST API通信：

```python
import requests
import os

WIKI_API_URL = os.environ.get('WIKI_API_URL', 'http://wiki:3000/api')
WIKI_API_TOKEN = os.environ.get('WIKI_API_TOKEN')

headers = {
    'Authorization': f'Bearer {WIKI_API_TOKEN}',
    'Content-Type': 'application/json'
}

# 创建页面
response = requests.post(
    f'{WIKI_API_URL}/pages',
    headers=headers,
    json={
        'title': 'My Page',
        'path': 'my-page',
        'content': '# Hello World'
    }
)
```

---

## 最佳实践

### 1. 安全性

```dockerfile
# ✅ 使用非root用户
RUN adduser -S plugin
USER plugin

# ✅ 最小化镜像
FROM python:3.11-alpine  # 而不是 python:3.11

# ✅ 多阶段构建减少镜像大小
FROM builder AS production

# ❌ 避免硬编码密钥
# 使用环境变量或Secrets
```

### 2. 资源管理

```yaml
# 设置合理的资源限制
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 256M
    reservations:
      cpus: '0.1'
      memory: 64M
```

### 3. 日志记录

```python
import logging
import sys

# 输出到stdout（Docker推荐）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)
logger.info("Plugin started")
```

### 4. 健康检查

```python
@app.route('/health')
def health():
    """健康检查端点"""
    # 检查依赖服务
    db_ok = check_database()
    cache_ok = check_cache()
    
    if db_ok and cache_ok:
        return jsonify({"status": "healthy"}), 200
    else:
        return jsonify({"status": "unhealthy"}), 503
```

### 5. 错误处理

```python
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    return jsonify({"error": "Invalid input"}), 400
except Exception as e:
    logger.exception("Unexpected error")
    return jsonify({"error": "Internal server error"}), 500
```

### 6. 配置管理

```python
import os

# 使用环境变量，提供默认值
CONFIG = {
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'api_timeout': int(os.getenv('API_TIMEOUT', '30')),
    'max_retries': int(os.getenv('MAX_RETRIES', '3'))
}
```

---

## 发布流程

### 1. 准备发布

```bash
# 更新版本号
# plugin.json: "version": "1.0.0"

# 编写CHANGELOG
# CHANGELOG.md

# 更新文档
# README.md
```

### 2. 构建和测试

```bash
# 构建镜像
docker build -t wikidemotongyi/plugin-my-plugin:1.0.0 .
docker build -t wikidemotongyi/plugin-my-plugin:latest .

# 运行测试
docker run --rm wikidemotongyi/plugin-my-plugin:1.0.0 pytest

# 本地测试
docker compose up -d
```

### 3. 推送到Registry

```bash
# 登录
docker login ghcr.io

# 推送
docker push wikidemotongyi/plugin-my-plugin:1.0.0
docker push wikidemotongyi/plugin-my-plugin:latest
```

### 4. 注册到插件市场

编辑 `plugins/registry.json`:

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "image": "wikidemotongyi/plugin-my-plugin:latest",
  "repository": "https://github.com/username/my-plugin",
  "status": "community"
}
```

### 5. 提交PR

```bash
git add plugins/registry.json
git commit -m "Add my-plugin v1.0.0"
git push
# 创建Pull Request
```

---

## Kubernetes部署

### 使用Helm安装插件

```bash
# 添加仓库
helm repo add wikidemotongyi https://charts.wikidemotongyi.com

# 安装插件
helm install my-plugin wikidemotongyi/plugin \
  --set plugin.name=my-plugin \
  --set plugin.image.tag=1.0.0
```

### 自定义values.yaml

```yaml
plugin:
  name: my-plugin
  replicaCount: 2
  image:
    repository: wikidemotongyi/plugin-my-plugin
    tag: "1.0.0"
  
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  
  autoscaling:
    enabled: true
    minReplicas: 1
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80
```

---

## 常见问题

### Q: 如何调试插件？

A: 
```bash
# 查看日志
docker logs wiki-plugin-my-plugin -f

# 进入容器
docker exec -it wiki-plugin-my-plugin sh

# 本地开发模式
docker run -v $(pwd):/app -p 8080:8080 plugin-image
```

### Q: 插件之间如何通信？

A: 通过Docker网络和服务发现：
```python
# 通过服务名访问其他插件
requests.get('http://wiki-plugin-other-plugin:8080/api')
```

### Q: 如何处理插件依赖？

A: 在plugin.json中声明：
```json
{
  "dependencies": [
    {
      "id": "base-plugin",
      "version": ">=1.0.0"
    }
  ]
}
```

---

## 参考资源

- [Docker最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes文档](https://kubernetes.io/docs/)
- [Helm Charts](https://helm.sh/docs/)
- [Wiki.js API文档](https://docs.requarks.io/api/)

---

**祝你开发愉快！** 🚀
