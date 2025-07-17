#!/usr/bin/env python3
"""
一键启动Web界面
自动执行数据获取、格式转换和服务器启动
"""

import subprocess
import sys
import json
import glob
import os
import time
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import TCPServer
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

def find_latest_data_file():
    """查找最新的数据文件"""
    pattern = "rising_only_trends_*.json"
    files = glob.glob(pattern)
    
    if not files:
        return None
    
    return max(files, key=os.path.getctime)

def convert_data_format():
    """转换数据格式为HTML期望的格式"""
    latest_file = find_latest_data_file()
    
    if not latest_file:
        print("❌ 未找到数据文件，请先运行数据获取")
        return False
    
    print(f"📄 使用数据文件: {latest_file}")
    
    # 读取原始数据
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取数据文件失败: {e}")
        return False
    
    # 转换为HTML期望的格式
    converted_data = {
        "data": {},
        "total_seeds": source_data.get("summary", {}).get("total_seed_keywords", 0),
        "last_updated": source_data.get("metadata", {}).get("timestamp", datetime.now().isoformat())
    }
    
    # 转换种子关键词数据
    seed_keywords = source_data.get("seed_keywords", {})
    for keyword, data in seed_keywords.items():
        rising_queries = data.get("rising_queries", [])
        
        # 转换每个rising查询的格式
        converted_rising = []
        for query in rising_queries:
            converted_query = {
                "query": query.get("query", ""),
                "value": query.get("growth_rate", 0),
                "link": query.get("link", "")
            }
            converted_rising.append(converted_query)
        
        # 只添加有数据的关键词
        if converted_rising:
            converted_data["data"][keyword] = {
                "rising": converted_rising
            }
    
    # 保存转换后的数据
    try:
        with open("trending_data.json", 'w', encoding='utf-8') as f:
            json.dump(converted_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据格式转换完成")
        print(f"📊 包含 {len(converted_data['data'])} 个有数据的关键词")
        return True
        
    except Exception as e:
        print(f"❌ 保存转换数据失败: {e}")
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
        print(f"📍 地址: http://localhost:{port}")
        print(f"🌐 优化版界面: http://localhost:{port}/waxinci-trends-optimized.html")
        print(f"🌐 原版界面: http://localhost:{port}/waxinci-trends.html")
        print(f"📊 数据API: http://localhost:{port}/trending_data.json")
        print(f"\n按 Ctrl+C 停止服务器")
        
        # 延迟打开浏览器
        def open_browser():
            time.sleep(2)
            webbrowser.open(f"http://localhost:{port}/waxinci-trends-optimized.html")
        
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
    print("🚀 谷歌趋势新词洞察 - 一键启动")
    print("=" * 50)
    
    # 步骤1：检查或获取数据
    print("\n📊 检查数据文件...")
    latest_file = find_latest_data_file()
    
    if not latest_file:
        print("📥 未找到数据文件，开始获取最新数据...")
        try:
            result = subprocess.run([sys.executable, "rising_only_trends.py"], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ 数据获取成功")
            else:
                print(f"❌ 数据获取失败: {result.stderr}")
                return
        except subprocess.TimeoutExpired:
            print("❌ 数据获取超时（5分钟）")
            return
        except Exception as e:
            print(f"❌ 数据获取异常: {e}")
            return
    else:
        # 检查数据文件是否太旧（超过1天）
        file_time = os.path.getctime(latest_file)
        current_time = time.time()
        
        if current_time - file_time > 24 * 3600:  # 24小时
            print(f"⚠️  数据文件较旧 ({latest_file})，建议更新")
            update = input("是否获取最新数据? (y/N): ").lower().strip()
            
            if update == 'y':
                print("📥 获取最新数据...")
                try:
                    result = subprocess.run([sys.executable, "rising_only_trends.py"], 
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        print("✅ 数据更新成功")
                    else:
                        print(f"❌ 数据更新失败: {result.stderr}")
                        print("⚠️  将使用现有数据")
                except Exception as e:
                    print(f"❌ 数据更新异常: {e}")
                    print("⚠️  将使用现有数据")
        else:
            print(f"✅ 发现较新的数据文件: {latest_file}")
    
    # 步骤2：转换数据格式
    print("\n🔄 转换数据格式...")
    if not convert_data_format():
        print("❌ 数据格式转换失败，程序退出")
        return
    
    # 步骤3：启动Web服务器
    print("\n🌐 启动Web服务器...")
    start_server()

if __name__ == "__main__":
    main() 