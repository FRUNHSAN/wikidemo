/**
 * Markdown Optimizer Plugin - Main Entry Point
 * 
 * 高性能Markdown处理引擎（C语言实现）
 * 展示C语言特性：
 * - 指针操作和内存管理
 * - 多线程并行处理
 * - SIMD优化（可选）
 * - 零拷贝字符串处理
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <sys/time.h>

// 模块声明
extern int start_http_server(int port);
extern void init_markdown_parser();
extern void init_indexer();
extern void init_dedup_engine();
extern void cleanup_all();

// 配置结构体
typedef struct {
    int port;
    int max_threads;
    int cache_size_mb;
    char log_level[10];
} PluginConfig;

// 全局配置
static PluginConfig g_config = {
    .port = 8080,
    .max_threads = 4,
    .cache_size_mb = 64,
    .log_level = "INFO"
};

/**
 * 从环境变量加载配置
 */
void load_config_from_env() {
    const char* port = getenv("PORT");
    if (port) g_config.port = atoi(port);
    
    const char* threads = getenv("MAX_THREADS");
    if (threads) g_config.max_threads = atoi(threads);
    
    const char* cache = getenv("CACHE_SIZE_MB");
    if (cache) g_config.cache_size_mb = atoi(cache);
    
    const char* log = getenv("LOG_LEVEL");
    if (log) strncpy(g_config.log_level, log, sizeof(g_config.log_level) - 1);
}

/**
 * 打印启动信息
 */
void print_startup_info() {
    printf("\n");
    printf("===========================================================\n");
    printf("         Markdown Optimizer Plugin v1.0.0                \n");
    printf("         High-Performance C Engine                       \n");
    printf("===========================================================\n");
    printf(" Port:        %-45d\n", g_config.port);
    printf(" Threads:     %-45d\n", g_config.max_threads);
    printf(" Cache:       %-43d MB\n", g_config.cache_size_mb);
    printf(" Log Level:   %-45s\n", g_config.log_level);
    printf("===========================================================\n");
    printf("\n");
}

/**
 * 性能测试函数
 */
void run_performance_test() {
    printf("[PERF] Running performance benchmarks...\n");
    
    // 测试1: 字符串处理性能
    struct timeval start, end;
    gettimeofday(&start, NULL);
    
    // 模拟大量字符串操作
    const char* test_data = "# Hello World\nThis is a **test** of markdown parsing.\n";
    size_t iterations = 1000000;
    
    for (size_t i = 0; i < iterations; i++) {
        volatile size_t len = strlen(test_data);
        (void)len;
    }
    
    gettimeofday(&end, NULL);
    double elapsed = (end.tv_sec - start.tv_sec) * 1000.0 +
                     (end.tv_usec - start.tv_usec) / 1000.0;
    
    printf("[PERF] String processing: %.2f ms for %zu iterations\n", 
           elapsed, iterations);
    printf("[PERF] Throughput: %.2f ops/sec\n", 
           (iterations / elapsed) * 1000.0);
}

int main(int argc, char* argv[]) {
    printf("[INFO] Markdown Optimizer starting...\n");
    
    // 加载配置
    load_config_from_env();
    print_startup_info();
    
    // 初始化各模块
    printf("[INFO] Initializing modules...\n");
    init_markdown_parser();
    init_indexer();
    init_dedup_engine();
    
    // 运行性能测试（可选）
    if (argc > 1 && strcmp(argv[1], "--benchmark") == 0) {
        run_performance_test();
    }
    
    // 启动HTTP服务器
    printf("[INFO] Starting HTTP server on port %d...\n", g_config.port);
    int ret = start_http_server(g_config.port);
    
    // 清理资源
    cleanup_all();
    
}
