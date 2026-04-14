# 中文文本处理与分析工具

这是一个基于 Python 3.10 的中文文本处理与分析工具包，提供中文分词、新闻词云生成、基于 HuggingFace 的情感分析、关键词提取等功能。

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 📋 项目概述

基于Python的中文文本处理与分析工具包，集成Microsoft Phi-2模型进行高级情感分析。

## 🎯 主要功能

- **Phi-2情感分析**: 使用2.7B参数的Phi-2模型进行中文情感分析
- **词典情感分析**: 基于情感词典的轻量级情感分析
- **中文分词对比**: 对比不同分词引擎的效果
- **关键词提取**: 基于TF-IDF算法提取关键词
- **新闻词云生成**: 从新闻API获取数据生成词云

## 🚀 快速开始

## 环境要求

- Python 3.10+
- 支持的操作系统：Windows 11, Ubuntu 24.04, macOS

## 安装指南

### 快速安装

1. **安装 Python 依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **设置中文字体**：
   ```bash
   # Windows 系统
   .\setup_fonts.ps1  # 或 .\setup_fonts.bat
   
   # 其他系统
   python download_fonts.py
   ```

3. **检查环境**：
   ```bash
   python check_environment.py
   ```

4. **验证安装**：
   ```bash
   python test_all_modules.py
   ```

### 详细安装说明

请查看下文“安装和设置指南”章节获取完整的安装说明和故障排除方法。

## 使用方法

### 1. 中文分词对比
```bash
python jieba_comparison.py
```

### 2. 新闻文章词云生成
```bash
python news_wordcloud.py
```

### 3. 情感分析（HuggingFace）
```bash
python hf_sentiment.py --text "这个产品非常好用"
# 批量分析评论
python hf_sentiment.py --file data/comments.txt
```

### 4. 关键词提取
```bash
python keyword_extraction.py
```

## 项目结构

```
.
├── requirements.txt          # 项目依赖
├── README.md                 # 项目说明（本文件）
├── jieba_comparison.py       # 分词对比模块
├── news_wordcloud.py         # 新闻词云生成模块
├── hf_sentiment.py           # HuggingFace 情感分析模块
├── keyword_extraction.py     # 关键词提取模块
├── config.py                 # 配置文件
├── utils.py                  # 工具函数
├── data/                     # 数据目录
│   ├── news_articles/        # 新闻文章文本文件
│   ├── wordclouds/           # 词云图片
│   └── comments/             # 评论数据
└── fonts/                    # 中文字体目录
    └── SimHei.ttf            # 中文字体文件
```

## 注意事项

1. 需要下载中文字体文件到 `fonts/` 目录
2. 新闻 API 可能需要申请 API 密钥（参见“新闻 API 接入指南”）
3. 情感分析模块首次运行时会自动下载 HuggingFace 模型（约 1GB）

---

# 安装和设置指南

## 系统要求

- **操作系统**：Windows 10/11, Ubuntu 18.04+, macOS 10.15+
- **Python 版本**：Python 3.8 或更高版本
- **内存**：至少 4GB RAM
- **磁盘空间**：至少 500MB 可用空间（情感分析模型额外需要约 1GB）

## 快速安装步骤

### 步骤1：克隆或下载项目

```bash
# 克隆项目（如果有 Git）
git clone https://github.com/Kolomovici/HNU_DZ133XC24-Solution
cd HNU_DZ133XC24-Solution

# 或者直接下载 ZIP 文件并解压
```

### 步骤2：安装 Python 依赖

```bash
# 使用 pip 安装所有依赖
pip install -r requirements.txt

# 如果遇到权限问题，使用以下命令
pip install --user -r requirements.txt

# 或者使用虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 然后在虚拟环境中安装依赖
pip install -r requirements.txt
```

### 步骤3：设置中文字体

#### Windows 系统：

```powershell
# 方法1：使用 PowerShell 脚本（推荐）
.\setup_fonts.ps1

# 方法2：使用批处理脚本
.\setup_fonts.bat

# 方法3：使用 Python 脚本
python download_fonts.py
```

#### Linux/macOS 系统：

```bash
# 方法1：使用 Python 脚本
python3 download_fonts.py

# 方法2：使用包管理器安装字体
# Ubuntu/Debian
sudo apt-get install fonts-wqy-microhei

# macOS
brew install font-wqy-microhei
```

### 步骤4：验证安装

```bash
# 运行测试脚本验证所有功能
python test_all_modules.py

# 或者运行演示
python start_demo.py
```

## 详细安装说明

### 1. Python 环境设置

#### 检查 Python 版本

```bash
python --version
# 或
python3 --version
```

如果未安装 Python，请从以下地址下载安装：
- 官方网站：https://www.python.org/downloads/
- 建议安装 Python 3.8 或更高版本

#### 安装 pip（如果未安装）

```bash
# 通常 pip 会随 Python 一起安装
# 如果未安装，可以使用以下命令
python -m ensurepip --upgrade
```

### 2. 依赖包安装问题解决

#### 常见问题1：pip 版本过旧

```bash
# 升级 pip
python -m pip install --upgrade pip
```

#### 常见问题2：权限不足

```bash
# 使用 --user 选项
pip install --user -r requirements.txt

# 或者使用虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
```

#### 常见问题3：网络问题

```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 3. 字体设置问题解决

#### Windows 系统字体问题

如果自动脚本失败，可以手动操作：

1. **检查系统字体**：
   ```powershell
   # 查看系统是否有中文字体
   dir C:\Windows\Fonts\*hei*.*
   dir C:\Windows\Fonts\*宋体*.*
   dir C:\Windows\Fonts\*雅黑*.*
   ```

2. **手动复制字体**：
   ```powershell
   # 创建 fonts 目录
   mkdir fonts

   # 复制字体（选择其中一个）
   copy "C:\Windows\Fonts\simhei.ttf" fonts\
   copy "C:\Windows\Fonts\msyh.ttc" fonts\
   copy "C:\Windows\Fonts\simsun.ttc" fonts\
   ```

3. **下载字体**：
   - 访问：https://github.com/googlefonts/noto-cjk
   - 下载 NotoSansSC-Regular.otf
   - 重命名为 simhei.ttf 并放入 fonts 目录

#### Linux/macOS 字体问题

```bash
# 检查字体是否安装
fc-list | grep -i "chinese\|simhei\|wqy"

# 安装中文字体
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei

# CentOS/RHEL
sudo yum install wqy-microhei-fonts

# macOS
brew tap homebrew/cask-fonts
brew install --cask font-wqy-microhei
```

### 4. 配置修改

如果需要修改默认配置，编辑 `config.py` 文件：

```python
# 修改字体路径
DEFAULT_FONT = "fonts/simhei.ttf"  # 根据实际字体文件名修改

# 修改新闻 API 密钥（如果需要使用新闻功能）
NEWS_API_CONFIG = {
    'api_key': '你的 API 密钥',  # 替换为你的 NewsAPI 密钥
    # ... 其他配置
}

# 修改数据目录
DATA_DIR = Path(__file__).parent / "my_data"  # 修改数据目录位置
```

## 测试安装

### 运行完整测试

```bash
python test_all_modules.py
```

预期输出：
```
开始测试中文文本处理与分析工具的所有模块
============================================================
...
[SUCCESS] 所有模块测试通过！
```

### 测试单个功能

```bash
# 测试分词对比
python jieba_comparison.py --text "测试文本"

# 测试关键词提取
python keyword_extraction.py --text "人工智能是未来的发展方向"

# 测试 HuggingFace 情感分析
python hf_sentiment.py --text "这个产品很好用"
```

## 故障排除

### 问题1：ModuleNotFoundError

**错误信息**：
```
ModuleNotFoundError: No module named 'jieba'
```

**解决方法**：
```bash
# 安装缺失的模块
pip install jieba

# 或者重新安装所有依赖
pip install -r requirements.txt
```

### 问题2：字体相关错误

**错误信息**：
```
OSError: cannot open resource
```

**解决方法**：
1. 确保 fonts 目录中有中文字体文件
2. 检查字体文件名是否正确
3. 修改 config.py 中的字体路径

### 问题3：内存不足

**错误信息**：
```
MemoryError
```

**解决方法**：
1. 减少处理的数据量
2. 增加系统虚拟内存
3. 使用更高效的算法

### 问题4：API 密钥错误

**错误信息**：
```
新闻 API 请求失败
```

**解决方法**：
1. 申请免费的 NewsAPI 密钥：https://newsapi.org/
2. 更新 config.py 中的 API 密钥
3. 或者不使用新闻功能

### 问题5：HuggingFace 模型下载失败

**错误信息**：
```
ConnectionError: 无法下载模型
```

**解决方法**：
1. 检查网络连接，或设置代理
2. 使用镜像源：在 `hf_sentiment.py` 中设置 `mirror="https://hf-mirror.com"`
3. 手动下载模型并放置到本地缓存目录

## 升级和更新

### 更新依赖包

```bash
# 更新所有包到最新版本
pip install --upgrade -r requirements.txt
```

### 更新项目

```bash
# 如果有 Git
git pull origin main

# 然后更新依赖
pip install --upgrade -r requirements.txt
```

## 卸载

### 卸载 Python 包

```bash
# 卸载所有依赖包
pip freeze | xargs pip uninstall -y

# 或者手动卸载
pip uninstall jieba wordcloud matplotlib numpy pandas requests beautifulsoup4 snownlp pypinyin pillow scikit-learn opencc-python-reimplemented transformers torch
```

### 删除项目文件

```bash
# 删除整个项目目录
rm -rf 项目目录  # Linux/macOS
# 或
rd /s /q 项目目录  # Windows
```

## 获取帮助

如果遇到问题，请：

1. 查看日志文件：`logs/app.log`
2. 运行测试脚本：`python test_all_modules.py`
3. 查阅本指南的故障排除部分

## 支持的系统

- ✅ Windows 10/11
- ✅ Ubuntu 18.04+
- ✅ Debian 10+
- ✅ macOS 10.15+
- ✅ CentOS 7+
- ⚠️ 其他 Linux 发行版（可能需要额外配置）

---

# 新闻 API 接入指南

本指南将帮助您将新闻 API 集成到词云生成项目中。

## 支持的新闻 API

### 1. NewsAPI.org（推荐）
- **网站**: https://newsapi.org
- **免费层**: 100 次请求/天
- **覆盖范围**: 全球 70,000+ 新闻源
- **语言支持**: 多语言，包括中文
- **注册**: https://newsapi.org/register

### 2. 模拟 API
- **特点**: 无需网络连接，用于测试
- **数据**: 模拟生成的新闻数据
- **适合**: 开发和测试环境

## 快速开始

### 步骤1: 安装依赖
```bash
pip install -r requirements.txt
```

### 步骤2: 配置 API 密钥
```bash
# 运行交互式配置向导
python news_api_config.py --setup

# 或者直接设置 NewsAPI 密钥
python news_api_config.py --set-key newsapi YOUR_API_KEY
```

### 步骤3: 测试 API 连接
```bash
# 测试模拟 API
python news_api_demo.py --api-type mock --query "科技"

# 测试 NewsAPI（如果已配置）
python news_api_demo.py --api-type newsapi --query "人工智能"
```

### 步骤4: 生成新闻词云
```bash
# 使用模拟 API 生成词云
python news_integration_example.py --api-type mock --query "科技"

# 使用 NewsAPI 生成词云
python news_integration_example.py --api-type newsapi --query "人工智能"
```

## 详细使用说明

### 1. 获取 NewsAPI 密钥

1. 访问 https://newsapi.org/register
2. 使用邮箱注册账号
3. 登录后进入 Dashboard
4. 复制您的 API 密钥
5. 在项目中配置密钥:
   ```bash
   python news_api_config.py --set-key newsapi your_api_key_here
   ```

### 2. 使用增强版词云生成器

```python
from news_integration_example import EnhancedNewsWordCloudGenerator

# 创建生成器实例
generator = EnhancedNewsWordCloudGenerator(
    api_type="newsapi",  # 或 "mock"
    api_key="your_api_key"  # 可选，如果已配置
)

# 运行完整流程
generator.run_enhanced_pipeline(
    query="人工智能",
    use_cache=True
)
```

### 3. 命令行使用

```bash
# 查看所有可用 API
python news_api_config.py --list-apis

# 查看 API 详细信息
python news_api_config.py --api-info newsapi

# 列出已配置的密钥
python news_api_config.py --list-keys

# 运行集成演示
python news_integration_example.py --demo

# 比较不同 API
python news_integration_example.py --compare
```

## API 配置详情

### NewsAPI 配置
```python
{
    "base_url": "https://newsapi.org/v2",
    "endpoints": {
        "everything": "/everything",      # 搜索所有文章
        "top_headlines": "/top-headlines", # 头条新闻
        "sources": "/sources"            # 新闻源列表
    },
    "参数": {
        "q": "搜索关键词",
        "from": "开始日期 (YYYY-MM-DD)",
        "to": "结束日期",
        "language": "语言 (zh=中文)",
        "sortBy": "排序方式",
        "pageSize": "每页数量 (1-100)",
        "page": "页码"
    }
}
```

### 示例请求
```python
import requests

params = {
    'q': '人工智能',
    'apiKey': 'YOUR_API_KEY',
    'pageSize': 50,
    'language': 'zh',
    'sortBy': 'publishedAt',
    'from': '2024-01-01'
}

response = requests.get('https://newsapi.org/v2/everything', params=params)
data = response.json()
```

## 项目结构（新闻相关）

```
项目根目录/
├── news_api_demo.py          # API 演示脚本
├── news_api_config.py        # API 配置管理
├── news_integration_example.py # 集成示例
├── news_wordcloud.py         # 原始词云生成器
├── config.py                 # 项目配置
└── data/
    ├── api_configs/          # API 密钥配置
    │   └── api_keys.json
    ├── news_data/            # 新闻数据
    └── wordclouds/           # 生成的词云
```

## 故障排除（新闻 API）

### 常见问题

1. **API 密钥无效**
   ```
   错误: 401 Unauthorized
   解决方案: 检查 API 密钥是否正确，或重新生成密钥
   ```

2. **请求限制**
   ```
   错误: 429 Too Many Requests
   解决方案: 免费层每天 100 次请求，请合理安排请求频率
   ```

3. **网络连接问题**
   ```
   错误: ConnectionError
   解决方案: 检查网络连接，或使用模拟 API 测试
   ```

4. **中文显示问题**
   ```
   问题: 词云中文显示为方框
   解决方案: 确保已安装中文字体，运行 setup_fonts.bat
   ```

### 调试模式

```bash
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 或运行时设置环境变量
set LOG_LEVEL=DEBUG
python news_api_demo.py --api-type mock --query "测试"
```

## 高级功能

### 1. 自定义新闻源
```python
# 在 config.py 中修改
NEWS_API_CONFIG = {
    'base_url': 'https://newsapi.org/v2/everything',
    'api_key': 'your_key',
    'sources': 'bbc-news,cnn,techcrunch',  # 指定新闻源
    'language': 'zh',
    'sort_by': 'relevancy'  # 按相关性排序
}
```

### 2. 批量处理
```python
# 批量处理多个关键词
keywords = ["人工智能", "机器学习", "深度学习", "自然语言处理"]

for keyword in keywords:
    generator = EnhancedNewsWordCloudGenerator(api_type="newsapi")
    generator.run_enhanced_pipeline(query=keyword)
```

### 3. 定时任务
```python
# 使用 schedule 库定时获取新闻
import schedule
import time

def daily_news_job():
    generator = EnhancedNewsWordCloudGenerator(api_type="newsapi")
    generator.run_enhanced_pipeline(query="科技")

# 每天上午 9 点运行
schedule.every().day.at("09:00").do(daily_news_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 性能优化建议

1. **使用缓存**: 启用缓存减少 API 请求
2. **批量请求**: 合理设置 pageSize 参数
3. **错误重试**: 实现重试机制处理临时错误
4. **本地存储**: 将新闻数据保存到本地文件
5. **异步处理**: 使用异步请求提高效率

## 扩展开发

### 添加新的 API
1. 在 `news_api_demo.py` 中创建新的 API 客户端类
2. 在 `news_api_config.py` 的 `API_TYPES` 中添加配置
3. 更新 `NewsAPIManager` 类支持新 API

### 自定义数据处理
```python
class CustomNewsProcessor:
    def process_article(self, article):
        # 自定义处理逻辑
        article['processed_content'] = self.clean_text(article['content'])
        return article
```

## 联系与支持

如有问题，请:
1. 查看项目 README.md
2. 检查日志文件 `logs/app.log`
3. 参考 NewsAPI 官方文档: https://newsapi.org/docs

## 更新日志

### v1.0.0
- 初始版本发布
- 支持 NewsAPI.org
- 支持模拟 API
- 集成词云生成功能
- 添加基于 HuggingFace 的情感分析模块

---

# 许可证

本项目采用 MIT 许可证。使用前请阅读 LICENSE 文件。
