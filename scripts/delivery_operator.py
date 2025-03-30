#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from mofa.run.run_agent import run_dspy_or_crewai_agent
from crewai import Agent, Task, Crew, Process

class DeliveryOperator:
    """负责将处理后的内容导出为Markdown文件"""
    
    def __init__(self, config_path: str = None):
        """初始化
        
        Args:
            config_path: 配置文件路径
        """
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        
        # 默认配置
        self.delivery_config = self.config.get('delivery_config', {
            'output_dir': 'output',
            'file_format': 'markdown',
            'date_format': '%Y-%m-%d'
        })
        
        # 确保输出目录存在
        os.makedirs(self.delivery_config.get('output_dir'), exist_ok=True)
    
    def save_as_markdown(self, processed_data: Dict[str, Any]) -> str:
        """保存为单个Markdown文件
        
        Args:
            processed_data: 处理后的数据
            
        Returns:
            文件保存路径
        """
        # 获取feed信息
        feed_info = processed_data.get('feed_info', {})
        feed_title = feed_info.get('title', '未知订阅源')
        
        # 生成文件名，添加时间戳以避免覆盖
        current_date = datetime.now().strftime(self.delivery_config.get('date_format'))
        current_time = datetime.now().strftime('%H%M')  # 添加小时和分钟
        filename = f"{feed_title.replace(' ', '_')}_{current_date}_{current_time}.md"
        file_path = os.path.join(self.delivery_config.get('output_dir'), filename)
        
        # 生成markdown内容
        markdown_content = f"# {feed_title} - {current_date}\n\n"
        markdown_content += f"来源: [{feed_info.get('title')}]({feed_info.get('link')})\n\n"
        markdown_content += f"## 摘要\n\n"
        
        # 添加条目
        for i, item in enumerate(processed_data.get('items', [])):
            markdown_content += f"### {i+1}. {item.get('title')}\n\n"
            markdown_content += f"**发布时间:** {item.get('published')}\n\n"
            markdown_content += f"**摘要:** {item.get('summary')}\n\n"
            markdown_content += f"**链接:** [{item.get('title')}]({item.get('link')})\n\n"
            markdown_content += "---\n\n"
        
        # 添加页脚
        markdown_content += f"\n*由InfoDigest生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return file_path
    
    def _generate_daily_summary(self, processed_feeds: List[Dict[str, Any]]) -> str:
        """生成每日总结
        
        Args:
            processed_feeds: 多个处理后的数据列表
            
        Returns:
            生成的日报总结文本
        """
        # 收集所有文章的标题和摘要
        all_items = []
        for feed in processed_feeds:
            feed_info = feed.get('feed_info', {})
            feed_title = feed_info.get('title', '未知订阅源')
            
            for item in feed.get('items', []):
                all_items.append({
                    'title': item.get('title', ''),
                    'source': feed_title,
                    'summary': item.get('summary', '')
                })
        
        # 构建提示词
        current_date = datetime.now().strftime('%Y年%m月%d日')
        weekday = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][datetime.now().weekday()]
        
        prompt = f"""你是一位专业的编辑，需要为用户生成一份简明扼要的RSS摘要日报。

今天是{current_date}，{weekday}。请创建一个精炼的信息摘要，类似于一篇学术论文的摘要或执行概要。

要求：
1. 简短明了，约300-400字
2. 以客观、中立的语气呈现信息
3. 重点突出今日最重要的2-3条新闻
4. 使用精准、专业的语言，避免口语和冗余表达
5. 结构清晰，段落分明
6. 不要加入个人见解或评论

以下是今天的RSS文章内容:
"""
        
        # 添加文章信息
        for i, item in enumerate(all_items):
            prompt += f"""
{i+1}. 标题: {item['title']}
   来源: {item['source']}
   摘要: {item['summary']}
"""
        
        # 调用LLM API
        if self.config.get('model', {}).get('model_provider', '').lower() == 'google':
            # 导入必要模块
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from llm_operator import LLMOperator
            
            llm = LLMOperator(config_path=None)
            llm.model_config = self.config.get('model', {})
            summary = llm.call_gemini_api(prompt)
        else:
            # 使用CrewAI方式
            agent_config = {
                'agents': [{
                    'name': 'daily_summarizer',
                    'role': '专业摘要编辑',
                    'goal': '生成一篇简明扼要的RSS日报摘要',
                    'backstory': '你是一位擅长总结复杂信息并提炼关键点的专业编辑，能够以精炼、客观的语言呈现信息精华。',
                    'verbose': True,
                    'allow_delegation': False
                }],
                'tasks': [{
                    'description': prompt,
                    'expected_output': '一篇简明扼要的日报摘要，包含今日最重要的信息要点',
                    'agent': 'daily_summarizer',
                    'max_inter': 1,
                    'human_input': False
                }],
                'model': self.config.get('model', {}),
                'crewai_config': {
                    'memory': False
                }
            }
            from mofa.run.run_agent import run_dspy_or_crewai_agent
            summary = run_dspy_or_crewai_agent(agent_config=agent_config)
        
        return summary
    
    def save_as_combined_markdown(self, processed_feeds: List[Dict[str, Any]]) -> str:
        """将多个RSS源合并为单个Markdown文件，提供信息摘要
        
        Args:
            processed_feeds: 多个处理后的数据列表
            
        Returns:
            文件保存路径
        """
        # 生成文件名，添加时间戳以避免覆盖
        current_date = datetime.now().strftime(self.delivery_config.get('date_format'))
        current_time = datetime.now().strftime('%H%M')  # 添加小时和分钟
        filename = f"RSS_Digest_{current_date}_{current_time}.md"
        file_path = os.path.join(self.delivery_config.get('output_dir'), filename)
        
        # 生成markdown内容
        markdown_content = f"# RSS信息聚合 - {current_date}\n\n"
        
        # 添加日报总结
        daily_summary = self._generate_daily_summary(processed_feeds)
        markdown_content += f"## 今日概览\n\n{daily_summary}\n\n---\n\n"
        
        # 添加目录
        markdown_content += f"## 目录\n\n"
        
        # 生成目录
        for i, feed in enumerate(processed_feeds):
            feed_info = feed.get('feed_info', {})
            feed_title = feed_info.get('title', '未知订阅源')
            markdown_content += f"{i+1}. [{feed_title}](#feed-{i+1})\n"
        
        markdown_content += "\n---\n\n"
        
        # 添加每个feed的内容
        for i, feed in enumerate(processed_feeds):
            feed_info = feed.get('feed_info', {})
            feed_title = feed_info.get('title', '未知订阅源')
            feed_link = feed_info.get('link', '')
            
            markdown_content += f"<a id='feed-{i+1}'></a>\n"
            markdown_content += f"## {i+1}. {feed_title}\n\n"
            markdown_content += f"来源: [{feed_title}]({feed_link})\n\n"
            
            # 添加条目
            for j, item in enumerate(feed.get('items', [])):
                markdown_content += f"### {j+1}. {item.get('title')}\n\n"
                markdown_content += f"**发布时间:** {item.get('published')}\n\n"
                markdown_content += f"**摘要:** {item.get('summary')}\n\n"
                markdown_content += f"**链接:** [{item.get('title')}]({item.get('link')})\n\n"
                markdown_content += "---\n\n"
        
        # 添加页脚
        markdown_content += f"\n*由InfoDigest生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return file_path

    def _generate_smart_analysis(self, processed_feeds: List[Dict[str, Any]]) -> str:
        """生成智能深度分析
        
        Args:
            processed_feeds: 多个处理后的数据列表
            
        Returns:
            生成的智能深度分析文本
        """
        # 收集所有文章的标题和摘要
        all_items = []
        for feed in processed_feeds:
            feed_info = feed.get('feed_info', {})
            feed_title = feed_info.get('title', '未知订阅源')
            
            for item in feed.get('items', []):
                all_items.append({
                    'title': item.get('title', ''),
                    'source': feed_title,
                    'summary': item.get('summary', '')
                })
        
        # 构建提示词
        current_date = datetime.now().strftime('%Y年%m月%d日')
        weekday = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][datetime.now().weekday()]
        
        prompt = f"""你是一位经验丰富的媒体分析师和评论家，需要为用户提供一份深度新闻分析。

今天是{current_date}，{weekday}。请以友好的语气向用户问好，并创建一份有深度的新闻分析。

要求：
1. 篇幅适中，约600-800字
2. 提供背景信息和上下文，帮助用户更好地理解新闻事件
3. 分析新闻之间的关联性和潜在影响
4. 提供有见地的评论和独特视角
5. 识别出潜在的重要趋势和发展方向
6. 语言生动活泼，富有吸引力
7. 在客观事实的基础上加入适度的分析和见解

以下是今天的RSS文章内容:
"""
        
        # 添加文章信息
        for i, item in enumerate(all_items):
            prompt += f"""
{i+1}. 标题: {item['title']}
   来源: {item['source']}
   摘要: {item['summary']}
"""
        
        # 调用LLM API
        if self.config.get('model', {}).get('model_provider', '').lower() == 'google':
            # 导入必要模块
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from llm_operator import LLMOperator
            
            llm = LLMOperator(config_path=None)
            llm.model_config = self.config.get('model', {})
            analysis = llm.call_gemini_api(prompt)
        else:
            # 使用CrewAI方式
            agent_config = {
                'agents': [{
                    'name': 'news_analyst',
                    'role': '媒体分析师',
                    'goal': '提供有深度和见解的新闻分析',
                    'backstory': '你是一位经验丰富的媒体分析师和评论家，擅长发现新闻背后的故事和趋势，并提供有价值的见解。',
                    'verbose': True,
                    'allow_delegation': False
                }],
                'tasks': [{
                    'description': prompt,
                    'expected_output': '一篇深度的新闻分析文章，包含背景信息、关联性分析和独特见解',
                    'agent': 'news_analyst',
                    'max_inter': 1,
                    'human_input': False
                }],
                'model': self.config.get('model', {}),
                'crewai_config': {
                    'memory': False
                }
            }
            from mofa.run.run_agent import run_dspy_or_crewai_agent
            analysis = run_dspy_or_crewai_agent(agent_config=agent_config)
        
        return analysis

    def save_as_categorized_markdown(self, processed_feeds: List[Dict[str, Any]]) -> str:
        """按主题智能分类并保存为Markdown，提供深度分析
        
        Args:
            processed_feeds: 多个处理后的数据列表
            
        Returns:
            文件保存路径
        """
        # 生成文件名，添加时间戳以避免覆盖
        current_date = datetime.now().strftime(self.delivery_config.get('date_format'))
        current_time = datetime.now().strftime('%H%M')  # 添加小时和分钟
        filename = f"智能聚合_{current_date}_{current_time}.md"
        file_path = os.path.join(self.delivery_config.get('output_dir'), filename)
        
        # 生成markdown内容
        markdown_content = f"# 智能RSS聚合 - {current_date}\n\n"
        
        # 添加智能深度分析
        daily_analysis = self._generate_smart_analysis(processed_feeds)
        markdown_content += f"## 今日概览\n\n{daily_analysis}\n\n---\n\n"
        
        # 准备所有文章条目
        all_items = []
        for feed in processed_feeds:
            feed_info = feed.get('feed_info', {})
            feed_title = feed_info.get('title', '未知订阅源')
            
            for item in feed.get('items', []):
                all_items.append({
                    'title': item.get('title', ''),
                    'source': feed_title,
                    'published': item.get('published', ''),
                    'summary': item.get('summary', ''),
                    'link': item.get('link', ''),
                    'content': item.get('original_content', '')
                })
        
        # 使用LLM进行智能分类
        categories = self._categorize_items(all_items)
        
        # 添加目录
        markdown_content += "## 目录\n\n"
        for category, items in categories.items():
            markdown_content += f"- [{category}](#category-{self._slugify(category)})\n"
        
        markdown_content += "\n---\n\n"
        
        # 添加分类内容
        for category, items in categories.items():
            markdown_content += f"<a id='category-{self._slugify(category)}'></a>\n"
            markdown_content += f"## {category}\n\n"
            
            for item in items:
                markdown_content += f"### {item['title']}\n\n"
                markdown_content += f"**来源:** {item['source']}\n\n"
                markdown_content += f"**发布时间:** {item['published']}\n\n"
                markdown_content += f"**摘要:** {item['summary']}\n\n"
                markdown_content += f"**链接:** [{item['title']}]({item['link']})\n\n"
                markdown_content += "---\n\n"
        
        # 添加页脚
        markdown_content += f"\n*由InfoDigest智能分类生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return file_path

    def _slugify(self, text: str) -> str:
        """转换文本为URL友好格式"""
        return text.lower().replace(' ', '-')

    def _categorize_items(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """用LLM对文章进行智能分类
        
        Args:
            items: 文章条目列表
            
        Returns:
            按类别组织的文章字典
        """
        # 准备LLM的输入
        titles_and_summaries = []
        for item in items:
            titles_and_summaries.append(f"标题: {item['title']}\n摘要: {item['summary']}")
        
        all_content = "\n\n".join(titles_and_summaries)
        
        prompt = f"""请分析以下文章的标题和摘要，将它们分类到4-7个有意义的类别中。
        每个类别应该有一个简短、描述性的名称。
        
        文章内容:
        {all_content}
        
        请以JSON格式返回结果，格式如下:
        {{
            "类别1": [0, 2, 5],  // 文章索引，从0开始
            "类别2": [1, 3, 4],
            ...
        }}
        
        只返回JSON格式的结果，不要有其他解释。"""
        
        # 调用LLM API
        if self.config.get('model', {}).get('model_provider', '').lower() == 'google':
            # 导入必要模块
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from llm_operator import LLMOperator
            
            llm = LLMOperator(config_path=None)
            llm.model_config = self.config.get('model', {})
            response = llm.call_gemini_api(prompt)
        else:
            # 使用CrewAI方式
            agent_config = {
                'agents': [{
                    'name': 'categorizer',
                    'role': '内容分类专家',
                    'goal': '将文章智能分类到合适的类别中',
                    'backstory': '你是一位擅长分析内容并进行智能分类的专家。',
                    'verbose': True,
                    'allow_delegation': False
                }],
                'tasks': [{
                    'description': prompt,
                    'expected_output': 'JSON格式的分类结果',
                    'agent': 'categorizer',
                    'max_inter': 1,
                    'human_input': False
                }],
                'model': self.config.get('model', {}),
                'crewai_config': {
                    'memory': False
                }
            }
            from mofa.run.run_agent import run_dspy_or_crewai_agent
            response = run_dspy_or_crewai_agent(agent_config=agent_config)
        
        # 解析JSON响应
        try:
            # 提取JSON部分
            import re
            json_match = re.search(r'({.*})', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            categories_map = json.loads(response)
            
            # 根据分类结果组织文章
            categorized_items = {}
            for category, indices in categories_map.items():
                categorized_items[category] = [items[idx] for idx in indices if idx < len(items)]
            
            return categorized_items
        except Exception as e:
            print(f"解析分类结果出错: {str(e)}")
            # 解析失败时使用默认分类
            return {"所有文章": items}

    def run_as_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """作为MoFA代理运行
        
        Args:
            inputs: 包含处理数据的输入
            
        Returns:
            投递结果字典
        """
        processed_feeds = inputs.get('processed_feeds', [])
        results = []
        
        # 为每个feed生成单独的文件
        for processed_data in processed_feeds:
            file_path = self.save_as_markdown(processed_data)
            results.append({
                'status': '成功',
                'file_path': file_path,
                'feed_title': processed_data.get('feed_info', {}).get('title', '未知订阅源'),
                'timestamp': datetime.now().isoformat()
            })
        
        # 生成智能分类的整合文件
        categorized_file_path = self.save_as_categorized_markdown(processed_feeds)
        
        # 生成常规整合文件
        combined_file_path = self.save_as_combined_markdown(processed_feeds)
        
        return {
            'status': '成功',
            'individual_results': results,
            'categorized_file': categorized_file_path,
            'combined_file': combined_file_path,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """测试用"""
    pass

if __name__ == "__main__":
    main()