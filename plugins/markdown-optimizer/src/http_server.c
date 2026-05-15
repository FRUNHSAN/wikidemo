/**
 * HTTP Server Module
 * 
 * 轻量级HTTP服务器，提供REST API
 * 使用原生socket实现，无外部依赖
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <time.h>
#include <sys/time.h>

// 外部函数声明
extern char* markdown_to_html(const char* markdown, size_t* out_len);
extern int index_document(int doc_id, const char* content);
extern int search(const char* query, void* results, int max_results);
extern int check_duplicate(const char* content, const char* doc_id);
extern void cleanup_parser();
extern void cleanup_indexer();
extern void cleanup_dedup_engine();

#define BUFFER_SIZE 65536
#define MAX_CONNECTIONS 100

/**
 * 获取当前时间戳（毫秒）
 */
static long long current_time_ms() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (long long)tv.tv_sec * 1000 + tv.tv_usec / 1000;
}

/**
 * 发送HTTP响应
 */
static void send_response(int client_fd, int status_code, 
                         const char* content_type, const char* body) {
    char header[BUFFER_SIZE];
    int body_len = strlen(body);
    
    const char* status_text = "OK";
    if (status_code == 400) status_text = "Bad Request";
    else if (status_code == 404) status_text = "Not Found";
    else if (status_code == 500) status_text = "Internal Server Error";
    
    snprintf(header, sizeof(header),
        "HTTP/1.1 %d %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "\r\n",
        status_code, status_text, content_type, body_len);
    
    write(client_fd, header, strlen(header));
    write(client_fd, body, body_len);
}

/**
 * 发送JSON响应
 */
static void send_json_response(int client_fd, int status_code, const char* json) {
    send_response(client_fd, status_code, "application/json", json);
}

/**
 * 解析HTTP请求行
 */
static int parse_request(const char* request, char* method, char* path, 
                        char* body, int body_size) {
    // 解析方法
    sscanf(request, "%s", method);
    
    // 解析路径
    const char* path_start = strchr(request, ' ');
    if (!path_start) return -1;
    path_start++;
    
    const char* path_end = strchr(path_start, ' ');
    if (!path_end) return -1;
    
    size_t path_len = path_end - path_start;
    strncpy(path, path_start, path_len);
    path[path_len] = '\0';
    
    // 解析body（如果有）
    const char* body_start = strstr(request, "\r\n\r\n");
    if (body_start && body_size > 0) {
        body_start += 4;  // 跳过\r\n\r\n
        strncpy(body, body_start, body_size - 1);
        body[body_size - 1] = '\0';
    } else {
        body[0] = '\0';
    }
    
    return 0;
}

/**
 * 处理 /health 端点
 */
static void handle_health(int client_fd) {
    const char* response = "{\"status\":\"healthy\",\"service\":\"markdown-optimizer\"}";
    send_json_response(client_fd, 200, response);
}

/**
 * 处理 /api/parse 端点（Markdown转HTML）
 */
static void handle_parse(int client_fd, const char* body) {
    long long start = current_time_ms();
    
    // 简单的JSON解析（提取markdown字段）
    const char* md_start = strstr(body, "\"markdown\":");
    if (!md_start) {
        send_json_response(client_fd, 400, "{\"error\":\"Missing markdown field\"}");
        return;
    }
    
    // 找到字符串开始位置
    const char* str_start = strchr(md_start + 11, '"');
    if (!str_start) {
        send_json_response(client_fd, 400, "{\"error\":\"Invalid format\"}");
        return;
    }
    str_start++;
    
    // 找到字符串结束位置（简化：不处理转义）
    const char* str_end = strchr(str_start, '"');
    if (!str_end) {
        send_json_response(client_fd, 400, "{\"error\":\"Invalid format\"}");
        return;
    }
    
    size_t md_len = str_end - str_start;
    char* markdown = (char*)malloc(md_len + 1);
    strncpy(markdown, str_start, md_len);
    markdown[md_len] = '\0';
    
    // 执行Markdown转换
    size_t html_len;
    char* html = markdown_to_html(markdown, &html_len);
    
    long long elapsed = current_time_ms() - start;
    
    if (html) {
        // 构建JSON响应
        char response[BUFFER_SIZE];
        snprintf(response, sizeof(response),
            "{\"success\":true,\"html\":\"%.*s\",\"processing_time_ms\":%lld}",
            (int)html_len, html, elapsed);
        
        send_json_response(client_fd, 200, response);
        free(html);
    } else {
        send_json_response(client_fd, 500, "{\"error\":\"Parse failed\"}");
    }
    
    free(markdown);
}

/**
 * 处理 /api/index 端点（构建索引）
 */
static void handle_index(int client_fd, const char* body) {
    // 简化：从body提取doc_id和content
    int doc_id = 1;
    
    int result = index_document(doc_id, body);
    
    if (result == 0) {
        send_json_response(client_fd, 200, "{\"success\":true,\"message\":\"Indexed\"}");
    } else {
        send_json_response(client_fd, 500, "{\"error\":\"Index failed\"}");
    }
}

/**
 * 处理 /api/dedup 端点（去重检查）
 */
static void handle_dedup(int client_fd, const char* body) {
    int is_dup = check_duplicate(body, "test-doc");
    
    char response[256];
    snprintf(response, sizeof(response),
        "{\"is_duplicate\":%s}",
        is_dup ? "true" : "false");
    
    send_json_response(client_fd, 200, response);
}

/**
 * 处理 /api/benchmark 端点（性能测试）
 */
static void handle_benchmark(int client_fd, const char* body) {
    long long start = current_time_ms();
    
    // 执行性能测试：大量Markdown解析
    const char* test_md = "# Test\nThis is **bold** and *italic* text.\n";
    int iterations = 10000;
    
    for (int i = 0; i < iterations; i++) {
        size_t html_len;
        char* html = markdown_to_html(test_md, &html_len);
        if (html) free(html);
    }
    
    long long elapsed = current_time_ms() - start;
    double ops_per_sec = (iterations / (double)elapsed) * 1000.0;
    
    char response[512];
    snprintf(response, sizeof(response),
        "{"
        "\"success\":true,"
        "\"iterations\":%d,"
        "\"total_time_ms\":%lld,"
        "\"ops_per_second\":%.2f,"
        "\"avg_time_us\":%.2f"
        "}",
        iterations, elapsed, ops_per_sec, 
        ((double)elapsed / iterations) * 1000.0);
    
    send_json_response(client_fd, 200, response);
}

/**
 * 客户端处理线程
 */
void* handle_client(void* arg) {
    int client_fd = *(int*)arg;
    free(arg);
    
    char buffer[BUFFER_SIZE];
    int bytes_read = read(client_fd, buffer, sizeof(buffer) - 1);
    
    if (bytes_read <= 0) {
        close(client_fd);
        return NULL;
    }
    
    buffer[bytes_read] = '\0';
    
    // 解析请求
    char method[16], path[256], body[BUFFER_SIZE];
    if (parse_request(buffer, method, path, body, sizeof(body)) != 0) {
        send_json_response(client_fd, 400, "{\"error\":\"Invalid request\"}");
        close(client_fd);
        return NULL;
    }
    
    // 路由处理
    if (strcmp(path, "/health") == 0 || strcmp(path, "/healthz") == 0) {
        handle_health(client_fd);
    }
    else if (strcmp(path, "/api/parse") == 0 && strcmp(method, "POST") == 0) {
        handle_parse(client_fd, body);
    }
    else if (strcmp(path, "/api/index") == 0 && strcmp(method, "POST") == 0) {
        handle_index(client_fd, body);
    }
    else if (strcmp(path, "/api/dedup") == 0 && strcmp(method, "POST") == 0) {
        handle_dedup(client_fd, body);
    }
    else if (strcmp(path, "/api/benchmark") == 0) {
        handle_benchmark(client_fd, body);
    }
    else {
        send_json_response(client_fd, 404, "{\"error\":\"Not found\"}");
    }
    
    close(client_fd);
    return NULL;
}

/**
 * 启动HTTP服务器
 */
int start_http_server(int port) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("Socket creation failed");
        return -1;
    }
    
    // 设置socket选项（地址重用）
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // 绑定地址
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);
    
    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("Bind failed");
        close(server_fd);
        return -1;
    }
    
    // 监听
    if (listen(server_fd, MAX_CONNECTIONS) < 0) {
        perror("Listen failed");
        close(server_fd);
        return -1;
    }
    
    printf("[HTTP] Server listening on port %d\n", port);
    
    // 接受连接循环
    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        
        int* client_fd = malloc(sizeof(int));
        *client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        
        if (*client_fd < 0) {
            perror("Accept failed");
            free(client_fd);
            continue;
        }
        
        // 创建线程处理客户端
        pthread_t thread;
        pthread_create(&thread, NULL, handle_client, client_fd);
        pthread_detach(thread);
    }
    
    close(server_fd);
    return 0;
}

/**
 * 清理所有资源
 */
void cleanup_all() {
    cleanup_parser();
    cleanup_indexer();
    cleanup_dedup_engine();
    printf("[MAIN] All resources cleaned up\n");
}
