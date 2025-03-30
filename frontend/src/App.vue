<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo-container">
        <img src="./assets/logo.svg" alt="InfoDigest Logo" class="logo" />
        <h1>InfoDigest</h1>
      </div>
      <nav class="main-nav">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/subscriptions" class="nav-link">订阅管理</router-link>
        <router-link to="/settings" class="nav-link">配置设置</router-link>
        <router-link to="/reader" class="nav-link">阅读器</router-link>
      </nav>
    </header>

    <main class="app-content">
      <router-view />
    </main>

    <footer class="app-footer">
      <p>InfoDigest &copy; {{ new Date().getFullYear() }} - RSS聚合与摘要工具</p>
    </footer>
  </div>
</template>

<script setup>
// 组件逻辑
</script>

<style>
/* 全局样式 */
:root {
  --primary-color: #3498db;
  --secondary-color: #2c3e50;
  --accent-color: #e74c3c;
  --text-color: #333;
  --light-bg: #f5f7fa;
  --border-color: #ddd;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: var(--text-color);
  background-color: var(--light-bg);
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  height: 40px;
}

.main-nav {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  position: relative;
}

.nav-link:hover {
  color: var(--primary-color);
}

.nav-link.router-link-active {
  color: var(--primary-color);
}

.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-color);
}

.app-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  background-color: var(--secondary-color);
  color: white;
  text-align: center;
  padding: 1rem;
  margin-top: auto;
}
</style>