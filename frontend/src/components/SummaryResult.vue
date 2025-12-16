<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: {
    type: Object,
    required: true
  }
})

const statusClass = computed(() => {
  if (props.result.notion_status && props.result.notion_status.includes('Success')) {
    return 'status-success'
  }
  return 'status-error'
})

const statusText = computed(() => {
  if (props.result.notion_status && props.result.notion_status.includes('Success')) {
    return 'Notion 同步成功'
  }
  return props.result.notion_status || '未知錯誤'
})
</script>

<template>
  <div class="result-box">
    <h2 class="section-title">分析結果</h2>

    <span :class="['status-tag', statusClass]">{{ statusText }}</span>

    <!-- File Processing Status -->
    <div v-if="result.file_details" class="file-status-section">
      <h3 class="status-header">
        檔案處理狀態
        <span class="file-count">({{ result.successful_files }}/{{ result.total_files }} 成功)</span>
      </h3>

      <div class="file-list">
        <div
          v-for="file in result.file_details"
          :key="file.filename"
          class="file-item"
          :class="file.status"
        >
          <span class="status-icon">
            <span v-if="file.status === 'success'" class="icon-success">✓</span>
            <span v-else-if="file.status === 'failed'" class="icon-failed">✗</span>
            <span v-else class="icon-skipped">⊘</span>
          </span>

          <div class="file-info">
            <span class="filename">{{ file.filename }}</span>
            <span v-if="file.method" class="method-tag">{{ file.method }}</span>
            <span v-if="file.char_count > 0" class="char-count">{{ file.char_count }} 字元</span>
          </div>

          <span v-if="file.message" class="error-message">{{ file.message }}</span>
        </div>
      </div>
    </div>

    <h3 class="section-title">摘要內容 (Markdown)</h3>
    <pre class="summary-content">{{ result.summary }}</pre>
  </div>
</template>

<style scoped>
.result-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px;
    margin-top: 20px;
}

.section-title {
    margin: 24px 0 8px;
    font-size: 16px;
    font-weight: 600;
    color: #111827;
}

.section-title:first-child {
    margin-top: 0;
}

.status-tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 12px;
}

.status-success {
    background: #dcfce7;
    color: #166534;
}

.status-error {
    background: #fee2e2;
    color: #991b1b;
}

pre.summary-content {
    background: #1e293b;
    color: #e2e8f0;
    padding: 16px;
    border-radius: 8px;
    max-height: 400px;
    overflow: auto;
    font-size: 14px;
    white-space: pre-wrap;
    margin: 0;
}

/* File Processing Status Section */
.file-status-section {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}

.status-header {
    margin: 0 0 12px 0;
    font-size: 15px;
    font-weight: 600;
    color: #374151;
    display: flex;
    align-items: center;
    gap: 8px;
}

.file-count {
    font-size: 13px;
    font-weight: 500;
    color: #6b7280;
}

.file-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.file-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 6px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
}

.file-item.success {
    background: #f0fdf4;
    border-color: #86efac;
}

.file-item.failed {
    background: #fef2f2;
    border-color: #fca5a5;
}

.file-item.skipped {
    background: #fefce8;
    border-color: #fde047;
}

.status-icon {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-size: 12px;
    font-weight: bold;
}

.icon-success {
    color: #16a34a;
    background: #dcfce7;
    padding: 2px;
}

.icon-failed {
    color: #dc2626;
    background: #fee2e2;
    padding: 2px;
}

.icon-skipped {
    color: #ca8a04;
    background: #fef9c3;
    padding: 2px;
}

.file-info {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.filename {
    font-size: 14px;
    font-weight: 500;
    color: #111827;
}

.method-tag {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    background: #e0e7ff;
    color: #4338ca;
    font-weight: 600;
    text-transform: uppercase;
}

.char-count {
    font-size: 12px;
    color: #6b7280;
}

.error-message {
    font-size: 12px;
    color: #dc2626;
    font-style: italic;
}
</style>
