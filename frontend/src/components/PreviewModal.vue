<script setup>
import { computed, ref } from 'vue'
import { useSummaryStore } from '../stores/summary'
import { marked } from 'marked'
import axios from 'axios'
import { 
  FilePdfOutlined, 
  ReloadOutlined, 
  CloudUploadOutlined,
  LoadingOutlined
} from '@ant-design/icons-vue'

const store = useSummaryStore()
const userFeedback = ref('')
const isRefining = ref(false)
const isSaving = ref(false)
const isGeneratingPdf = ref(false)
const summaryRef = ref(null)

// Convert Notion Blocks to Markdown
const notionBlocksToMarkdown = (blocks) => {
  if (!blocks) return ''
  
  let markdown = ''
  
  const processRichText = (richText) => {
    return richText.map(t => {
      let content = t.text.content
      if (t.annotations?.bold) content = `**${content}**`
      if (t.annotations?.italic) content = `*${content}*`
      if (t.annotations?.code) content = `\`${content}\``
      return content
    }).join('')
  }
  
  blocks.forEach(block => {
    const type = block.type
    
    if (type === 'callout') {
        const icon = block.callout.icon.emoji || '💡'
        const text = processRichText(block.callout.rich_text)
        markdown += `> ${icon} ${text}\n\n`
    } else if (type === 'heading_2') {
        markdown += `## ${processRichText(block.heading_2.rich_text)}\n\n`
    } else if (type === 'heading_3') {
        markdown += `### ${processRichText(block.heading_3.rich_text)}\n\n`
    } else if (type === 'bulleted_list_item') {
        markdown += `- ${processRichText(block.bulleted_list_item.rich_text)}\n`
    } else if (type === 'code') {
        const lang = block.code.language
        const text = processRichText(block.code.rich_text)
        markdown += `\`\`\`${lang}\n${text}\n\`\`\`\n\n`
    } else if (type === 'quote') {
        markdown += `> ${processRichText(block.quote.rich_text)}\n\n`
    } else if (type === 'toggle') {
        const text = processRichText(block.toggle.rich_text)
        markdown += `<details>\n<summary>${text}</summary>\n\n`
        if (block.toggle.children) {
            markdown += notionBlocksToMarkdown(block.toggle.children)
        }
        markdown += `</details>\n\n`
    }
  })
  
  return markdown
}

const renderedSummary = computed(() => {
  if (!store.currentSummary || !store.currentSummary.blocks) return ''
  try {
     return marked.parse(notionBlocksToMarkdown(store.currentSummary.blocks))
  } catch (e) {
     return marked(notionBlocksToMarkdown(store.currentSummary.blocks))
  }
})

// Actions
const submitRefinement = async () => {
  if (!userFeedback.value.trim()) return
  
  isRefining.value = true
  try {
    const response = await axios.post('/api/refine', {
        original_summary: store.currentSummary,
        user_feedback: userFeedback.value
    })
    
    if (response.data.title) {
        store.updateSummary(response.data)
        userFeedback.value = ''
    }
  } catch (e) {
    alert('調整失敗: ' + e.message)
  } finally {
    isRefining.value = false
  }
}

const saveToNotion = async () => {
    isSaving.value = true
    try {
        const response = await axios.post('/api/save-to-notion', store.currentSummary)
        if (response.data.status === 'success') {
            alert('成功儲存到 Notion!')
            store.closeModal()
        } else {
            throw new Error(response.data.message || 'Unknown Error')
        }
    } catch (e) {
        alert('儲存失敗: ' + e.message)
    } finally {
        isSaving.value = false
    }
}

const generatePDF = async () => {
    isGeneratingPdf.value = true
    try {
        // 呼叫後端 API 生成 PDF
        const response = await axios.post('/api/generate-pdf', store.currentSummary, {
            responseType: 'blob'  // 重要：接收二進位資料
        })
        
        // 建立下載連結
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `summary_${Date.now()}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
    } catch (e) {
        alert('PDF 生成失敗: ' + e.message)
    } finally {
        isGeneratingPdf.value = false
    }
}

const handleClose = () => {
  store.closeModal()
}
</script>

<template>
  <a-modal
    v-model:open="store.isModalOpen"
    :title="store.currentSummary?.title || '論文筆記預覽'"
    width="90vw"
    :style="{ maxWidth: '1400px' }"
    centered
    @cancel="handleClose"
  >
    <!-- Main Content -->
    <div class="modal-body">
      <!-- PDF Preview (Left) -->
      <div class="pdf-panel">
         <embed 
           v-if="store.pdfUrl" 
           :src="store.pdfUrl" 
           type="application/pdf"
           class="pdf-embed"
         />
         <a-empty v-else description="無法載入 PDF" />
      </div>
      
      <!-- Summary Preview (Right) -->
      <div ref="summaryRef" class="summary-panel markdown-body" v-html="renderedSummary"></div>
    </div>

    <!-- Feedback Input -->
    <div class="feedback-section">
      <a-textarea 
          v-model:value="userFeedback" 
          placeholder="輸入調整需求（例如：請補充實驗細節...）"
          :disabled="isRefining"
          :rows="2"
          :maxLength="500"
          showCount
      />
      <div class="api-notice">💡 已調整 {{ store.refinementCount }} 次</div>
    </div>

    <!-- Footer Slot -->
    <template #footer>
      <div class="footer-buttons">
        <a-button @click="generatePDF" :loading="isGeneratingPdf">
          <template #icon><FilePdfOutlined /></template>
          生成 PDF
        </a-button>
        <a-button type="primary" @click="submitRefinement" :loading="isRefining">
          <template #icon><ReloadOutlined /></template>
          提交調整
        </a-button>
        <a-button type="primary" class="save-btn" @click="saveToNotion" :loading="isSaving">
          <template #icon><CloudUploadOutlined /></template>
          儲存到 Notion
        </a-button>
      </div>
    </template>
  </a-modal>
</template>

<style scoped>
.modal-body {
  display: flex;
  gap: 16px;
  height: 60vh;
  min-height: 400px;
}

.pdf-panel {
  flex: 1;
  background: #525659;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.pdf-embed {
  width: 100%;
  height: 100%;
  border: none;
}

.summary-panel {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.6;
}

.feedback-section {
  margin-top: 16px;
}

.api-notice {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.footer-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.save-btn {
  background: #10b981;
  border-color: #10b981;
}

.save-btn:hover {
  background: #059669;
  border-color: #059669;
}

/* Markdown Styles */
:deep(h2) { border-bottom: 1px solid #eee; padding-bottom: 0.3em; margin-top: 1.5em; font-weight: 700; }
:deep(h3) { margin-top: 1.2em; font-weight: 600; }
:deep(strong) { font-weight: 700; color: #111827; }
:deep(code) { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; font-family: monospace; color: #ef4444; }
:deep(pre) { background: #1f2937; color: white; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 1em 0; }
:deep(blockquote) { border-left: 4px solid #e5e7eb; margin: 1em 0; padding-left: 1em; color: #4b5563; font-style: italic; }
:deep(ul), :deep(ol) { padding-left: 20px; margin: 1em 0; }
:deep(li) { margin-bottom: 0.5em; }
:deep(details) { border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; margin: 12px 0; background: #fafafa; }
:deep(summary) { cursor: pointer; font-weight: 600; color: #374151; list-style: none; }
:deep(summary::-webkit-details-marker) { display: none; }

/* RWD: 小螢幕調整 */
@media (max-width: 768px) {
  .modal-body {
    flex-direction: column;
    height: auto;
    max-height: 50vh;
  }
  
  .pdf-panel {
    min-height: 200px;
    flex: none;
  }
  
  .summary-panel {
    flex: none;
    max-height: 300px;
  }
  
  .footer-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .footer-buttons button {
    flex: 1;
    min-width: 100px;
  }
}
</style>
