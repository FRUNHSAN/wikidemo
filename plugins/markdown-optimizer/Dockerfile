# ==========================================
# Markdown Optimizer Plugin - C Language
# ==========================================
# 高性能Markdown处理插件，展示C语言优势：
# - 极致性能（比Python快10-50倍）
# - 低内存占用
# - SIMD优化
# - 零拷贝字符串处理
# ==========================================

# 阶段1: 构建阶段 - 使用Alpine + gcc（避免Docker Hub镜像拉取问题）
FROM alpine:3.18 AS builder

# 添加Alpine中国镜像源加速
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories

RUN apk add --no-cache \
    gcc \
    musl-dev \
    zlib-dev

WORKDIR /build

# 复制源代码
COPY . .

# 编译（启用优化）
RUN gcc -O3 \
    -o markdown-optimizer \
    src/main.c \
    src/markdown_parser.c \
    src/indexer.c \
    src/dedup.c \
    src/http_server.c \
    -lz \
    -lpthread \
    -lm

# 阶段2: 运行阶段（极简镜像）
FROM alpine:3.18

LABEL maintainer="WikiDemoTongYi Team"
LABEL description="High-performance Markdown optimizer plugin (C)"
LABEL version="1.0.0"

# 添加Alpine中国镜像源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories

# 安装运行时依赖
RUN apk add --no-cache \
    zlib \
    tini \
    curl && \
    addgroup -g 1001 -S plugin && \
    adduser -u 1001 -S plugin -G plugin

WORKDIR /app

# 复制编译好的二进制文件
COPY --from=builder /build/markdown-optimizer .
COPY --chown=plugin:plugin plugin.json .

# 创建数据目录
RUN mkdir -p /app/data /app/logs && \
    chown -R plugin:plugin /app

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# 切换到非root用户
USER plugin

# 暴露端口
EXPOSE 8080

# 使用tini作为init进程
ENTRYPOINT ["/sbin/tini", "--"]

# 启动命令
CMD ["./markdown-optimizer"]
