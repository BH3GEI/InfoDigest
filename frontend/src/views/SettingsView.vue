<template>
  <div class="settings-view">
    <div class="page-header">
      <h1>配置设置</h1>
      <div class="header-actions">
        <button @click="saveSettings" class="btn btn-primary" :disabled="isSaving">
          <span v-if="isSaving">保存中...</span>
          <span v-else>保存配置</span>
        </button>
        <button @click="resetSettings" class="btn btn-outline" :disabled="isSaving">
          重置
        </button>
      </div>
    </div>

    <div class="settings-container">
      <!-- 模型配置 -->
      <div class="card settings-card">
        <h2>模型配置</h2>
        <div class="form-group">
          <label for="model-provider">模型提供商</label>
          <select id="model-provider" v-model="settings.model.model_provider">
            <option value="google">Google</option>
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
          </select>
        </div>

        <div class="form-group">
          <label for="model-name">模型名称</label>
          <input 
            type="text" 
            id="model-name" 
            v-model="settings.model.model_name" 
            placeholder="例如：gemini-2.0-flash"
          >
        </div>

        <div class="form-group">
          <label for="model-api-key">API密钥</label>
          <div class="api-key-input">
            <input 
              :type="showApiKey ? 'text' : 'password'" 
              id="model-api-key" 
              v-model="settings.model.model_api_key" 
              placeholder="输入API密钥"
            >
            <button @click="showApiKey = !showApiKey" class="toggle-visibility">
              <span :class="['mdi', showApiKey ? 'mdi-eye-off-outline' : 'mdi-eye-outline']"></span>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="model-endpoint">API端点</label>
          <input 
            type="text" 
            id="model-endpoint" 
            v-model="settings.model.model_endpoint" 
            placeholder="https://api.example.com/v1/completions"
          >
        </div>

        <div class="form-group">
          <label for="model-max-tokens">最大令牌数</label>
          <input 
            type="number" 
            id="model-max-tokens" 
            v-model.number="settings.model.model_max_tokens" 
            min="1"
            max="8192"
          >
        </div>
      </div>

      <!-- RSS配置 -->
      <div class="card settings-card">
        <h2>RSS配置</h2>
        
        <div class="form-group">
          <label for="default-url">默认URL</label>
          <input 
            type="url" 
            id="default-url" 
            v-model="settings.rss_config.default_url" 
            placeholder="https://example.com/feed.xml"
          >
        </div>

        <div class="form-group">
          <label for="timeout">超时时间 (秒)</label>
          <input 
            type="number" 
            id="timeout" 
            v-model.number="settings.rss_config.timeout" 
            min="1"
            max="120"
          >
        </div>

        <div class="form-group">
          <label for="max-items">每个源的最大条目数</label>
          <input 
            type="number" 
            id="max-items" 
            v-model.number="settings.rss_config.max_items" 
            min="1"
            max="100"
          >
        </div>

        <div class="form-group">
          <label for="user-agent">User Agent</label>
          <input 
            type="text" 
            id="user-agent" 
            v-model="settings.rss_config.user_agent" 
            placeholder="Mozilla/5.0..."
          >
        </div>

        <div class="form-group">
          <label for="max-retries">最大重试次数</label>
          <input 
            type="number" 
            id="max-retries" 
            v-model.number="settings.rss_config.max_retries" 
            min="0"
            max="10"
          >
        </div>
      </div>

      <!-- 输出配置 -->
      <div class="card settings-card">
        <h2>输出配置</h2>
        
        <div class="form-group">
          <label for="output-dir">输出目录</label>
          <input 
            type="text" 
            id="output-dir" 
            v-model="settings.delivery_config.output_dir" 
            placeholder="output"
          >
        </div>

        <div class="form-group">
          <label for="file-format">文件格式</label>
          <select id="file-format" v-model="settings.delivery_config.file_format">
            <option value="markdown">Markdown</option>
            <option value="json">JSON</option>
            <option value="html">HTML</option>
          </select>
        </div>

        <div class="form-group">
          <label for="date-format">日期格式</label>
          <input 
            type="text" 
            id="date-format" 
            v-model="settings.delivery_config.date_format" 
            placeholder="%Y-%m-%d"
          >
        </div>

        <div class="form-group checkbox-group">
          <input 
            type="checkbox" 
            id="generate-combined" 
            v-model="settings.delivery_config.generate_combined"
          >
          <label for="generate-combined">生成合并文件</label>
        </div>

        <div class="form-group checkbox-group">
          <input 
            type="checkbox" 
            id="generate-categorized" 
            v-model="settings.delivery_config.generate_categorized"
          >
          <label for="generate-categorized">生成分类文件</label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import yaml from 'js-yaml'

const isSaving = ref(false)
const showApiKey = ref(false)
const settings = ref({
  model: {
    model_api_key: '',
    model_name: 'gemini-2.0-flash',
    model_provider: 'google',
    model_max_tokens: 2048,
    model_endpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
  },
  rss_config: {
    default_url: 'https://news.google.com/rss',
    timeout: 30,
    max_items: 20,
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    max_retries: 2
  },
  delivery_config: {
    output_dir: 'output',
    file_format: 'markdown',
    date_format: '%Y-%m-%d',
    generate_combined: true,
    generate_categorized: true
  }
})

const originalSettings = ref({})

onMounted(async () => {
  await loadSettings()
})

async function loadSettings() {
  try {
    // 从后端API获取配置
    const response = await axios.get('/api/settings')
    settings.value = response.data
    // 保存原始设置用于重置
    originalSettings.value = JSON.parse(JSON.stringify(response.data))
  } catch (error) {
    console.error('加载配置失败:', error)
    // 使用默认配置
  }
}

async function saveSettings() {
  if (isSaving.value) return
  
  isSaving.value = true
  try {
    // 保存配置到后端
    await axios.post('/api/settings', settings.value)
    alert('配置已保存')
    // 更新原始设置
    originalSettings.value = JSON.parse(JSON.stringify(settings.value))
  } catch (error) {
    console.error('保存配置失败:', error)
    alert('保存配置失败，请稍后重试')
  } finally {
    isSaving.value = false
  }
}

function resetSettings() {
  // 重置为原始设置
  settings.value = JSON.parse(JSON.stringify(originalSettings.value))
}
</script>

<style scoped>
.settings-view {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.settings-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.settings-card {
  padding: 1.5rem;
}

.settings-card h2 {
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.form-group {
  margin-bottom: 1.5rem;
}

.api-key-input {
  position: relative;
}

.toggle-visibility {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-group input {
  width: auto;
}

@media (min-width: 768px) {
  .settings-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .settings-card:first-child {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .header-actions .btn {
    flex: 1;
  }
}
</style>