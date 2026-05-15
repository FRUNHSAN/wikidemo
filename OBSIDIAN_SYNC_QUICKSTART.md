# Obsidian同步 - 5分钟快速开始

## 🎯 已完成的功能

✅ **Obsidian双向同步工具**已创建完成！

### 核心特性
- ✅ 双向同步（本地↔Wiki）
- ✅ 智能冲突处理（草稿箱机制）
- ✅ 细粒度同步策略（每个文件夹可配置）
- ✅ 文件类型过滤
- ✅ 自动元数据跟踪

---

## 🚀 立即启用（4步）

### 步骤1: 准备Obsidian仓库

```bash
# 创建Obsidian文件夹
mkdir obsidian-vault

# （可选）初始化为Git仓库
cd obsidian-vault
git init
cd ..
```

### 步骤2: 配置同步

```bash
# Windows
copy obsidian-sync-config.example.json obsidian-sync-config.json

# Linux/macOS
cp obsidian-sync-config.example.json obsidian-sync-config.json
```

编辑 `obsidian-sync-config.json`：

```json
{
  "local_folder": "./obsidian-vault",
  "wiki_base_url": "http://localhost",
  "wiki_api_token": "从Wiki管理后台获取"
}
```

### 步骤3: 获取Wiki API Token

1. 登录Wiki: http://localhost
2. 点击右上角头像 → 系统设置
3. 进入"API"标签
4. 点击"生成新Token"
5. 复制Token到配置文件

### 步骤4: 运行同步

```bash
# Windows
scripts\obsidian-sync\sync.bat

# Linux/macOS
chmod +x scripts/obsidian-sync/sync.sh
./scripts/obsidian-sync/sync.sh
```

---

## 📝 测试同步

### 1. 在Obsidian中创建笔记

在 `obsidian-vault/` 文件夹中创建文件：

```markdown
# 我的测试笔记

这是从Obsidian同步到Wiki的测试内容。

## 功能列表
- 双向同步
- 冲突处理
- 自动更新
```

保存为 `test-note.md`

### 2. 执行同步

```bash
scripts\obsidian-sync\sync.bat
```

### 3. 在Wiki中查看

访问: `http://localhost/test-note`

你应该能看到刚才创建的内容！

---

## ⚙️ 配置同步策略

### 示例配置

编辑 `obsidian-sync-config.json`：

```json
{
  "sync_rules": [
    {
      "path_pattern": "daily-notes/",
      "strategy": "immediate",
      "file_types": [".md"]
    },
    {
      "path_pattern": "projects/",
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

### 策略说明

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| immediate | 立即同步，无需确认 | 日常笔记、日记 |
| auto_confirm | 检测后等待确认 | 重要文档 |
| manual | 手动触发 | 草稿 |
| disabled | 不同步 | 私密内容 |

---

## ⚠️ 处理冲突

### 当发生冲突时

```
[WARN] 检测到冲突: daily-notes/2026-05-14.md
[INFO] 已创建冲突草稿: drafts/daily-notes/2026-05-14.md
```

### 解决步骤

1. **打开草稿文件**
   ```
   drafts/daily-notes/2026-05-14.md
   ```

2. **你会看到两个版本**
   ```markdown
   <!-- ===== 本地版本 ===== -->
   本地的内容...

   <!-- ===== Wiki版本 ===== -->
   Wiki的内容...

   <!-- ===== 请在此处编辑合并后的内容 ===== -->
   ```

3. **编辑合并后的内容**

4. **标记为已解决**
   ```bash
   # TODO: 实现命令
   python scripts/obsidian-sync/sync_manager.py --resolve daily-notes/2026-05-14.md
   ```

---

## 🔧 常用命令

### Windows

```bash
# 同步
scripts\obsidian-sync\sync.bat

# 查看状态
scripts\obsidian-sync\sync.bat status

# 查看冲突
scripts\obsidian-sync\sync.bat conflicts
```

### Linux/macOS

```bash
# 同步
./scripts/obsidian-sync/sync.sh

# 查看状态
./scripts/obsidian-sync/sync.sh status

# 查看冲突
./scripts/obsidian-sync/sync.sh conflicts
```

---

## 💡 高级技巧

### 1. 定时同步

**Windows:** 使用任务计划程序
- 触发器: 每5分钟
- 操作: 运行 `sync.bat`

**Linux/macOS:** 使用cron

```bash
crontab -e

# 添加这一行
*/5 * * * * cd /path/to/wiki && ./scripts/obsidian-sync/sync.sh >> logs/sync.log 2>&1
```

### 2. 排除特定文件夹

```json
{
  "excluded_paths": [
    ".git/",
    ".obsidian/",
    "templates/",
    "private/"
  ]
}
```

### 3. 同步图片

```json
{
  "file_type_filters": {
    "allowed_types": [".md", ".png", ".jpg", ".gif"]
  }
}
```

---

## 📊 查看同步状态

```bash
# Windows
scripts\obsidian-sync\sync.bat status

# 输出示例:
# 同步状态:
#   总文件数: 42
#   待处理冲突: 0
#   最后同步: 2026-05-14T15:30:00
```

---

## 🔍 故障排查

### 问题: 同步失败

**检查日志:**
```bash
cat logs/obsidian-sync.log
```

**常见原因:**
1. API Token错误 → 重新生成Token
2. 网络连接问题 → 检查Wiki是否运行
3. 路径配置错误 → 检查 `local_folder` 配置

### 问题: 文件未同步

**检查:**
```bash
# 查看文件是否在排除列表
cat obsidian-sync-config.json | grep excluded

# 查看文件类型是否允许
cat obsidian-sync-config.json | grep allowed_types
```

---

## 🎯 完整工作流

结合RSS插件使用：

```
1. RSS插件自动抓取资讯
   ↓
2. 发布到Wiki (rss-digest/YYYY-MM-DD)
   ↓
3. Obsidian同步工具下载到本地
   ↓
4. 在Obsidian中阅读和标注
   ↓
5. 添加个人笔记
   ↓
6. 自动同步回Wiki
```

---

## 📚 更多文档

- [完整指南](docs/OBSIDIAN_SYNC_GUIDE.md)
- [配置示例](obsidian-sync-config.example.json)
- [RSS阅读器](docs/RSS_READER_GUIDE.md)

---

**开始享受无缝同步吧！** 🔄✨
