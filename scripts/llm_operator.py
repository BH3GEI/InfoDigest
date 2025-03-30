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
    
    # 在 LLMOperator 类中的 call_gemini_api 方法中添加重试和延迟机制
    
    def call_gemini_api(self, prompt: str) -> str:
        """调用Google Gemini API
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        import time
        import random
        
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
        
        # 添加重试机制
        max_retries = 3
        base_delay = 2  # 基础延迟秒数
        
        for retry in range(max_retries + 1):
            try:
                # 添加随机延迟，避免请求过于集中
                if retry > 0:
                    delay = base_delay * (2 ** (retry - 1)) + random.uniform(0, 1)
                    print(f"API请求延迟 {delay:.2f} 秒后重试 ({retry}/{max_retries})...")
                    time.sleep(delay)
                
                response = requests.post(endpoint, headers=headers, data=json.dumps(data))
                
                # 如果遇到速率限制，等待后重试
                if response.status_code == 429:
                    if retry < max_retries:
                        continue
                    else:
                        response.raise_for_status()  # 最后一次重试仍失败，抛出异常
                
                response.raise_for_status()  # 检查其他HTTP错误
                
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
                if retry < max_retries:
                    print(f"调用Gemini API时出错 (尝试 {retry+1}/{max_retries+1}): {str(e)}")
                else:
                    print(f"调用Gemini API失败，已达到最大重试次数: {str(e)}")
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
        
        # 获取所有条目
        items = rss_data.get('items', [])
        
        # 如果没有条目，直接返回
        if not items:
            return result
        
        # 批量处理所有条目
        # 构建批量提示词
        batch_prompt = f"""为以下多篇文章分别生成简洁的摘要，每篇2-3句话，捕捉主要观点。
        
来源: {rss_data.get('feed_title', '未知订阅源')}

        """
        
        # 为每篇文章添加编号和内容
        for i, item in enumerate(items):
            content = item.get('content', '') or item.get('summary', '')
            title = item.get('title', 'No Title')
            
            batch_prompt += f"""--- 文章 {i+1} ---
标题: {title}
内容: {content[:1000]}...（内容已截断）

        """
        
        batch_prompt += """请按以下格式返回每篇文章的摘要:
[文章1]
摘要内容...

[文章2]
摘要内容...

依此类推。确保每篇文章的摘要都有明确的标记。"""
        
        # 检查是否使用Google API
        if self.model_config.get('model_provider', '').lower() == 'google':
            all_summaries = self.call_gemini_api(batch_prompt)
        else:
            # 使用原有的CrewAI方式
            agent_config = {
                'agents': [{
                    'name': 'summarizer',
                    'role': '内容摘要器',
                    'goal': '批量生成简洁且信息丰富的文章摘要',
                    'backstory': '你是一位擅长将复杂信息提炼为清晰、简洁摘要的专家。',
                    'verbose': True,
                    'allow_delegation': False
                }],
                'tasks': [{
                    'description': batch_prompt,
                    'expected_output': '多篇文章的简洁摘要',
                    'agent': 'summarizer',
                    'max_inter': 1,
                    'human_input': False
                }],
                'model': self.model_config,
                'crewai_config': {
                    'memory': False
                }
            }
            all_summaries = run_dspy_or_crewai_agent(agent_config=agent_config)
        
        # 解析返回的摘要
        summaries = self.parse_batch_summaries(all_summaries, len(items))
        
        # 将摘要添加到结果中
        for i, item in enumerate(items):
            summary = summaries.get(i, "无法生成摘要")
            processed_item = {
                'title': item.get('title', 'No Title'),
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'original_content': item.get('content', '') or item.get('summary', ''),
                'summary': summary
            }
            result['items'].append(processed_item)
        
        return result
    
    def parse_batch_summaries(self, all_summaries: str, num_items: int) -> Dict[int, str]:
        """解析批量生成的摘要
        
        Args:
            all_summaries: LLM返回的所有摘要文本
            num_items: 原始条目数量
            
        Returns:
            索引到摘要的映射字典
        """
        summaries = {}
        
        # 尝试使用正则表达式匹配 [文章X] 格式
        import re
        pattern = r'\[文章(\d+)\](.*?)(?=\[文章\d+\]|$)'
        matches = re.findall(pattern, all_summaries, re.DOTALL)
        
        if matches:
            for match in matches:
                try:
                    index = int(match[0]) - 1  # 转换为0基索引
                    if 0 <= index < num_items:
                        summaries[index] = match[1].strip()
                except ValueError:
                    continue
        
        # 如果正则匹配失败，尝试简单的分割方法
        if not summaries:
            parts = all_summaries.split('[文章')
            for i, part in enumerate(parts[1:], 0):  # 跳过第一个空元素
                if i < num_items:
                    # 提取数字后的内容
                    content = part.split(']', 1)
                    if len(content) > 1:
                        summaries[i] = content[1].strip()
        
        # 确保所有条目都有摘要
        for i in range(num_items):
            if i not in summaries:
                # 尝试从文本中提取可能的摘要
                summaries[i] = "无法解析摘要"
        
        return summaries
    
    # 修改LLMOperator类的run_as_agent和generate_summary方法
    
    def run_as_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """作为MoFA代理运行
        
        Args:
            inputs: 包含RSS数据的输入参数
            
        Returns:
            包含处理数据和摘要的字典
        """
        rss_data = inputs.get('rss_data', {})
        feeds = rss_data.get('feeds', [])
        
        # 处理每个feed
        processed_feeds = []
        for feed in feeds:
            processed_feed = self.generate_summary(feed)
            processed_feeds.append(processed_feed)
        
        return {'processed_feeds': processed_feeds}

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
