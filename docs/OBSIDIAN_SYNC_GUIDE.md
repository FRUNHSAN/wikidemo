# Obsidian双向同步指南

## 📚 功能概述

Obsidian双向同步工具实现了本地Obsidian仓库与Wiki.js之间的智能同步，包含：

- ✅ **双向同步** - 本地↔Wiki自动同步
- ✅ **冲突缓冲池** - 智能处理冲突，草稿箱机制
- ✅ **细粒度策略** - 每个文件夹可配置不同的同步策略
- ✅ **文件类型过滤** - 选择性同步.md、图片等
- ✅ **实时监听** - 文件保存时立即同步（可选）

---

## 🏗️ 架构设计

```
┌─────────────────┐         ┌──────────────────┐
│  Obsidian Vault │◄───────►│   Sync Manager   │
│  (本地文件夹)    │  监听    │  (Python脚本)     │
└─────────────────┘         └────────┬─────────┘
                                     │
                              冲突检测&处理
                                     │
                                     ▼
                          ┌──────────────────┐
                          │  Conflict Pool   │
                          │  (草稿箱)         │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │   Wiki.js API    │
                          │  (远程Wiki)       │
                          └──────────────────┘
```

---

## 🚀 快速开始

### 步骤1: 准备Obsidian仓库

```bash
# 创建Obsidian仓库文件夹
mkdir obsidian-vault
cd obsidian-vault

# 初始化Git（推荐）
git init
```

### 步骤2: 配置同步

```bash
# 复制配置模板
cp obsidian-sync-config.example.json obsidian-sync-config.json

# 编辑配置
vim obsidian-sync-config.json
```

修改以下关键配置：

```json
{
  "local_folder": "./obsidian-vault",
  "wiki_base_url": "http://localhost",
  "wiki_api_token": "从Wiki管理后台获取"
}
```

### 步骤3: 获取Wiki API Token

1. 登录Wiki管理后台
2. 进入"系统设置" → "API"
3. 生成新的API Token
4. 复制到配置文件

### 步骤4: 运行同步

```bash
# 首次同步
python scripts/obsidian-sync/sync_manager.py

# 查看状态
python scripts/obsidian-sync/sync_manager.py --status
```

---

## ⚙️ 配置详解

### 同步策略说明

#### 1. immediate（立即同步）
- 文件保存后立即同步到Wiki
- 无需确认
- 适合：日常笔记、日记

```json
{
  "path_pattern": "daily-notes/",
  "strategy": "immediate"
}
```

#### 2. auto_confirm（自动检测+确认）
- 检测到变化后等待确认
- 可以审查更改
- 适合：重要文档

```json
{
  "path_pattern": "projects/",
  "strategy": "auto_confirm"
}
```

#### 3. manual（手动触发）
- 只在手动执行时同步
- 完全控制
- 适合：草稿、实验性内容

#### 4. disabled（不同步）
- 完全不参与同步
- 适合：私密笔记

### 文件类型过滤

```json
{
  "file_type_filters": {
    "enabled": true,
    "allowed_types": [".md", ".png", ".jpg"],
    "max_file_size_mb": 10
  }
}
```

支持的类型：
- `.md` - Markdown文档
- `.png`, `.jpg` - 图片
- `.pdf` - PDF文档
- 任意自定义类型

### 排除路径

```json
{
  "excluded_paths": [
    ".git/",
    ".obsidian/",
    "templates/",
    "trash/"
  ]
}
```

---

## 🔄 同步流程

### 本地→Wiki（上传）

```
1. 检测本地文件变化
   ↓
2. 计算文件哈希值
   ↓
3. 对比上次同步状态
   ↓
4. 检查是否有冲突
   ↓
5a. 无冲突 → 直接上传
5b. 有冲突 → 创建草稿
   ↓
6. 更新元数据
```

### Wiki→本地（下载）

```
1. 列出Wiki所有页面
   ↓
2. 对比本地文件
   ↓
3. 检测新增/修改/删除
   ↓
4. 下载到本地
   ↓
5. 处理冲突（如有）
```

---

## ⚠️ 冲突处理

### 什么是冲突？

当**本地和Wiki都修改了同一个文件**时，就产生了冲突。

### 冲突解决流程

```
检测到冲突
    ↓
创建冲突记录
    ↓
生成草稿文件（drafts/xxx.md）
    ↓
用户在草稿中合并两个版本
    ↓
标记冲突已解决
    ↓
同步合并后的内容
```

### 查看待处理冲突

```bash
# 查看冲突列表
python scripts/obsidian-sync/sync_manager.py --conflicts

# 输出示例:
# 待处理冲突: 2
# 1. daily-notes/2026-05-14.md
# 2. projects/project-a.md
```

### 解决冲突

**方法1: 手动合并**

1. 打开 `drafts/xxx.md`
2. 你会看到两个版本的内容标记
3. 编辑合并后的最终版本
4. 保存并标记为已解决

```bash
# 标记冲突已解决
python scripts/obsidian-sync/sync_manager.py --resolve <file-path>
```

**方法2: 选择一方**

```bash
# 使用本地版本
python scripts/obsidian-sync/sync_manager.py --resolve <file-path> --use local

# 使用Wiki版本
python scripts/obsidian-sync/sync_manager.py --resolve <file-path> --use wiki
```

---

## 📊 同步规则示例

### 场景1: 个人知识库

```json
{
  "sync_rules": [
    {
      "path_pattern": "daily-notes/",
      "strategy": "immediate",
      "file_types": [".md"]
    },
    {
      "path_pattern": "knowledge/",
      "strategy": "auto_confirm",
      "file_types": [".md", ".png"]
    },
    {
      "path_pattern": "private/",
      "strategy": "disabled"
    }
  ]
}
```

### 场景2: 团队协作

```json
{
  "sync_rules": [
    {
      "path_pattern": "shared/",
      "strategy": "auto_confirm",
      "file_types": [".md"]
    },
    {
      "path_pattern": "meetings/",
      "strategy": "immediate"
    }
  ],
  "excluded_paths": [
    "personal/",
    "drafts/"
  ]
}
```

---

## 🔧 高级用法

### 定时同步

使用cron或任务计划程序：

**Linux/macOS:**
```bash
# 每5分钟同步一次
*/5 * * * * cd /path/to/wiki && python scripts/obsidian-sync/sync_manager.py >> logs/sync.log 2>&1
```

**Windows:**
使用任务计划程序，设置每5分钟运行一次：
```
程序: python
参数: scripts/obsidian-sync/sync_manager.py
起始位置: f:\wikidemotongyi
```

### 实时监控（开发中）

未来版本将支持文件系统监听：

```python
# 使用watchdog库监听文件变化
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SyncHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            trigger_sync(event.src_path)
```

### 批量导入

```bash
# 从现有文件夹导入
python scripts/obsidian-sync/sync_manager.py --import ./my-notes

# 指定目标路径
python scripts/obsidian-sync/sync_manager.py --import ./my-notes --target imported/2026
```

---

## 📁 目录结构

```
wikidemotongyi/
├── obsidian-vault/          # Obsidian本地仓库
│   ├── daily-notes/
│   ├── projects/
│   └── knowledge/
│
├── drafts/                  # 冲突草稿
│   └── ...
│
├── scripts/obsidian-sync/
│   ├── sync_manager.py      # 同步管理器
│   └── ...
│
├── obsidian-sync-config.json  # 配置文件
├── sync-metadata.json         # 同步元数据（自动生成）
└── sync-conflicts.json        # 冲突记录（自动生成）
```

---

## 🔍 故障排查

### 问题1: 同步失败

**检查:**
```bash
# 查看详细日志
cat logs/obsidian-sync.log

# 测试Wiki API连接
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost/api/pages
```

**常见原因:**
- API Token错误
- 网络连接问题
- 权限不足

### 问题2: 冲突不断产生

**原因:** 两边同时修改

**解决:**
1. 改用 `immediate` 策略（减少冲突窗口）
2. 避免在多处同时编辑
3. 使用Git作为中间层

### 问题3: 文件未同步

**检查:**
```bash
# 查看同步状态
python scripts/obsidian-sync/sync_manager.py --status

# 检查文件是否在排除列表
cat obsidian-sync-config.json | grep excluded
```

### 问题4: 性能问题

**优化:**
```json
{
  "file_type_filters": {
    "max_file_size_mb": 5  // 降低文件大小限制
  },
  "excluded_paths": [
    "large-folder/"  // 排除大文件夹
  ]
}
```

---

## 💡 最佳实践

### 1. 使用Git作为中间层

```
Obsidian ←→ Git ←→ Sync Script ←→ Wiki
```

**优势:**
- 版本控制
- 离线工作
- 冲突解决更简单

### 2. 合理的文件夹组织

```
obsidian-vault/
├── daily-notes/      # 立即同步
├── projects/         # 自动确认
├── knowledge/        # 自动确认
├── drafts/           # 不同步
└── private/          # 不同步
```

### 3. 定期清理

```bash
# 清理旧草稿
find drafts/ -mtime +30 -delete

# 清理旧日志
find logs/ -name "*.log" -mtime +7 -delete
```

### 4. 备份配置

```bash
# 备份配置文件
cp obsidian-sync-config.json backups/config-$(date +%Y%m%d).json
```

---

## 🎯 与RSS插件配合使用

你可以结合RSS阅读器插件打造完整的知识工作流：

```
RSS资讯 → Wiki日报 → Obsidian整理 → 同步回Wiki
```

**工作流:**
1. RSS插件自动抓取资讯到Wiki
2. 在Obsidian中阅读和整理
3. 添加个人笔记和标注
4. 自动同步回Wiki分享

---

## 📞 获取帮助

- 查看日志: `logs/obsidian-sync.log`
- 检查状态: `python sync_manager.py --status`
- 查看冲突: `python sync_manager.py --conflicts`

---

**祝你同步愉快！** 🔄✨
