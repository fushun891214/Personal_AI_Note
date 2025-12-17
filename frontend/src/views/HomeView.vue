<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import FileUploader from '../components/FileUploader.vue'
import FileList from '../components/FileList.vue'
import SummaryResult from '../components/SummaryResult.vue'
import PreviewModal from '../components/PreviewModal.vue'
import { useSummaryStore } from '../stores/summary'

const store = useSummaryStore()
const files = ref([])
const isProcessing = ref(false)
const result = ref(null)

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

  isProcessing.value = true
  result.value = null

  const formData = new FormData()
  files.value.forEach(file => {
    formData.append('files', file)
  })

  try {
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
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
    alert(`上傳發生錯誤: ${error.message || '未知錯誤'}`)
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
    <div class="layout-container">
      <div class="upload-section">
        <div class="hero">
          <h1>讓 AI 幫你自動化生成論文摘要</h1>
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

      <!-- Old result section (optional, maybe keep for error display or history?) -->
      <!-- For now, we rely on the Modal -->
      <!-- <div class="result-section" v-if="result">
        <SummaryResult :result="result" />
      </div> -->

      <!-- New Preview Modal -->
      <PreviewModal />
      
    </div>
  </div>
</template>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 100%;
  margin: 0 auto;
  width: 100%;
}

@media (min-width: 1024px) {
  .layout-container {
    display: grid;
    grid-template-columns: 560px 1fr;
    align-items: start;
    text-align: left;
    gap: 3rem;
  }
}

.upload-section {
  display: flex;
  flex-direction: column;
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
  margin: 0 0 12px;
  font-size: 36px;
  font-weight: 800;
  color: #111827;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.button-group {
  display: flex;
  gap: 16px;
  margin-top: 32px;
}
</style>
