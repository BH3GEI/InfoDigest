<template>
  <div class="reader-view">
    <div class="page-header">
      <h1>内容阅读器</h1>
      <div class="view-controls">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索文件..."
            @input="filterDigests"
          >
          <span class="search-icon mdi mdi-magnify"></span>
        </div>
        <select v-model="sortOption" @change="sortDigests">
          <option value="date-desc">日期 (最新优先)</option>
          <option value="date-asc">日期 (最早优先)</option>
          <option value="name-asc">名称 (A-Z)</option>
          <option value="name-desc">名称 (Z-A)</option>
        </select>
      </div>
    </div>

    <div class="reader-container">
      <div class="digests-sidebar">
        <div v-if="filteredDigests.length === 0" class="empty-state">
          <p>没有找到匹配的文件</p>
        </div>
        <div v-else class="digest-list">
          <div 
            v-for="digest in filteredDigests" 
            :key="digest.filename"
            :class="['digest-item', selectedDigest === digest.filename ? 'active' : '']"
            @click="selectDigest(digest.filename)"
          >
            <div class="digest-icon">
              <span class="mdi mdi-file-document-outline"></span>
            </div>
            <div class="digest-info">
              <h3 class="digest-title">{{ digest.title }}</h3>
              <p class="digest-date">{{ digest.date }} {{ digest.formattedTime ? `${digest.formattedTime}` : '' }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="content-viewer">
        <div v-if="!selectedDigest" class="empty-viewer">
          <div class="empty-icon">
            <span class="mdi mdi-file-document-outline"></span>
          </div>
          <h2>选择一个文件查看内容</h2>
          <p>从左侧列表中选择一个文件以查看其内容</p>
        </div>
        <div v-else class="markdown-content">
          <div class="content-header">
            <h2>{{ currentDigestTitle }}</h2>
            <div class="content-actions">
              <button @click="openInNewTab" class="btn btn-outline btn-sm">
                <span class="mdi mdi-open-in-new"></span> 新标签页打开
              </button>
            </div>
          </div>
          <div class="markdown-container" v-html="renderedMarkdown"></div>
        </div>
      </div>
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
const digests = ref([])
const filteredDigests = ref([])
const selectedDigest = ref('')
const digestContent = ref('')
const searchQuery = ref('')
const sortOption = ref('date-desc')

// 计算属性
const renderedMarkdown = computed(() => {
  return digestContent.value ? marked(digestContent.value) : ''
})

const currentDigestTitle = computed(() => {
  const digest = digests.value.find(d => d.filename === selectedDigest.value)
  return digest ? digest.title : ''
})

// 生命周期钩子
onMounted(async () => {
  await loadDigests()
  
  // 如果路由中有文件名参数，则选择该文件
  if (route.params.filename) {
    selectDigest(route.params.filename)
  }
})

// 监听路由变化
watch(() => route.params.filename, (newFilename) => {
  if (newFilename) {
    selectDigest(newFilename)
  }
})

// 方法
async function loadDigests() {
  try {
    // 从后端API获取摘要文件列表
    const response = await axios.get('/api/digests')
    digests.value = response.data || []
    
    // 处理每个摘要的时间戳和格式化显示
    digests.value = digests.value.map(digest => {
      // 格式化日期
      const dateMatch = digest.filename.match(/(\d{4}-\d{2}-\d{2})/);
      if (dateMatch) {
        digest.date = dateMatch[1];
      }
      
      // 提取时间戳
      let timeStamp = null;
      
      // 匹配模式: filename_YYYY-MM-DD_HHMM.md
      const timePattern = digest.filename.match(/_(\d{4}-\d{2}-\d{2})_(\d{4})\.(md)$/);
      if (timePattern) {
        timeStamp = parseInt(timePattern[2], 10);
        digest.timestamp = timeStamp;
        
        // 格式化为时:分显示
        const hours = Math.floor(timeStamp / 100);
        const minutes = timeStamp % 100;
        digest.formattedTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
      } else {
        // 匹配无时间的情况
        digest.formattedTime = '';
        digest.timestamp = 0;
      }
      
      return digest;
    });
    
    filterDigests()
    sortDigests()
  } catch (error) {
    console.error('加载摘要文件列表失败:', error)
    // 使用模拟数据
    digests.value = [
      { filename: 'RSS_Digest_2025-03-30_1946.md', title: 'RSS信息聚合', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: 'NYT_>_World_News_2025-03-30_1946.md', title: 'NYT > World News', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: 'BBC_News_2025-03-30_1946.md', title: 'BBC News', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: '36氪_2025-03-30_1946.md', title: '36氪', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: 'Hacker_News_2025-03-30_1946.md', title: 'Hacker News', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: 'InfoQ_-_促进软件开发领域知识与创新的传播_2025-03-30_1946.md', title: 'InfoQ - 促进软件开发领域知识与创新的传播', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: '少数派_2025-03-30_1946.md', title: '少数派', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: '智能聚合_2025-03-30_2147.md', title: '智能聚合', date: '2025-03-30', timestamp: 2147, formattedTime: '21:47' },
      { filename: 'Top_stories_-_Google_News_2025-03-30_1946.md', title: 'Top stories - Google News', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' }
    ]
    filterDigests()
    sortDigests()
  }
}

async function selectDigest(filename) {
  selectedDigest.value = filename
  
  // 更新路由，但不重新加载页面
  if (route.params.filename !== filename) {
    router.push({ name: 'reader-detail', params: { filename } })
  }
  
  try {
    // 从后端API获取摘要内容
    const response = await axios.get(`/api/digests/${filename}`)
    digestContent.value = response.data || ''
  } catch (error) {
    console.error('加载摘要内容失败:', error)
    // 使用模拟数据或显示错误信息
    digestContent.value = '# 加载内容失败\n\n无法加载所选文件的内容，请稍后重试。'
  }
}

function filterDigests() {
  if (!searchQuery.value) {
    filteredDigests.value = [...digests.value]
  } else {
    const query = searchQuery.value.toLowerCase()
    filteredDigests.value = digests.value.filter(digest => {
      return digest.title.toLowerCase().includes(query) || 
             digest.filename.toLowerCase().includes(query)
    })
  }
  sortDigests()
}

function sortDigests() {
  switch (sortOption.value) {
    case 'date-desc':
      filteredDigests.value.sort((a, b) => {
        // 首先按日期排序
        const dateComp = b.date.localeCompare(a.date);
        if (dateComp !== 0) return dateComp;
        
        // 如果日期相同，按时间戳排序
        if (a.timestamp && b.timestamp) {
          return b.timestamp - a.timestamp;
        }
        return b.filename.localeCompare(a.filename);
      })
      break
    case 'date-asc':
      filteredDigests.value.sort((a, b) => {
        // 首先按日期排序
        const dateComp = a.date.localeCompare(b.date);
        if (dateComp !== 0) return dateComp;
        
        // 如果日期相同，按时间戳排序
        if (a.timestamp && b.timestamp) {
          return a.timestamp - b.timestamp;
        }
        return a.filename.localeCompare(b.filename);
      })
      break
    case 'name-asc':
      filteredDigests.value.sort((a, b) => a.title.localeCompare(b.title))
      break
    case 'name-desc':
      filteredDigests.value.sort((a, b) => b.title.localeCompare(a.title))
      break
  }
}

function openInNewTab() {
  if (selectedDigest.value) {
    const baseUrl = window.location.origin
    const url = `${baseUrl}/api/digests/${selectedDigest.value}/raw`
    window.open(url, '_blank')
  }
}
</script>

<style scoped>
.reader-view {
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.view-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-box {
  position: relative;
}

.search-box input {
  padding-left: 2.5rem;
  width: 250px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
}

.reader-container {
  display: flex;
  flex: 1;
  gap: 1.5rem;
  height: 100%;
  overflow: hidden;
}

.digests-sidebar {
  width: 300px;
  min-width: 300px;
  background-color: white;
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  overflow-y: auto;
  height: 100%;
}

.digest-list {
  display: flex;
  flex-direction: column;
}

.digest-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color 0.2s;
}

.digest-item:hover {
  background-color: #f5f7fa;
}

.digest-item.active {
  background-color: rgba(52, 152, 219, 0.1);
  border-left: 3px solid var(--primary-color);
}

.digest-icon {
  font-size: 1.5rem;
  color: var(--primary-color);
  margin-right: 1rem;
  flex-shrink: 0;
}

.digest-info {
  overflow: hidden;
  flex: 1;
}

.digest-title {
  font-size: 1rem;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.digest-date {
  font-size: 0.85rem;
  color: var(--text-light);
}

.content-viewer {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  overflow-y: auto;
  height: 100%;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.empty-viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-light);
  padding: 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.3;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 10;
}

.content-header h2 {
  margin: 0;
  font-size: 1.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.9rem;
  white-space: nowrap;
}

.markdown-container {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

/* Markdown 样式 */
:deep(.markdown-container h1) {
  font-size: 2rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

:deep(.markdown-container h2) {
  font-size: 1.5rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

:deep(.markdown-container h3) {
  font-size: 1.25rem;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

:deep(.markdown-container p) {
  margin-bottom: 1rem;
  line-height: 1.6;
}

:deep(.markdown-container a) {
  color: var(--primary-color);
  text-decoration: none;
}

:deep(.markdown-container a:hover) {
  text-decoration: underline;
}

:deep(.markdown-container ul),
:deep(.markdown-container ol) {
  margin-bottom: 1rem;
  padding-left: 2rem;
}

:deep(.markdown-container li) {
  margin-bottom: 0.5rem;
}

:deep(.markdown-container blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: 1rem;
  margin-left: 0;
  color: var(--text-light);
}

:deep(.markdown-container code) {
  font-family: 'Courier New', Courier, monospace;
  background-color: #f5f7fa;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-size: 0.9em;
}

:deep(.markdown-container pre) {
  background-color: #f5f7fa;
  padding: 1rem;
  border-radius: 5px;
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

:deep(.markdown-container pre code) {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

:deep(.markdown-container table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
}

:deep(.markdown-container th),
:deep(.markdown-container td) {
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  text-align: left;
}

:deep(.markdown-container th) {
  background-color: #f5f7fa;
}

:deep(.markdown-container img) {
  max-width: 100%;
  height: auto;
  border-radius: 5px;
  margin: 1rem 0;
}

:deep(.markdown-container hr) {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 2rem 0;
}

@media (max-width: 768px) {
  .reader-view {
    height: auto;
    min-height: calc(100vh - 180px);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .view-controls {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }
  
  .reader-container {
    flex-direction: column;
    height: auto;
    min-height: 800px;
  }
  
  .digests-sidebar {
    width: 100%;
    max-height: 300px;
    min-height: 300px;
  }
  
  .content-viewer {
    height: auto;
    min-height: 500px;
  }
  
  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .content-header h2 {
    width: 100%;
  }
}
</style>