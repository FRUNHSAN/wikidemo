/**
 * Deduplication Engine Module
 * 
 * 内容去重引擎，展示C语言优势：
 * - 高效的哈希计算
 * - 布隆过滤器（Bloom Filter）
 * - 位运算优化
 * - 低内存占用的相似性检测
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// 布隆过滤器配置
#define BLOOM_FILTER_SIZE 1000000  // 1M bits = 125KB
#define HASH_FUNCTION_COUNT 7

// 布隆过滤器结构
typedef struct {
    unsigned char* bit_array;
    size_t size;
    int hash_count;
} BloomFilter;

// 内容指纹结构
typedef struct {
    uint64_t hash;
    char doc_id[64];
} ContentFingerprint;

// 去重引擎
typedef struct {
    BloomFilter bloom;
    ContentFingerprint* fingerprints;
    int fingerprint_count;
    int capacity;
} DedupEngine;

static DedupEngine g_engine = {0};

/**
 * 初始化布隆过滤器
 */
static void init_bloom_filter(BloomFilter* bloom, size_t size) {
    bloom->size = size;
    bloom->bit_array = (unsigned char*)calloc(size / 8 + 1, 1);
    bloom->hash_count = HASH_FUNCTION_COUNT;
}

/**
 * 多个哈希函数（使用不同种子）
 */
static uint64_t hash_with_seed(const char* data, size_t len, uint64_t seed) {
    uint64_t hash = seed;
    
    for (size_t i = 0; i < len; i++) {
        hash ^= data[i];
        hash *= 0x5bd1e99553bd1ee5ULL;  // MurmurHash常量
        hash ^= hash >> 47;
    }
    
    return hash;
}

/**
 * 添加到布隆过滤器
 */
static void bloom_add(BloomFilter* bloom, const char* data, size_t len) {
    for (int i = 0; i < bloom->hash_count; i++) {
        uint64_t hash = hash_with_seed(data, len, i * 0x9e3779b97f4a7c15ULL);
        size_t pos = hash % bloom->size;
        bloom->bit_array[pos / 8] |= (1 << (pos % 8));
    }
}

/**
 * 检查是否在布隆过滤器中
 */
static int bloom_contains(BloomFilter* bloom, const char* data, size_t len) {
    for (int i = 0; i < bloom->hash_count; i++) {
        uint64_t hash = hash_with_seed(data, len, i * 0x9e3779b97f4a7c15ULL);
        size_t pos = hash % bloom->size;
        
        if (!(bloom->bit_array[pos / 8] & (1 << (pos % 8)))) {
            return 0;  // 肯定不存在
        }
    }
    
    return 1;  // 可能存在（有误判）
}

/**
 * 计算内容的SHA256风格哈希（简化版）
 */
static uint64_t compute_content_hash(const char* content) {
    return hash_with_seed(content, strlen(content), 0x123456789abcdefULL);
}

/**
 * 初始化去重引擎
 */
void init_dedup_engine() {
    init_bloom_filter(&g_engine.bloom, BLOOM_FILTER_SIZE);
    
    g_engine.capacity = 10000;
    g_engine.fingerprints = (ContentFingerprint*)malloc(
        g_engine.capacity * sizeof(ContentFingerprint)
    );
    g_engine.fingerprint_count = 0;
    
    printf("[DEDUP] Initialized (Bloom filter: %zu bytes, Capacity: %d)\n",
           BLOOM_FILTER_SIZE / 8, g_engine.capacity);
}

/**
 * 检查内容是否重复
 * 
 * @return 0=不重复, 1=可能重复
 */
int check_duplicate(const char* content, const char* doc_id) {
    uint64_t hash = compute_content_hash(content);
    
    // 第一步：布隆过滤器快速检查
    if (!bloom_contains(&g_engine.bloom, content, strlen(content))) {
        // 肯定不重复，添加进去
        bloom_add(&g_engine.bloom, content, strlen(content));
        
        // 保存指纹
        if (g_engine.fingerprint_count < g_engine.capacity) {
            ContentFingerprint* fp = &g_engine.fingerprints[g_engine.fingerprint_count++];
            fp->hash = hash;
            strncpy(fp->doc_id, doc_id, sizeof(fp->doc_id) - 1);
        }
        
        return 0;
    }
    
    // 第二步：精确检查（避免误判）
    for (int i = 0; i < g_engine.fingerprint_count; i++) {
        if (g_engine.fingerprints[i].hash == hash) {
            printf("[DEDUP] Duplicate found! Doc '%s' matches doc '%s'\n",
                   doc_id, g_engine.fingerprints[i].doc_id);
            return 1;
        }
    }
    
    // 布隆过滤器误判，实际不重复
    bloom_add(&g_engine.bloom, content, strlen(content));
    
    if (g_engine.fingerprint_count < g_engine.capacity) {
        ContentFingerprint* fp = &g_engine.fingerprints[g_engine.fingerprint_count++];
        fp->hash = hash;
        strncpy(fp->doc_id, doc_id, sizeof(fp->doc_id) - 1);
    }
    
    return 0;
}

/**
 * 批量检查重复（优化版本）
 */
int batch_check_duplicates(const char** contents, const char** doc_ids, 
                          int count, int* duplicate_flags) {
    int duplicate_count = 0;
    
    for (int i = 0; i < count; i++) {
        duplicate_flags[i] = check_duplicate(contents[i], doc_ids[i]);
        if (duplicate_flags[i]) {
            duplicate_count++;
        }
    }
    
    return duplicate_count;
}

/**
 * 获取统计信息
 */
void get_dedup_stats(int* total_checked, int* duplicates_found, 
                    int* bloom_false_positives) {
    *total_checked = g_engine.fingerprint_count;
    // 简化：不精确统计误判数
    *duplicates_found = 0;
    *bloom_false_positives = 0;
}

/**
 * 清理资源
 */
void cleanup_dedup_engine() {
    if (g_engine.bloom.bit_array) {
        free(g_engine.bloom.bit_array);
    }
    
    if (g_engine.fingerprints) {
        free(g_engine.fingerprints);
    }
    
    printf("[DEDUP] Cleaned up (%d fingerprints)\n", g_engine.fingerprint_count);
}
