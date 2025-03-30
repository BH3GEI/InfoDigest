#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import feedparser
from datetime import datetime
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew, Process

# 添加项目根目录到 Python 路径，以便能够导入同级目录下的 mofa 包
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入 mofa 包中的 run_agent 模块
from mofa.run.run_agent import run_dspy_or_crewai_agent

class RSSOperator:
    """RSS操作器，用于获取和解析RSS订阅源"""
    
    def __init__(self, config_path: str = None):
        """初始化RSS操作器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        
        # 默认RSS配置
        self.rss_config = self.config.get('rss_config', {
            'default_url': 'https://news.google.com/rss',
            'timeout': 30,
            'max_items': 10,
            'user_agent': 'Mozilla/5.0'
        })
    
    def fetch_rss(self, url: Optional[str] = None) -> Dict[str, Any]:
        """从给定URL获取RSS订阅源
        
        Args:
            url: RSS订阅源URL，如果为None，则使用配置中的默认URL
            
        Returns:
            包含RSS订阅源数据的字典
        """
        try:
            url = url or self.rss_config.get('default_url')
            
            if not url:
                raise ValueError("未提供RSS URL且未配置默认URL")
            
            # 配置feedparser
            feedparser.USER_AGENT = self.rss_config.get('user_agent')
            
            # 解析订阅源 - 移除timeout参数
            feed = feedparser.parse(url)
            
            # 检查订阅源是否成功解析
            if hasattr(feed, 'status') and feed.status >= 400:
                raise Exception(f"获取RSS订阅源失败: HTTP状态码 {feed.status}")
            
            if not feed.entries and not hasattr(feed.feed, 'title'):
                raise Exception("无效或空的RSS订阅源")
            
            # 处理订阅源数据
            result = {
                'feed_title': feed.feed.get('title', '未知订阅源'),
                'feed_link': feed.feed.get('link', ''),
                'feed_description': feed.feed.get('description', ''),
                'items': []
            }
            
            # 处理条目
            max_items = min(len(feed.entries), self.rss_config.get('max_items'))
            for i in range(max_items):
                entry = feed.entries[i]
                item = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'content': entry.get('content', [{'value': ''}])[0]['value'] if 'content' in entry else ''
                }
                result['items'].append(item)
        except Exception as e:
            # 记录错误
            print(f"获取RSS订阅源时出错: {str(e)}")
            # 返回最小有效结构
            result = {
                'feed_title': '错误',
                'feed_link': '',
                'feed_description': f'获取RSS订阅源失败: {str(e)}',
                'items': []
            }
        
        return result

    def run_as_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """作为MoFA代理运行
        
        Args:
            inputs: 包含RSS URL的输入参数
            
        Returns:
            包含RSS订阅源数据的字典
        """
        url = inputs.get('rss_url', None)
        return self.fetch_rss(url)

def main():
    """运行RSS操作器的主函数"""
    # 从环境变量获取配置路径或使用默认值
    config_path = os.environ.get('RSS_CONFIG_PATH', '../configs/rss_agent.yml')
    
    # 初始化操作器
    operator = RSSOperator(config_path)
    
    # 从命令行参数获取URL或使用默认值
    url = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 获取RSS订阅源
    result = operator.fetch_rss(url)
    
    # 打印结果
    print(f"订阅源: {result['feed_title']}")
    print(f"条目数: {len(result['items'])}")
    for i, item in enumerate(result['items']):
        print(f"\n--- 条目 {i+1} ---")
        print(f"标题: {item['title']}")
        print(f"链接: {item['link']}")
        print(f"发布时间: {item['published']}")

if __name__ == "__main__":
    main()