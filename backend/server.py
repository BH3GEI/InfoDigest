#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import json
import glob
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS

# 添加项目根目录到Python路径
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

# 配置文件路径
CONFIG_PATH = os.path.join(root_dir, 'configs', 'rss_agent.yml')
# 输出目录路径
OUTPUT_DIR = os.path.join(root_dir, 'output')

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/digests')
def get_digests():
    """获取所有摘要文件列表"""
    try:
        files = glob.glob(os.path.join(OUTPUT_DIR, '*.md'))
        digests = []
        
        for file_path in files:
            filename = os.path.basename(file_path)
            # 从文件名中提取标题和日期
            parts = os.path.splitext(filename)[0].split('_')
            date_part = parts[-1] if len(parts) > 1 else ''
            title_part = ' '.join(parts[:-1]) if len(parts) > 1 else filename
            
            # 处理特殊情况，如NYT_>_World_News
            if '>' in title_part:
                title_part = title_part.replace('_>_', ' > ')
            
            # 替换下划线为空格
            title_part = title_part.replace('_', ' ')
            
            digests.append({
                'filename': filename,
                'title': title_part,
                'date': date_part
            })
        
        # 按日期降序排序
        digests.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(digests)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/digests/recent')
def get_recent_digests():
    """获取最近的摘要文件列表（最多5个）"""
    try:
        files = glob.glob(os.path.join(OUTPUT_DIR, '*.md'))
        digests = []
        
        for file_path in files:
            filename = os.path.basename(file_path)
            # 从文件名中提取标题和日期
            parts = os.path.splitext(filename)[0].split('_')
            date_part = parts[-1] if len(parts) > 1 else ''
            title_part = ' '.join(parts[:-1]) if len(parts) > 1 else filename
            
            # 处理特殊情况
            if '>' in title_part:
                title_part = title_part.replace('_>_', ' > ')
            
            # 替换下划线为空格
            title_part = title_part.replace('_', ' ')
            
            digests.append({
                'filename': filename,
                'title': title_part,
                'date': date_part
            })
        
        # 按日期降序排序并只返回前5个
        digests.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(digests[:5])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/digests/<filename>')
def get_digest_content(filename):
    """获取特定摘要文件的内容"""
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/digests/<filename>/raw')
def get_digest_raw(filename):
    """获取特定摘要文件的原始内容（直接下载）"""
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-rssflow', methods=['POST'])
def run_rssflow():
    """运行RSS流程"""
    try:
        # 运行rssflow.py脚本
        script_path = os.path.join(root_dir, 'scripts', 'rssflow.py')
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=root_dir
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
        
        return jsonify({
            'success': True,
            'output': result.stdout
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subscriptions', methods=['GET'])
def get_subscriptions():
    """获取订阅源列表"""
    try:
        if not os.path.exists(CONFIG_PATH):
            return jsonify([]), 404
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        subscriptions = []
        for feed in config.get('rss_config', {}).get('urls', []):
            subscriptions.append({
                'name': feed.get('name', ''),
                'url': feed.get('url', ''),
                'active': True  # 默认为启用状态
            })
        
        return jsonify(subscriptions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subscriptions', methods=['POST'])
def save_subscriptions():
    """保存订阅源列表"""
    try:
        subscriptions = request.json
        
        if not os.path.exists(CONFIG_PATH):
            return jsonify({'error': '配置文件不存在'}), 404
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 更新订阅源列表
        urls = []
        for sub in subscriptions:
            if sub.get('active', True):  # 只添加启用的订阅源
                urls.append({
                    'name': sub.get('name', ''),
                    'url': sub.get('url', '')
                })
        
        config['rss_config']['urls'] = urls
        
        # 保存配置文件
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """获取配置设置"""
    try:
        if not os.path.exists(CONFIG_PATH):
            return jsonify({'error': '配置文件不存在'}), 404
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 提取需要的配置项
        settings = {
            'model': config.get('model', {}),
            'rss_config': config.get('rss_config', {}),
            'delivery_config': config.get('delivery_config', {})
        }
        
        # 移除urls字段，因为它在订阅管理中单独处理
        if 'urls' in settings['rss_config']:
            del settings['rss_config']['urls']
        
        return jsonify(settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """保存配置设置"""
    try:
        settings = request.json
        
        if not os.path.exists(CONFIG_PATH):
            return jsonify({'error': '配置文件不存在'}), 404
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 更新配置项
        if 'model' in settings:
            config['model'] = settings['model']
        
        if 'rss_config' in settings:
            # 保留原有的urls字段
            urls = config['rss_config'].get('urls', [])
            config['rss_config'] = settings['rss_config']
            config['rss_config']['urls'] = urls
        
        if 'delivery_config' in settings:
            config['delivery_config'] = settings['delivery_config']
        
        # 保存配置文件
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 处理所有其他路由，返回前端应用
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)