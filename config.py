"""
配置文件 - 跨平台兼容性设置
"""

import os
import platform
from pathlib import Path

# 获取当前项目根目录
PROJECT_ROOT = Path(__file__).parent

# 平台检测
SYSTEM = platform.system()

# 数据目录配置
DATA_DIR = PROJECT_ROOT / "data"
NEWS_DIR = DATA_DIR / "news_articles"
WORDCLOUD_DIR = DATA_DIR / "wordclouds"
COMMENTS_DIR = DATA_DIR / "comments"

# 字体配置
FONTS_DIR = PROJECT_ROOT / "fonts"
# 跨平台字体路径设置
if SYSTEM == "Windows":
    # Windows系统字体路径
    DEFAULT_FONT = str(FONTS_DIR / "simhei.ttf")
elif SYSTEM == "Darwin":  # macOS
    # macOS系统字体路径
    DEFAULT_FONT = str(FONTS_DIR / "SimHei.ttf")
else:  # Linux/Ubuntu
    # Linux系统字体路径
    DEFAULT_FONT = str(FONTS_DIR / "SimHei.ttf")

# 创建必要的目录
for directory in [DATA_DIR, NEWS_DIR, WORDCLOUD_DIR, COMMENTS_DIR, FONTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API配置（使用您提供的API密钥）
NEWS_API_CONFIG = {
    'base_url': 'https://newsapi.org/v2/everything',
    'api_key': '________________________',  # 您的API密钥
    'page_size': 50,
    'language': 'zh',
    'sort_by': 'publishedAt'
}

# 分词配置
JIEBA_CONFIG = {
    'stopwords_file': str(PROJECT_ROOT / 'data' / 'stopwords.txt'),
    'user_dict': str(PROJECT_ROOT / 'data' / 'user_dict.txt')
}

# 词云配置
WORDCLOUD_CONFIG = {
    'width': 800,
    'height': 600,
    'background_color': 'white',
    'max_words': 200,
    'font_path': DEFAULT_FONT,
    'max_font_size': 100,
    'random_state': 42
}

# 情感分析配置
SENTIMENT_CONFIG = {
    'min_comment_length': 10,
    'batch_size': 100
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': str(PROJECT_ROOT / 'logs' / 'app.log')
}

# 创建日志目录
(PROJECT_ROOT / 'logs').mkdir(exist_ok=True)
