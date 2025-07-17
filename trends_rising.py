#!/usr/bin/env python3
"""
谷歌趋势新词洞察 - 优化版本
功能：标准模式API调用 + 并发处理 + 限流机制 + 网站格式输出
"""

import json
import requests
import base64
import time
import logging
import os
import threading
import concurrent.futures
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

# 配置日志 - 生产环境只输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API配置
API_LOGIN = "chen8mei@yeah.net"
API_PASSWORD = "128216638d1a29af"
API_BASE_URL = "https://api.dataforseo.com/v3/keywords_data/google_trends/explore"

# 限流参数
REQUEST_LIMIT = 240
WINDOW_SECONDS = 60
request_times = []
request_lock = threading.Lock()

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

def generate_google_search_link(query):
    """生成谷歌搜索链接"""
    return f"https://www.google.com/search?q={quote_plus(query)}"

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

def get_auth_header():
    """获取认证头"""
    credentials = f"{API_LOGIN}:{API_PASSWORD}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {base64_credentials}"}

# 限流包装器
def rate_limited_request(func):
    def wrapper(*args, **kwargs):
        global request_times
        while True:
            with request_lock:
                now = time.time()
                request_times = [t for t in request_times if now - t < WINDOW_SECONDS]
                if len(request_times) < REQUEST_LIMIT:
                    request_times.append(now)
                    break
            logger.warning(f"触发限流，等待重试...")
            time.sleep(0.1)
        return func(*args, **kwargs)
    return wrapper

@rate_limited_request
def submit_task(keyword, time_range="2024-01-01 2024-12-31", max_retries=3):
    """提交单个任务到DataForSEO API"""
    headers = {
        **get_auth_header(),
        "Content-Type": "application/json"
    }
    
    payload = [{
        "keywords": [keyword],
        "location_name": "United States",
        "language_name": "English",
        "date_from": time_range.split()[0],
        "date_to": time_range.split()[1],
        "item_types": ["google_trends_queries_list"],
        "tag": keyword  # 用于识别任务对应的关键词
    }]
    
    submit_url = f"{API_BASE_URL}/task_post"
    
    for attempt in range(max_retries):
        try:
            logger.info(f"[{keyword}] 提交任务，第{attempt+1}次尝试")
            response = requests.post(submit_url, headers=headers, json=payload, timeout=60)
            response_data = response.json()
            
            if response_data.get("status_code") == 20000:
                if "tasks" in response_data and response_data["tasks"]:
                    task_id = response_data["tasks"][0].get("id")
                    if task_id:
                        logger.info(f"[{keyword}] 任务提交成功，任务ID: {task_id}")
                        return task_id
                    else:
                        logger.error(f"[{keyword}] 任务ID不存在")
                else:
                    logger.error(f"[{keyword}] 响应中无tasks或为空")
            else:
                error_msg = response_data.get('status_message', '未知错误')
                error_code = response_data.get('status_code', '未知状态码')
                logger.error(f"[{keyword}] API错误: 代码={error_code}, 消息={error_msg}")
                
            time.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"[{keyword}] 网络错误: {str(e)}")
            time.sleep(2 ** attempt)
    
    logger.error(f"[{keyword}] 任务提交失败，已尝试{max_retries}次")
    return None

@rate_limited_request
def get_ready_tasks():
    """获取已完成任务列表"""
    headers = get_auth_header()
    ready_url = f"{API_BASE_URL}/tasks_ready"
    
    try:
        response = requests.get(ready_url, headers=headers, timeout=60)
        response_data = response.json()
        
        if response_data.get("status_code") != 20000:
            logger.error(f"获取已完成任务失败: {response_data.get('status_message', '未知错误')}")
            return []
        
        # 提取所有已完成任务ID
        all_ready_tasks = []
        for task in response_data.get("tasks", []):
            result = task.get("result")
            if isinstance(result, list) and result:
                all_ready_tasks.extend(result)
        
        logger.info(f"找到 {len(all_ready_tasks)} 个已完成任务")
        return all_ready_tasks
        
    except Exception as e:
        logger.error(f"获取已完成任务失败: {e}")
        return []

@rate_limited_request
def get_task_result(task_id):
    """获取任务结果"""
    headers = get_auth_header()
    result_url = f"{API_BASE_URL}/task_get/{task_id}"
    
    try:
        response = requests.get(result_url, headers=headers, timeout=60)
        response_data = response.json()
        
        if response_data.get("status_code") == 20000:
            if "tasks" in response_data and response_data["tasks"]:
                task_result = response_data["tasks"][0]
                if task_result.get("status_code") == 20000:
                    # 获取任务标签（关键词）
                    task_data = task_result.get("data", {})
                    keyword = task_data.get("tag")
                    return task_result.get("result"), keyword
                else:
                    logger.error(f"[任务ID: {task_id}] 任务执行失败")
            else:
                logger.error(f"[任务ID: {task_id}] 结果中无tasks或为空")
        else:
            logger.error(f"[任务ID: {task_id}] API错误")
            
    except Exception as e:
        logger.error(f"[任务ID: {task_id}] 获取结果失败: {e}")
    
    return None, None

def extract_related_queries(task_result, original_keyword):
    """从任务结果中提取相关查询"""
    related_queries = []
    
    if not task_result or not isinstance(task_result, list):
        return related_queries
    
    if not task_result[0] or not isinstance(task_result[0], dict):
        return related_queries
    
    result_item = task_result[0]
    
    if "items" not in result_item or not result_item["items"]:
        return related_queries
    
    for item in result_item["items"]:
        if item.get("type") == "google_trends_queries_list":
            queries_data = item.get("data", {})
            
            for category, query_list in queries_data.items():
                if category in ["top", "rising"] and isinstance(query_list, list):
                    for query_item in query_list:
                        query_text = query_item.get("query")
                        if query_text:
                            growth_rate = query_item.get("value")
                            
                            if category == "rising":
                                if growth_rate == "BREAKOUT":
                                    numeric_growth_rate = 10000
                                else:
                                    try:
                                        numeric_growth_rate = float(growth_rate) if growth_rate is not None else 0
                                    except:
                                        numeric_growth_rate = 0
                            else:
                                numeric_growth_rate = 0
                            
                            related_queries.append({
                                "query": query_text,
                                "value": growth_rate,
                                "numeric_value": numeric_growth_rate,
                                "category": category,
                                "trends_link": generate_google_trends_link(query_text),
                                "search_link": generate_google_search_link(query_text)
                            })
            break
    
    logger.info(f"[{original_keyword}] 提取到 {len(related_queries)} 个相关查询")
    return related_queries

def process_tasks_batch(task_ids_with_keywords, max_workers=5):
    """并发处理多个已完成的任务"""
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(get_task_result, task_id): (task_id, keyword) 
            for task_id, keyword in task_ids_with_keywords
        }
        
        for future in concurrent.futures.as_completed(future_to_task):
            task_id, keyword = future_to_task[future]
            try:
                task_result, result_keyword = future.result()
                
                # 使用任务结果中的关键词或指定的关键词
                keyword_to_use = result_keyword if result_keyword else keyword
                if not keyword_to_use:
                    keyword_to_use = f"未知关键词_{task_id[-8:]}"
                
                if task_result:
                    related_queries = extract_related_queries(task_result, keyword_to_use)
                    if related_queries:
                        results[keyword_to_use] = {
                            "rising": [q for q in related_queries if q["category"] == "rising"]
                        }
                        logger.info(f"[{keyword_to_use}] 处理完成，获取到 {len(related_queries)} 个相关查询")
                else:
                    logger.error(f"[{keyword_to_use}] 获取结果失败")
            except Exception as e:
                logger.error(f"[任务ID: {task_id}] 处理异常: {e}")
                
    return results

def save_website_data(data, filename="trending_data.json"):
    """保存网站格式的数据"""
    try:
        # 计算统计信息
        total_seeds = len(data)
        total_queries = sum(len(item.get('rising', [])) for item in data.values())
        
        # 构建网站格式数据
        website_data = {
            "data": data,
            "total_seeds": total_seeds,
            "total_queries": total_queries,
            "last_updated": datetime.now().isoformat()
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

def main():
    """主函数 - 使用标准模式的优化工作流程"""
    logger.info("开始运行谷歌趋势新词洞察脚本（标准模式 - 优化版）")
    
    try:
        # 加载关键词
        keywords = load_keywords_from_csv(limit=100)
        if not keywords:
            logger.error("未能加载关键词，退出程序")
            return
        
        # 第一步：并发提交所有任务
        logger.info(f"开始并发提交 {len(keywords)} 个任务...")
        task_id_map = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_keyword = {
                executor.submit(submit_task, keyword): keyword 
                for keyword in keywords
            }
            
            for future in concurrent.futures.as_completed(future_to_keyword):
                keyword = future_to_keyword[future]
                try:
                    task_id = future.result()
                    if task_id:
                        task_id_map[task_id] = keyword
                        logger.info(f"[{keyword}] 任务提交成功")
                except Exception as e:
                    logger.error(f"[{keyword}] 任务提交异常: {e}")
        
        logger.info(f"成功提交 {len(task_id_map)} 个任务")
        
        if not task_id_map:
            logger.error("没有成功提交的任务，退出程序")
            return
        
        # 第二步：轮询等待任务完成
        logger.info("开始轮询等待任务完成...")
        pending_task_ids = set(task_id_map.keys())
        check_interval = 15  # 15秒检查一次
        all_processed_data = {}
        
        while pending_task_ids:
            logger.info(f"还有 {len(pending_task_ids)} 个任务等待完成，检查任务状态...")
            ready_tasks = get_ready_tasks()
            
            # 找出我们正在等待的已完成任务
            ready_task_ids = []
            for task in ready_tasks:
                task_id = task.get("id")
                if task_id in pending_task_ids:
                    ready_task_ids.append(task_id)
            
            if ready_task_ids:
                logger.info(f"发现 {len(ready_task_ids)} 个新完成的任务")
                
                # 准备批量处理
                tasks_to_process = [(task_id, task_id_map[task_id]) for task_id in ready_task_ids]
                
                # 并发处理已完成的任务
                batch_results = process_tasks_batch(tasks_to_process, max_workers=8)
                all_processed_data.update(batch_results)
                
                # 从待处理列表中移除已处理的任务
                for task_id in ready_task_ids:
                    pending_task_ids.remove(task_id)
                
                logger.info(f"已处理 {len(ready_task_ids)} 个任务，还剩 {len(pending_task_ids)} 个任务")
            else:
                logger.info("没有新完成的任务，继续等待...")
            
            if pending_task_ids:
                time.sleep(check_interval)
        
        # 第三步：保存数据
        if all_processed_data:
            success = save_website_data(all_processed_data)
            if success:
                logger.info(f"脚本运行完成，共处理 {len(all_processed_data)} 个关键词")
            else:
                logger.error("数据保存失败")
        else:
            logger.warning("未能处理出有效数据")
    
    except Exception as e:
        logger.error(f"脚本运行异常: {e}")
        raise

if __name__ == "__main__":
    main() 