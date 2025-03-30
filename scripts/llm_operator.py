#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import requests
import json
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
            'model_provider': 'openai',
            'model_max_tokens': 2048,
            'model_endpoint': ''
        })
    
    def call_gemini_api(self, prompt: str) -> str:
        """调用Google Gemini API
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        api_key = self.model_config.get('model_api_key')
        endpoint = self.model_config.get('model_endpoint')
        
        # 如果endpoint中已包含API key，则不再添加
        if '?key=' not in endpoint:
            endpoint = f"{endpoint}?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(endpoint, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # 检查HTTP错误
            
            result = response.json()
            # 提取生成的文本
            if 'candidates' in result and len(result['candidates']) > 0:
                if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                    for part in result['candidates'][0]['content']['parts']:
                        if 'text' in part:
                            return part['text']
            
            # 如果无法提取文本，返回错误信息
            return "无法从API响应中提取文本"
        except Exception as e:
            print(f"调用Gemini API时出错: {str(e)}")
            return f"API调用失败: {str(e)}"
    
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
            
            # 检查是否使用Google API
            if self.model_config.get('model_provider', '').lower() == 'google':
                summary = self.call_gemini_api(prompt)
            else:
                # 使用原有的CrewAI方式
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
    # 初始化操作器
    operator = LLMOperator(config_path="../configs/rss_agent.yml")
    
    # 模拟RSS数据
    test_data = {
        "feed_title": "测试订阅源",
        "feed_link": "http://example.com",
        "feed_description": "这是一个测试RSS源",
        "items": [
            {
                "title": "测试文章1",
                "link": "http://example.com/1",
                "published": "2024-01-01",
                "content": "这是测试文章1的内容，主要讲述了人工智能在医疗领域的应用前景..."
            },
            {
                "title": "测试文章2",
                "summary": "这是测试文章2的摘要，讨论了区块链技术在金融行业的创新应用..."
            }
        ]
    }
    
    # 生成摘要
    result = operator.generate_summary(test_data)
    print("生成的摘要结果:")
    print(yaml.dump(result, allow_unicode=True, sort_keys=False))

if __name__ == "__main__":
    main()