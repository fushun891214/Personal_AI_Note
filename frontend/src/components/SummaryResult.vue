<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: {
    type: Object,
    required: true
  }
})

const isSuccess = computed(() => {
  return props.result.notion_status && props.result.notion_status.includes('Success')
})

const statusClass = computed(() => {
  return isSuccess.value ? 'status-success' : 'status-error'
})

const statusText = computed(() => {
  if (isSuccess.value) {
    return 'Notion 同步成功'
  }
  return 'Notion 同步失敗'
})
</script>

<template>
  <div class="result-box">
    <h2 class="section-title">分析結果</h2>

    <span :class="['status-tag', statusClass]">{{ statusText }}</span>

    <!-- Processed Files List -->
    <div v-if="result.files && result.files.length > 0" class="files-section">
      <h3 class="files-header">
        已處理檔案 ({{ result.files.length }})
      </h3>

      <div class="file-list">
        <div
          v-for="filename in result.files"
          :key="filename"
          class="file-item"
          :class="{ 'file-item-error': !isSuccess }"
        >
          <span class="file-icon">{{ isSuccess ? '✓' : '!' }}</span>
          <span class="filename">{{ filename }}</span>
        </div>
      </div>
    </div>

    <div v-if="result.title" class="title-section">
      <h3 class="section-title">生成標題</h3>
      <p class="title-content">{{ result.title }}</p>
    </div>

    <div v-if="isSuccess" class="success-message">
      <p>✅ 內容已同步到 Notion，請前往 Notion 查看完整筆記</p>
    </div>

    <div v-else class="error-message">
      <p>❌ 同步失敗: {{ result.notion_status || '未知錯誤' }}</p>
    </div>
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

.title-section {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}

.title-content {
    margin: 8px 0 0 0;
    font-size: 16px;
    font-weight: 600;
    color: #111827;
}

.success-message {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}

.success-message p {
    margin: 0;
    font-size: 14px;
    color: #166534;
    text-align: center;
}

.error-message {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
    word-break: break-word; 
}

.error-message p {
    margin: 0;
    font-size: 14px;
    color: #991b1b;
}

/* Processed Files Section */
.files-section {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}

.files-header {
    margin: 0 0 12px 0;
    font-size: 15px;
    font-weight: 600;
    color: #374151;
}

.file-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.file-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 6px;
    background: #f0fdf4;
    border: 1px solid #86efac;
}

.file-item-error {
    background: #fef2f2;
    border: 1px solid #fecaca;
}

.file-item-error .file-icon {
    background: #fee2e2;
    color: #dc2626;
}

.file-icon {
    flex-shrink: 0;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #dcfce7;
    color: #16a34a;
    font-size: 12px;
    font-weight: bold;
}

.filename {
    font-size: 14px;
    font-weight: 500;
    color: #111827;
}
</style>
