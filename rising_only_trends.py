#!/usr/bin/env python3
"""
精简版Google Trends脚本 - 只处理Rising查询
为种子关键词添加固定的gpts值，只返回rising字段数据
"""

import json
import requests
import base64
import time
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('rising_only_trends.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API配置
API_LOGIN = "chen8mei@yeah.net"
API_PASSWORD = "128216638d1a29af"
API_BASE_URL = "https://api.dataforseo.com/v3/keywords_data/google_trends/explore"

# 种子关键词的固定GPTS值设置
SEED_KEYWORDS_GPTS = {
    "generator": 85,
    "creator": 78,
    "maker": 82,
    "builder": 75,
    "constructor": 70,
    "composer": 65,
    "helper": 88,
    "assistant": 92,
    "agent": 80,
    "advisor": 77,
    "tool": 95,
    "directory": 60,
    "top": 90,
    "best": 85,
    "list": 75,
    "portal": 55,
    "finder": 70,
    "example": 65,
    "template": 80,
    "sample": 70,
    "pattern": 68,
    "resources": 72,
    "guide": 85,
    "format": 60,
    "model": 88,
    "layout": 65,
    "ideas": 78,
    "starter": 70,
    "cataloger": 50,
    "dashboard": 82,
    "designer": 90,
    "uploader": 75,
    "downloader": 78,
    "scraper": 85,
    "crawler": 80,
    "syncer": 55,
    "translator": 88,
    "converter": 82,
    "editor": 90,
    "optimizer": 85,
    "enhancer": 75,
    "modifier": 70,
    "processor": 82,
    "compiler": 78,
    "analyzer": 85,
    "evaluator": 72,
    "calculator": 88,
    "online": 95,
    "checker": 82,
    "detector": 78,
    "humanizer": 60,
    "tester": 75,
    "planner": 82,
    "scheduler": 78,
    "manager": 88,
    "tracker": 85,
    "sender": 65,
    "receiver": 68,
    "responder": 70,
    "recorder": 75,
    "connector": 72,
    "viewer": 80,
    "monitor": 85,
    "notifier": 75,
    "verifier": 78,
    "simulator": 82,
    "comparator": 75,
    "answer": 90,
    "hint": 70,
    "clue": 68,
    "cheat": 75,
    "solver": 88,
    "extractor": 82,
    "summarizer": 85,
    "transcriber": 78,
    "paraphaser": 70,
    "writer": 92,
    "image": 95,
    "photo": 90,
    "picture": 88,
    "face": 85,
    "emoji": 80,
    "meme": 85,
    "chart": 82,
    "graph": 78,
    "style": 88,
    "filter": 85,
    "text": 92,
    "chat": 95,
    "code": 90,
    "video": 95,
    "audio": 88,
    "voice": 85,
    "sound": 82,
    "speech": 80,
    "song": 88,
    "music": 90,
    "how to": 98,
    "icon": 78,
    "logo": 85,
    "avatar": 82,
    "anime": 88,
    "portrait": 80,
    "product photo": 85,
    "cartoon": 85,
    "tattoo": 82,
    "character": 88,
    "coloring page": 75,
    "action": 85,
    "figure": 78,
    "diagram": 80,
    "font": 88,
    "illustration": 85,
    "interior design": 82,
    "upscaler": 78
}

def get_auth_header():
    """获取认证头"""
    credentials = f"{API_LOGIN}:{API_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}", "Content-Type": "application/json"}

def generate_google_trends_link(query, time_range="past_7_days", language="en"):
    """生成Google Trends链接"""
    base_url = "https://trends.google.com/trends/explore"
    
    # 时间范围映射
    time_mapping = {
        "past_hour": "now%201-H",
        "past_4_hours": "now%204-H", 
        "past_day": "now%201-d",
        "past_7_days": "now%207-d",
        "past_30_days": "today%201-m",
        "past_90_days": "today%203-m",
        "past_year": "today%2012-m",
        "past_5_years": "today%205-y"
    }
    
    # 构建URL参数
    params = {
        "hl": language,
        "date": time_mapping.get(time_range, "now%207-d"),
        "q": query
    }
    
    # 构建完整URL
    param_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
    full_url = f"{base_url}?{param_string}"
    
    return full_url

def load_keywords_from_csv(limit=None):
    """从CSV文件加载关键词"""
    csv_path = Path("keywords_list.csv")
    if not csv_path.exists():
        logger.error(f"未找到关键词文件: {csv_path}")
        return []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        keywords = [line.strip('"\'') for line in lines if line.strip()]
        if limit:
            keywords = keywords[:limit]
        
        logger.info(f"成功读取 {len(keywords)} 个关键词")
        return keywords
    except Exception as e:
        logger.error(f"读取关键词文件失败: {str(e)}")
        return []

def post_batch_tasks(keywords, time_range="past_7_days"):
    """批量提交任务"""
    tasks = []
    for keyword in keywords:
        task = {
            "keywords": [keyword],
            "time_range": time_range,
            "type": "web",
            "item_types": ["google_trends_queries_list"],
            "language_code": "en",
            "tag": keyword
        }
        tasks.append(task)
    
    url = f"{API_BASE_URL}/task_post"
    headers = get_auth_header()
    
    try:
        logger.info(f"批量提交任务，包含 {len(keywords)} 个关键词")
        response = requests.post(url, headers=headers, json=tasks, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status_code") == 20000:
                task_ids = [task.get("id") for task in data.get("tasks", []) if task.get("id")]
                logger.info(f"✅ 成功提交 {len(task_ids)} 个任务")
                return task_ids
            else:
                logger.error(f"API错误: {data.get('status_message', '未知错误')}")
        else:
            logger.error(f"HTTP错误: {response.status_code}")
    
    except Exception as e:
        logger.error(f"提交任务异常: {str(e)}")
    
    return []

def wait_for_completion(task_ids, max_wait=1800):
    """等待任务完成"""
    logger.info(f"等待 {len(task_ids)} 个任务完成...")
    
    completed_ids = set()
    start_time = time.time()
    
    while len(completed_ids) < len(task_ids):
        if time.time() - start_time > max_wait:
            logger.warning("等待超时")
            break
        
        try:
            url = f"{API_BASE_URL}/tasks_ready"
            headers = get_auth_header()
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status_code") == 20000:
                    for entry in data.get("tasks", []):
                        for task in entry.get("result", []):
                            task_id = task.get("id")
                            if task_id in task_ids and task_id not in completed_ids:
                                completed_ids.add(task_id)
            
            if len(completed_ids) >= len(task_ids):
                break
                
            logger.info(f"已完成 {len(completed_ids)}/{len(task_ids)} 个任务，等待30秒后继续检查...")
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"检查任务状态异常: {str(e)}")
            time.sleep(30)
    
    logger.info(f"最终完成 {len(completed_ids)} 个任务")
    return list(completed_ids)

def get_task_results(task_ids, time_range="past_7_days"):
    """获取任务结果，只处理rising字段"""
    logger.info(f"获取 {len(task_ids)} 个任务的结果...")
    
    results = {}
    headers = get_auth_header()
    
    for task_id in task_ids:
        try:
            url = f"{API_BASE_URL}/task_get/{task_id}"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status_code") == 20000:
                    tasks = data.get("tasks", [])
                    if tasks:
                        task = tasks[0]
                        if task.get("status_code") == 20000:
                            keyword = task.get("data", {}).get("tag", "")
                            result = task.get("result", [])
                            
                            if keyword and result:
                                results[keyword] = parse_rising_only(result, keyword, time_range)
                                logger.info(f"获取结果成功: {keyword}")
        
        except Exception as e:
            logger.error(f"获取任务结果异常 [{task_id}]: {str(e)}")
    
    logger.info(f"成功获取 {len(results)} 个关键词的结果")
    return results

def parse_rising_only(result, original_keyword, time_range="past_7_days"):
    """只解析rising字段，为种子关键词添加固定gpts值"""
    # 种子关键词数据
    seed_data = {
        "keyword": original_keyword,
        "gpts": SEED_KEYWORDS_GPTS.get(original_keyword.lower(), 75),  # 默认75
        "rising_queries": []
    }
    
    # 解析API返回的rising查询
    for item in result:
        if not isinstance(item, dict):
            continue
        
        for sub_item in item.get("items", []):
            if sub_item.get("type") == "google_trends_queries_list":
                data = sub_item.get("data", {})
                
                # 只处理rising查询
                if "rising" in data:
                    for i, query in enumerate(data["rising"][:10], 1):
                        query_text = query.get("query", "")
                        growth_value = query.get("value", 0)
                        
                        parsed_query = {
                            "query": query_text,
                            "growth_rate": growth_value,
                            "growth_rate_formatted": format_growth_rate(growth_value),
                            "rank": i,
                            "link": generate_google_trends_link(query_text, time_range)
                        }
                        seed_data["rising_queries"].append(parsed_query)
    
    return seed_data

def format_growth_rate(value):
    """格式化增长率"""
    if value == "BREAKOUT":
        return "BREAKOUT"
    
    try:
        numeric_value = float(value)
        return f"+{numeric_value:.0f}%"
    except (ValueError, TypeError):
        return "0%"

def save_rising_only_results(results, keywords, time_range="past_7_days"):
    """保存只包含rising字段的结果"""
    # 统计信息
    total_rising_queries = sum(len(data.get("rising_queries", [])) for data in results.values())
    keywords_with_rising = len([k for k, v in results.items() if v.get("rising_queries")])
    
    # 按gpts值排序种子关键词
    sorted_keywords = sorted(results.items(), key=lambda x: x[1].get("gpts", 0), reverse=True)
    
    output_data = {
        "metadata": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "time_range": time_range,
            "api_info": {
                "rising_value_meaning": "增长率百分比 (整数) 或 BREAKOUT (突破性增长)",
                "gpts_meaning": "Google Trends 趋势分数 (0-100)，数值越高表示越热门"
            },
            "description": "只包含Rising查询的Google Trends数据"
        },
        "summary": {
            "total_seed_keywords": len(keywords),
            "processed_keywords": len(results),
            "total_rising_queries": total_rising_queries,
            "keywords_with_rising": keywords_with_rising,
            "completion_rate": f"{len(results)/len(keywords)*100:.1f}%" if keywords else "0%",
            "avg_gpts": f"{sum(data.get('gpts', 0) for data in results.values()) / len(results):.1f}" if results else "0"
        },
        "seed_keywords": {
            keyword: {
                "gpts": data["gpts"],
                "rising_queries_count": len(data["rising_queries"]),
                "rising_queries": data["rising_queries"]
            }
            for keyword, data in sorted_keywords
        }
    }
    
    output_file = f"rising_only_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 结果已保存到: {output_file}")
        return output_file
    
    except Exception as e:
        logger.error(f"保存结果失败: {str(e)}")
        return ""

def main():
    """主函数"""
    logger.info("🚀 开始Rising-only Google Trends数据获取...")
    
    # 1. 加载关键词（测试用10个）
    keywords = load_keywords_from_csv(limit=10)
    if not keywords:
        logger.error("没有关键词，程序退出")
        return
    
    # 2. 显示种子关键词的固定GPTS值
    logger.info("📊 种子关键词固定GPTS值:")
    for keyword in keywords:
        gpts = SEED_KEYWORDS_GPTS.get(keyword.lower(), 75)
        logger.info(f"   {keyword}: {gpts}")
    
    # 3. 批量提交任务
    time_range = "past_7_days"
    task_ids = post_batch_tasks(keywords, time_range)
    if not task_ids:
        logger.error("任务提交失败，程序退出")
        return
    
    # 4. 等待任务完成
    completed_ids = wait_for_completion(task_ids)
    
    # 5. 获取结果（只处理rising字段）
    results = get_task_results(completed_ids, time_range)
    
    # 6. 保存结果
    output_file = save_rising_only_results(results, keywords, time_range)
    
    # 7. 显示统计信息
    logger.info("📊 处理完成！统计信息:")
    logger.info(f"   🎯 关键词总数: {len(keywords)}")
    logger.info(f"   📤 提交任务: {len(task_ids)}")
    logger.info(f"   ✅ 完成任务: {len(completed_ids)}")
    logger.info(f"   📊 获取结果: {len(results)}")
    logger.info(f"   💾 输出文件: {output_file}")
    
    # 显示示例数据
    if results:
        logger.info("🔍 结果示例:")
        for keyword, data in list(results.items())[:3]:
            gpts = data.get("gpts", 0)
            rising_count = len(data.get("rising_queries", []))
            logger.info(f"   {keyword} (GPTS: {gpts}): {rising_count} 个rising查询")
            
            # 显示前2个rising查询
            for query in data.get("rising_queries", [])[:2]:
                logger.info(f"     - {query['query']} ({query['growth_rate_formatted']})")

if __name__ == "__main__":
    main() 