# Markdown Optimizer Plugin - Makefile
# 
# 编译选项说明：
# -O3: 最高优化级别
# -march=native: 针对当前CPU优化
# -flto: 链接时优化
# -pthread: 多线程支持

CC = gcc
CFLAGS = -O3 -march=native -mtune=native -ffast-math -flto
LDFLAGS = -lpthread -lm -lz

# 启用调试信息（开发时使用）
# CFLAGS += -g -Wall -Wextra

SRCDIR = src
SOURCES = $(SRCDIR)/main.c \
          $(SRCDIR)/markdown_parser.c \
          $(SRCDIR)/indexer.c \
          $(SRCDIR)/dedup.c \
          $(SRCDIR)/http_server.c

TARGET = markdown-optimizer

.PHONY: all clean benchmark docker-build docker-run

all: $(TARGET)

$(TARGET): $(SOURCES)
	@echo "Building Markdown Optimizer..."
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
	@echo "Build complete: $(TARGET)"
	@ls -lh $(TARGET)

clean:
	rm -f $(TARGET)
	rm -f *.o
	@echo "Cleaned"

benchmark: $(TARGET)
	@echo "Running performance benchmarks..."
	./$(TARGET) --benchmark

# Docker相关
docker-build:
	docker build -t wikidemotongyi/plugin-markdown-optimizer:latest .
	docker build -t wikidemotongyi/plugin-markdown-optimizer:1.0.0 .

docker-run:
	docker run -p 8080:8080 \
		-e LOG_LEVEL=INFO \
		-e MAX_THREADS=4 \
		wikidemotongyi/plugin-markdown-optimizer:latest

docker-push:
	docker push wikidemotongyi/plugin-markdown-optimizer:latest
	docker push wikidemotongyi/plugin-markdown-optimizer:1.0.0

# 帮助信息
help:
	@echo "Markdown Optimizer Plugin - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all           - Build the plugin (default)"
	@echo "  clean         - Remove build artifacts"
	@echo "  benchmark     - Run performance tests"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run in Docker"
	@echo "  docker-push   - Push to registry"
	@echo "  help          - Show this help"
