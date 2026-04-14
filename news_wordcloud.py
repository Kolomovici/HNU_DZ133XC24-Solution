"""
新闻文章词云生成模块 - 从开放API获取新闻并生成词云
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from config import (
    NEWS_API_CONFIG, WORDCLOUD_CONFIG, NEWS_DIR, 
    WORDCLOUD_DIR, PROJECT_ROOT, DEFAULT_FONT
)
from utils import (
    clean_text, save_text_to_file, load_text_from_file,
    save_json, load_json, check_font_file
)

# 设置日志
logger = logging.getLogger(__name__)

class NewsWordCloudGenerator:
    """新闻词云生成器"""
    
    def __init__(self, api_key: str = None):
        """初始化"""
        self.api_key = api_key or NEWS_API_CONFIG['api_key']
        self.base_url = NEWS_API_CONFIG['base_url']
        self.page_size = NEWS_API_CONFIG['page_size']
        
        # 检查字体文件
        if not check_font_file(Path(DEFAULT_FONT)):
            logger.warning("未找到中文字体文件，词云可能无法正确显示中文")
        
        # 创建必要的目录
        NEWS_DIR.mkdir(parents=True, exist_ok=True)
        WORDCLOUD_DIR.mkdir(parents=True, exist_ok=True)
        
        # 加载停用词
        self.stopwords = self._load_stopwords()
        
        # 新闻文章缓存
        self.articles_cache = NEWS_DIR / 'articles_cache.json'
    
    def _load_stopwords(self) -> set:
        """加载停用词"""
        stopwords_file = PROJECT_ROOT / 'data' / 'stopwords.txt'
        stopwords = set()
        
        if stopwords_file.exists():
            try:
                with open(stopwords_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip()
                        if word:
                            stopwords.add(word)
                logger.info(f"已加载 {len(stopwords)} 个停用词")
            except Exception as e:
                logger.error(f"加载停用词失败: {e}")
        
        return stopwords
    
    def fetch_news_from_api(self, query: str = "科技", days: int = 7) -> List[Dict[str, Any]]:
        """
        从新闻API获取新闻文章
        
        Args:
            query: 搜索关键词
            days: 获取最近几天的新闻
            
        Returns:
            新闻文章列表
        """
        articles = []
        
        try:
            # 计算日期范围
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # API参数
            params = {
                'q': query,
                'apiKey': self.api_key,
                'pageSize': self.page_size,
                'language': NEWS_API_CONFIG['language'],
                'sortBy': NEWS_API_CONFIG['sort_by'],
                'from': from_date
            }
            
            logger.info(f"正在从API获取新闻，关键词: {query}")
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'ok':
                    articles = data.get('articles', [])
                    logger.info(f"成功获取 {len(articles)} 篇新闻文章")
                    
                    # 缓存文章数据
                    cache_data = {
                        'query': query,
                        'fetch_time': datetime.now().isoformat(),
                        'articles': articles
                    }
                    save_json(cache_data, self.articles_cache)
                else:
                    logger.error(f"API返回错误: {data.get('message', 'Unknown error')}")
            else:
                logger.error(f"API请求失败: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}")
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
        
        return articles
    
    def load_cached_news(self) -> Optional[List[Dict[str, Any]]]:
        """加载缓存的新闻文章"""
        if self.articles_cache.exists():
            cache_data = load_json(self.articles_cache)
            if cache_data and 'articles' in cache_data:
                logger.info(f"从缓存加载 {len(cache_data['articles'])} 篇新闻文章")
                return cache_data['articles']
        
        return None
    
    def save_article_to_file(self, article: Dict[str, Any], index: int) -> bool:
        """
        保存单篇文章到文本文件
        
        Args:
            article: 文章数据
            index: 文章索引
            
        Returns:
            是否保存成功
        """
        try:
            # 提取文章内容
            title = article.get('title', '')
            content = article.get('content', '') or article.get('description', '')
            source = article.get('source', {}).get('name', '')
            published_at = article.get('publishedAt', '')
            url = article.get('url', '')
            
            # 清理和组合文本
            full_text = f"标题: {title}\n\n"
            full_text += f"来源: {source}\n"
            full_text += f"发布时间: {published_at}\n"
            full_text += f"原文链接: {url}\n\n"
            full_text += f"内容:\n{content}"
            
            # 清理文本
            full_text = clean_text(full_text)
            
            # 生成文件名
            filename = f"article_{index:03d}_{datetime.now().strftime('%Y%m%d')}.txt"
            filepath = NEWS_DIR / filename
            
            # 保存文件
            return save_text_to_file(full_text, filepath)
            
        except Exception as e:
            logger.error(f"保存文章失败: {e}")
            return False
    
    def save_all_articles(self, articles: List[Dict[str, Any]]) -> int:
        """
        保存所有文章到独立的文本文件
        
        Args:
            articles: 文章列表
            
        Returns:
            成功保存的文章数量
        """
        saved_count = 0
        
        logger.info(f"开始保存 {len(articles)} 篇文章...")
        
        for i, article in enumerate(articles, 1):
            if self.save_article_to_file(article, i):
                saved_count += 1
                logger.info(f"已保存第 {i} 篇文章")
            
            # 避免请求过快
            time.sleep(0.1)
        
        logger.info(f"成功保存 {saved_count}/{len(articles)} 篇文章")
        return saved_count
    
    def process_text_for_wordcloud(self, text: str) -> str:
        """
        处理文本用于生成词云
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        # 分词
        words = jieba.lcut(text)
        
        # 移除停用词
        filtered_words = [word for word in words if word not in self.stopwords]
        
        # 移除单个字符（除了中文）
        filtered_words = [word for word in filtered_words if len(word) > 1 or '\u4e00' <= word <= '\u9fff']
        
        # 用空格连接
        return ' '.join(filtered_words)
    
    def generate_wordcloud(self, text: str, output_path: Path, 
                          mask_image: Optional[Path] = None) -> bool:
        """
        生成词云图
        
        Args:
            text: 处理后的文本
            output_path: 输出图片路径
            mask_image: 掩码图片路径（可选）
            
        Returns:
            是否生成成功
        """
        try:
            # 准备掩码
            mask = None
            if mask_image and mask_image.exists():
                mask = np.array(Image.open(mask_image))
            
            # 创建词云
            wc = WordCloud(
                font_path=DEFAULT_FONT,
                width=WORDCLOUD_CONFIG['width'],
                height=WORDCLOUD_CONFIG['height'],
                background_color=WORDCLOUD_CONFIG['background_color'],
                max_words=WORDCLOUD_CONFIG['max_words'],
                max_font_size=WORDCLOUD_CONFIG['max_font_size'],
                random_state=WORDCLOUD_CONFIG['random_state'],
                mask=mask,
                contour_width=1,
                contour_color='steelblue'
            )
            
            # 生成词云
            wc.generate(text)
            
            # 保存图片
            plt.figure(figsize=(12, 8))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"词云图已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成词云失败: {e}")
            return False
    
    def generate_wordcloud_for_article(self, article_file: Path) -> bool:
        """
        为单篇文章生成词云
        
        Args:
            article_file: 文章文本文件路径
            
        Returns:
            是否生成成功
        """
        try:
            # 读取文章内容
            text = load_text_from_file(article_file)
            if not text:
                return False
            
            # 处理文本
            processed_text = self.process_text_for_wordcloud(text)
            
            # 生成输出文件名
            output_filename = article_file.stem + '.png'
            output_path = WORDCLOUD_DIR / output_filename
            
            # 生成词云
            return self.generate_wordcloud(processed_text, output_path)
            
        except Exception as e:
            logger.error(f"为文章生成词云失败 {article_file}: {e}")
            return False
    
    def generate_all_wordclouds(self) -> int:
        """
        为所有文章生成词云
        
        Returns:
            成功生成的词云数量
        """
        generated_count = 0
        
        # 获取所有文章文件
        article_files = list(NEWS_DIR.glob('*.txt'))
        
        if not article_files:
            logger.warning("没有找到文章文件")
            return 0
        
        logger.info(f"开始为 {len(article_files)} 篇文章生成词云...")
        
        for i, article_file in enumerate(article_files, 1):
            if self.generate_wordcloud_for_article(article_file):
                generated_count += 1
                logger.info(f"已生成第 {i} 个词云")
        
        logger.info(f"成功生成 {generated_count}/{len(article_files)} 个词云")
        return generated_count
    
    def generate_combined_wordcloud(self, output_name: str = "combined_wordcloud.png") -> bool:
        """
        生成所有文章的合并词云
        
        Args:
            output_name: 输出文件名
            
        Returns:
            是否生成成功
        """
        try:
            all_text = ""
            
            # 读取所有文章
            article_files = list(NEWS_DIR.glob('*.txt'))
            
            for article_file in article_files:
                text = load_text_from_file(article_file)
                if text:
                    all_text += text + "\n\n"
            
            if not all_text:
                logger.warning("没有找到文章内容")
                return False
            
            # 处理文本
            processed_text = self.process_text_for_wordcloud(all_text)
            
            # 生成输出路径
            output_path = WORDCLOUD_DIR / output_name
            
            # 生成词云
            return self.generate_wordcloud(processed_text, output_path)
            
        except Exception as e:
            logger.error(f"生成合并词云失败: {e}")
            return False
    
    def run_full_pipeline(self, query: str = "科技", use_cache: bool = True):
        """
        运行完整的新闻词云生成流程
        
        Args:
            query: 搜索关键词
            use_cache: 是否使用缓存
        """
        logger.info("开始新闻词云生成流程...")
        
        # 1. 获取新闻文章
        articles = []
        
        if use_cache:
            articles = self.load_cached_news()
        
        if not articles:
            articles = self.fetch_news_from_api(query)
        
        if not articles:
            logger.error("无法获取新闻文章，流程终止")
            return
        
        # 2. 保存文章到文件
        saved_count = self.save_all_articles(articles)
        
        if saved_count == 0:
            logger.error("没有成功保存文章，流程终止")
            return
        
        # 3. 为每篇文章生成词云
        wordcloud_count = self.generate_all_wordclouds()
        
        # 4. 生成合并词云
        if wordcloud_count > 0:
            self.generate_combined_wordcloud()
        
        logger.info("新闻词云生成流程完成！")

def main():
    """主函数"""
    import argparse
    from datetime import timedelta
    
    parser = argparse.ArgumentParser(description='新闻词云生成工具')
    parser.add_argument('--query', type=str, default='科技', help='搜索关键词')
    parser.add_argument('--days', type=int, default=7, help='获取最近几天的新闻')
    parser.add_argument('--api-key', type=str, help='NewsAPI密钥')
    parser.add_argument('--no-cache', action='store_true', help='不使用缓存')
    parser.add_argument('--single-file', type=str, help='为单个文件生成词云')
    
    args = parser.parse_args()
    
    # 创建词云生成器
    generator = NewsWordCloudGenerator(api_key=args.api_key)
    
    if args.single_file:
        # 为单个文件生成词云
        article_file = Path(args.single_file)
        if article_file.exists():
            success = generator.generate_wordcloud_for_article(article_file)
            if success:
                print(f"成功为 {article_file.name} 生成词云")
            else:
                print(f"为 {article_file.name} 生成词云失败")
        else:
            print(f"文件不存在: {args.single_file}")
    
    else:
        # 运行完整流程
        generator.run_full_pipeline(
            query=args.query,
            use_cache=not args.no_cache
        )

if __name__ == "__main__":
    main()