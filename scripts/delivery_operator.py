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
        
        # 生成文件名
        current_date = datetime.now().strftime(self.delivery_config.get('date_format'))
        filename = f"{feed_title.replace(' ', '_')}_{current_date}.md"
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
    
    def save_as_combined_markdown(self, processed_feeds: List[Dict[str, Any]]) -> str:
        """将多个RSS源合并为单个Markdown文件
        
        Args:
            processed_feeds: 多个处理后的数据列表
            
        Returns:
            文件保存路径
        """
        # 生成文件名
        current_date = datetime.now().strftime(self.delivery_config.get('date_format'))
        filename = f"RSS_Digest_{current_date}.md"
        file_path = os.path.join(self.delivery_config.get('output_dir'), filename)
        
        # 生成markdown内容
        markdown_content = f"# RSS信息聚合 - {current_date}\n\n"
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

    def save_as_categorized_markdown(self, processed_feeds: List[Dict[str, Any]]) -> str:
        """按主题智能分类并保存为Markdown
        
        Args:
            processed_feeds: 多个处理后的数据列表
            
        Returns:
            文件保存路径
        """
        # 生成文件名
        current_date = datetime.now().strftime(self.delivery_config.get('date_format'))
        filename = f"智能聚合_{current_date}.md"
        file_path = os.path.join(self.delivery_config.get('output_dir'), filename)
        
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
        
        # 生成markdown内容
        markdown_content = f"# 智能RSS聚合 - {current_date}\n\n"
        
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
    """测试用主函数"""
    # todo: 集成到MoFA框架中
    pass

if __name__ == "__main__":
    main()