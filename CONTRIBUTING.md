# 贡献指南

感谢你对 WikiDemoTongYi 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题

如果你发现了bug或有新功能建议，请[创建Issue](https://github.com/your-username/wikidemotongyi/issues)，并包含以下信息：

1. **问题描述** - 清晰简洁地描述问题
2. **复现步骤** - 如何重现这个问题
3. **预期行为** - 你期望发生什么
4. **实际行为** - 实际发生了什么
5. **环境信息** - Docker版本、操作系统等
6. **日志文件** - 相关的错误日志（如果有）

### 提交代码

1. **Fork** 本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 **Pull Request**

### 代码规范

- 遵循现有的代码风格
- Python代码使用PEP 8规范
- 添加必要的注释和文档
- 确保代码通过现有测试
- 更新相关文档

### 文档改进

- 修正拼写或语法错误
- 补充缺失的说明
- 添加示例和截图
- 翻译文档到其他语言

## 📋 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/your-username/wikidemotongyi.git
cd wikidemotongyi
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动开发环境

```bash
./deploy.sh start  # Linux/macOS
deploy.bat start   # Windows
```

### 4. 运行测试

```bash
# 检查Docker容器状态
docker compose ps

# 查看服务日志
docker compose logs -f
```

## 🎯 贡献领域

### 高优先级

- 🐛 Bug修复
- 📝 文档完善
- 🔒 安全加固
- ⚡ 性能优化

### 中优先级

- 🔌 新插件开发
- 🌍 国际化支持
- 🎨 UI/UX改进
- 🧪 测试用例

### 低优先级

- ✨ 新功能建议
- 🔄 代码重构
- 🛠️ 工具链改进

## 💡 插件开发

如果你想开发新插件，请参考 [插件开发指南](docs/PLUGIN_DEVELOPMENT_GUIDE.md)。

基本步骤：
1. 在 `plugins/` 目录创建插件文件夹
2. 实现 `plugin.py` 和 `plugin.json`
3. 注册插件到插件管理器
4. 编写插件文档

## 📞 联系方式

- GitHub Issues: [报告问题](https://github.com/your-username/wikidemotongyi/issues)
- Email: your-email@example.com

## 📜 行为准则

请遵守以下原则：

1. **尊重他人** - 友善交流，尊重不同观点
2. **建设性反馈** - 提供具体的改进建议
3. **保持专业** - 避免人身攻击和不适当言论
4. **协作精神** - 乐于帮助他人，接受他人帮助

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

**注意：** 在提交PR之前，请确保你的代码通过了基本测试，并且没有引入新的问题。
