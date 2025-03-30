#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import signal
import webbrowser
from threading import Thread

# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))

# 前端和后端目录
frontend_dir = os.path.join(root_dir, 'frontend')
backend_dir = os.path.join(root_dir, 'backend')

# 进程列表
processes = []

def signal_handler(sig, frame):
    """处理终止信号"""
    print('\n正在关闭服务...')
    for process in processes:
        if process.poll() is None:  # 如果进程还在运行
            process.terminate()
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_frontend_dist():
    """检查前端构建文件是否存在，如果不存在则构建"""
    dist_dir = os.path.join(frontend_dir, 'dist')
    if not os.path.exists(dist_dir):
        print('前端构建文件不存在，正在构建...')
        # 安装依赖
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        # 构建前端
        subprocess.run(['npm', 'run', 'build'], cwd=frontend_dir, check=True)
        print('前端构建完成')

def start_backend():
    """启动后端服务"""
    print('正在启动后端服务...')
    backend_process = subprocess.Popen(
        [sys.executable, 'server.py'],
        cwd=backend_dir
    )
    processes.append(backend_process)
    return backend_process

def start_frontend_dev():
    """启动前端开发服务器"""
    print('正在启动前端开发服务器...')
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=frontend_dir
    )
    processes.append(frontend_process)
    return frontend_process

def open_browser(url, delay=2):
    """在浏览器中打开URL"""
    def _open_browser():
        time.sleep(delay)
        print(f'正在浏览器中打开 {url}')
        webbrowser.open(url)
    
    browser_thread = Thread(target=_open_browser)
    browser_thread.daemon = True
    browser_thread.start()

def main():
    """主函数"""
    print('=== InfoDigest 启动脚本 ===')
    
    # 检查命令行参数
    dev_mode = '--dev' in sys.argv
    
    if dev_mode:
        print('以开发模式启动')
        # 启动前端开发服务器
        frontend_process = start_frontend_dev()
        # 启动后端服务
        backend_process = start_backend()
        # 在浏览器中打开前端开发服务器
        open_browser('http://localhost:5173')
    else:
        print('以生产模式启动')
        # 检查并构建前端
        check_frontend_dist()
        # 启动后端服务
        backend_process = start_backend()
        # 在浏览器中打开后端服务
        open_browser('http://localhost:5000')
    
    print('服务已启动，按Ctrl+C停止')
    
    try:
        # 等待后端进程结束
        backend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main()