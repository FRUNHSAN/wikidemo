# ==========================================
# Wiki.js 插件标准 Dockerfile 模板
# ==========================================
# 使用说明：
# 1. 复制此模板到你的插件目录
# 2. 根据插件需求修改构建阶段
# 3. 确保插件根目录包含 plugin.json
#
# 支持的编程语言：
# - Python (默认)
# - Node.js
# - Go
# - Rust
# - Java
# ==========================================

# ==========================================
# 阶段1: 构建阶段（多语言支持）
# ==========================================

# --- Python 插件示例 ---
FROM python:3.11-slim AS builder-python
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Node.js 插件示例 ---
# FROM node:18-alpine AS builder-nodejs
# WORKDIR /build
# COPY package*.json ./
# RUN npm ci --only=production && \
#     npm cache clean --force

# --- Go 插件示例 ---
# FROM golang:1.21-alpine AS builder-go
# WORKDIR /build
# COPY go.mod go.sum ./
# RUN go mod download
# COPY . .
# RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o plugin-server .

# --- Rust 插件示例 ---
# FROM rust:1.70-alpine AS builder-rust
# WORKDIR /build
# COPY Cargo.toml Cargo.lock ./
# RUN cargo fetch
# COPY . .
# RUN cargo build --release

# ==========================================
# 阶段2: 运行阶段（轻量级）
# ==========================================

# --- Python 运行时 ---
FROM python:3.11-alpine AS runtime-python
LABEL maintainer="WikiDemoTongYi Community"
LABEL description="Wiki.js Plugin - Your Plugin Name"
LABEL version="1.0.0"

# 安装系统依赖
RUN apk add --no-cache curl tini

# 创建非root用户
RUN addgroup -g 1001 -S plugin && \
    adduser -u 1001 -S plugin -G plugin

WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder-python /install /usr/local

# 复制插件代码
COPY --chown=plugin:plugin . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# 切换到非root用户
USER plugin

# 暴露端口（根据插件配置修改）
EXPOSE 8080

# 使用tini作为init进程
ENTRYPOINT ["/sbin/tini", "--"]

# 启动命令
CMD ["python", "plugin.py"]

# --- Node.js 运行时 ---
# FROM node:18-alpine AS runtime-nodejs
# LABEL maintainer="WikiDemoTongYi Community"
# RUN apk add --no-cache curl tini
# RUN addgroup -g 1001 -S plugin && adduser -u 1001 -S plugin -G plugin
# WORKDIR /app
# COPY --from=builder-nodejs /build/node_modules ./node_modules
# COPY --chown=plugin:plugin . .
# USER plugin
# EXPOSE 8080
# ENTRYPOINT ["/sbin/tini", "--"]
# CMD ["node", "index.js"]

# --- Go 运行时（极简）---
# FROM alpine:3.18 AS runtime-go
# LABEL maintainer="WikiDemoTongYi Community"
# RUN apk add --no-cache curl tini
# RUN addgroup -g 1001 -S plugin && adduser -u 1001 -S plugin -G plugin
# WORKDIR /app
# COPY --from=builder-go /build/plugin-server .
# COPY --chown=plugin:plugin plugin.json .
# USER plugin
# EXPOSE 8080
# ENTRYPOINT ["/sbin/tini", "--"]
# CMD ["./plugin-server"]
