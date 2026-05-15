# 云原生架构设计文档

## 📋 目录

1. [架构概览](#架构概览)
2. [核心组件](#核心组件)
3. [插件系统](#插件系统)
4. [服务网格](#服务网格)
5. [可观测性](#可观测性)
6. [安全架构](#安全架构)
7. [扩展性设计](#扩展性设计)
8. [迁移指南](#迁移指南)

---

## 架构概览

WikiDemoTongYi采用**云原生（Cloud-Native）**架构设计，遵循以下原则：

- ✅ **容器化**: 所有组件运行在Docker容器中
- ✅ **微服务**: 松耦合、独立部署的服务
- ✅ **声明式API**: Kubernetes-native配置
- ✅ **服务网格**: 统一的服务发现和通信
- ✅ **自动化运维**: CI/CD、自动扩缩容、自愈

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Ingress Controller                     │
│                  (Nginx / Traefik)                        │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────┼──────────┬──────────────┐
    │          │          │              │
┌───▼───┐ ┌───▼───┐ ┌───▼────┐ ┌──────▼──────┐
│ Wiki  │ │Config │ │ Plugin │ │ Monitoring  │
│  JS   │ │Manager│ │Gateway │ │(Prometheus) │
└───┬───┘ └───┬───┘ └───┬────┘ └─────────────┘
    │         │          │
    └─────────┴──────────┘
              │
    ┌─────────▼──────────┐
    │ Service Discovery   │
    │  (Consul/Etcd)      │
    └─────────┬──────────┘
              │
    ┌─────────┼──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼──┐ ┌────▼───┐ ┌───▼────┐
│Plugin1│ │P2   │ │Plugin3 │ │PluginN │
│Python │ │Node │ │  Go    │ │ Rust   │
└───────┘ └─────┘ └────────┘ └────────┘
    │
┌───▼────────┐
│ PostgreSQL │
│ (Stateful) │
└────────────┘
```

---

## 核心组件

### 1. 控制平面 (Control Plane)

| 组件 | 职责 | 技术栈 |
|------|------|--------|
| API Gateway | 路由转发、认证、限流 | Nginx / Kong |
| Service Discovery | 服务注册与发现 | Consul / Etcd |
| Config Manager | 配置管理、模板应用 | Python + Flask |
| Plugin Manager | 插件生命周期管理 | Python |

### 2. 数据平面 (Data Plane)

| 组件 | 职责 | 技术栈 |
|------|------|--------|
| Wiki.js | 核心Wiki引擎 | Node.js |
| PostgreSQL | 持久化存储 | PostgreSQL 15 |
| Plugins | 业务逻辑扩展 | 多语言支持 |

### 3. 可观测性 (Observability)

| 组件 | 职责 | 技术栈 |
|------|------|--------|
| Prometheus | 指标收集 | Prometheus |
| Grafana | 可视化监控 | Grafana |
| Loki | 日志聚合 | Grafana Loki |
| Jaeger | 分布式追踪 | Jaeger |

---

## 插件系统

### 插件分类

```
插件类型
├── Content Plugins (内容类)
│   ├── RSS Reader
│   ├── Web Scraper
│   └── AI Generator
│
├── Sync Plugins (同步类)
│   ├── Obsidian Sync
│   ├── Notion Sync
│   └── GitHub Sync
│
├── Integration Plugins (集成类)
│   ├── Slack Bot
│   ├── Discord Bot
│   └── Email Notification
│
├── Security Plugins (安全类)
│   ├── OAuth Provider
│   ├── LDAP Auth
│   └── Audit Logger
│
└── Analytics Plugins (分析类)
    ├── Page Views
    ├── User Behavior
    └── Search Analytics
```

### 插件生命周期

```
┌─────────┐     ┌──────────┐     ┌─────────┐
│Develop  │────▶│  Build   │────▶│ Publish │
└─────────┘     └──────────┘     └────┬────┘
                                      │
                                      ▼
┌─────────┐     ┌──────────┐     ┌─────────┐
│Destroy  │◀────│ Uninstall│◀────│ Install │
└─────────┘     └──────────┘     └─────────┘
                      ▲
                      │
                 ┌────┴────┐
                 │ Update  │
                 └─────────┘
```

### 插件通信模式

#### 1. 同步调用 (REST API)

```python
# 插件A调用插件B
response = requests.post(
    'http://wiki-plugin-b:8080/api/process',
    json={'data': '...'}
)
```

#### 2. 异步消息 (Message Queue)

```python
# 发布事件
rabbitmq.publish('plugin.event.created', {
    'plugin_id': 'rss-reader',
    'event': 'article_fetched'
})

# 订阅事件
rabbitmq.subscribe('plugin.event.*', handler)
```

#### 3. 数据共享 (Shared Volume)

```yaml
volumes:
  - plugin-shared-data:/app/shared
```

---

## 服务网格

### 服务发现机制

#### Docker环境

基于Docker Label的服务发现：

```yaml
labels:
  - "wiki.plugin=true"
  - "wiki.plugin.name=rss-reader"
  - "wiki.plugin.version=1.0.0"
```

自动发现脚本：

```bash
docker ps --filter label=wiki.plugin=true \
  --format '{{.Labels}}'
```

#### Kubernetes环境

使用Kubernetes Service和Endpoints：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: plugin-rss-reader
spec:
  selector:
    app.kubernetes.io/name: rss-reader
  ports:
    - port: 8080
```

### API网关配置

#### Nginx配置示例

```nginx
upstream plugin_rss_reader {
    server wiki-plugin-rss-reader:8080;
}

location /api/plugins/rss-reader {
    proxy_pass http://plugin_rss_reader;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    
    # 限流
    limit_req zone=plugins burst=20 nodelay;
    
    # 超时
    proxy_read_timeout 30s;
}
```

---

## 可观测性

### 1. 指标收集 (Metrics)

#### Prometheus配置

```yaml
scrape_configs:
  - job_name: 'wiki-plugins'
    static_configs:
      - targets: 
        - 'wiki-plugin-rss-reader:8080'
        - 'wiki-plugin-obsidian-sync:8080'
    metrics_path: '/metrics'
```

#### 关键指标

- `plugin_requests_total` - 请求总数
- `plugin_request_duration_seconds` - 请求延迟
- `plugin_errors_total` - 错误数
- `plugin_memory_usage_bytes` - 内存使用
- `plugin_cpu_usage_percent` - CPU使用率

### 2. 日志聚合 (Logging)

#### 日志格式 (JSON)

```json
{
  "timestamp": "2026-05-15T12:00:00Z",
  "level": "INFO",
  "plugin": "rss-reader",
  "message": "Fetched 10 articles",
  "duration_ms": 1234,
  "trace_id": "abc123"
}
```

#### Loki配置

```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push

positions:
  filename: /tmp/positions.yaml

scrape_configs:
  - job_name: plugins
    static_configs:
      - targets:
          - localhost
        labels:
          job: plugin-logs
          __path__: /var/log/plugins/*.log
```

### 3. 分布式追踪 (Tracing)

#### Jaeger集成

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

tracer = trace.get_tracer("plugin-tracer")

with tracer.start_as_current_span("process_article"):
    # 业务逻辑
    pass
```

---

## 安全架构

### 1. 网络隔离

```
┌─────────────────────────┐
│    External Network      │
└──────────┬──────────────┘
           │
    ┌──────▼──────┐
    │ DMZ (Nginx) │
    └──────┬──────┘
           │
    ┌──────▼──────────┐
    │ Internal Network│
    │  (Wiki + Plugins)│
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │ Database Network│
    │  (PostgreSQL)    │
    └─────────────────┘
```

### 2. RBAC权限控制

```yaml
# Kubernetes RBAC
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: plugin-role
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list"]
```

### 3. Secret管理

```yaml
# Kubernetes Secrets
apiVersion: v1
kind: Secret
metadata:
  name: plugin-secrets
type: Opaque
data:
  api-key: <base64-encoded>
  db-password: <base64-encoded>
```

### 4. 镜像安全

```bash
# 扫描镜像漏洞
trivy image wikidemotongyi/plugin-rss-reader:latest

# 签名镜像
cosign sign wikidemotongyi/plugin-rss-reader:latest
```

---

## 扩展性设计

### 1. 水平扩展

#### Kubernetes HPA (Horizontal Pod Autoscaler)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: plugin-rss-reader-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: plugin-rss-reader
  minReplicas: 1
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### 2. 垂直扩展

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

### 3. 插件市场扩展

```
插件注册表架构
├── Official Plugins (官方维护)
│   ├── RSS Reader
│   ├── Obsidian Sync
│   └── Daily Digest
│
├── Community Plugins (社区贡献)
│   ├── Plugin A
│   ├── Plugin B
│   └── ...
│
└── Enterprise Plugins (企业版)
    ├── Advanced Auth
    ├── Audit Trail
    └── Custom Integrations
```

---

## 迁移指南

### 从Docker Compose到Kubernetes

#### 步骤1: 准备Helm Chart

```bash
# 已提供Helm Chart
helm install wiki ./helm/wikidemotongyi
```

#### 步骤2: 迁移配置

```bash
# Docker Compose环境变量 → Kubernetes ConfigMap
kubectl create configmap wiki-config \
  --from-env-file=.env
```

#### 步骤3: 迁移数据

```bash
# 备份PostgreSQL
kubectl exec -it postgresql-0 -- pg_dump wikidb > backup.sql

# 恢复数据
cat backup.sql | kubectl exec -i postgresql-0 -- psql wikidb
```

#### 步骤4: 验证

```bash
# 检查所有Pod状态
kubectl get pods -n wiki-system

# 检查服务
kubectl get svc -n wiki-system

# 访问应用
kubectl port-forward svc/wiki 8080:80
```

### 云平台特定配置

#### AWS EKS

```yaml
# 使用EBS存储
storageClass: gp2

# 使用ALB Ingress
ingressClassName: alb
```

#### Azure AKS

```yaml
# 使用Azure Disk
storageClass: managed-premium

# 使用Application Gateway
ingressClassName: azure-application-gateway
```

#### GCP GKE

```yaml
# 使用Persistent Disk
storageClass: standard

# 使用GCLB
ingressClassName: gce
```

---

## 性能优化

### 1. 缓存策略

```python
# Redis缓存
import redis

cache = redis.Redis(host='redis', port=6379)

def get_data(key):
    # 先查缓存
    data = cache.get(key)
    if data:
        return json.loads(data)
    
    # 缓存未命中，查询数据库
    data = query_database(key)
    cache.setex(key, 300, json.dumps(data))  # 5分钟过期
    return data
```

### 2. 连接池

```python
# 数据库连接池
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql://user:pass@db:5432/wikidb',
    pool_size=10,
    max_overflow=20
)
```

### 3. 异步处理

```python
# Celery异步任务
from celery import Celery

celery = Celery('tasks', broker='redis://redis:6379')

@celery.task
def process_article(article_id):
    # 耗时操作
    pass
```

---

## 故障恢复

### 1. 健康检查

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 2. 重启策略

```yaml
restartPolicy: Always

# 退避策略
backoffLimit: 6
```

### 3. 数据备份

```bash
# 定时备份CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:15
              command:
                - /bin/sh
                - -c
                - pg_dump wikidb > /backup/$(date +%Y%m%d).sql
          restartPolicy: OnFailure
```

---

## 总结

WikiDemoTongYi的云原生架构具有以下优势：

✅ **高可用**: 多副本、自动故障恢复  
✅ **可扩展**: 水平/垂直自动扩缩容  
✅ **可观测**: 完整的监控、日志、追踪  
✅ **安全**: 网络隔离、RBAC、Secret管理  
✅ **便携**: Docker/Kubernetes无缝迁移  
✅ **生态**: 丰富的插件市场和社区支持  

---

**最后更新**: 2026-05-15  
**版本**: v1.0.0
