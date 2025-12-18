<script setup>
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '../stores/settings'

const store = useSettingsStore()

const geminiKey = ref('')
const notionKey = ref('')
const notionDbId = ref('')

onMounted(() => {
    // initialize with current store values
    geminiKey.value = store.geminiApiKey
    notionKey.value = store.notionApiKey
    notionDbId.value = store.notionDatabaseId
})

const handleSave = () => {
    store.setGeminiApiKey(geminiKey.value)
    store.setNotionApiKey(notionKey.value)
    store.setNotionDatabaseId(notionDbId.value)
    store.closeSettingsModal()
}

const handleClose = () => {
    // Reset to store values on close without saving
    geminiKey.value = store.geminiApiKey
    notionKey.value = store.notionApiKey
    notionDbId.value = store.notionDatabaseId
    store.closeSettingsModal()
}
</script>

<template>
  <Teleport to="body">
    <div v-if="store.isSettingsModalOpen" class="modal-overlay" @click.self="handleClose">
      <div class="modal-content">
        <div class="modal-header">
          <h2>設定 (Settings)</h2>
          <button class="close-btn" @click="handleClose">×</button>
        </div>
        
        <div class="modal-body">
          <p class="description">
              請輸入您的 API Key，這些資訊僅會儲存在您的瀏覽器中。
          </p>

          <div class="form-group">
              <label for="gemini-key">Gemini API Key <span class="required">*</span></label>
              <input 
                  id="gemini-key" 
                  v-model="geminiKey" 
                  type="password" 
                  placeholder="Entries starts with AIza..."
              >
              <small>用於生成論文筆記</small>
          </div>

          <div class="form-group">
              <label for="notion-key">Notion API Key</label>
              <input 
                  id="notion-key" 
                  v-model="notionKey" 
                  type="password" 
                  placeholder="Entries starts with secret_..."
              >
          </div>

          <div class="form-group">
              <label for="notion-db">Notion Database ID</label>
              <input 
                  id="notion-db" 
                  v-model="notionDbId" 
                  type="text" 
                  placeholder="Your Database ID"
              >
              <small>匯出筆記到 Notion 時需要</small>
          </div>
        </div>

        <div class="modal-footer">
          <button class="secondary-btn" @click="handleClose">取消</button>
          <button class="primary-btn" @click="handleSave">儲存設定</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2000;
    backdrop-filter: blur(4px);
    animation: fadeIn 0.2s ease-out;
}

.modal-content {
    background: white;
    padding: 24px;
    border-radius: 16px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    gap: 20px;
    animation: slideUp 0.3s ease-out;
    position: relative; /* For absolute close button */
}

.modal-header {
    /* Removed flex space-between */
    margin-bottom: 8px;
}

.modal-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 700;
    color: #111827;
}

.close-btn {
    position: absolute;
    top: 16px;
    right: 16px;
    background: none;
    border: none;
    font-size: 24px;
    color: #9ca3af;
    cursor: pointer;
    line-height: 1;
    padding: 4px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
    box-shadow: none;
}

.close-btn:hover {
    background: #f3f4f6;
    color: #374151;
    transform: none;
}

.description {
    font-size: 14px;
    color: #6b7280;
    margin: 0;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 12px;
}

.form-group label {
    font-weight: 600;
    font-size: 14px;
    color: #374151;
}

.required {
    color: #ef4444;
}

.form-group input {
    padding: 10px 12px;
    border: 1px solid #000000;
    background-color: #ffffff;
    color: #000000;
    border-radius: 8px;
    font-size: 15px;
    transition: border-color 0.2s;
}

.form-group input:focus {
    outline: none;
    border-color: #000000;
    box-shadow: 0 0 0 1px #000000;
}

.form-group small {
    font-size: 12px;
    color: #9ca3af;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.primary-btn {
    background: #4f46e5;
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    font-weight: 500;
    font-size: 14px;
    width: auto;
    flex: none;
    display: inline-block;
    box-shadow: 0 1px 2px 0 rgba(79, 70, 229, 0.2);
}

.primary-btn:hover {
    background: #4338ca;
}

.secondary-btn {
    background: white;
    color: #374151;
    padding: 8px 16px;
    border-radius: 6px;
    border: 1px solid #e5e7eb;
    cursor: pointer;
    font-weight: 500;
    font-size: 14px;
    width: auto;
    flex: none;
    box-shadow: none;
}

.secondary-btn:hover {
    background: #f9fafb;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
