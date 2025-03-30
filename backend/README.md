# InfoDigest 后端API服务

这是InfoDigest RSS聚合工具的后端API服务，为前端界面提供数据支持，同时与现有的Python脚本无缝集成。

## 功能特点

- 提供RESTful API接口，支持前端界面的所有功能
- 读取和管理RSS订阅源配置
- 运行RSS聚合和摘要生成流程
- 获取和展示生成的Markdown内容
- 管理API密钥、端点和其他配置选项

## 技术栈

- Flask - 轻量级Web框架
- Flask-CORS - 跨域资源共享支持
- PyYAML - YAML文件处理
- Python标准库 - 文件操作、进程管理等

## API端点

### 摘要文件相关

- `GET /api/digests` - 获取所有摘要文件列表
- `GET /api/digests/recent` - 获取最近的摘要文件列表（最多5个）
- `GET /api/digests/<filename>` - 获取特定摘要文件的内容
- `GET /api/digests/<filename>/raw` - 获取特定摘要文件的原始内容（直接下载）

### RSS流程相关

- `POST /api/run-rssflow` - 运行RSS流程，获取最新内容

### 订阅管理相关

- `GET /api/subscriptions` - 获取订阅源列表
- `POST /api/subscriptions` - 保存订阅源列表

### 配置管理相关

- `GET /api/settings` - 获取配置设置
- `POST /api/settings` - 保存配置设置

## 安装与运行

### 前提条件

- Python 3.8+
- pip

### 安装依赖

```bash
pip install flask flask-cors pyyaml
```

### 运行服务

```bash
python server.py
```

服务将在 http://localhost:5000 上运行。

## 与前端集成

后端API服务设计为与前端无缝集成：

1. 前端构建后的静态文件会被服务于根路径 `/`
2. 所有API端点都以 `/api` 开头
3. 所有其他路由都会返回前端应用，支持前端路由

## 与现有Python脚本集成

后端API服务通过以下方式与现有Python脚本集成：

1. 读取和修改相同的配置文件（`configs/rss_agent.yml`）
2. 通过子进程调用现有的RSS流程脚本（`scripts/rssflow.py`）
3. 读取相同的输出目录（`output/`）中的Markdown文件

这种设计确保了前端界面可以与现有的Python逻辑无缝协作，而不需要重新实现任何功能。