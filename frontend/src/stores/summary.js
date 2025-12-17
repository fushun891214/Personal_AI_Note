
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSummaryStore = defineStore('summary', () => {
  const originalSummary = ref(null)
  const currentSummary = ref(null)
  const pdfUrl = ref(null)
  const refinementCount = ref(0)
  const isModalOpen = ref(false)

  const setSummary = (summary, url) => {
    // Deep copy original to keep it safe
    originalSummary.value = JSON.parse(JSON.stringify(summary))
    currentSummary.value = summary
    pdfUrl.value = url
    refinementCount.value = 0
    isModalOpen.value = true
  }

  const updateSummary = (newSummary) => {
    currentSummary.value = newSummary
    refinementCount.value++
  }

  const closeModal = () => {
    isModalOpen.value = false
  }

  return {
    originalSummary,
    currentSummary,
    pdfUrl,
    refinementCount,
    isModalOpen,
    setSummary,
    updateSummary,
    closeModal
  }
})
