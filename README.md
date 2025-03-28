# InfoDigest

一个基于 MoFA 框架的智能 RSS 聚合与分发工具，能自动获取、处理和分发您感兴趣的内容。

## 功能特点

- 🔍 **智能内容获取**
  - RSS 源订阅与管理
  - 关键词过滤系统
  - 自定义主题追踪

- 🤖 **AI 内容处理**
  - 自动生成日报/周报
  - 支持自定义模板
  - 多维度内容分析

- 📨 **灵活分发系统**
  - RSS Feed 生成
  - 邮件定时推送
  - 格式化输出

## 项目结构

```plaintext
rssflow/
├── configs/                # 配置文件目录
│   ├── rss_agent.yml      # RSS 抓取配置
│   ├── llm_agent.yml      # LLM 处理配置
│   └── delivery_agent.yml # 分发系统配置
├── scripts/               # Agent 脚本目录
│   ├── rss_operator.py    # RSS 抓取实现
│   ├── llm_operator.py    # 内容处理实现
│   └── delivery_operator.py # 分发系统实现
├── data/                  # 数据目录
│   ├── templates/         # 报告模板
│   └── output/           # 输出内容
└── tests/                # 测试目录
    └── test_agents.py    # Agent 测试用例
```

