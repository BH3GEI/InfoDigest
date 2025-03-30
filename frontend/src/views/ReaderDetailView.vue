<template>
  <div class="reader-detail-view">
    <div class="page-header">
      <div class="header-left">
        <router-link to="/reader" class="back-link">
          <span class="mdi mdi-arrow-left"></span> 返回列表
        </router-link>
        <h1>{{ digestTitle }}</h1>
      </div>
      <div class="header-actions">
        <button @click="openInNewTab" class="btn btn-outline">
          <span class="mdi mdi-open-in-new"></span> 新标签页打开
        </button>
      </div>
    </div>

    <div class="content-container card">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>加载内容中...</p>
      </div>
      <div v-else-if="error" class="error-state">
        <div class="error-icon">
          <span class="mdi mdi-alert-circle-outline"></span>
        </div>
        <h2>加载失败</h2>
        <p>{{ error }}</p>
        <button @click="loadDigestContent" class="btn btn-primary">重试</button>
      </div>
      <div v-else class="markdown-content" v-html="renderedMarkdown"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked'
import 'highlight.js/styles/github.css'
import hljs from 'highlight.js'

// 配置marked使用highlight.js进行代码高亮
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true
})

const route = useRoute()
const router = useRouter()

// 状态变量
const digestContent = ref('')
const digestTitle = ref('')
const isLoading = ref(true)
const error = ref(null)

// 计算属性
const renderedMarkdown = computed(() => {
  return digestContent.value ? marked(digestContent.value) : ''
})

// 生命周期钩子
onMounted(() => {
  loadDigestContent()
})

// 监听路由变化
watch(() => route.params.filename, (newFilename) => {
  if (newFilename) {
    loadDigestContent()
  }
})

// 方法
async function loadDigestContent() {
  if (!route.params.filename) {
    router.push('/reader')
    return
  }
  
  isLoading.value = true
  error.value = null
  
  try {
    // 从文件名中提取标题
    const filename = route.params.filename
    const titleMatch = filename.match(/(.+)_\d{4}-\d{2}-\d{2}\.md$/)
    digestTitle.value = titleMatch ? titleMatch[1].replace(/_/g, ' ') : filename
    
    // 从后端API获取摘要内容
    const response = await axios.get(`/api/digests/${filename}`)
    digestContent.value = response.data || ''
  } catch (err) {
    console.error('加载摘要内容失败:', err)
    error.value = '无法加载所选文件的内容，请稍后重试。'
  } finally {
    isLoading.value = false
  }
}

function openInNewTab() {
  if (route.params.filename) {
    const baseUrl = window.location.origin
    const url = `${baseUrl}/api/digests/${route.params.filename}/raw`
    window.open(url, '_blank')
  }
}
</script>

<style scoped>
.reader-detail-view {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-light);
  text-decoration: none;
  font-weight: 500;
}

.back-link:hover {
  color: var(--primary-color);
}

.content-container {
  padding: 2rem;
  min-height: 500px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  color: var(--error-color);
  margin-bottom: 1rem;
}

.error-state h2 {
  margin-bottom: 0.5rem;
  color: var(--error-color);
}

.error-state p {
  margin-bottom: 1.5rem;
  color: var(--text-light);
}

/* Markdown 样式 */
:deep(.markdown-content h1) {
  font-size: 2rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

:deep(.markdown-content h2) {
  font-size: 1.5rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

:deep(.markdown-content h3) {
  font-size: 1.25rem;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

:deep(.markdown-content p) {
  margin-bottom: 1rem;
  line-height: 1.6;
}

:deep(.markdown-content a) {
  color: var(--primary-color);
  text-decoration: none;
}

:deep(.markdown-content a:hover) {
  text-decoration: underline;
}

:deep(.markdown-content ul),
:deep(.markdown-content ol) {
  margin-bottom: 1rem;
  padding-left: 2rem;
}

:deep(.markdown-content li) {
  margin-bottom: 0.5rem;
}

:deep(.markdown-content blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: 1rem;
  margin-left: 0;
  color: var(--text-light);
}

:deep(.markdown-content code) {
  font-family: 'Courier New', Courier, monospace;
  background-color: #f5f7fa;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-size: 0.9em;
}

:deep(.markdown-content pre) {
  background-color: #f5f7fa;
  padding: 1rem;
  border-radius: 5px;
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

:deep(.markdown-content pre code) {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

:deep(.markdown-content table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
}

:deep(.markdown-content th),
:deep(.markdown-content td) {
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  text-align: left;
}

:deep(.markdown-content th) {
  background-color: #f5f7fa;
}

:deep(.markdown-content img) {
  max-width: 100%;
  height: auto;
  border-radius: 5px;
  margin: 1rem 0;
}

:deep(.markdown-content hr) {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 2rem 0;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .content-container {
    padding: 1.5rem;
  }
}
</style>