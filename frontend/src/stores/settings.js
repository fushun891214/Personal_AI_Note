import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
    // API Keys
    const geminiApiKey = ref(localStorage.getItem('gemini_api_key') || '')
    const notionApiKey = ref(localStorage.getItem('notion_api_key') || '')
    const notionDatabaseId = ref(localStorage.getItem('notion_database_id') || '')

    // UI state
    const isSettingsModalOpen = ref(false)

    // Actions
    function setGeminiApiKey(key) {
        geminiApiKey.value = key
        localStorage.setItem('gemini_api_key', key)
    }

    function setNotionApiKey(key) {
        notionApiKey.value = key
        localStorage.setItem('notion_api_key', key)
    }

    function setNotionDatabaseId(id) {
        notionDatabaseId.value = id
        localStorage.setItem('notion_database_id', id)
    }

    function openSettingsModal() {
        isSettingsModalOpen.value = true
    }

    function closeSettingsModal() {
        isSettingsModalOpen.value = false
    }

    // Validation Helpers
    function hasGeminiKey() {
        return !!geminiApiKey.value && geminiApiKey.value.trim() !== ''
    }

    function hasNotionKeys() {
        return !!notionApiKey.value && notionApiKey.value.trim() !== '' && 
               !!notionDatabaseId.value && notionDatabaseId.value.trim() !== ''
    }

    return {
        geminiApiKey,
        notionApiKey,
        notionDatabaseId,
        isSettingsModalOpen,
        setGeminiApiKey,
        setNotionApiKey,
        setNotionDatabaseId,
        openSettingsModal,
        closeSettingsModal,
        hasGeminiKey,
        hasNotionKeys
    }
})
