# InfoDigest 前端界面

这是InfoDigest RSS聚合工具的前端界面，提供了订阅管理、配置编辑和Markdown渲染功能。

## 功能特点

- 美观的用户界面，展示RSS摘要内容
- 订阅源管理：添加、编辑、删除RSS订阅源
- 配置管理：编辑API密钥、端点和其他设置
- Markdown渲染：优雅地显示生成的摘要内容
- 与现有Python后端无缝集成

## 技术栈

- Vue.js 3 - 前端框架
- Vite - 构建工具
- Axios - HTTP客户端
- Marked - Markdown解析器
- Highlight.js - 代码高亮
- Flask - 后端API服务器

## 安装与运行

### 前提条件

- Node.js 14+
- Python 3.8+
- pip

### 安装步骤

1. 安装前端依赖：

```bash
cd frontend
npm install
```

2. 安装后端依赖：

```bash
pip install flask flask-cors pyyaml
```

### 运行应用

使用提供的启动脚本运行整个应用：

```bash
python start.py
```

这将启动后端API服务器并构建前端应用。完成后，浏览器会自动打开应用。

如果要以开发模式运行（支持热重载）：

```bash
python start.py --dev
```

## 使用说明

### 首页

首页显示应用概览和最近生成的摘要文件。您可以点击"立即获取最新内容"按钮运行RSS流程，获取最新内容。

### 订阅管理

在订阅管理页面，您可以：
- 查看所有RSS订阅源
- 添加新的订阅源
- 编辑现有订阅源
- 启用/禁用订阅源
- 删除订阅源

### 配置设置

配置设置页面允许您编辑：
- 模型配置（API密钥、模型名称、端点等）
- RSS配置（超时时间、最大条目数等）
- 输出配置（输出目录、文件格式等）

### 阅读器

阅读器页面显示所有生成的摘要文件，您可以：
- 浏览所有摘要文件
- 搜索特定文件
- 按日期或名称排序
- 查看文件内容
- 在新标签页中打开原始文件

## 项目结构

```
frontend/            # 前端代码
  ├── src/            # 源代码
  │   ├── assets/     # 静态资源
  │   ├── components/ # Vue组件
  │   ├── router/     # 路由配置
  │   ├── views/      # 页面视图
  │   ├── App.vue     # 根组件
  │   └── main.js     # 入口文件
  ├── index.html      # HTML模板
  └── vite.config.js  # Vite配置

backend/             # 后端代码
  └── server.py       # Flask API服务器

start.py             # 启动脚本
```

## 注意事项

- 此前端界面不会修改原有的Python逻辑，只是提供了一个更友好的用户界面
- 所有配置仍然存储在原有的YAML文件中
- 前端通过后端API与Python脚本交互，不直接修改文件