<script setup>
defineProps({
  files: {
    type: Array,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['remove-file'])
</script>

<template>
  <div class="file-list" v-if="files.length > 0">
    <div 
      v-for="(file, index) in files" 
      :key="index + file.name" 
      class="file-item"
    >
      <span class="file-info">{{ file.name }}</span>
      <button 
        v-if="!disabled"
        class="delete-btn" 
        @click="$emit('remove-file', index)"
        type="button"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<style scoped>
.file-list {
    margin-bottom: 24px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 200px;
    overflow-y: auto;
    width: 100%;
}

.file-item {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 14px;
    color: #4b5563;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.file-info {
    display: flex;
    align-items: center;
}

.file-info::before {
    content: "📄";
    margin-right: 10px;
}


.delete-btn {
    background: transparent;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: bold;
    transition: all 0.2s;
    font-size: 14px;
    line-height: 1;
    
    /* Reset global button styles */
    width: auto;
    display: inline-flex;
    flex: none;
    box-shadow: none;
    margin: 0;
    align-items: center;
    justify-content: center;
}

.delete-btn:hover {
    background-color: #fee2e2;
    color: #ef4444;
    transform: none; /* Prevent global hover transform */
    box-shadow: none;
}

</style>
