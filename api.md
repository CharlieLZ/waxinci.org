# Google Trends API 文档

## 目录
1. [概述](#概述)
2. [认证](#认证)
3. [基础信息查询](#基础信息查询)
4. [数据查询](#数据查询)
5. [响应数据结构](#响应数据结构)
6. [错误处理](#错误处理)
7. [计费](#计费)
8. [使用示例](#使用示例)
9. [注意事项](#注意事项)
10. [支持](#支持)

## 概述

Google Trends API 基于 Google Trends 服务，提供关键词相对流行度数据及相关主题和查询信息。

### 核心功能
- 关键词时间段流行度趋势
- 地区特定关键词流行度
- 相关主题推荐
- 相关查询推荐
- 最多支持5个关键词对比

### 数据来源
- Google 搜索
- Google 新闻
- Google 图片
- Google 购物
- YouTube

### 调用限制
- 每分钟最多2000次API调用
- 每个POST请求最多包含100个任务

## 认证

使用 Basic Authentication：
```bash
# 使用你的DataForSEO凭据
login="your_login"
password="your_password"
cred="$(printf ${login}:${password} | base64)"
```

## 基础信息查询

### 获取支持的位置列表
```bash
GET https://api.dataforseo.com/v3/keywords_data/google_trends/locations
```

**可选参数:**
- `country`: 国家ISO代码，用于过滤位置列表

**响应字段:**
- `location_code`: 位置代码
- `location_name`: 位置名称
- `country_iso_code`: 国家ISO代码
- `location_type`: 位置类型
- `geo_name`: Google Trends位置名称
- `geo_id`: Google Trends位置ID

### 获取支持的语言列表
```bash
GET https://api.dataforseo.com/v3/keywords_data/google_trends/languages
```

**响应字段:**
- `language_name`: 语言名称
- `language_code`: 语言代码（ISO 639-1）

### 获取支持的分类列表
```bash
GET https://api.dataforseo.com/v3/keywords_data/google_trends/categories
```

**响应字段:**
- `category_code`: 分类代码
- `category_name`: 分类名称
- `category_code_parent`: 上级分类代码

## 数据查询

### 方法说明
- **标准方法**: 分别发送POST和GET请求，适用于非实时需求
- **实时方法**: 单次请求即时返回结果，适用于实时需求

### 设置查询任务
```bash
POST https://api.dataforseo.com/v3/keywords_data/google_trends/explore/task_post
```

**请求参数:**

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `keywords` | array | 是 | 关键词列表（最多5个，每个最多100字符） |
| `location_name` | string | 否 | 位置名称 |
| `location_code` | integer | 否 | 位置代码 |
| `language_name` | string | 否 | 语言名称（默认：English） |
| `language_code` | string | 否 | 语言代码（默认：en） |
| `type` | string | 否 | 类型（web/news/youtube/images/froogle，默认：web） |
| `category_code` | integer | 否 | 分类代码（默认：0，所有分类） |
| `date_from` | string | 否 | 开始日期（yyyy-mm-dd格式） |
| `date_to` | string | 否 | 结束日期（yyyy-mm-dd格式） |
| `time_range` | string | 否 | 预设时间范围 |
| `item_types` | array | 否 | 返回项类型 |
| `postback_url` | string | 否 | 结果回调URL（任务完成后发送结果） |
| `pingback_url` | string | 否 | 完成通知URL（任务完成后发送通知） |
| `tag` | string | 否 | 用户标识符 |

**时间范围选项:**
- `past_hour`, `past_4_hours`, `past_day`, `past_7_days`
- `past_30_days`, `past_90_days`, `past_12_months`, `past_5_years`
- `2004_present`（仅web）, `2008_present`（其他类型）

**返回项类型:**
- `google_trends_graph`: 趋势图数据
- `google_trends_map`: 地图数据
- `google_trends_topics_list`: 相关主题列表
- `google_trends_queries_list`: 相关查询列表

**回调URL说明:**
- `postback_url`: 任务完成后会将结果以gzip压缩格式POST到此URL
- `pingback_url`: 任务完成后会向此URL发送GET通知请求
- 服务器响应超时时间：10秒
- 如果服务器响应超时或返回非200-300状态码，任务会转移到tasks_ready列表

### 获取已完成任务列表
```bash
GET https://api.dataforseo.com/v3/keywords_data/google_trends/explore/tasks_ready
```

**重要信息:**
- 每分钟最多20次API调用
- 每次调用最多获取1000个已完成任务
- 任务在完成后保留3天
- 已收集的任务不会出现在列表中
- 使用postback_url的任务不会出现在此列表中（除非回调失败）

### 获取任务结果
```bash
GET https://api.dataforseo.com/v3/keywords_data/google_trends/explore/task_get/{task_id}
```

### 实时查询
```bash
POST https://api.dataforseo.com/v3/keywords_data/google_trends/explore/live
```

**重要限制:**
- 每分钟最多250个Live任务
- 超过此限制可能收到限制相关错误
- 建议优先使用标准方法（更经济实惠）

## 响应数据结构

### 基本响应格式
```json
{
  "version": "0.1.20220420",
  "status_code": 20000,
  "status_message": "Ok.",
  "time": "0.2249 sec.",
  "cost": 0,
  "tasks_count": 1,
  "tasks_error": 0,
  "tasks": [
    {
      "id": "task_id",
      "status_code": 20000,
      "status_message": "Ok.",
      "time": "0.0273 sec.",
      "cost": 0,
      "result_count": 1,
      "path": ["v3", "keywords_data", "google_trends", "explore", "task_get"],
      "data": {
        "keywords": ["seo api"],
        "location_code": 2840,
        "language_code": "en"
      },
      "result": [
        {
          "keywords": ["seo api"],
          "type": "trends",
          "location_code": 2840,
          "language_code": "en",
          "check_url": "https://trends.google.com/trends/explore?...",
          "datetime": "2022-04-21 18:22:05 +00:00",
          "items_count": 4,
          "items": [
            // 各种数据项
          ]
        }
      ]
    }
  ]
}
```

### 具体数据项类型

### 趋势图数据 (google_trends_graph)
```json
{
  "type": "google_trends_graph",
  "title": "Interest over time",
  "keywords": ["keyword1", "keyword2"],
  "data": [
    {
      "date_from": "2019-01-06",
      "date_to": "2019-01-12",
      "timestamp": 1546732800,
      "missing_data": false,
      "values": [62, 37]
    }
  ],
  "averages": [62, 46]
}
```

### 地图数据 (google_trends_map)
```json
{
  "type": "google_trends_map",
  "title": "Compared breakdown by region",
  "keywords": ["keyword1", "keyword2"],
  "data": [
    {
      "geo_id": "US",
      "geo_name": "United States",
      "values": [64, 36],
      "max_value_index": 0
    }
  ]
}
```

### 相关主题列表 (google_trends_topics_list)
```json
{
  "type": "google_trends_topics_list",
  "title": "Related topics",
  "keywords": ["keyword"],
  "data": {
    "top": [
      {
        "topic_id": "/m/019qb_",
        "topic_title": "Search Engine Optimization",
        "topic_type": "Topic",
        "value": 100
      }
    ],
    "rising": [
      {
        "topic_id": "/m/05z1_",
        "topic_title": "Python",
        "topic_type": "Programming language",
        "value": 60
      }
    ]
  }
}
```

**说明:**
- `top`: 最相关的主题
- `rising`: 上升趋势的主题
- `value`: 相对流行度分数（100为最高）

### 相关查询列表 (google_trends_queries_list)
```json
{
  "type": "google_trends_queries_list",
  "title": "Related queries",
  "keywords": ["keyword"],
  "data": {
    "top": [
      {
        "query": "analytics seo api",
        "value": 100
      }
    ],
    "rising": [
      {
        "query": "moz api",
        "value": 80
      }
    ]
  }
}
```

**说明:**
- `top`: 最相关的查询
- `rising`: 上升趋势的查询
- `value`: 相对流行度分数（100为最高）

## 错误处理

### 常见状态码
- `20000`: 成功
- `20100`: 任务已创建
- `40006`: 任务数超过限制（>100）
- `50000`: 内部服务器错误
- 状态码范围：10000-60000（由DataForSEO生成）

### 错误响应示例
```json
{
  "status_code": 40006,
  "status_message": "Task limit exceeded",
  "tasks_count": 0,
  "tasks_error": 1
}
```

## 计费

- 仅设置任务时收费
- 获取结果不收费
- 详细价格请查看[定价页面](https://dataforseo.com/pricing)
- 可在账户仪表板查看花费，或通过User Data endpoint查询

## 使用示例

### 基本查询示例
```bash
curl -X POST "https://api.dataforseo.com/v3/keywords_data/google_trends/explore/task_post" \
  -H "Authorization: Basic ${cred}" \
  -H "Content-Type: application/json" \
  -d '[{
    "keywords": ["seo api", "rank api"],
    "date_from": "2019-01-01",
    "date_to": "2020-01-01",
    "type": "web",
    "category_code": 0,
    "location_code": 2840
  }]'
```

### 实时查询示例
```bash
curl -X POST "https://api.dataforseo.com/v3/keywords_data/google_trends/explore/live" \
  -H "Authorization: Basic ${cred}" \
  -H "Content-Type: application/json" \
  -d '[{
    "keywords": ["seo"],
    "location_name": "United States",
    "type": "web",
    "time_range": "past_30_days",
    "item_types": ["google_trends_graph", "google_trends_map"]
  }]'
```

### 使用回调URL示例
```bash
curl -X POST "https://api.dataforseo.com/v3/keywords_data/google_trends/explore/task_post" \
  -H "Authorization: Basic ${cred}" \
  -H "Content-Type: application/json" \
  -d '[{
    "keywords": ["seo api"],
    "type": "web",
    "postback_url": "https://your-server.com/callback",
    "pingback_url": "https://your-server.com/ping",
    "tag": "my_task_001"
  }]'
```

## 注意事项

### 关键词限制
1. 获取相关主题和查询列表时，关键词数量不能超过1个
2. 关键词不能包含特殊字符: `< > | \ " - + = ~ ! : * ( ) [ ] { }`
3. 逗号字符会被自动移除
4. 每个关键词最多100个字符，最少2个字符
5. 最多同时比较5个关键词

### 地区限制
- 俄罗斯和白俄罗斯地区不再支持（由于乌克兰战争）

### 回调机制
- 如果指定了postback_url，任务不会出现在已完成任务列表中
- 服务器必须在10秒内响应，否则任务转移到tasks_ready列表
- 服务器响应状态码必须在200-300范围内

### 最佳实践
1. 对于大量任务，建议使用标准方法而非Live方法
2. 合理设置postback_url可以提高效率
3. 定期检查tasks_ready列表以处理失败的回调
4. 使用tag参数便于任务管理和匹配

## 支持

### 联系方式
- 如需提高API调用限制，请联系客服
- 技术支持：访问[DataForSEO帮助中心](https://help.dataforseo.com/)

### 相关资源
- [定价页面](https://dataforseo.com/pricing)：查看详细费用
- [API访问页面](https://app.dataforseo.com/api-access)：获取API凭据
- [帮助中心文章](https://help.dataforseo.com/)：任务完成和结果获取指南
- [错误代码列表](https://docs.dataforseo.com/v3/appendix/errors)：完整的响应代码说明

### 开发建议
- 大量请求时访问帮助中心获取最佳实践
- 使用pingback/postback机制提高效率
- 合理设计错误处理和重试逻辑
- 定期监控API使用情况和费用


Standard Queue
Queue-based system with POST and GET requests
Turnaround time
up to 45 minutes
Price per task
$0.00225
Price per 1M keywords
$450
for 200,000 tasks with 5 keywords in each task
Live Mode
Real-time results with a single POST request
Turnaround time
up to 32 seconds on average
Price per task
$0.009
Price per 1M keywords
$1800
for 200,000 tasks with 5 keywords in each task 