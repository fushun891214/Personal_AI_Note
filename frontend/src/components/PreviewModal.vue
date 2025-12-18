<script setup>
import { computed, ref } from 'vue'
import { useSummaryStore } from '../stores/summary'
import { useSettingsStore } from '../stores/settings'
import { marked } from 'marked'
import axios from 'axios'
import { 
  FilePdfOutlined, 
  ReloadOutlined, 
  CloudUploadOutlined,
  LoadingOutlined
} from '@ant-design/icons-vue'
import { Modal, Dropdown, Menu, MenuItem, Button } from 'ant-design-vue'
import { DownOutlined, ThunderboltOutlined } from '@ant-design/icons-vue'

const store = useSummaryStore()
const settingsStore = useSettingsStore()
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
      // Use HTML tags to avoid Markdown parser issues with spaces
      if (t.annotations?.bold) content = `<strong>${content}</strong>`
      if (t.annotations?.italic) content = `<em>${content}</em>`
      if (t.annotations?.code) content = `<code>${content}</code>`
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
        markdown += `<details open>\n<summary>${text}</summary>\n\n`
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
  
  if (!settingsStore.hasGeminiKey()) {
      Modal.warn({
          title: '未設定 Gemini Key',
          content: '請先在設定中輸入 Gemini API Key',
          onOk: () => settingsStore.openSettingsModal(),
          centered: true
      })
      return
  }

  isRefining.value = true
  try {
    const response = await axios.post('/api/refine', {
        original_summary: store.currentSummary,
        user_feedback: userFeedback.value
    }, {
        headers: {
            'X-Gemini-API-Key': settingsStore.geminiApiKey
        }
    })
    
    if (response.data.title) {
        store.updateSummary(response.data)
        userFeedback.value = ''
    }
  } catch (e) {
    if (e.response && (e.response.status === 401 || e.response.status === 403)) {
        Modal.error({ 
            title: 'Gemini API Error', 
            content: `額度已滿或 Key 無效 (${e.response.data.error || e.message})`,
            centered: true,
            okText: '去設定',
            onOk: () => settingsStore.openSettingsModal()
        })
    } else {
        Modal.error({ title: '調整失敗', content: e.message, centered: true })
    }
  } finally {
    isRefining.value = false
  }
}

    const saveToNotion = async () => {
        if (!settingsStore.hasNotionKeys()) {
            Modal.warn({
                title: '未設定 Notion Keys',
                content: '匯出到 Notion 需要設定 API Key 和 Database ID',
                okText: '去設定',
                onOk: () => settingsStore.openSettingsModal(),
                centered: true
            })
            return
        }

        isSaving.value = true
        try {
            // Append _summary to the title for Notion
            const payload = {
                ...store.currentSummary,
                title: store.currentSummary.title
            }
            const response = await axios.post('/api/save-to-notion', payload, {
                headers: {
                    'X-Notion-API-Key': settingsStore.notionApiKey,
                    'X-Notion-Database-ID': settingsStore.notionDatabaseId
                }
            })
            if (response.data.status === 'success') {
                Modal.success({ title: '儲存成功', content: '已成功儲存到 Notion!', centered: true })
            } else {
                throw new Error(response.data.message || 'Unknown Error')
            }
        } catch (e) {
            if (e.response && (e.response.status === 401 || e.response.status === 403)) {
                Modal.error({ 
                    title: 'Notion API Error', 
                    content: `權限不足或 Key 無效 (${e.response.data.error || e.message})`,
                    centered: true,
                    okText: '去設定',
                    onOk: () => settingsStore.openSettingsModal()
                })
            } else {
                 Modal.error({ title: '儲存失敗', content: e.message, centered: true })
            }
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
            // Use title_summary.pdf format
            const safeTitle = (store.currentSummary?.title || 'summary').replace(/[\\/:*?"<>|]/g, '_')
            link.download = `${safeTitle}_summary.pdf`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            window.URL.revokeObjectURL(url)
        } catch (e) {
            Modal.error({ title: 'PDF 生成失敗', content: e.message, centered: true })
        } finally {
            isGeneratingPdf.value = false
        }
    }

    // Prompt Templates (Hardcoded)
    const promptTemplates = ref([
        {
            label: "選項 A - 快速摘要指令",
            value: "請閱讀這篇論文，生成一個不超過 500 字 的摘要，包含以下內容：\n1. 研究目的\n2. 研究方法\n3. 主要結果\n4. 結論\n附上 關鍵字列表。"
        },
        {
            label: "選項 B - 論文結構解析指令",
            value: "請解析這篇論文的結構，並提供以下部分的詳細說明：\n1. 摘要重點\n2. 引言：研究背景和動機\n3. 方法：核心步驟與流程\n4. 結果：重要發現\n5. 討論：主要論點與結論\n如有 數據、圖表或統計分析，請簡要說明它們的意義。"
        },
        {
            label: "選項 C - 深入技術或理論解析指令",
            value: "針對論文中提到的每個「[技術/理論名稱]」，請詳細說明：\n1. 概念定義\n2. 應用範圍\n3. 運作原理\n若有 公式或流程圖，請進行簡化說明，並提供 具體例子。"
        },
        {
            label: "選項 D - 批判性分析指令",
            value: "請進行批判性分析，內容包括：\n1. 研究設計的優點與缺點\n2. 資料分析的合理性\n3. 結果與結論是否支持研究假設\n4. 潛在的偏誤或限制\n附上 改善建議，以優化研究設計或分析方法。"
        }
    ])

    const applyTemplate = (tpl) => {
        userFeedback.value = tpl.value
    }
    
    // Fetch prompts when modal opens
    import { watch } from 'vue'
    watch(() => store.isModalOpen, (newVal) => {
        if (newVal) {
            userFeedback.value = '' // Clear previous feedback
        }
    })

    const handleClose = async () => {
      // 嘗試刪除後端臨時檔案
      if (store.pdfUrl) {
          try {
              // Extract filename from URL (e.g., /uploads/temp/uuid.pdf -> uuid.pdf)
              const filename = store.pdfUrl.split('/').pop()
              if (filename) {
                  await axios.delete(`/api/delete-temp?filename=${filename}`)
              }
          } catch (e) {
              console.error('Failed to cleanup temp file:', e)
          }
      }
      store.closeModal()
    }
    </script>

    <template>
      <a-modal
        v-model:open="store.isModalOpen"
        title="論文瀏覽"
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
      <div class="feedback-header">
         <a-dropdown :trigger="['click']">
            <a-button size="small">
                分析選項
                <DownOutlined />
            </a-button>
            <template #overlay>
                <a-menu>
                    <a-menu-item 
                        v-for="(tpl, index) in promptTemplates" 
                        :key="index"
                        @click="applyTemplate(tpl)"
                    >
                        {{ tpl.label }}
                    </a-menu-item>
                </a-menu>
            </template>
         </a-dropdown>
      </div>
      <a-textarea 
          v-model:value="userFeedback" 
          placeholder="輸入調整需求（例如：請詳細解釋 Figure 內容）"
          :disabled="isRefining"
          :rows="4"
          :maxLength="2000"
      />
      <div class="feedback-footer">
        <div class="api-notice">💡 已調整 {{ store.refinementCount }} 次</div>
        <div class="char-count">{{ userFeedback.length }} / 2000</div>
      </div>
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
  max-height: 60vh;
  overflow: hidden;
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
  max-height: 100%;
}

.feedback-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 0;
  background: #ffffff;
  padding: 8px;
  border-radius: 8px;
  position: relative;
  z-index: 10;
}

.feedback-header {
  display: flex;
  justify-content: flex-end;
}

.feedback-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.api-notice {
  font-size: 12px;
  color: #6b7280;
}

.char-count {
  font-size: 12px;
  color: #bfbfbf;
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
    display: flex;
    height: 40vh;         /* Reduced to 40vh to prevent double scrollbars */
    max-height: 40vh;
    overflow: hidden;
  }
  
  .pdf-panel {
    flex: 0 0 150px;      /* Reduced height further */
    min-height: 150px;
    margin-bottom: 8px;
  }
  
  .summary-panel {
    flex: 1;
    overflow-y: auto;
    max-height: none;
    height: auto;
    font-size: 14px;
  }
  
  .footer-buttons {
    flex-wrap: nowrap;
    gap: 4px;             /* Tighter gap */
    width: 100%;
    justify-content: space-between; 
  }
  
  /* Target Ant Design buttons specifically for compactness */
  .footer-buttons :deep(.ant-btn) {
    font-size: 12px !important; /* Smaller font */
    height: 32px !important;
    padding: 0 4px !important; /* Minimal padding */
    flex: 1;
    min-width: 0;
    
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Ensure text is centered */
  .footer-buttons :deep(.ant-btn > span) {
    flex: 1;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* Hide icons on mobile to save space */
  .footer-buttons :deep(.ant-btn .anticon) {
    display: none !important;
  }
}

/* RWD: 小螢幕調整 */
@media (max-width: 768px) {
  /* ... (other styles) ... */

  /* Remove border/block above footer */
  :deep(.ant-modal-footer) {
    border-top: none !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
  }
}
</style>
