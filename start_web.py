#!/usr/bin/env python3
"""
生产环境Web服务启动脚本
适配GitHub Pages和静态部署
"""

import json
import os
import time
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

def check_port(port):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except:
            return False

def find_available_port(start_port=3000, max_attempts=10):
    """查找可用端口"""
    for i in range(max_attempts):
        port = start_port + i
        if check_port(port):
            return port
    return None

def validate_data_file():
    """验证数据文件是否存在和有效"""
    if not os.path.exists("trending_data.json"):
        print("❌ 未找到trending_data.json文件")
        print("💡 请先运行: python trends_crawler_all_in_one.py")
        return False
    
    try:
        with open("trending_data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 验证数据结构
        if not isinstance(data, dict):
            print("❌ 数据格式错误：不是有效的JSON对象")
            return False
        
        required_fields = ['data', 'total_seeds', 'last_updated']
        for field in required_fields:
            if field not in data:
                print(f"❌ 数据格式错误：缺少字段 '{field}'")
                return False
        
        # 显示数据信息
        print(f"✅ 数据文件验证通过")
        print(f"📊 包含 {data['total_seeds']} 个种子词")
        print(f"🕒 最后更新: {data['last_updated']}")
        
        # 检查数据是否过期（超过7天）
        try:
            last_update = datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
            now = datetime.now()
            days_old = (now - last_update).days
            
            if days_old > 7:
                print(f"⚠️  数据已过期 {days_old} 天，建议更新")
                print("💡 运行: python trends_crawler_all_in_one.py")
            elif days_old > 0:
                print(f"📅 数据更新于 {days_old} 天前")
        except:
            print("⚠️  无法解析更新时间")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ 数据文件格式错误：无效的JSON")
        return False
    except Exception as e:
        print(f"❌ 验证数据文件失败: {e}")
        return False

def start_server(start_port=3000):
    """启动HTTP服务器"""
    try:
        # 查找可用端口
        port = find_available_port(start_port)
        if not port:
            print(f"❌ 无法找到可用端口（尝试范围: {start_port}-{start_port+9}）")
            return
        
        if port != start_port:
            print(f"⚠️  端口 {start_port} 已被占用，使用端口 {port}")
        
        # 启动服务器
        httpd = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
        print(f"🚀 HTTP服务器启动成功")
        print(f"📍 本地地址: http://localhost:{port}")
        print(f"📊 数据API: http://localhost:{port}/trending_data.json")
        print(f"🌐 网站界面: http://localhost:{port}/index.html")
        print(f"\n按 Ctrl+C 停止服务器")
        
        # 延迟打开浏览器
        def open_browser():
            time.sleep(2)
            webbrowser.open(f"http://localhost:{port}/index.html")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # 启动服务器（阻塞）
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print(f"\n⏹️  服务器已停止")
        if 'httpd' in locals():
            httpd.shutdown()
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")

def main():
    """主函数"""
    print("🌐 谷歌趋势新词洞察 - Web服务启动")
    print("=" * 50)
    
    # 验证数据文件
    print("\n📊 验证数据文件...")
    if not validate_data_file():
        print("\n💡 生产环境部署说明:")
        print("1. 确保trending_data.json文件存在")
        print("2. 使用GitHub Actions定时运行数据更新")
        print("3. 静态文件部署到GitHub Pages")
        return
    
    # 启动Web服务器（仅用于本地开发）
    print("\n🌐 启动本地开发服务器...")
    print("💡 生产环境请使用GitHub Pages或其他静态托管服务")
    start_server()

if __name__ == "__main__":
    main() 