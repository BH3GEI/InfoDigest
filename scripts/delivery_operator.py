#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional

from mofa.run.run_agent import run_dspy_or_crewai_agent
from crewai import Agent, Task, Crew, Process

class DeliveryOperator:
    """投递操作器，用于将处理后的内容保存为Markdown文件"""
    
    def __init__(self, config_path: str = None):
        """初始化投递操作器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        
        # 默认投递配置
        self.delivery_config = self.config.get('delivery_config', {
            'output_dir': 'output',
            'file_format': 'markdown',
            'date_format': '%Y-%m-%d'
        })
        
        # 确保输出目录存在
        os.makedirs(self.delivery_config.get('output_dir'), exist_ok=True)
    
    def save_as_markdown(self, processed_data: Dict[str, Any]) -> str:
        """将处理后的数据保存为Markdown文件
        
        Args:
            processed_data: 来自LLM操作器的处理数据
            
        Returns:
            保存文件的路径
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

    def run_as_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """作为MoFA代理运行
        
        Args:
            inputs: 包含处理数据的输入参数
            
        Returns:
            包含投递结果的字典
        """
        processed_data = inputs.get('processed_data', {})
        file_path = self.save_as_markdown(processed_data)
        
        return {
            'status': '成功',
            'file_path': file_path,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """测试投递操作器的主函数"""
    # todo: 集成到MoFA框架中
    pass

if __name__ == "__main__":
    main()