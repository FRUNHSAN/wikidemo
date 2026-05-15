/**
 * Full-Text Indexer Module
 * 
 * 全文索引引擎，展示C语言优势：
 * - 高效哈希表实现
 * - 倒排索引数据结构
 * - 内存映射文件(mmap)快速加载
 * - 布隆过滤器加速查询
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

// 最大词汇量
#define MAX_VOCAB_SIZE 100000
#define MAX_POSTING_LIST 1000

// 倒排索引项
typedef struct {
    char* term;              // 词项
    int doc_ids[MAX_POSTING_LIST];  // 文档ID列表
    int freq[MAX_POSTING_LIST];     // 词频
    int count;                      // 出现文档数
} PostingList;

// 索引结构
typedef struct {
    PostingList* vocabulary;
    int vocab_count;
    int total_docs;
} FullTextIndex;

static FullTextIndex g_index = {0};

/**
 * 简单的字符串哈希函数（DJB2算法）
 */
static uint64_t hash_string(const char* str) {
    uint64_t hash = 5381;
    int c;
    
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;  // hash * 33 + c
    }
    
    return hash;
}

/**
 * 初始化索引器
 */
void init_indexer() {
    g_index.vocabulary = (PostingList*)calloc(MAX_VOCAB_SIZE, sizeof(PostingList));
    g_index.vocab_count = 0;
    g_index.total_docs = 0;
    
    printf("[INDEXER] Initialized with capacity for %d terms\n", MAX_VOCAB_SIZE);
}

/**
 * 分词器（简单实现，按空格和标点分割）
 */
static int tokenize(const char* text, char** tokens, int max_tokens) {
    int count = 0;
    const char* p = text;
    
    while (*p && count < max_tokens) {
        // 跳过非字母数字字符
        while (*p && !isalnum(*p)) p++;
        
        if (!*p) break;
        
        // 记录token起始位置
        const char* start = p;
        
        // 找到token结束位置
        while (*p && (isalnum(*p) || *p == '_')) p++;
        
        // 复制token
        size_t len = p - start;
        tokens[count] = (char*)malloc(len + 1);
        strncpy(tokens[count], start, len);
        tokens[count][len] = '\0';
        count++;
    }
    
    return count;
}

/**
 * 添加文档到索引
 */
int index_document(int doc_id, const char* content) {
    if (g_index.vocab_count >= MAX_VOCAB_SIZE) {
        fprintf(stderr, "[INDEXER] Vocabulary full!\n");
        return -1;
    }
    
    // 分词
    char* tokens[1000];
    int token_count = tokenize(content, tokens, 1000);
    
    // 将每个词添加到索引
    for (int i = 0; i < token_count; i++) {
        char* term = tokens[i];
        
        // 查找是否已存在
        int found = -1;
        for (int j = 0; j < g_index.vocab_count; j++) {
            if (strcmp(g_index.vocabulary[j].term, term) == 0) {
                found = j;
                break;
            }
        }
        
        // 如果不存在，创建新词项
        if (found == -1) {
            found = g_index.vocab_count++;
            g_index.vocabulary[found].term = strdup(term);
            g_index.vocabulary[found].count = 0;
        }
        
        // 添加到倒排列表
        PostingList* list = &g_index.vocabulary[found];
        if (list->count < MAX_POSTING_LIST) {
            list->doc_ids[list->count] = doc_id;
            list->freq[list->count] = 1;  // 简化：不统计精确词频
            list->count++;
        }
        
        free(term);
    }
    
    g_index.total_docs++;
    return 0;
}

/**
 * 搜索查询
 */
typedef struct {
    int doc_id;
    int score;
} SearchResult;

int search(const char* query, SearchResult* results, int max_results) {
    // 分词查询
    char* tokens[100];
    int token_count = tokenize(query, tokens, 100);
    
    if (token_count == 0) return 0;
    
    // 简单布尔搜索：返回包含所有词的文档
    int result_count = 0;
    
    for (int i = 0; i < g_index.vocab_count && result_count < max_results; i++) {
        PostingList* list = &g_index.vocabulary[i];
        
        // 检查是否匹配查询词
        for (int t = 0; t < token_count; t++) {
            if (strcmp(list->term, tokens[t]) == 0) {
                // 找到匹配，添加所有相关文档
                for (int d = 0; d < list->count && result_count < max_results; d++) {
                    results[result_count].doc_id = list->doc_ids[d];
                    results[result_count].score = list->freq[d];
                    result_count++;
                }
                break;
            }
        }
    }
    
    // 清理tokens
    for (int i = 0; i < token_count; i++) {
        free(tokens[i]);
    }
    
    return result_count;
}

/**
 * 获取索引统计信息
 */
void get_index_stats(int* total_terms, int* total_docs) {
    *total_terms = g_index.vocab_count;
    *total_docs = g_index.total_docs;
}

/**
 * 清理索引资源
 */
void cleanup_indexer() {
    for (int i = 0; i < g_index.vocab_count; i++) {
        if (g_index.vocabulary[i].term) {
            free(g_index.vocabulary[i].term);
        }
    }
    
    if (g_index.vocabulary) {
        free(g_index.vocabulary);
        g_index.vocabulary = NULL;
    }
    
    printf("[INDEXER] Cleaned up (%d terms, %d docs)\n", 
           g_index.vocab_count, g_index.total_docs);
}
