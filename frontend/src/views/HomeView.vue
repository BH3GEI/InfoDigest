<template>
  <div class="home-view">
    <section class="hero">
      <div class="hero-content">
        <h1>InfoDigest</h1>
        <p class="subtitle">智能RSS聚合与摘要工具</p>
        <p class="description">
          InfoDigest帮助您轻松管理RSS订阅源，使用AI生成内容摘要，让您快速了解重要信息。
        </p>
        <div class="hero-actions">
          <button @click="runRssFlow" class="btn btn-primary" :disabled="isProcessing">
            <span v-if="isProcessing">处理中...</span>
            <span v-else>立即获取最新内容</span>
          </button>
          <router-link to="/reader" class="btn btn-outline">浏览已生成内容</router-link>
        </div>
        <div class="digest-buttons">
          <router-link v-if="latestRssDigest" :to="`/reader/${encodeURIComponent(latestRssDigest.filename)}`" class="digest-button">
            <span class="digest-icon mdi mdi-file-document-outline"></span>
            <div class="digest-info">
              <h3>RSS 摘要</h3>
              <p>{{ latestRssDigest.date }} {{ latestRssDigest.formattedTime }}</p>
            </div>
          </router-link>
          
          <router-link v-if="latestSmartDigest" :to="`/reader/${encodeURIComponent(latestSmartDigest.filename)}`" class="digest-button">
            <span class="digest-icon mdi mdi-brain"></span>
            <div class="digest-info">
              <h3>智能聚合</h3>
              <p>{{ latestSmartDigest.date }} {{ latestSmartDigest.formattedTime }}</p>
            </div>
          </router-link>
          
          <router-link v-if="latestTopStories" :to="`/reader/${encodeURIComponent(latestTopStories.filename)}`" class="digest-button">
            <span class="digest-icon mdi mdi-trending-up"></span>
            <div class="digest-info">
              <h3>热门新闻</h3>
              <p>{{ latestTopStories.date }} {{ latestTopStories.formattedTime }}</p>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <section class="stats-section card">
      <h2>内容概览</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon"><span class="mdi mdi-rss"></span></div>
          <div class="stat-value">{{ stats.feedCount }}</div>
          <div class="stat-label">订阅源</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><span class="mdi mdi-file-document-outline"></span></div>
          <div class="stat-value">{{ stats.articleCount }}</div>
          <div class="stat-label">文章</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><span class="mdi mdi-calendar"></span></div>
          <div class="stat-value">{{ stats.lastUpdate }}</div>
          <div class="stat-label">最后更新</div>
        </div>
      </div>
    </section>

    <div class="content-sections">
      <section class="rss-digest card">
        <div class="section-header">
          <h2>RSS 摘要</h2>
          <router-link to="/reader" class="view-all">查看全部</router-link>
        </div>
        <div v-if="isLoadingRssDigest" class="loading-state">
          <p>加载中...</p>
        </div>
        <div v-else-if="rssDigestContent" class="digest-content markdown-body" v-html="renderedRssDigest"></div>
        <div v-else class="empty-state">
          <p>暂无 RSS 摘要内容</p>
          <button @click="runRssFlow" class="btn btn-primary" :disabled="isProcessing">
            立即获取内容
          </button>
        </div>
      </section>

      <section class="smart-digests card">
        <div class="section-header">
          <h2>智能聚合</h2>
          <router-link to="/reader" class="view-all">查看全部</router-link>
        </div>
        <div v-if="isLoadingContent" class="loading-state">
          <p>加载中...</p>
        </div>
        <div v-else-if="latestSmartDigestContent" class="digest-content markdown-body" v-html="renderedContent"></div>
        <div v-else class="empty-state">
          <p>暂无智能聚合内容</p>
          <button @click="runRssFlow" class="btn btn-primary" :disabled="isProcessing">
            立即获取内容
          </button>
        </div>
      </section>
    </div>

    <section class="recent-digests card">
      <div class="section-header">
        <h2>其他订阅源摘要</h2>
        <router-link to="/reader" class="view-all">查看全部</router-link>
      </div>
      <div v-if="otherDigests.length > 0" class="digest-list">
        <div v-for="(digest, index) in otherDigests" :key="index" class="digest-item">
          <div class="digest-icon"><span class="mdi mdi-file-document-outline"></span></div>
          <div class="digest-info">
            <h3 class="digest-title">
              <router-link :to="`/reader/${encodeURIComponent(digest.filename)}`">{{ digest.title }}</router-link>
            </h3>
            <p class="digest-date">{{ digest.date }} {{ digest.formattedTime ? `${digest.formattedTime}` : '' }}</p>
          </div>
          <div class="digest-actions">
            <router-link :to="`/reader/${encodeURIComponent(digest.filename)}`" class="btn btn-sm btn-outline">
              阅读
            </router-link>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>暂无其他摘要内容</p>
        <button @click="runRssFlow" class="btn btn-primary" :disabled="isProcessing">
          立即获取内容
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

const isProcessing = ref(false)
const isLoadingContent = ref(false)
const isLoadingRssDigest = ref(false)
const stats = ref({
  feedCount: 0,
  articleCount: 0,
  lastUpdate: '无数据'
})
const recentDigests = ref([])
const latestSmartDigestContent = ref('')
const rssDigestContent = ref('')

// 渲染Markdown内容
const renderedContent = computed(() => {
  return latestSmartDigestContent.value ? marked(latestSmartDigestContent.value) : ''
})

const renderedRssDigest = computed(() => {
  return rssDigestContent.value ? marked(rssDigestContent.value) : ''
})

// 智能聚合和Digest文件列表
const smartDigests = computed(() => {
  return recentDigests.value
    .filter(digest => 
      digest.title.includes('智能聚合')
    )
    .sort((a, b) => {
      // 首先按日期排序
      const dateComp = b.date.localeCompare(a.date);
      if (dateComp !== 0) return dateComp;
      
      // 如果日期相同，按时间戳排序
      if (a.timestamp && b.timestamp) {
        return b.timestamp - a.timestamp;
      }
      return b.filename.localeCompare(a.filename);
    })
})

// RSS摘要文件列表
const rssDigests = computed(() => {
  return recentDigests.value
    .filter(digest => 
      digest.title.includes('RSS信息聚合') || 
      digest.title.includes('RSS Digest') ||
      digest.title.includes('RSS_Digest')
    )
    .sort((a, b) => {
      // 首先按日期排序
      const dateComp = b.date.localeCompare(a.date);
      if (dateComp !== 0) return dateComp;
      
      // 如果日期相同，按时间戳排序
      if (a.timestamp && b.timestamp) {
        return b.timestamp - a.timestamp;
      }
      return b.filename.localeCompare(a.filename);
    })
})

// 其他摘要文件列表
const otherDigests = computed(() => {
  return recentDigests.value
    .filter(digest => 
      !digest.title.includes('智能聚合') && 
      !digest.title.includes('RSS信息聚合') && 
      !digest.title.includes('RSS Digest') &&
      !digest.title.includes('RSS_Digest') &&
      !digest.title.includes('Top stories')
    )
    .sort((a, b) => {
      // 首先按日期排序
      const dateComp = b.date.localeCompare(a.date);
      if (dateComp !== 0) return dateComp;
      
      // 如果日期相同，按时间戳排序
      if (a.timestamp && b.timestamp) {
        return b.timestamp - a.timestamp;
      }
      return b.filename.localeCompare(a.filename);
    })
})

// 查找最新的RSS摘要
const latestRssDigest = computed(() => {
  return rssDigests.value[0] || null
})

const latestTopStories = computed(() => {
  // 过滤出所有热门新闻类型的文件
  const stories = recentDigests.value.filter(digest => 
    digest.title.includes('Top stories')
  )
  // 按时间戳排序，取最新的
  return stories.sort((a, b) => {
    // 首先按日期排序
    const dateComp = b.date.localeCompare(a.date);
    if (dateComp !== 0) return dateComp;
      
    // 如果日期相同，按时间戳排序
    if (a.timestamp && b.timestamp) {
      return b.timestamp - a.timestamp;
    }
    return b.filename.localeCompare(a.filename);
  })[0] || null
})

// 查找最新的智能聚合文件
const latestSmartDigest = computed(() => {
  return smartDigests.value[0] || null
})

// 使用watch监听latestSmartDigest变化，自动加载内容
watch(latestSmartDigest, async (newDigest) => {
  if (newDigest) {
    await loadSmartDigestContent(newDigest.filename);
  }
}, { immediate: true });

// 使用watch监听latestRssDigest变化，自动加载内容
watch(latestRssDigest, async (newDigest) => {
  if (newDigest) {
    await loadRssDigestContent(newDigest.filename);
  }
}, { immediate: true });

onMounted(async () => {
  await loadStats()
  await loadRecentDigests()
})

async function loadStats() {
  try {
    // 获取统计数据
    const statsResponse = await axios.get('/api/stats');
    if (statsResponse.data) {
      stats.value = statsResponse.data;
    } else {
      // 使用摘要数量作为统计
      stats.value = {
        feedCount: 0, // 这个将由后台提供
        articleCount: recentDigests.value.length,
        lastUpdate: new Date().toLocaleDateString()
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error);
    // 使用摘要数量作为统计
    stats.value = {
      feedCount: 0,
      articleCount: recentDigests.value.length,
      lastUpdate: new Date().toLocaleDateString()
    }
  }
}

async function loadRecentDigests() {
  try {
    // 从output目录读取文件列表，限制获取最近的15个文件
    const response = await axios.get('/api/digests/recent?limit=15')
    recentDigests.value = response.data || []
    // 处理每个摘要的时间戳
    recentDigests.value = recentDigests.value.map(digest => {
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
  } catch (error) {
    console.error('加载最近摘要失败:', error)
    // 使用模拟数据
    recentDigests.value = [
      { filename: 'RSS_Digest_2025-03-30_1946.md', title: 'RSS Digest', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: 'NYT_>_World_News_2025-03-30_1946.md', title: 'NYT > World News', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: 'BBC_News_2025-03-30_1946.md', title: 'BBC News', date: '2025-03-30', timestamp: 1946, formattedTime: '19:46' },
      { filename: '智能聚合_2025-03-30_2147.md', title: '智能聚合', date: '2025-03-30', timestamp: 2147, formattedTime: '21:47' }
    ]
  }
}

// 专门加载智能聚合内容的函数
async function loadSmartDigestContent(filename) {
  if (!filename) return;
  
  isLoadingContent.value = true;
  try {
    const contentResponse = await axios.get(`/api/digests/${encodeURIComponent(filename)}`);
    latestSmartDigestContent.value = contentResponse.data || '';
  } catch (error) {
    console.error('加载智能聚合内容失败:', error);
    latestSmartDigestContent.value = '# 加载内容失败\n\n无法加载智能聚合内容，请稍后重试。';
  } finally {
    isLoadingContent.value = false;
  }
}

// 专门加载RSS摘要内容的函数
async function loadRssDigestContent(filename) {
  if (!filename) return;
  
  isLoadingRssDigest.value = true;
  try {
    const contentResponse = await axios.get(`/api/digests/${encodeURIComponent(filename)}`);
    rssDigestContent.value = contentResponse.data || '';
  } catch (error) {
    console.error('加载RSS摘要内容失败:', error);
    rssDigestContent.value = '# 加载内容失败\n\n无法加载RSS摘要内容，请稍后重试。';
  } finally {
    isLoadingRssDigest.value = false;
  }
}

async function runRssFlow() {
  if (isProcessing.value) return
  
  isProcessing.value = true
  try {
    // 调用后端API运行RSS流程
    await axios.post('/api/run-rssflow')
    // 重新加载数据
    await loadStats()
    await loadRecentDigests()
  } catch (error) {
    console.error('运行RSS流程失败:', error)
    alert('运行RSS流程失败，请查看控制台获取详细信息')
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.hero {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  border-radius: 12px;
  padding: 3rem 2rem;
  text-align: center;
  margin-bottom: 2rem;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  opacity: 0.9;
}

.description {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  opacity: 0.8;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
  flex-wrap: wrap; /* 允许按钮在小屏幕上换行 */
}

.digest-buttons {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.digest-button {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: white;
  transition: all 0.3s ease;
  text-decoration: none;
  border: 1px solid rgba(255, 255, 255, 0.3);
  min-width: 200px;
}

.digest-button:hover {
  background-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.digest-button .digest-icon {
  font-size: 2rem;
  margin-right: 1rem;
}

.digest-button .digest-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
}

.digest-button .digest-info p {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.8;
}

.secondary-actions {
  margin-top: 0;
}

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.hero .btn {
  padding: 0.75rem 1.5rem;
  font-size: 1.1rem;
  margin: 0.5rem;
  min-width: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero .btn-outline {
  border-color: white;
  color: white;
}

.hero .btn-outline:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.stats-section {
  padding: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.stat-card {
  text-align: center;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: var(--secondary-color);
}

.stat-label {
  font-size: 1rem;
  color: var(--text-light);
}

.content-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.view-all {
  font-size: 0.9rem;
}

.digest-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.digest-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.digest-item:hover {
  background-color: #e9ecef;
}

.digest-icon {
  font-size: 1.5rem;
  color: var(--primary-color);
  margin-right: 1rem;
}

.digest-info {
  flex: 1;
}

.digest-title {
  font-size: 1.1rem;
  margin-bottom: 0.25rem;
}

.digest-date {
  font-size: 0.9rem;
  color: var(--text-light);
}

.digest-actions {
  margin-left: 1rem;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.9rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-light);
}

.digest-content {
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  max-height: 500px;
  overflow-y: auto;
}

.card {
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  word-wrap: break-word;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body h1 {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body p {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body a {
  color: var(--primary-color);
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 2em;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
}

.markdown-body pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
}

.markdown-body blockquote {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  margin: 0 0 16px 0;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-light);
}

@media (max-width: 768px) {
  .hero {
    padding: 2rem 1rem;
  }
  
  .hero h1 {
    font-size: 2.5rem;
  }
  
  .subtitle {
    font-size: 1.25rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .digest-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .digest-button {
    width: 100%;
    margin-bottom: 1rem;
  }
  
  .content-sections {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>