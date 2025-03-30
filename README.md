# InfoDigest - RSS内容聚合与摘要系统

## 团队信息

- 项目Github仓库：[InfoDigest](https://github.com/BH3GEI/InfoDigest)
- Contributor: BH3GEI(李尧)

## 项目简介

InfoDigest是一个基于MOFA框架的RSS聚合与摘要工具，能自动获取RSS源内容，利用大语言模型生成摘要，并将处理后的内容导出为Markdown文件。系统采用数据流驱动设计，通过三个主要组件完成从RSS获取到内容分发的全流程。

### 核心功能

- 🔍 **RSS内容获取**
  - 支持多RSS源订阅
  - 网页内容自动提取
  - 错误重试与容错机制

- 🤖 **内容智能处理**
  - 基于大语言模型的摘要生成
  - 批量处理多文章
  - 支持多种LLM提供商(OpenAI/Google)

- 📨 **灵活输出方式**
  - Markdown格式输出
  - 日报生成与智能总结
  - 多源内容合并与分类

## 安装和运行说明

### 环境依赖

1. Python 3.8+
2. 依赖库：requests, feedparser, beautifulsoup4, pyyaml, crewai

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/BH3GEI/InfoDigest.git
cd InfoDigest
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置设置
```bash
# 编辑configs/rss_agent.yml文件，添加您的RSS源和API密钥
```

### 运行程序

1. 启动全流程
```bash
python start.py
```

2. 或者运行特定节点
```bash
python scripts/rssflow.py --node rss-operator
```

## 创新点和突破点

1. **数据流驱动的组件化设计**
   - 基于MOFA框架的数据流设计，使各组件间解耦
   - 每个组件可独立运行和测试，便于开发和维护

2. **灵活的LLM集成方式**
   - 支持多种LLM提供商(OpenAI/Google Gemini)
   - API调用错误重试机制
   - 批量处理优化，减少API请求次数

3. **多样化输出格式**
   - 支持单源和多源合并输出
   - 智能日报生成
   - 文章智能分类

## 技术难点和解决方案

1. **RSS源内容获取挑战**
   - **难点**：不同RSS源格式差异大，部分源不提供完整内容
   - **解决方案**：实现网页内容提取和错误重试机制，对各种HTML结构进行智能解析

2. **大规模内容处理效率**
   - **难点**：单独处理每篇文章API调用成本高
   - **解决方案**：实现批量处理机制，减少API调用次数并提高处理效率

3. **内容智能分类**
   - **难点**：需要对内容进行语义理解而非简单关键词匹配
   - **解决方案**：利用LLM进行内容分类，实现更智能的主题聚合

## 运行案例

### 案例1：多源RSS日报生成

系统能够获取多个RSS源，将不同内容进行聚合，并生成一份每日摘要，帮助用户快速了解主要信息。输出为结构化的Markdown文件，包含各源内容摘要和智能归纳的"今日概览"部分。

### 案例2：单源内容摘要

系统可以获取单个RSS源的内容，为每篇文章生成摘要，并输出为独立的Markdown文件。这些摘要保留原文重要信息，但大大减少了阅读时间，便于快速浏览。

### 案例3：多源内容智能分类

系统能够分析多个RSS源的内容，根据主题自动对文章进行分类，并按类别组织输出内容。这种智能分类让用户能够按兴趣领域浏览信息，提高信息获取效率。

## 运行效果：
![image](https://github.com/user-attachments/assets/d0563398-8285-4e53-8a71-15de00f5e09f)

![image](https://github.com/user-attachments/assets/f724a7df-3959-4ed9-9db6-d6d0653122c2)

![image](https://github.com/user-attachments/assets/ea84d69a-de3b-4692-a1cb-bd91a4911598)

![image](https://github.com/user-attachments/assets/bf96f49f-d5ad-4e72-826e-e6f05bb33a5b)

![image](https://github.com/user-attachments/assets/5a2ae6d9-3e46-48db-a9a2-6f3cd13a2857)

![image](https://github.com/user-attachments/assets/dfd3bf84-6237-4bde-92ad-2c32045e1e77)




