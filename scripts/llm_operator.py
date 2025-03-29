#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from typing import Dict, List, Any, Optional

from mofa.run.run_agent import run_dspy_or_crewai_agent
from crewai import Agent, Task, Crew, Process

class LLMOperator:
    """LLM操作器，用于生成内容摘要"""
    
    def __init__(self, config_path: str = None):
        """初始化LLM操作器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        
        # 默认LLM配置
        self.model_config = self.config.get('model', {
            'model_api_key': '',
            'model_name': 'gpt-4o-mini',
            'model_max_tokens': 2048
        })
    
    def generate_summary(self, rss_data: Dict[str, Any]) -> Dict[str, Any]:
        """为RSS feed条目生成摘要
        
        Args:
            rss_data: 来自RSS操作器的RSS feed数据
            
        Returns:
            包含原始RSS数据和生成摘要的字典
        """
        # 准备结果结构
        result = {
            'feed_info': {
                'title': rss_data.get('feed_title', '未知订阅源'),
                'link': rss_data.get('feed_link', ''),
                'description': rss_data.get('feed_description', '')
            },
            'items': []
        }
        
        # 处理每个条目
        for item in rss_data.get('items', []):
            # 准备LLM的输入
            content = item.get('content', '') or item.get('summary', '')
            title = item.get('title', 'No Title')
            
            # 创建摘要生成的提示词
            prompt = f"""为以下文章生成简洁的摘要：
            
标题: {title}

内容: {content}

提供2-3句话的摘要，捕捉主要观点。"""
            
            # 创建LLM的代理配置
            agent_config = {
                'agents': [{
                    'name': 'summarizer',
                    'role': '内容摘要器',
                    'goal': '生成简洁且信息丰富的文章摘要',
                    'backstory': '你是一位擅长将复杂信息提炼为清晰、简洁摘要的专家。',
                    'verbose': True,
                    'allow_delegation': False
                }],
                'tasks': [{
                    'description': prompt,
                    'expected_output': '文章的简洁摘要',
                    'agent': 'summarizer',
                    'max_inter': 1,
                    'human_input': False
                }],
                'model': self.model_config,
                'crewai_config': {
                    'memory': False
                }
            }
            
            # 运行LLM代理
            summary = run_dspy_or_crewai_agent(agent_config=agent_config)
            
            # 添加到结果
            processed_item = {
                'title': title,
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'original_content': content,
                'summary': summary
            }
            result['items'].append(processed_item)
        
        return result

    def run_as_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """作为MoFA代理运行
        
        Args:
            inputs: 包含RSS数据的输入参数
            
        Returns:
            包含处理数据和摘要的字典
        """
        rss_data = inputs.get('rss_data', {})
        return self.generate_summary(rss_data)

def main():
    """测试LLM操作器的主函数"""
    # todo: 集成到MoFA框架中
    pass

if __name__ == "__main__":
    main()