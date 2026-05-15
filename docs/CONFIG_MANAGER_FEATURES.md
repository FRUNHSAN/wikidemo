# 配置管理系统 - 完整功能说明

## 🎉 已完成的三大增强功能

### ✅ 1. 集成到Wiki.js作为子路由

现在你可以通过Wiki.js直接访问配置管理界面！

#### 访问方式

```
http://localhost/config
```

无需单独启动服务器，Nginx会自动将请求转发到配置管理器。

#### 技术实现

- **Nginx反向代理**: 配置了`/config`、`/api/config`、`/api/plugins`路由
- **Docker服务**: 添加了`config-manager`容器，与Wiki.js在同一网络
- **无缝集成**: 用户感觉像是Wiki.js的一部分

#### 优势

✅ 统一入口 - 不需要记住多个端口
✅ 单点登录 - 可以集成Wiki.js的认证
✅ 简化部署 - 一个命令启动所有服务

---

### ✅ 2. 配置模板功能

快速应用预设配置，适合不同使用场景！

#### 内置模板

##### 模板1: 个人Wiki基础配置 (`personal-wiki`)
**适用场景**: 个人知识库

**包含配置**:
- ✅ RSS阅读器插件（启用）
- ✅ Obsidian同步（auto_confirm策略）
- ✅ 基础安全设置

**使用方法**:
```bash
# CLI
config> apply-template personal-wiki

# Web UI
在"模板"标签页选择"个人Wiki基础配置" → 点击"应用"
```

---

##### 模板2: 团队协作配置 (`team-collab`)
**适用场景**: 小团队共享Wiki

**包含配置**:
- ✅ 所有插件启用
- ✅ Git同步启用
- ✅ 立即同步策略
- ✅ 支持图片文件

---

##### 模板3: AI增强配置 (`ai-powered`)
**适用场景**: 喜欢自动化资讯整理

**包含配置**:
- ✅ OpenAI API集成
- ✅ RSS智能摘要
- ✅ 每小时自动更新
- ✅ Git备份

---

#### 自定义模板

创建你自己的模板：

1. 在 `config-manager/templates/` 目录创建JSON文件
2. 按照以下格式：

```json
{
  "name": "我的模板",
  "description": "模板描述",
  "version": "1.0",
  "configs": {
    "env": {...},
    "plugins": {...},
    "sync": {...}
  }
}
```

3. 保存后即可在Web UI中看到

---

### ✅ 3. 配置回滚功能

再也不怕改错配置了！随时回滚到之前的状态。

#### 自动快照

系统会在以下情况自动创建快照：
- ✅ 应用模板前后
- ✅ 批量导入配置
- ✅ 手动触发

#### 查看快照列表

**CLI:**
```bash
config> snapshots

# 输出示例:
# [0] 2026-05-14 15:30:00 - 初始状态
# [1] 2026-05-14 15:35:00 - 应用模板前: personal-wiki
# [2] 2026-05-14 15:35:05 - 已应用模板: personal-wiki
```

**Web UI:**
在"历史记录"标签页查看

---

#### 回滚操作

**方法1: 回滚到指定快照**

```bash
config> rollback 1

# 回滚到索引为1的快照
```

**方法2: 回滚最后一次变更**

```bash
config> rollback-last

# 撤销最后一次配置修改
```

**Web UI:**
在"历史记录"标签页点击"回滚"按钮

---

#### 快照管理

- **自动清理**: 只保留最近20个快照
- **详细描述**: 每个快照都有时间戳和描述
- **安全机制**: 回滚前会创建新快照（可再次回滚）

---

## 🚀 完整使用流程示例

### 场景1: 新用户快速 setup

```bash
# 1. 启动系统
./deploy.sh start

# 2. 访问配置界面
# 浏览器打开: http://localhost/config

# 3. 应用个人Wiki模板
# 在Web UI中选择"个人Wiki基础配置" → 应用

# 4. 修改OpenAI API Key
config> set env OPENAI_API_KEY sk-your-key

# 5. 完成！开始使用
```

### 场景2: 配置出错后回滚

```bash
# 1. 不小心改错了配置
config> set env POSTGRES_PASSWORD wrong-password

# 2. 发现服务无法启动

# 3. 查看历史
config> history 5

# 4. 回滚最后一次变更
config> rollback-last

# 5. 问题解决！
```

### 场景3: 团队批量部署

```bash
# 1. 在一台机器上配置好

# 2. 导出配置
config> export json team-config.json

# 3. 复制到其他机器
scp team-config.json user@server2:/path/to/wiki

# 4. 在其他机器导入
config> import team-config.json

# 5. 或者直接使用模板
config> apply-template team-collab
```

---

## 📊 功能对比

| 功能 | 之前 | 现在 |
|------|------|------|
| 配置方式 | 手动编辑文件 | CLI + Web UI |
| 配置验证 | 无 | 自动验证 |
| 历史记录 | 无 | 完整追踪 |
| 快速部署 | 手动配置 | 模板一键应用 |
| 错误恢复 | 手动修复 | 一键回滚 |
| 访问方式 | 多个端口 | 统一入口(/config) |

---

## 🎯 API参考

### 模板API

```bash
# 列出所有模板
GET /api/config/templates

# 应用模板
POST /api/config/templates/apply
{
  "template_id": "personal-wiki"
}
```

### 快照API

```bash
# 列出快照
GET /api/config/snapshots

# 回滚到指定快照
POST /api/config/snapshots/rollback
{
  "snapshot_index": 1
}

# 回滚最后一次变更
POST /api/config/rollback-last
```

---

## 💡 最佳实践

### 1. 定期创建快照

```bash
# 在进行重大配置变更前
config> snapshot "Before major changes"
```

### 2. 使用模板快速部署

```bash
# 新环境setup
config> apply-template personal-wiki
# 然后微调配置
```

### 3. 测试配置变更

```bash
# 1. 创建快照
config> snapshot "Before test"

# 2. 修改配置
config> set ...

# 3. 测试

# 4. 如有问题，回滚
config> rollback-last
```

### 4. 分享自定义模板

```bash
# 1. 导出当前配置
config> export json my-template.json

# 2. 编辑添加元数据
{
  "name": "My Custom Config",
  "description": "...",
  "configs": {...}
}

# 3. 放到templates目录
# 4. 分享给团队
```

---

## 🔍 故障排查

### 问题1: /config 无法访问

**检查:**
```bash
# 确认config-manager容器运行
docker compose ps

# 查看日志
docker compose logs config-manager

# 重启服务
docker compose restart config-manager
```

### 问题2: 模板应用失败

**检查:**
```bash
# 查看模板文件
ls config-manager/templates/

# 验证JSON格式
cat config-manager/templates/xxx.json | python -m json.tool
```

### 问题3: 回滚失败

**检查:**
```bash
# 查看快照列表
config> snapshots

# 检查是否有可用快照
# 如果没有，只能手动修复配置
```

---

## 📚 相关文档

- [配置管理指南](CONFIG_MANAGER_GUIDE.md)
- [RSS阅读器指南](RSS_READER_GUIDE.md)
- [Obsidian同步指南](OBSIDIAN_SYNC_GUIDE.md)

---

**享受便捷的配置管理体验！** ⚙️✨
