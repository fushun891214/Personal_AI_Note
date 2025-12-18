<script setup>
// App.vue is now a pure container component
// All business logic has been moved to views/
</script>

<template>
  <div class="app-container">
    <main class="main-container">
      <RouterView />
    </main>
  </div>
</template>

<style>
/* Global Styles from original CSS */
* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    background: #ffffff;
    color: #111827;
    overflow: auto;
    height: auto;
    min-height: 100%;
}

.app-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header Styles */
.app-header {
    border-bottom: 1px solid #f3f4f6;
    padding: 20px 0;
    background: #ffffff;
    position: sticky;
    top: 0;
    z-index: 10;
}

/* ... existing styles ... */

/* Main Content */
.main-container {
    max-width: 100%;
    margin: 0 auto;
    padding: 0;
    width: 100%;
}

button {
    width: 100%;
    padding: 16px 24px;
    border-radius: 12px;
    border: none;
    font-size: 16px;
    cursor: pointer;
    background: #4f46e5;
    color: #ffffff;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    transition: all 0.2s;
    display: block;
    flex: 1;
}

button:hover {
    background: #4338ca;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
}

button:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
}

.secondary-btn {
    background: #ffffff;
    color: #374151;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    border: 1px solid #e5e7eb;
}

.secondary-btn:hover {
    background: #f9fafb;
    border-color: #d1d5db;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
</style>
