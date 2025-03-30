<template>
  <div class="subscriptions-view">
    <div class="page-header">
      <h1>订阅管理</h1>
      <button @click="showAddModal = true" class="btn btn-primary">
        <span class="mdi mdi-plus"></span> 添加订阅源
      </button>
    </div>

    <div class="card">
      <div class="subscription-list">
        <div v-if="subscriptions.length === 0" class="empty-state">
          <p>暂无订阅源</p>
          <button @click="showAddModal = true" class="btn btn-primary">添加第一个订阅源</button>
        </div>
        <table v-else class="subscription-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>URL</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(subscription, index) in subscriptions" :key="index">
              <td>{{ subscription.name }}</td>
              <td class="url-cell">
                <div class="url-wrapper">
                  {{ subscription.url }}
                </div>
              </td>
              <td>
                <span :class="['status-badge', subscription.active ? 'active' : 'inactive']">
                  {{ subscription.active ? '启用' : '禁用' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="editSubscription(index)" class="btn-icon" title="编辑">
                    <span class="mdi mdi-pencil"></span>
                  </button>
                  <button @click="toggleSubscription(index)" class="btn-icon" :title="subscription.active ? '禁用' : '启用'">
                    <span :class="['mdi', subscription.active ? 'mdi-eye-off-outline' : 'mdi-eye-outline']"></span>
                  </button>
                  <button @click="confirmDelete(index)" class="btn-icon delete" title="删除">
                    <span class="mdi mdi-delete-outline"></span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 添加/编辑订阅源模态框 -->
    <div v-if="showAddModal || showEditModal" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h2>{{ showEditModal ? '编辑订阅源' : '添加订阅源' }}</h2>
          <button @click="closeModals" class="close-btn">
            <span class="mdi mdi-close"></span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="feed-name">名称</label>
            <input 
              type="text" 
              id="feed-name" 
              v-model="currentSubscription.name" 
              placeholder="例如：纽约时报"
              required
            >
          </div>
          <div class="form-group">
            <label for="feed-url">RSS URL</label>
            <input 
              type="url" 
              id="feed-url" 
              v-model="currentSubscription.url" 
              placeholder="https://example.com/feed.xml"
              required
            >
          </div>
          <div class="form-group checkbox-group">
            <input 
              type="checkbox" 
              id="feed-active" 
              v-model="currentSubscription.active"
            >
            <label for="feed-active">启用此订阅源</label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeModals" class="btn btn-secondary">取消</button>
          <button @click="saveSubscription" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>

    <!-- 删除确认模态框 -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-container delete-modal">
        <div class="modal-header">
          <h2>确认删除</h2>
          <button @click="showDeleteModal = false" class="close-btn">
            <span class="mdi mdi-close"></span>
          </button>
        </div>
        <div class="modal-body">
          <p>确定要删除订阅源 <strong>{{ subscriptions[deleteIndex]?.name }}</strong> 吗？</p>
          <p class="warning">此操作无法撤销。</p>
        </div>
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-secondary">取消</button>
          <button @click="deleteSubscription" class="btn btn-accent">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// 状态变量
const subscriptions = ref([])
const showAddModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const currentSubscription = ref({ name: '', url: '', active: true })
const editIndex = ref(-1)
const deleteIndex = ref(-1)

// 生命周期钩子
onMounted(async () => {
  await loadSubscriptions()
})

// 方法
async function loadSubscriptions() {
  try {
    // 从配置文件加载订阅源
    // 实际项目中会从后端API获取
    const response = await axios.get('/api/subscriptions')
    subscriptions.value = response.data || []
  } catch (error) {
    console.error('加载订阅源失败:', error)
    // 使用模拟数据
    subscriptions.value = [
      { name: "Google News", url: "https://news.google.com/rss", active: true },
      { name: "BBC News", url: "http://feeds.bbci.co.uk/news/world/rss.xml", active: true },
      { name: "纽约时报", url: "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", active: true },
      { name: "36氪", url: "https://36kr.com/feed", active: true },
      { name: "少数派", url: "https://sspai.com/feed", active: true },
      { name: "InfoQ", url: "https://www.infoq.cn/feed", active: true },
      { name: "Hacker News", url: "https://news.ycombinator.com/rss", active: true }
    ]
  }
}

async function saveSubscriptions() {
  try {
    // 保存订阅源到配置文件
    await axios.post('/api/subscriptions', subscriptions.value)
  } catch (error) {
    console.error('保存订阅源失败:', error)
    alert('保存订阅源失败，请稍后重试')
  }
}

function editSubscription(index) {
  editIndex.value = index
  currentSubscription.value = { ...subscriptions.value[index] }
  showEditModal.value = true
}

function toggleSubscription(index) {
  subscriptions.value[index].active = !subscriptions.value[index].active
  saveSubscriptions()
}

function confirmDelete(index) {
  deleteIndex.value = index
  showDeleteModal.value = true
}

async function deleteSubscription() {
  if (deleteIndex.value > -1) {
    subscriptions.value.splice(deleteIndex.value, 1)
    await saveSubscriptions()
    showDeleteModal.value = false
  }
}

async function saveSubscription() {
  if (!currentSubscription.value.name || !currentSubscription.value.url) {
    alert('请填写名称和URL')
    return
  }

  if (showEditModal.value && editIndex.value > -1) {
    // 编辑现有订阅源
    subscriptions.value[editIndex.value] = { ...currentSubscription.value }
  } else {
    // 添加新订阅源
    subscriptions.value.push({ ...currentSubscription.value })
  }

  await saveSubscriptions()
  closeModals()
}

function closeModals() {
  showAddModal.value = false
  showEditModal.value = false
  currentSubscription.value = { name: '', url: '', active: true }
  editIndex.value = -1
}
</script>

<style scoped>
.subscriptions-view {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.subscription-table {
  width: 100%;
  border-collapse: collapse;
}

.subscription-table th,
.subscription-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.subscription-table th {
  font-weight: 600;
  color: var(--text-light);
  background-color: #f8f9fa;
}

.url-cell {
  max-width: 300px;
}

.url-wrapper {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.active {
  background-color: rgba(46, 204, 113, 0.2);
  color: var(--success-color);
}

.status-badge.inactive {
  background-color: rgba(149, 165, 166, 0.2);
  color: var(--text-lighter);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  border: none;
  background-color: transparent;
  color: var(--text-light);
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.btn-icon:hover {
  background-color: rgba(52, 152, 219, 0.1);
  color: var(--primary-color);
}

.btn-icon.delete:hover {
  background-color: rgba(231, 76, 60, 0.1);
  color: var(--error-color);
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-light);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.delete-modal {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--text-light);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid var(--border-color);
}

.form-group {
  margin-bottom: 1.5rem;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-group input {
  width: auto;
}

.warning {
  color: var(--error-color);
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .subscription-table {
    display: block;
    overflow-x: auto;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>