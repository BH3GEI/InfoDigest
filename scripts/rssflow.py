#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from typing import Dict, Any, Optional

from rss_operator import RSSOperator
from llm_operator import LLMOperator
from delivery_operator import DeliveryOperator

def parse_arguments():
    """解析命令行参数"""
    # 获取当前脚本的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 相对于脚本目录的默认配置路径
    default_config_path = os.path.join(script_dir, '..', 'configs', 'rss_agent.yml')
    # 相对于项目根目录的默认输出目录
    default_output_dir = os.path.join(script_dir, '..', 'output')
    
    parser = argparse.ArgumentParser(description='RSSFlow - RSS聚合工具')
    parser.add_argument('--url', type=str, help='RSS订阅源URL')
    parser.add_argument('--config', type=str, default=default_config_path, 
                        help='配置文件路径')
    parser.add_argument('--output-dir', type=str, default=default_output_dir,
                        help='生成文件的输出目录')
    return parser.parse_args()

def main():
    """RSSFlow的主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 设置配置路径
    config_path = os.path.abspath(args.config)
    if not os.path.exists(config_path):
        print(f"错误: 在{config_path}找不到配置文件")
        sys.exit(1)
    
    print("=== RSSFlow - RSS聚合工具 ===")
    print(f"使用配置: {config_path}")
    
    # 初始化操作器
    rss_operator = RSSOperator(config_path)
    llm_operator = LLMOperator(config_path)
    delivery_operator = DeliveryOperator(config_path)
    
    # 步骤1: 获取RSS订阅源
    print("\n[1/3] 正在获取RSS订阅源...")
    rss_data = rss_operator.fetch_rss(args.url)
    print(f"  - 订阅源: {rss_data['feed_title']}")
    print(f"  - 条目数: {len(rss_data['items'])}")
    
    # 步骤2: 生成摘要
    print("\n[2/3] 正在生成摘要...")
    processed_data = llm_operator.generate_summary(rss_data)
    print(f"  - 已处理 {len(processed_data['items'])} 个条目")
    
    # 步骤3: 保存为Markdown
    print("\n[3/3] 正在保存为Markdown...")
    delivery_result = delivery_operator.run_as_agent({'processed_data': processed_data})
    print(f"  - 已保存到: {delivery_result['file_path']}")
    
    print("\n=== 处理成功完成 ===")

if __name__ == "__main__":
    main()