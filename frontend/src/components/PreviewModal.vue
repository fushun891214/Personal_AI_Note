<script setup>
import { computed, ref } from 'vue'
import { useSummaryStore } from '../stores/summary'
import { marked } from 'marked'
import jsPDF from 'jspdf'
import axios from 'axios'

const store = useSummaryStore()
const userFeedback = ref('')
const isRefining = ref(false)
const isSaving = ref(false)

// Convert Notion Blocks to Markdown
const notionBlocksToMarkdown = (blocks) => {
  if (!blocks) return ''
  
  let markdown = ''
  
  const processRichText = (richText) => {
    return richText.map(t => {
      let content = t.text.content
      // Escape markdown characters in content to avoid accidental formatting? 
      // For now, trust content but handle bold/italic.
      if (t.annotations?.bold) content = `**${content}**`
      if (t.annotations?.italic) content = `*${content}*`
      if (t.annotations?.code) content = `\`${content}\``
      return content
    }).join('')
  }
  
  blocks.forEach(block => {
    const type = block.type
    // Add newlines to ensure markdown parses blocks correctly
    
    if (type === 'callout') {
        const icon = block.callout.icon.emoji || '💡'
        const text = processRichText(block.callout.rich_text)
        markdown += `> ${icon} ${text}\n\n`
    } else if (type === 'heading_2') {
        markdown += `## ${processRichText(block.heading_2.rich_text)}\n\n`
    } else if (type === 'heading_3') {
        markdown += `### ${processRichText(block.heading_3.rich_text)}\n\n`
    } else if (type === 'bulleted_list_item') {
        // Ensure space after *
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
  // Use marked.parse if available (newer versions), or marked()
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
        original_summary: store.currentSummary, // Use current to iterate
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

const generatePDF = () => {
    const doc = new jsPDF()
    const text = notionBlocksToMarkdown(store.currentSummary.blocks)
    // Remove markdown symbols for PDF readability (simple cleanup)
    const cleanText = text.replace(/\*\*/g, '').replace(/## /g, '').replace(/> /g, '')
    
    const splitText = doc.splitTextToSize(cleanText, 180)
    doc.text(splitText, 10, 10)
    doc.save(`${store.currentSummary.title || 'summary'}.pdf`)
}

</script>

<template>
  <div v-if="store.isModalOpen" class="modal-overlay">
    <div class="modal-container">
      <div class="modal-header">
        <h3>{{ store.currentSummary?.title || '論文筆記預覽' }}</h3>
        <button class="close-btn" @click="store.closeModal">×</button>
      </div>
      
      <div class="modal-content">
        <!-- PDF Preview (Left) -->
        <div class="pdf-panel">
           <!-- Added type and correct styling for embed -->
           <embed 
             v-if="store.pdfUrl" 
             :src="store.pdfUrl" 
             type="application/pdf"
             class="pdf-embed"
           />
           <div v-else class="no-pdf">
             <p>無法載入 PDF</p>
             <p class="debug-url">{{ store.pdfUrl }}</p>
           </div>
        </div>
        
        <!-- Summary Preview (Right) -->
        <div class="summary-panel markdown-body" v-html="renderedSummary"></div>
      </div>
      
      <!-- Footer Controls -->
      <div class="modal-footer">
        <div class="refine-input">
            <textarea 
                v-model="userFeedback" 
                placeholder="輸入調整需求（例如：請補充實驗細節...）"
                :disabled="isRefining"
            ></textarea>
            <div class="api-notice">💡 已調整 {{ store.refinementCount }} 次</div>
        </div>
        
        <div class="action-buttons">
            <button class="btn-pdf" @click="generatePDF">📄 生成 PDF</button>
            <button class="btn-refine" @click="submitRefinement" :disabled="isRefining">
                {{ isRefining ? '調整中...' : '🔄 提交調整' }}
            </button>
            <button class="btn-save" @click="saveToNotion" :disabled="isSaving">
                {{ isSaving ? '儲存中...' : '💾 儲存到 Notion' }}
            </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: white; /* Full screen, so background can be white */
  z-index: 1000;
}

.modal-container {
  background: white;
  width: 100vw;
  height: 100vh;
  border-radius: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 0 16px; /* Remove vertical padding, set height instead */
  height: 56px;
  border-bottom: 1px solid #e5e7eb;
  display: grid;
  grid-template-columns: 40px 1fr 40px; /* Left spacer, Center title, Right button */
  align-items: center;
  background: #ffffff; /* White background usually looks cleaner */
}

.modal-header h3 {
  grid-column: 2;
  margin: 0;
  font-size: 1.125rem; /* 18px */
  font-weight: 600;
  color: #111827;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.close-btn {
  grid-column: 3;
  justify-self: end;
  background: transparent;
  border: none;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #6b7280;
  border-radius: 6px;
  transition: background-color 0.2s, color 0.2s;
  padding: 0;
}

.close-btn:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.close-btn svg {
   /* If we were using svg, but here text x is used */
   font-size: 20px;
   font-weight: 500;
}

.modal-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative; /* Context */
}

.pdf-panel {
  flex: 1;
  border-right: 1px solid #e5e7eb;
  background: #525659;
  position: relative;
  display: flex; /* Flex to center no-pdf message */
  flex-direction: column;
}

.pdf-embed {
  width: 100%;
  height: 100%;
  border: none;
  display: block; /* Remove inline spacing */
}

.no-pdf {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
}

.summary-panel {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.6;
  background: white;
}

/* Footer & Controls */
.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.refine-input textarea {
  width: 100%;
  height: 60px;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  resize: none;
  font-family: inherit;
  background: #ffffff; /* Explicit white background */
  color: #111827;      /* Explicit dark text */
}

.api-notice {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 4px;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

button {
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-pdf {
  background: #4b5563;
  color: white;
}

.btn-refine {
  background: #3b82f6;
  color: white;
  flex: 1; 
  max-width: 300px;
}

.btn-save {
  background: #10b981;
  color: white;
}

/* Markdown Styles (Simple subset) */
:deep(h2) { border-bottom: 1px solid #eee; padding-bottom: 0.3em; margin-top: 1.5em; font-weight: 700; }
:deep(h3) { margin-top: 1.2em; font-weight: 600; }
:deep(strong) { font-weight: 700; color: #111827; } /* Ensure bold works */
:deep(code) { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; font-family: monospace; color: #ef4444; }
:deep(pre) { background: #1f2937; color: white; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 1em 0; }
:deep(blockquote) { border-left: 4px solid #e5e7eb; margin: 1em 0; padding-left: 1em; color: #4b5563; font-style: italic; }
:deep(ul), :deep(ol) { padding-left: 20px; margin: 1em 0; }
:deep(li) { margin-bottom: 0.5em; }
:deep(details) { border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; margin: 12px 0; background: #fafafa; }
:deep(summary) { cursor: pointer; font-weight: 600; color: #374151; }
</style>
