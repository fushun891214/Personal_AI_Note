<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import FileUploader from '../components/FileUploader.vue'
import FileList from '../components/FileList.vue'
import SummaryResult from '../components/SummaryResult.vue'

const files = ref([])
const isProcessing = ref(false)
const result = ref(null)

const handleFilesSelected = (newFiles) => {
  files.value = [...files.value, ...newFiles]
  // Hide previous result if adding new files
  if (result.value) {
    result.value = null
  }
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

    result.value = response.data
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
    <div class="hero">
      <h1>讓 AI 幫你自動化生成會議摘要</h1>
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

    <SummaryResult v-if="result" :result="result" />
  </div>
</template>

<style scoped>
.hero {
  margin-bottom: 48px;
  text-align: center;
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
