# ==========================================
# Markdown Optimizer Plugin - C Language
# ==========================================
# 高性能Markdown处理插件，展示C语言优势：
# - 极致性能（比Python快10-50倍）
# - 低内存占用
# - SIMD优化
# - 零拷贝字符串处理
# ==========================================

# 单阶段构建：直接在Alpine上编译
FROM alpine:3.18

LABEL maintainer="WikiDemoTongYi Team"
LABEL description="High-performance Markdown optimizer plugin (C)"
LABEL version="1.0.0"

# 使用阿里云Alpine镜像源（中国大陆可访问）
RUN echo "https://mirrors.aliyun.com/alpine/v3.18/main" > /etc/apk/repositories && \
    echo "https://mirrors.aliyun.com/alpine/v3.18/community" >> /etc/apk/repositories && \
    apk add --no-cache \
    gcc \
    musl-dev \
    zlib-dev \
    zlib \
    tini \
    wget && \
    addgroup -g 1001 -S plugin && \
    adduser -u 1001 -S plugin -G plugin

WORKDIR /app

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
    -lm && \
    chown -R plugin:plugin /app

# 创建数据目录
RUN mkdir -p /app/data /app/logs

# 健康检查（使用wget替代curl）
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q --spider http://localhost:8080/health || exit 1

# 切换到非root用户
USER plugin

# 暴露端口
EXPOSE 8080

# 使用tini作为init进程
ENTRYPOINT ["/sbin/tini", "--"]

# 启动命令
CMD ["./markdown-optimizer"]
