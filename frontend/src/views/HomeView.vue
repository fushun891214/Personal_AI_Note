<script setup>
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import FileUploader from '../components/FileUploader.vue'
import FileList from '../components/FileList.vue'

import PreviewModal from '../components/PreviewModal.vue'
import SettingsModal from '../components/SettingsModal.vue'
import { useSummaryStore } from '../stores/summary'
import { useSettingsStore } from '../stores/settings'
import { Modal } from 'ant-design-vue'

const store = useSummaryStore()
const settingsStore = useSettingsStore()
const files = ref([])
const isProcessing = ref(false)
const result = ref(null)

// ... existing code ...
// 監聽 Modal 關閉事件，清空檔案列表
watch(() => store.isModalOpen, (newVal, oldVal) => {
  if (oldVal === true && newVal === false) {
    files.value = []
    result.value = null
  }
})

const handleFilesSelected = (newFiles) => {
  files.value = [...files.value, ...newFiles]
}

const handleRemoveFile = (index) => {
  if (isProcessing.value) return
  files.value.splice(index, 1)
}

const handleReset = () => {
  files.value = []
  result.value = null
}

const handleSubmit = async () => {
  if (files.value.length === 0) return
  
  // Check Gemini Key
  if (!settingsStore.hasGeminiKey()) {
      Modal.warning({
          title: '未設定 Gemini Key',
          content: '請先在設定中輸入 Gemini API Key 以使用此功能',
          okText: '去設定',
          onOk: () => settingsStore.openSettingsModal(),
          centered: true
      })
      return
  }

  isProcessing.value = true
  result.value = null

  const formData = new FormData()
  files.value.forEach(file => {
    formData.append('files', file)
  })

  try {
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-Gemini-API-Key': settingsStore.geminiApiKey
      }
    })

    if (response.data.error) {
      throw new Error(response.data.message)
    }

    // New Flow: Open Preview Modal
    // response.data contains { title, blocks, pdf_urls, ... }
    const pdfUrl = response.data.pdf_urls ? response.data.pdf_urls[0] : null
    store.setSummary(response.data, pdfUrl)

  } catch (error) {
    console.error('Error:', error)
    // Handle 401/Quota specific errors if status is available
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        Modal.error({
            title: 'Gemini API Error',
            content: `額度已滿或 Key 無效 (${error.response.data.error || error.message})`,
            okText: '去設定',
            onOk: () => settingsStore.openSettingsModal(),
            centered: true
        })
    } else {
        Modal.error({
            title: '上傳發生錯誤',
            content: error.message || '未知錯誤',
            centered: true
        })
    }
  } finally {
    isProcessing.value = false
  }
}

const buttonText = computed(() => {
  if (isProcessing.value) return '處理中...'
  return '上傳並生成'
})
</script>

<template>
  <div class="home-view">
    <header class="app-header">
      <div class="header-content">
        <div class="brand">Paper Note AI</div>
        <!-- Right side icons -->
        <div class="header-actions">
           <button class="icon-btn" @click="settingsStore.openSettingsModal" title="設定 (Settings)">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.18-.08a2 2 0 0 0-2 0l-.45.26a2 2 0 0 0-.9 1.57v.26a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.18-.08a2 2 0 0 0-2 0l-.45.26a2 2 0 0 0-.9 1.57v.26a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.18-.08a2 2 0 0 0-2 0l-.45.26a2 2 0 0 0-.9 1.57v.26a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.18-.08a2 2 0 0 0-2 0l-.45.26a2 2 0 0 0-.9 1.57z"></path>
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
              </svg>
           </button>
        </div>
      </div>
    </header>

    <div class="layout-container">
      <div class="upload-section">
        <div class="hero">
          <h1>讓 AI 幫你自動整理論文筆記</h1>
        </div>

        <form @submit.prevent="handleSubmit">
          <FileUploader :disabled="isProcessing" @files-selected="handleFilesSelected" />

          <FileList :files="files" :disabled="isProcessing" @remove-file="handleRemoveFile" />

          <div class="button-group">
            <button
              type="button"
              v-if="files.length > 0"
              class="secondary-btn"
              @click="handleReset"
              :disabled="isProcessing"
            >
              重新選擇
            </button>

            <button
              type="submit"
              :disabled="files.length === 0 || isProcessing"
            >
              {{ buttonText }}
            </button>
          </div>
        </form>
      </div>

      <PreviewModal />
      <SettingsModal />
      
    </div>
  </div>
</template>

<style scoped>
/* Header Styles */
.app-header {
    border-bottom: 1px solid #f3f4f6;
    padding: 20px 0;
    background: #ffffff;
    /* Removed sticky since it's now internal */
    margin-bottom: 32px;
}

.header-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand {
    font-weight: 700;
    font-size: 20px;
    color: #4f46e5;
    letter-spacing: -0.01em;
}

.header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
}

.icon-btn {
    background: transparent;
    border: none;
    color: #6b7280;
    cursor: pointer;
    padding: 8px;
    border-radius: 8px;
    width: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: none;
    transition: all 0.2s;
    font-weight: normal;
    font-size: inherit;
    box-shadow: none;
}

/* Fix conflict with global button */
button.icon-btn {
    width: auto;
    flex: none;
    background: transparent;
    color: #6b7280;
    box-shadow: none;
}

button.icon-btn:hover {
    background: #f3f4f6;
    color: #374151;
    transform: none;
    box-shadow: none;
}

.layout-container {
  display: flex;
  flex-direction: column;
/*   gap: 2rem; Removed gap since header margin handles it */
  max-width: 100%;
  margin: 0 auto;
  width: 100%;
  align-items: center;
}

.upload-section {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 700px;
}

.result-section {
  width: 100%;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.hero {
  margin-bottom: 32px;
  text-align: center;
}

@media (min-width: 1024px) {
  .hero {
    text-align: left;
  }
}


.hero h1 {
  margin: 0 0 16px;
  font-size: 48px;
  font-weight: 800;
  color: #111827;
  line-height: 1.2;
  letter-spacing: -0.02em;
  white-space: nowrap;
}

/* RWD: 小螢幕調整 */
@media (max-width: 768px) {
  .hero h1 {
    font-size: 28px;
    white-space: normal;
  }
  
  .upload-section {
    max-width: 100%;
    padding: 0 16px;
  }
}

.button-group {
  display: flex;
  gap: 16px;
  margin-top: 32px;
}
</style>
