#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew, Process

# 添加项目根目录到Python路径，确保能导入同级目录的模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入run_agent模块
from mofa.run.run_agent import run_dspy_or_crewai_agent

# 修改RSSOperator类，添加fetch_multiple_rss方法

class RSSOperator:
    """RSS订阅源获取与解析工具"""
    
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
            'user_agent': 'Mozilla/5.0',
            'fetch_full_content': True,
            'content_min_length': 500
        })
    
    def fetch_full_content(self, url: str) -> tuple[str, str]:
        """获取文章完整内容
        
        Args:
            url: 文章链接
            
        Returns:
            tuple: (文章全文, 错误信息)
        """
        error_msg = ""
        try:
            headers = {'User-Agent': self.rss_config.get('user_agent')}
            
            # 添加重试机制
            max_retries = self.rss_config.get('max_retries', 2)
            retry_count = 0
            
            while retry_count <= max_retries:
                try:
                    response = requests.get(url, headers=headers, timeout=self.rss_config.get('timeout'))
                    response.raise_for_status()
                    break  # 获取成功，跳出循环
                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        raise  # 重试次数用完，抛出异常
                    print(f"获取文章重试 ({retry_count}/{max_retries}): {url}")
                    time.sleep(1)  # 重试前等待1秒
            
            # 解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 清理页面中的脚本和样式
            for script in soup(["script", "style"]):
                script.extract()
            
            # 尝试定位文章主体
            # 根据常见网站结构选择合适的选择器
            content_selectors = [
                'article', '.article', '.post', '.content', '.entry-content',
                '#content', '#main-content', '.post-content', '.article-content',
                '.blog-post', '.markdown-body', '.post-body', '.entry', '.blog-entry'
            ]
            
            content = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    content = content_element.get_text(strip=True)
                    break
            
            # 找不到特定容器时使用body内容
            if not content:
                content = soup.body.get_text(strip=True)
            
            # 整理文本格式
            content = ' '.join(content.split())
            
            # 验证内容有效性
            if len(content.split()) < 10:
                error_msg = "提取的内容过短，可能不是有效文章"
                return "", error_msg
            
            return content, ""
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP错误: {e}"
        except requests.exceptions.ConnectionError as e:
            error_msg = f"连接错误: {e}"
        except requests.exceptions.Timeout as e:
            error_msg = f"请求超时: {e}"
        except requests.exceptions.RequestException as e:
            error_msg = f"请求错误: {e}"
        except Exception as e:
            error_msg = f"未知错误: {e}"
        
        print(f"获取文章全文失败: {error_msg}")
        return "", error_msg
    
    def fetch_multiple_rss(self) -> List[Dict[str, Any]]:
        """获取多个RSS源的内容
        
        Returns:
            包含RSS数据的字典列表
        """
        results = []
        
        # 获取配置的URL列表
        urls = self.rss_config.get('urls', [])
        
        # 无配置URLs时使用默认URL
        if not urls:
            default_url = self.rss_config.get('default_url')
            if default_url:
                result = self.fetch_rss(default_url)
                results.append(result)
            return results
        
        # 处理每个配置的URL
        for feed_config in urls:
            url = feed_config.get('url')
            name = feed_config.get('name', 'Unknown Feed')
            
            try:
                result = self.fetch_rss(url)
                # 获取失败时使用配置名称
                if result.get('feed_title') == 'Error':
                    result['feed_title'] = f"{name} (获取失败)"
                results.append(result)
            except Exception as e:
                print(f"获取RSS源 {name} 失败: {str(e)}")
                # 添加错误结果
                results.append({
                    'feed_title': f"{name} (获取失败)",
                    'feed_link': url or '',
                    'feed_description': f'RSS源获取失败: {str(e)}',
                    'items': []
                })
        
        return results
    
    def fetch_rss(self, url: Optional[str] = None) -> Dict[str, Any]:
        """获取指定URL的RSS内容
        
        Args:
            url: RSS源URL，为空时使用配置中的默认URL
            
        Returns:
            包含RSS数据的字典
        """
        try:
            url = url or self.rss_config.get('default_url')
            
            if not url:
                raise ValueError("未提供RSS URL且无默认URL配置")
            
            # 设置feedparser
            feedparser.USER_AGENT = self.rss_config.get('user_agent')
            
            # 解析RSS源
            feed = feedparser.parse(url)
            
            # 检查解析结果
            if hasattr(feed, 'status') and feed.status >= 400:
                raise Exception(f"RSS源获取失败: HTTP状态 {feed.status}")
            
            if not feed.entries and not hasattr(feed.feed, 'title'):
                raise Exception("无效或空的RSS源")
            
            # 整理源数据
            result = {
                'feed_title': feed.feed.get('title', '未知源'),
                'feed_link': feed.feed.get('link', ''),
                'feed_description': feed.feed.get('description', ''),
                'items': []
            }
            
            # 处理文章条目
            max_items = min(len(feed.entries), self.rss_config.get('max_items'))
            for i in range(max_items):
                entry = feed.entries[i]
                
                # 提取现有内容
                content = entry.get('content', [{'value': ''}])[0]['value'] if 'content' in entry else ''
                if not content:
                    content = entry.get('summary', '')
                
                # 判断是否需要获取全文
                fetch_full = self.rss_config.get('fetch_full_content', False)
                content_min_length = self.rss_config.get('content_min_length', 500)
                
                # 保存原始内容用于比较
                original_content = content
                
                # 内容过短且配置了全文获取时尝试抓取
                if fetch_full and len(content) < content_min_length and entry.get('link'):
                    print(f"获取全文: {entry.get('title')}")
                    full_content, error = self.fetch_full_content(entry.get('link'))
                    
                    # 仅在获取成功且内容更丰富时替换
                    if full_content and len(full_content) > len(original_content):
                        content = full_content
                        print(f"  - 全文获取成功 ({len(content)} 字符)")
                    else:
                        # 保留原始内容
                        if error:
                            print(f"  - 使用原始内容: {error}")
                        else:
                            print(f"  - 使用原始内容: 抓取内容不比原内容更丰富")
                
                item = {
                    'title': entry.get('title', '无标题'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'content': content,
                    'content_source': 'full_text' if content != original_content else 'rss_feed'
                }
                result['items'].append(item)
        except Exception as e:
            # 记录错误
            print(f"RSS源获取出错: {str(e)}")
            # 返回基本结构
            result = {
                'feed_title': '错误',
                'feed_link': '',
                'feed_description': f'RSS源获取失败: {str(e)}',
                'items': []
            }
        
        return result

    def run_as_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """作为MoFA代理运行
        
        Args:
            inputs: 包含RSS URL的输入参数
            
        Returns:
            包含RSS数据的字典
        """
        # 检查是否指定了单个URL
        url = inputs.get('rss_url', None)
        if url:
            return {'feeds': [self.fetch_rss(url)]}
        
        # 否则获取所有配置的URLs
        return {'feeds': self.fetch_multiple_rss()}

def main():
    """RSS操作器主函数"""
    # 获取配置路径
    config_path = os.environ.get('RSS_CONFIG_PATH', '../configs/rss_agent.yml')
    
    # 初始化操作器
    operator = RSSOperator(config_path)
    
    # 获取URL参数
    url = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 获取RSS数据
    result = operator.fetch_rss(url)
    
    # 输出结果
    print(f"订阅源: {result['feed_title']}")
    print(f"条目数: {len(result['items'])}")
    for i, item in enumerate(result['items']):
        print(f"\n--- 条目 {i+1} ---")
        print(f"标题: {item['title']}")
        print(f"链接: {item['link']}")
        print(f"发布时间: {item['published']}")

if __name__ == "__main__":
    main()