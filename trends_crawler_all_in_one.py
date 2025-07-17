#!/usr/bin/env python3
"""
谷歌趋势新词洞察 - 一体化数据获取脚本
功能：API调用 + 数据处理 + 网站格式输出
"""

import json
import requests
import base64
import time
import logging
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('trends_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API配置
API_LOGIN = "chen8mei@yeah.net"
API_PASSWORD = "128216638d1a29af"
API_BASE_URL = "https://api.dataforseo.com/v3/keywords_data/google_trends/explore"

def get_auth_header():
    """获取认证头"""
    credentials = f"{API_LOGIN}:{API_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}", "Content-Type": "application/json"}

def generate_google_trends_link(query, time_range="2024-01-01 2024-12-31"):
    """生成谷歌趋势链接"""
    base_url = "https://trends.google.com/trends/explore"
    params = {
        "date": time_range,
        "geo": "US",
        "q": query
    }
    
    param_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
    return f"{base_url}?{param_string}"

def load_keywords_from_csv(limit=None):
    """从CSV文件加载关键词"""
    csv_path = Path("keywords_list.csv")
    if not csv_path.exists():
        logger.error(f"未找到关键词文件: {csv_path}")
        return []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 清理和过滤关键词
        keywords = []
        for line in lines:
            keyword = line.strip()
            if keyword and not keyword.startswith('#'):  # 跳过空行和注释
                keywords.append(keyword)
        
        # 应用限制
        if limit:
            keywords = keywords[:limit]
            
        logger.info(f"从CSV文件加载了 {len(keywords)} 个关键词")
        return keywords
        
    except Exception as e:
        logger.error(f"读取CSV文件失败: {e}")
        return []

def create_api_request(keywords, time_range="2024-01-01 2024-12-31"):
    """创建API请求"""
    return {
        "keywords": keywords,
        "location_name": "United States",
        "language_name": "English",
        "date_from": time_range.split()[0],
        "date_to": time_range.split()[1],
        "time_range": {
            "date_from": time_range.split()[0],
            "date_to": time_range.split()[1]
        }
    }

def call_api(keywords, time_range="2024-01-01 2024-12-31"):
    """调用DataForSEO API"""
    try:
        # 创建请求
        request_data = create_api_request(keywords, time_range)
        
        # 准备认证
        auth_string = f"{API_LOGIN}:{API_PASSWORD}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
        
        # 发送请求
        logger.info(f"正在调用API，关键词数量: {len(keywords)}")
        response = requests.post(
            API_BASE_URL,
            headers=headers,
            json=[request_data],
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        # 检查API响应
        if result.get('status_code') != 20000:
            logger.error(f"API调用失败: {result.get('status_message', '未知错误')}")
            return None
        
        logger.info("API调用成功")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求失败: {e}")
        return None
    except Exception as e:
        logger.error(f"API调用异常: {e}")
        return None

def process_api_response(api_result, time_range="2024-01-01 2024-12-31"):
    """处理API响应数据，转换为网站格式"""
    if not api_result or not api_result.get('tasks'):
        logger.warning("API结果为空或格式不正确")
        return []
    
    processed_data = {}
    
    for task in api_result['tasks']:
        if not task.get('result'):
            continue
            
        # 获取关键词
        keywords = task['data'].get('keywords', [])
        if not keywords:
            continue
            
        keyword = keywords[0]  # 获取第一个关键词作为种子关键词
        
        # 处理结果
        rising_queries = []
        
        for item in task['result']:
            if not isinstance(item, dict):
                continue
            
            for sub_item in item.get("items", []):
                if sub_item.get("type") == "google_trends_queries_list":
                    data = sub_item.get("data", {})
                    
                    # 只处理rising查询
                    if "rising" in data:
                        for query in data["rising"][:10]:  # 只取前10个
                            query_text = query.get("query", "")
                            growth_value = query.get("value", 0)
                            
                            # 网站格式的查询对象
                            rising_query = {
                                "query": query_text,
                                "value": growth_value,  # 保持原有的增长率
                                "link": generate_google_trends_link(query_text, time_range)
                            }
                            rising_queries.append(rising_query)
        
        # 如果有rising查询，添加到结果中
        if rising_queries:
            processed_data[keyword] = {
                "rising": rising_queries
            }
    
    return processed_data

def save_website_data(data, filename="trending_data.json"):
    """保存网站格式的数据"""
    try:
        # 计算统计信息
        total_seeds = len(data)
        total_queries = sum(len(item.get('rising', [])) for item in data.values())
        
        # 构建网站格式数据
        website_data = {
            "last_updated": datetime.now().isoformat(),
            "total_seeds": total_seeds,
            "total_queries": total_queries,
            "data": data
        }
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(website_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"网站数据已保存到: {filename}")
        logger.info(f"统计信息: {total_seeds} 个种子词，{total_queries} 个相关查询")
        
        return True
        
    except Exception as e:
        logger.error(f"保存网站数据失败: {e}")
        return False

def save_detailed_data(data, filename=None):
    """保存详细数据（用于备份和调试）"""
    if not filename:
        filename = f"detailed_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 详细数据已保存到: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"保存详细数据失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("开始运行谷歌趋势新词洞察脚本")
    
    try:
        # 加载关键词
        keywords = load_keywords_from_csv(limit=100)  # 限制100个关键词
        if not keywords:
            logger.error("未能加载关键词，退出程序")
            return
        
        # 调用API
        api_result = call_api(keywords)
        if not api_result:
            logger.error("API调用失败，退出程序")
            return
        
        # 处理数据
        processed_data = process_api_response(api_result)
        if not processed_data:
            logger.warning("未能处理出有效数据")
            return
        
        # 保存网站数据
        success = save_website_data(processed_data)
        if success:
            logger.info("脚本运行完成")
        else:
            logger.error("数据保存失败")
    
    except Exception as e:
        logger.error(f"脚本运行异常: {e}")
        raise

if __name__ == "__main__":
    main() 