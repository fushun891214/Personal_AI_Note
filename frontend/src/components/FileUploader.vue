<script setup>
import { ref } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['files-selected'])
const fileInput = ref(null)

const triggerInput = () => {
  if (props.disabled) return
  fileInput.value.click()
}

const handleFileChange = (event) => {
  if (event.target.files.length > 0) {
    emit('files-selected', Array.from(event.target.files))
    event.target.value = ''
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  if (props.disabled) return
  if (event.dataTransfer.files.length > 0) {
    emit('files-selected', Array.from(event.dataTransfer.files))
  }
}
</script>

<template>
  <div 
    class="upload-box" 
    :class="{ 'is-disabled': disabled }"
    @click="triggerInput" 
    @dragover.prevent 
    @drop="handleDrop"
  >
    <input 
      type="file" 
      ref="fileInput" 
      accept=".pdf, .ppt, .pptx, audio/*" 
      multiple 
      hidden
      @change="handleFileChange"
      :disabled="disabled"
    >
    <div class="icon">📁</div>
    <p>拖放檔案或點擊上傳</p>
    <div class="hint">支援格式：.pdf .ppt .pptx .mp3 .wav .m4a .ogg</div>
  </div>
</template>

<style scoped>
.upload-box {
    border: 2px dashed #d1d5db;
    border-radius: 20px;
    padding: 60px 40px;
    text-align: center;
    background: #f9fafb;
    margin-bottom: 32px;
    transition: all 0.2s;
    cursor: pointer;
    position: relative;
    user-select: none;
}

.upload-box:hover:not(.is-disabled) {
    border-color: #4f46e5;
    background: #f5f3ff;
}

.upload-box.is-disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background: #f3f4f6;
    border-color: #e5e7eb;
}

.upload-box p {
    margin: 12px 0 8px;
    font-size: 20px;
    font-weight: 600;
    color: #374151;
}

.icon {
    font-size: 72px; 
    margin-bottom: 20px;
}

.hint {
    margin-top: 12px;
    font-size: 14px;
    color: #9ca3af;
}

/* RWD: 小螢幕調整 */
@media (max-width: 768px) {
    .upload-box {
        padding: 40px 20px;
        border-radius: 14px;
    }
    
    .icon {
        font-size: 48px;
        margin-bottom: 12px;
    }
    
    .upload-box p {
        font-size: 16px;
    }
    
    .hint {
        font-size: 12px;
    }
}
</style>
