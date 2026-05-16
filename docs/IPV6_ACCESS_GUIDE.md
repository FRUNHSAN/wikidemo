# Wiki.js IPv6 公网访问完整指南

## 🎯 概述

本指南将帮助你通过IPv6公网地址远程访问你的Wiki.js个人知识管理系统。

## ✅ 前置条件检查

### 1. 确认你有公网IPv6地址

运行检测脚本：
```powershell
.\scripts\check-ipv6.ps1
```

或者直接获取公网IP：
```powershell
Invoke-RestMethod -Uri "https://api64.ipify.org?format=json"
```

**判断标准**：
- ✅ **公网IPv6**：以 `2` 开头（如 `2a13:edc0:...`）
- ❌ **内网IPv6**：以 `fe80:` 开头（本地链路地址）

你当前的公网IPv6地址是：**`2a13:edc0:301:4d70:9c8e:f12a:32b5:e04d`**

### 2. 确认网络连通性

```powershell
# 测试IPv6网络
Test-Connection -ComputerName ipv6.google.com -Count 4

# 完整测试
curl https://test-ipv6.com
```

## 🚀 快速配置（5分钟）

### 步骤 1：运行自动配置脚本

```powershell
.\scripts\setup-ipv6-access.ps1
```

这个脚本会自动：
- ✅ 获取你的公网IPv6地址
- ✅ 配置Windows防火墙规则
- ✅ 测试端口可达性
- ✅ 生成访问URL
- ✅ 保存配置信息

### 步骤 2：配置路由器（如果需要）

**大多数情况下，IPv6不需要端口转发！** 因为：
- IPv6每个设备都有独立的公网地址
- 不需要NAT（网络地址转换）
- 只需要配置防火墙

但有些路由器可能需要：
1. 登录路由器管理界面（通常是 `192.168.1.1` 或 `192.168.0.1`）
2. 找到"IPv6防火墙"或"IPv6设置"
3. 确保以下端口未被阻止：
   - `80` (HTTP)
   - `443` (HTTPS)
4. 保存设置并重启路由器

### 步骤 3：验证外部访问

从**外地网络**（手机流量、朋友家、公司等）访问：

```
http://[2a13:edc0:301:4d70:9c8e:f12a:32b5:e04d]
```

**注意**：IPv6地址必须用方括号 `[]` 包裹！

## 🔧 详细配置步骤

### 配置 Windows 防火墙

如果自动脚本失败，手动配置：

```powershell
# 开放HTTP端口
New-NetFirewallRule -Name "Wiki-HTTP" `
                   -DisplayName "Wiki.js HTTP" `
                   -Direction Inbound `
                   -Protocol TCP `
                   -LocalPort 80 `
                   -Action Allow

# 开放HTTPS端口
New-NetFirewallRule -Name "Wiki-HTTPS" `
                   -DisplayName "Wiki.js HTTPS" `
                   -Direction Inbound `
                   -Protocol TCP `
                   -LocalPort 443 `
                   -Action Allow
```

### 配置 Docker 网络

确保docker-compose.yml已启用IPv6：

```yaml
networks:
  wiki-network:
    driver: bridge
    enable_ipv6: true  # ✅ 必须启用
    ipam:
      config:
        - subnet: 172.20.0.0/16
        - subnet: fd00:1::/64  # IPv6子网
```

### 测试端口开放

从**本机**测试：
```powershell
Test-NetConnection -ComputerName localhost -Port 80
Test-NetConnection -ComputerName localhost -Port 443
```

从**外网**测试（使用手机流量）：
```powershell
Test-NetConnection -ComputerName 2a13:edc0:301:4d70:9c8e:f12a:32b5:e04d -Port 80
```

或使用在线工具：
- https://portchecker.co/
- https://www.yougetsignal.com/tools/open-ports/

## 🌐 配置域名访问（推荐）

### 方案 1：使用 DDNS（动态DNS）

由于家用宽带的IPv6地址可能会变化，建议使用DDNS：

**推荐服务**：
- [Cloudflare DDNS](https://www.cloudflare.com/)（免费）
- [阿里云DDNS](https://help.aliyun.com/)
- [腾讯云DDNS](https://cloud.tencent.com/)
- [DuckDNS](https://www.duckdns.org/)（免费）

**配置步骤**（以Cloudflare为例）：
1. 注册Cloudflare账号
2. 添加你的域名
3. 安装DDNS客户端：
   ```powershell
   # 使用 ddclient
   choco install ddclient
   ```
4. 配置DDNS：
   ```bash
   server=cloudflare
   zone=yourdomain.com
   login=your@email.com
   password=your-api-key
   wiki.yourdomain.com
   ```

### 方案 2：配置 Nginx 域名转发

修改 `nginx/conf.d/wiki.conf`：

```nginx
server {
    listen 80;
    listen [::]:80;  # IPv6
    
    server_name wiki.yourdomain.com;  # 你的域名
    
    location / {
        proxy_pass http://wiki:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔒 安全配置（重要！）

### 1. 立即修改默认密码

```bash
# 访问Wiki.js后第一件事
http://[your-ipv6-address]/login
# 使用默认凭证登录后立即修改密码
# 默认: admin@example.com / changeme123
```

### 2. 配置 HTTPS（强烈推荐）

使用 Let's Encrypt 免费SSL证书：

```bash
# 安装 certbot
choco install certbot

# 获取证书
certbot certonly --standalone -d wiki.yourdomain.com

# 配置Nginx使用SSL
# 参考 nginx/ssl-wiki.conf 示例
```

### 3. 配置访问控制

修改 `nginx/conf.d/wiki.conf` 添加IP白名单：

```nginx
# 只允许特定IP访问
allow 2a13:edc0::/32;  # 你的网络段
deny all;
```

### 4. 启用速率限制

防止暴力破解：

```nginx
limit_req_zone $binary_remote_addr zone=wiki:10m rate=10r/s;

server {
    location / {
        limit_req zone=wiki burst=20 nodelay;
        proxy_pass http://wiki:3000;
    }
}
```

## 📱 移动端访问

### 手机浏览器访问

1. 确保手机使用**移动数据**（非WiFi）
2. 在浏览器地址栏输入：
   ```
   http://[2a13:edc0:301:4d70:9c8e:f12a:32b5:e04d]
   ```
3. 如果是域名访问：
   ```
   http://wiki.yourdomain.com
   ```

### 配置 Obsidian 同步

在Obsidian中配置Git远程仓库：
```
https://wiki.yourdomain.com/git
```

## 🔍 故障排查

### 问题 1：无法从外网访问

**检查清单**：
- [ ] 确认IPv6地址是公网地址（不是fe80开头）
- [ ] 确认Windows防火墙已开放端口
- [ ] 确认路由器未阻止IPv6流量
- [ ] 确认运营商未封禁80/443端口
- [ ] 使用手机流量测试（非WiFi）

**诊断命令**：
```powershell
# 从本机测试
Test-NetConnection -ComputerName localhost -Port 80

# 从外网测试（需要另一台IPv6设备）
Test-NetConnection -ComputerName <your-ipv6> -Port 80
```

### 问题 2：IPv6地址频繁变化

**解决方案**：
- 使用DDNS服务自动更新域名解析
- 配置脚本定期更新记录：
  ```powershell
  # 添加到任务计划程序
  schtasks /create /tn "Update-DDNS" /tr "powershell -File update-ddns.ps1" /sc daily /st 02:00
  ```

### 问题 3：访问速度慢

**优化建议**：
- 启用Nginx缓存
- 配置CDN（如Cloudflare）
- 压缩静态资源
- 启用HTTP/2

## 📊 监控和维护

### 查看访问日志

```bash
# Nginx访问日志
docker logs wiki-nginx

# 实时查看
docker logs -f wiki-nginx
```

### 定期备份

```bash
# 备份数据库
docker exec wiki-db pg_dump -U wikiuser wikidb > backup-$(date +%Y%m%d).sql

# 备份配置
docker compose config > compose-backup-$(date +%Y%m%d).yml
```

### 更新镜像

```bash
# 拉取最新镜像
docker compose pull

# 重新创建容器
docker compose up -d
```

## 🎓 进阶配置

### 配置 IPv6 优先

修改 `nginx/nginx.conf`：

```nginx
# 优先使用IPv6
listen [::]:80 default_server;
listen 80;

listen [::]:443 ssl default_server;
listen 443 ssl;
```

### 配置多站点

如果有多个服务，可以配置不同的子域名：

```nginx
# wiki.yourdomain.com -> Wiki.js
server {
    server_name wiki.yourdomain.com;
    location / { proxy_pass http://wiki:3000; }
}

# blog.yourdomain.com -> 博客系统
server {
    server_name blog.yourdomain.com;
    location / { proxy_pass http://blog:8080; }
}
```

## 📚 相关资源

- [IPv6 测试网站](https://test-ipv6.com)
- [Cloudflare DDNS 文档](https://developers.cloudflare.com/dns/manage-dns-records/how-to/use-dynamic-dns)
- [Let's Encrypt 文档](https://letsencrypt.org/docs/)
- [Docker IPv6 文档](https://docs.docker.com/config/daemon/ipv6/)
- [Nginx IPv6 配置](https://nginx.org/en/docs/ipv6.html)

## ️ 安全提醒

1. **永远不要**使用默认密码
2. **强烈建议**配置HTTPS
3. **定期更新**Docker镜像和系统补丁
4. **监控日志**，及时发现异常访问
5. **备份数据**，防止数据丢失

---

**祝你的Wiki.js公网访问配置顺利！** 🚀

如有问题，可以查看：
- 项目文档：`README.md`
- 故障排查：`TROUBLESHOOTING.md`
- GitHub Issues：提交问题反馈