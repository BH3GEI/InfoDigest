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

# 添加count_items函数定义
def count_items(processed_data: Dict[str, Any]) -> int:
    """计算处理后数据中的条目总数
    
    Args:
        processed_data: 处理后的数据字典
        
    Returns:
        条目总数
    """
    count = 0
    for feed in processed_data.get('processed_feeds', []):
        count += len(feed.get('items', []))
    return count

# 在main函数中，修改打印结果的部分
def main():
    """Main function to run the RSS flow"""
    args = parse_arguments()
    
    print("=== RSSFlow - RSS聚合工具 ===")
    print(f"使用配置: {args.config}")
    print()
    
    # 1. 获取RSS数据
    print("[1/3] 正在获取RSS订阅源...")
    rss_operator = RSSOperator(config_path=args.config)
    
    # 如果命令行指定了URL，则使用该URL
    if args.url:
        rss_data = rss_operator.run_as_agent({'rss_url': args.url})
    else:
        # 否则使用配置文件中的URLs
        rss_data = rss_operator.run_as_agent({})
    
    # 显示获取的RSS源信息
    for feed in rss_data.get('feeds', []):
        print(f"  - 订阅源: {feed.get('feed_title')}")
        print(f"  - 条目数: {len(feed.get('items', []))}")
    print()
    
    # 2. 生成摘要
    print("[2/3] 正在生成摘要...")
    llm_operator = LLMOperator(config_path=args.config)
    processed_data = llm_operator.run_as_agent({'rss_data': rss_data})
    print(f"  - 已处理 {count_items(processed_data)} 个条目")
    
    # 投递处理后的数据
    print("\n[3/3] 正在保存为Markdown...")
    delivery_operator = DeliveryOperator(config_path=args.config)
    delivery_result = delivery_operator.run_as_agent({'processed_feeds': processed_data['processed_feeds']})
    
    # 打印结果信息
    for result in delivery_result.get('individual_results', []):
        print(f"  - 已生成文件: {result['file_path']}")
    
    # 使用get方法安全地获取键值，提供默认值防止KeyError
    if 'combined_file' in delivery_result:
        print(f"  - 已生成整合文件: {delivery_result['combined_file']}")
    
    if 'categorized_file' in delivery_result:
        print(f"  - 已生成智能分类文件: {delivery_result['categorized_file']}")
    
    print("\n处理完成!")
    print("\n完成! 所有RSS源已成功处理并保存。")

if __name__ == "__main__":
    main()