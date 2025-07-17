# 谷歌趋势新词洞察

> 通过Google Trends API自动发现和展示新兴趋势词汇的Web应用

## 🌟 项目特色

- **自动化数据获取**: 使用DataForSEO API获取Google Trends数据
- **智能数据处理**: 筛选和处理rising趋势词汇
- **现代化界面**: 响应式设计，支持深色模式
- **生产环境就绪**: GitHub Actions自动部署到GitHub Pages
- **成本优化**: 每周自动更新，平衡数据新鲜度和API成本

## 📋 项目结构

```
waxinci.org/
├── index.html                          # 主页面
├── css/
│   ├── core-tokens.css                 # 核心设计令牌
│   └── global.css                      # 全局样式
├── js/
│   └── theme-manager.js                # 主题管理器
├── trends_crawler_all_in_one.py        # 数据获取脚本
├── start_web.py                        # 本地开发服务器
├── trending_data.json                  # 趋势数据（自动生成）
├── keywords_list.csv                   # 种子关键词列表
├── .github/workflows/
│   ├── update-trends.yml               # 自动更新数据
│   └── deploy-pages.yml                # 自动部署到GitHub Pages
└── README.md                           # 项目说明
```

## 🚀 快速开始

### 本地开发

1. **克隆项目**
   ```bash
   git clone https://github.com/CharlieLZ/waxinci.org.git
   cd waxinci.org
   ```

2. **安装依赖**
   ```bash
   pip install requests
   ```

3. **获取数据**
   ```bash
   python trends_crawler_all_in_one.py
   ```

4. **启动本地服务器**
   ```bash
   python start_web.py
   ```

5. **访问应用**
   打开浏览器访问 `http://localhost:3000`

### 生产环境部署

项目已配置自动部署到GitHub Pages：

1. **Fork项目**到您的GitHub账户
2. **启用GitHub Pages**：
   - 进入仓库设置 → Pages
   - Source选择 "GitHub Actions"
3. **配置API密钥**（可选）：
   - 在仓库设置 → Secrets中添加API配置
4. **自动部署**：
   - 每周一自动更新数据
   - 数据更新后自动部署网站

## 📊 数据格式

生成的`trending_data.json`结构如下：

```json
{
  "data": {
    "关键词": {
      "rising": [
        {
          "query": "相关搜索词",
          "value": 增长百分比,
          "link": "Google Trends链接"
        }
      ]
    }
  },
  "total_seeds": 种子关键词数量,
  "total_queries": 相关查询总数,
  "last_updated": "更新时间"
}
```

## 🔧 配置说明

### API配置

在`trends_crawler_all_in_one.py`中配置DataForSEO API：

```python
API_LOGIN = "your_email@example.com"
API_PASSWORD = "your_api_password"
```

### 种子关键词

编辑`keywords_list.csv`文件来自定义种子关键词：

```csv
generator
creator
maker
assistant
...
```

### 更新频率

在`.github/workflows/update-trends.yml`中调整cron表达式：

```yaml
schedule:
  # 每周一上午9点（北京时间）
  - cron: '0 1 * * 1'
  
  # 每天上午9点（更频繁但成本更高）
  # - cron: '0 1 * * *'
```

## 💡 成本优化建议

### API成本分析

- DataForSEO API：约$0.001/请求
- 100个关键词 = 约$0.1
- 每周更新 = 约$5.2/年
- 每天更新 = 约$36.5/年

### 优化策略

1. **减少关键词数量**：筛选最有价值的种子词
2. **延长更新间隔**：每周或每两周更新
3. **批量处理**：合并多个关键词到单个请求
4. **缓存策略**：只有数据变化时才更新

## 🎨 界面特色

- **响应式设计**：适配桌面和移动设备
- **深色模式**：自动跟随系统主题
- **现代UI**：使用Tailwind CSS和自定义令牌
- **高性能**：静态文件，快速加载

## 🔄 自动化流程

### 数据更新流程

1. GitHub Actions定时触发
2. 运行`trends_crawler_all_in_one.py`
3. 调用DataForSEO API获取数据
4. 处理和格式化数据
5. 生成`trending_data.json`
6. 提交更新到仓库

### 部署流程

1. 检测到数据文件变化
2. 验证文件完整性
3. 准备部署文件
4. 部署到GitHub Pages
5. 更新生产环境

## 🛠️ 技术栈

- **后端**: Python 3.9+
- **API**: DataForSEO Google Trends API
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **样式**: Tailwind CSS + 自定义令牌
- **部署**: GitHub Actions + GitHub Pages
- **字体**: Inter (Google Fonts)

## 📝 更新日志

### v2.0.0 (当前版本)
- ✅ 修正了错误的搜索量估算逻辑
- ✅ 移除了虚假的volume字段
- ✅ 简化了数据处理流程
- ✅ 优化了生产环境部署
- ✅ 添加了GitHub Actions自动化

### v1.0.0
- ✅ 基础功能实现
- ✅ 数据获取和展示
- ✅ 响应式界面

## 📄 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📧 联系方式

- **项目地址**: https://github.com/CharlieLZ/waxinci.org
- **在线预览**: https://charlielz.github.io/waxinci.org/
- **问题反馈**: https://github.com/CharlieLZ/waxinci.org/issues

---

**为哥飞群友服务 · 免费版本额度有限**

如觉得好用请成为付费用户（[trend.new](https://trend.new)）支持我有更好的动力继续完善本产品。 