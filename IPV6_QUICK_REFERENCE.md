# ========================================
# 你的 IPv6 公网访问快速参考
# ========================================

📍 你的公网 IPv6 地址:
   2a13:edc0:301:4d70:9c8e:f12a:32b5:e04d

🌐 访问地址:
   HTTP:  http://[2a13:edc0:301:4d70:9c8e:f12a:32b5:e04d]
   HTTPS: https://[2a13:edc0:301:4d70:9c8e:f12a:32b5:e04d]

📱 手机访问（使用流量，非WiFi）:
   在浏览器输入: http://[2a13:edc0:301:4d70:9c8e:f12a:32b5:e04d]

🔧 快速配置命令:
   1. 配置防火墙:
      .\scripts\setup-ipv6-access.ps1
   
   2. 检查服务状态:
      docker compose ps
   
   3. 查看日志:
      docker compose logs -f nginx

🔒 安全清单（按顺序完成）:
   □ 修改默认管理员密码
   □ 配置 HTTPS（SSL证书）
   □ 设置域名和DDNS
   □ 启用访问日志监控
   □ 配置定期备份

⚠️ 重要提醒:
   - IPv6地址可能变化，建议使用DDNS
   - 首次访问会显示"不安全"警告（正常）
   - 必须修改默认密码: changeme123
   - 定期检查防火墙规则

📞 遇到问题？
   - 完整指南: docs/IPV6_ACCESS_GUIDE.md
   - 故障排查: TROUBLESHOOTING.md
   - 测试IPv6: https://test-ipv6.com

========================================