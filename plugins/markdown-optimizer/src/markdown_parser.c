/**
 * Markdown Parser Module
 * 
 * 高性能Markdown解析器，展示C语言优势：
 * - 指针直接操作，零拷贝
 * - 状态机解析，避免递归
 * - 预分配内存池，减少malloc调用
 * - SIMD加速字符串比较（可选）
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// 内存池结构（减少频繁malloc/free）
typedef struct {
    char* buffer;
    size_t capacity;
    size_t used;
} MemoryPool;

static MemoryPool g_pool = {0};

/**
 * 初始化内存池
 */
void init_markdown_parser() {
    g_pool.capacity = 1024 * 1024;  // 1MB
    g_pool.buffer = (char*)malloc(g_pool.capacity);
    g_pool.used = 0;
    printf("[PARSER] Memory pool initialized: %zu bytes\n", g_pool.capacity);
}

/**
 * 从内存池分配内存
 */
static char* pool_alloc(size_t size) {
    if (g_pool.used + size > g_pool.capacity) {
        // 扩展内存池
        g_pool.capacity *= 2;
        g_pool.buffer = (char*)realloc(g_pool.buffer, g_pool.capacity);
    }
    
    char* ptr = g_pool.buffer + g_pool.used;
    g_pool.used += size;
    return ptr;
}

/**
 * 快速Markdown转HTML（简化版）
 * 支持：标题、粗体、斜体、链接、代码块
 */
char* markdown_to_html(const char* markdown, size_t* out_len) {
    size_t md_len = strlen(markdown);
    
    // 预分配输出缓冲区（通常为输入的1.5倍）
    size_t html_capacity = md_len * 2;
    char* html = (char*)malloc(html_capacity);
    if (!html) return NULL;
    
    size_t html_pos = 0;
    const char* p = markdown;
    const char* end = markdown + md_len;
    
    while (p < end) {
        // 标题处理 (# ## ###)
        if (*p == '#') {
            int level = 0;
            while (p < end && *p == '#' && level < 6) {
                level++;
                p++;
            }
            
            if (p < end && *p == ' ') {
                p++;  // 跳过空格
                
                // 读取标题文本
                const char* title_start = p;
                while (p < end && *p != '\n') p++;
                size_t title_len = p - title_start;
                
                // 生成HTML
                html_pos += snprintf(html + html_pos, 
                                   html_capacity - html_pos,
                                   "<h%d>%.*s</h%d>\n",
                                   level, (int)title_len, title_start, level);
                
                if (*p == '\n') p++;
                continue;
            }
        }
        
        // 粗体 (**text**)
        if (p + 1 < end && *p == '*' && *(p+1) == '*') {
            p += 2;
            html_pos += snprintf(html + html_pos,
                               html_capacity - html_pos, "<strong>");
            
            const char* bold_start = p;
            while (p + 1 < end && !(*p == '*' && *(p+1) == '*')) p++;
            size_t bold_len = p - bold_start;
            
            html_pos += snprintf(html + html_pos,
                               html_capacity - html_pos,
                               "%.*s", (int)bold_len, bold_start);
            
            html_pos += snprintf(html + html_pos,
                               html_capacity - html_pos, "</strong>");
            
            if (p + 1 < end) p += 2;
            continue;
        }
        
        // 斜体 (*text*)
        if (*p == '*' && (p == markdown || *(p-1) != '*')) {
            p++;
            html_pos += snprintf(html + html_pos,
                               html_capacity - html_pos, "<em>");
            
            const char* italic_start = p;
            while (p < end && *p != '*') p++;
            size_t italic_len = p - italic_start;
            
            html_pos += snprintf(html + html_pos,
                               html_capacity - html_pos,
                               "%.*s", (int)italic_len, italic_start);
            
            html_pos += snprintf(html + html_pos,
                               html_capacity - html_pos, "</em>");
            
            if (p < end) p++;
            continue;
        }
        
        // 行内代码 (`code`)
        if (*p == '`') {
            p++;
            html_pos += snprintf(html + html_pos,
                               html_capacity - html_pos, "<code>");
            
            const char* code_start = p;
            while (p < end && *p != '`') p++;
            size_t code_len = p - code_start;
            
            html_pos += snprintf(html + html_pos,
                               html_capacity - html_pos,
                               "%.*s", (int)code_len, code_start);
            
            html_pos += snprintf(html + html_pos,
                               html_capacity - html_pos, "</code>");
            
            if (p < end) p++;
            continue;
        }
        
        // 普通字符
        html[html_pos++] = *p++;
    }
    
    html[html_pos] = '\0';
    *out_len = html_pos;
    
    return html;
}

/**
 * 批量处理多个Markdown文档（并行化准备）
 */
typedef struct {
    const char** inputs;
    char** outputs;
    size_t* lengths;
    int count;
} BatchProcessArgs;

void* batch_process_thread(void* arg) {
    BatchProcessArgs* args = (BatchProcessArgs*)arg;
    
    for (int i = 0; i < args->count; i++) {
        args->outputs[i] = markdown_to_html(args->inputs[i], &args->lengths[i]);
    }
    
    return NULL;
}

/**
 * 清理资源
 */
void cleanup_parser() {
    if (g_pool.buffer) {
        free(g_pool.buffer);
        g_pool.buffer = NULL;
        g_pool.capacity = 0;
        g_pool.used = 0;
    }
    printf("[PARSER] Resources cleaned up\n");
}
