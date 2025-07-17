#!/usr/bin/env python3
"""
谷歌趋势测试脚本
功能：只处理少量关键词，用于开发和测试，避免浪费API配额
"""

import json
import requests
import base64
import time
import logging
import threading
import concurrent.futures
from datetime import datetime
from urllib.parse import quote_plus

# 配置日志
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

# 测试关键词列表
TEST_KEYWORDS = [
    "generator",
    "creator", 
    "maker",
    "builder",
    "assistant"
]

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
def get_ready_tasks(max_calls=3):
    """获取已完成任务列表（测试模式只查询3次）"""
    headers = get_auth_header()
    ready_url = f"{API_BASE_URL}/tasks_ready"
    all_ready_tasks = []
    
    for call_num in range(max_calls):
        try:
            logger.info(f"获取已完成任务 (第{call_num+1}/{max_calls}次API调用)")
            response = requests.get(ready_url, headers=headers, timeout=60)
            response_data = response.json()
            
            if response_data.get("status_code") != 20000:
                logger.error(f"获取已完成任务失败: {response_data.get('status_message', '未知错误')}")
                break
            
            # 遍历所有 tasks 项，收集所有 result 列表中的任务
            tasks_list = response_data.get("tasks", [])
            
            if not tasks_list:
                logger.warning("响应中的tasks列表为空")
                break
                
            total_found = 0
            for entry in tasks_list:
                ready_tasks = entry.get("result")
                if isinstance(ready_tasks, list) and ready_tasks:
                    # 过滤出测试关键词相关的任务
                    filtered_tasks = []
                    for task in ready_tasks:
                        task_id = task.get("id")
                        if task_id:
                            filtered_tasks.append(task)
                    
                    total_found += len(filtered_tasks)
                    all_ready_tasks.extend(filtered_tasks)
                    
            if total_found > 0:
                logger.info(f"本次API调用发现 {total_found} 个已完成的任务")
                # 测试模式：找到一些任务就够了
                if len(all_ready_tasks) >= 20:
                    logger.info(f"测试模式：已获取足够的任务，共 {len(all_ready_tasks)} 个")
                    break
            else:
                logger.info("当前无已完成任务")
                break
            
            # 如果还有剩余可拉取，等待后续调用
            if call_num < max_calls - 1:
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"获取已完成任务失败: {e}")
            break
    
    logger.info(f"总共获取到 {len(all_ready_tasks)} 个已完成任务")
    return all_ready_tasks

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
                    keyword = task_data.get("tag") or task_data.get("keywords", [None])[0]
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
    
    return related_queries

def process_tasks_batch(task_ids, max_workers=5):
    """并发处理多个已完成的任务（测试模式限制并发数）"""
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(get_task_result, task_id): task_id 
            for task_id in task_ids
        }
        
        for future in concurrent.futures.as_completed(future_to_task):
            task_id = future_to_task[future]
            try:
                task_result, keyword = future.result()
                
                if not keyword:
                    keyword = f"未知关键词_{task_id[-8:]}"
                
                if task_result:
                    related_queries = extract_related_queries(task_result, keyword)
                    if related_queries:
                        results[keyword] = {
                            "rising": [q for q in related_queries if q["category"] == "rising"]
                        }
                        logger.info(f"[{keyword}] 处理完成，获取到 {len(related_queries)} 个相关查询")
                else:
                    logger.warning(f"[{keyword}] 无有效结果")
                    
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
    """主函数 - 测试模式"""
    logger.info("开始运行谷歌趋势测试脚本（测试模式）")
    logger.info(f"测试关键词: {TEST_KEYWORDS}")
    
    try:
        # 获取已完成任务
        logger.info("获取已完成任务...")
        ready_tasks = get_ready_tasks(max_calls=3)
        
        if not ready_tasks:
            logger.error("没有找到已完成的任务")
            return
        
        # 提取任务ID
        task_ids = [task.get("id") for task in ready_tasks if task.get("id")]
        logger.info(f"找到 {len(task_ids)} 个有效任务ID")
        
        if not task_ids:
            logger.error("没有有效的任务ID")
            return
        
        # 测试模式：只处理前10个任务
        max_tasks = 10
        if len(task_ids) > max_tasks:
            task_ids = task_ids[:max_tasks]
            logger.info(f"测试模式：只处理前 {max_tasks} 个任务")
        
        # 并发处理任务
        logger.info(f"开始并发处理 {len(task_ids)} 个任务...")
        results = process_tasks_batch(task_ids, max_workers=5)
        
        if results:
            # 保存数据
            success = save_website_data(results)
            if success:
                logger.info(f"测试完成，共处理 {len(results)} 个关键词")
            else:
                logger.error("数据保存失败")
        else:
            logger.warning("没有获取到有效数据")
    
    except Exception as e:
        logger.error(f"脚本运行异常: {e}")
        raise

if __name__ == "__main__":
    main() 