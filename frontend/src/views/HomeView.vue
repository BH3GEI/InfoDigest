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

    <section class="recent-digests card">
      <div class="section-header">
        <h2>最近生成的摘要</h2>
        <router-link to="/reader" class="view-all">查看全部</router-link>
      </div>
      <div v-if="recentDigests.length > 0" class="digest-list">
        <div v-for="(digest, index) in recentDigests" :key="index" class="digest-item">
          <div class="digest-icon"><span class="mdi mdi-file-document-outline"></span></div>
          <div class="digest-info">
            <h3 class="digest-title">
              <router-link :to="`/reader/${encodeURIComponent(digest.filename)}`">{{ digest.title }}</router-link>
            </h3>
            <p class="digest-date">{{ digest.date }}</p>
          </div>
          <div class="digest-actions">
            <router-link :to="`/reader/${encodeURIComponent(digest.filename)}`" class="btn btn-sm btn-outline">
              阅读
            </router-link>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>暂无生成的摘要内容</p>
        <button @click="runRssFlow" class="btn btn-primary" :disabled="isProcessing">
          立即获取内容
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const isProcessing = ref(false)
const stats = ref({
  feedCount: 0,
  articleCount: 0,
  lastUpdate: '无数据'
})
const recentDigests = ref([])

onMounted(async () => {
  await loadStats()
  await loadRecentDigests()
})

async function loadStats() {
  try {
    // 这里将来会从后端API获取数据
    // 目前使用模拟数据
    stats.value = {
      feedCount: 7,
      articleCount: 140,
      lastUpdate: new Date().toLocaleDateString()
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

async function loadRecentDigests() {
  try {
    // 从output目录读取文件列表
    const response = await axios.get('/api/digests/recent')
    recentDigests.value = response.data || []
  } catch (error) {
    console.error('加载最近摘要失败:', error)
    // 使用模拟数据
    recentDigests.value = [
      { filename: 'RSS_Digest_2025-03-30.md', title: 'RSS信息聚合', date: '2025-03-30' },
      { filename: 'NYT_>_World_News_2025-03-30.md', title: 'NYT > World News', date: '2025-03-30' },
      { filename: 'BBC_News_2025-03-30.md', title: 'BBC News', date: '2025-03-30' }
    ]
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
}

.hero .btn {
  padding: 0.75rem 1.5rem;
  font-size: 1.1rem;
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
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>