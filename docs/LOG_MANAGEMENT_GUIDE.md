# 日志管理系统使用指南

## 🎯 功能概述

日志管理系统提供了完整的日志收集、存储、查看、搜索、轮转和清理功能。

### 核心特性

- ✅ **自动日志收集** - 所有组件的日志统一存储
- ✅ **智能日志轮转** - 按大小自动压缩归档
- ✅ **快速搜索** - 跨文件关键词搜索
- ✅ **Web界面** - 直观的日志浏览和管理
- ✅ **CLI工具** - 命令行快速操作
- ✅ **自动清理** - 定期删除旧日志，节省空间

---

## 📁 日志目录结构

```
logs/
├── app.log                  # 应用主日志
├── app_error.log            # 错误日志
├── plugin-manager.log       # 插件管理器日志
├── config-manager.log       # 配置管理器日志
├── archive/                 # 归档日志（压缩）
│   ├── app_20260514_120000.log.gz
│   └── ...
└── temp/                    # 临时日志
```

---

## 🚀 使用方法

### 方式1: Web界面（推荐）

```bash
# 访问日志管理界面
http://localhost/config/log-viewer.html

# 或直接访问
http://localhost:5000/log-manager/log_viewer.html
```

**功能:**
- 📄 查看所有日志文件
- 🔍 搜索日志内容
- ⚙️ 轮转和清理日志
- 📊 查看统计信息

---

### 方式2: CLI工具

```bash
# Windows
python log-manager\log_cli.py [command]

# Linux/macOS
python3 log-manager/log_cli.py [command]
```

**常用命令:**

```bash
# 列出日志文件
python log-manager\log_cli.py list

# 查看日志末尾50行
python log-manager\log_cli.py tail app.log 50

# 搜索关键词
python log-manager\log_cli.py search "ERROR" 100

# 查看统计
python log-manager\log_cli.py stats

# 预览日志轮转
python log-manager\log_cli.py rotate -n

# 清理30天前的日志
python log-manager\log_cli.py cleanup 30
```

---

### 方式3: REST API

```bash
# 获取日志列表
curl http://localhost:5000/api/logs

# 读取日志内容
curl http://localhost:5000/api/logs/app.log?lines=100

# 搜索日志
curl "http://localhost:5000/api/logs/search?keyword=ERROR"

# 获取统计
curl http://localhost:5000/api/logs/stats

# 轮转日志
curl -X POST http://localhost:5000/api/logs/rotate

# 清理旧日志
curl -X POST "http://localhost:5000/api/logs/cleanup?days=30"
```

---

## ⚙️ 配置说明

### 日志轮转策略

**默认配置:**
- 单个文件最大: 10MB
- 备份数量: 5个
- 归档保留: 30天

**修改配置:**

在代码中调整：

```python
# log_manager.py
LogManager(
    log_dir='logs',
    max_size_mb=20,      # 改为20MB
    backup_count=10      # 保留10个备份
)
```

---

## 📊 日志级别

| 级别 | 说明 | 示例 |
|------|------|------|
| DEBUG | 调试信息 | 变量值、流程跟踪 |
| INFO | 一般信息 | 启动、停止、操作成功 |
| WARNING | 警告 | 配置缺失、性能下降 |
| ERROR | 错误 | 操作失败、异常 |
| CRITICAL | 严重错误 | 系统崩溃、数据丢失 |

---

## 🔍 搜索技巧

### 基本搜索

```bash
# 搜索ERROR
python log-manager\log_cli.py search "ERROR"

# 搜索特定模块
python log-manager\log_cli.py search "PluginManager"

# 搜索时间范围（需要手动过滤）
python log-manager\log_cli.py search "2026-05-14 15:"
```

### 高级搜索（Web UI）

1. 打开Web界面
2. 切换到"搜索日志"标签
3. 输入关键词
4. 点击搜索

**支持的搜索:**
- 精确匹配: `"exact phrase"`
- 大小写敏感: 勾选选项
- 限制结果数: 默认100条

---

## 🔄 日志轮转

### 自动轮转

当日志文件超过10MB时，系统会：

1. 压缩当前日志为 `.gz` 格式
2. 移动到 `archive/` 目录
3. 创建新的空日志文件
4. 添加轮转时间戳标记

### 手动轮转

```bash
# 预览（不实际执行）
python log-manager\log_cli.py rotate -n

# 执行轮转
python log-manager\log_cli.py rotate
```

### Web UI操作

1. 切换到"日志管理"标签
2. 点击"预览"或"立即轮转"
3. 查看操作结果

---

## 🗑️ 日志清理

### 自动清理建议

**生产环境:**
- 保留天数: 30-90天
- 执行频率: 每周一次

**开发环境:**
- 保留天数: 7-14天
- 执行频率: 每天一次

### 手动清理

```bash
# 预览清理（不实际删除）
python log-manager\log_cli.py cleanup 30 -n

# 执行清理
python log-manager\log_cli.py cleanup 30
```

### Web UI操作

1. 切换到"日志管理"标签
2. 设置保留天数
3. 点击"预览"或"立即清理"

---

## 💡 最佳实践

### 1. 定期监控日志大小

```bash
# 每天检查
python log-manager\log_cli.py stats
```

### 2. 设置自动清理任务

**Linux (cron):**
```bash
# 每周日凌晨2点清理30天前的日志
0 2 * * 0 cd /path/to/wiki && python log-manager/log_cli.py cleanup 30 >> logs/cron.log 2>&1
```

**Windows (任务计划程序):**
- 触发器: 每周日 2:00
- 操作: 运行 `log_cli.py cleanup 30`

### 3. 重要日志备份

```bash
# 导出关键日志
cp logs/app_error.log backups/error-$(date +%Y%m%d).log
```

### 4. 实时监控错误

```bash
# 实时跟踪错误日志
tail -f logs/app_error.log

# 或使用CLI
python log-manager\log_cli.py tail app_error.log 20
```

---

## 🔧 故障排查

### 问题1: 日志文件过大

**解决:**
```bash
# 立即轮转
python log-manager\log_cli.py rotate

# 清理旧日志
python log-manager\log_cli.py cleanup 7
```

### 问题2: 找不到日志

**检查:**
```bash
# 确认日志目录
ls -la logs/

# 查看统计
python log-manager\log_cli.py stats
```

### 问题3: 搜索无结果

**可能原因:**
- 关键词拼写错误
- 日志已被清理
- 搜索范围限制

**解决:**
- 尝试更短的关键词
- 减少保留天数限制
- 检查是否在正确的日志文件中

---

## 📈 性能优化

### 1. 调整日志级别

生产环境使用WARNING以上：

```python
logger.setLevel(logging.WARNING)
```

### 2. 异步日志

对于高并发场景，考虑使用异步日志handler。

### 3. 外部日志服务

大规模部署时，考虑集成：
- ELK Stack (Elasticsearch + Logstash + Kibana)
- Graylog
- Splunk

---

## 🎯 常见场景

### 场景1: 排查启动失败

```bash
# 1. 查看错误日志
python log-manager\log_cli.py tail app_error.log 100

# 2. 搜索关键词
python log-manager\log_cli.py search "ERROR" 50

# 3. Web界面详细查看
# 访问 http://localhost/config/log-viewer.html
```

### 场景2: 监控系统健康

```bash
# 定时检查
watch -n 60 'python log-manager/log_cli.py stats'
```

### 场景3: 审计操作历史

```bash
# 搜索特定用户的操作
python log-manager\log_cli.py search "user=admin" 200
```

---

## 📚 API参考

### GET /api/logs
获取日志文件列表

### GET /api/logs/{filename}
读取日志内容
- 参数: lines, offset

### GET /api/logs/{filename}/tail
查看日志末尾

### GET /api/logs/search
搜索日志
- 参数: keyword, case_sensitive, max_results

### POST /api/logs/rotate
轮转日志
- 参数: dry_run

### POST /api/logs/cleanup
清理旧日志
- 参数: days, dry_run

### GET /api/logs/stats
获取统计信息

---

**享受便捷的日志管理体验！** 📋✨
