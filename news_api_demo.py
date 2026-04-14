"""
新闻API接入演示 - 支持多种新闻API
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsAPIClient:
    """新闻API客户端基类"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = ""
    
    def fetch_news(self, query: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取新闻文章"""
        raise NotImplementedError
    
    def parse_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析文章数据"""
        raise NotImplementedError

class NewsAPIOfficial(NewsAPIClient):
    """NewsAPI.org官方API"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch_news(self, query: str, days: int = 7) -> List[Dict[str, Any]]:
        """从NewsAPI获取新闻"""
        articles = []
        
        try:
            # 计算日期范围
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # API参数
            params = {
                'q': query,
                'apiKey': self.api_key,
                'pageSize': 50,
                'language': 'zh',
                'sortBy': 'publishedAt',
                'from': from_date
            }
            
            logger.info(f"正在从NewsAPI获取新闻，关键词: {query}")
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'ok':
                    raw_articles = data.get('articles', [])
                    articles = [self.parse_article(article) for article in raw_articles]
                    logger.info(f"成功获取 {len(articles)} 篇新闻文章")
                else:
                    logger.error(f"API返回错误: {data.get('message', 'Unknown error')}")
            else:
                logger.error(f"API请求失败: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}")
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
        
        return articles
    
    def parse_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析NewsAPI文章数据"""
        return {
            'title': article_data.get('title', ''),
            'content': article_data.get('content', '') or article_data.get('description', ''),
            'source': article_data.get('source', {}).get('name', ''),
            'published_at': article_data.get('publishedAt', ''),
            'url': article_data.get('url', ''),
            'author': article_data.get('author', ''),
            'api_source': 'NewsAPI'
        }

class TencentNewsAPI(NewsAPIClient):
    """腾讯新闻API（示例）"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.news.qq.com/news"
    
    def fetch_news(self, query: str, days: int = 7) -> List[Dict[str, Any]]:
        """从腾讯新闻API获取新闻"""
        articles = []
        
        try:
            # 腾讯新闻API参数
            params = {
                'key': self.api_key,
                'keyword': query,
                'num': 50,
                'page': 1
            }
            
            logger.info(f"正在从腾讯新闻API获取新闻，关键词: {query}")
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 0:
                    raw_articles = data.get('data', {}).get('list', [])
                    articles = [self.parse_article(article) for article in raw_articles]
                    logger.info(f"成功获取 {len(articles)} 篇新闻文章")
                else:
                    logger.error(f"API返回错误: {data.get('msg', 'Unknown error')}")
            else:
                logger.error(f"API请求失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
        
        return articles
    
    def parse_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析腾讯新闻文章数据"""
        return {
            'title': article_data.get('title', ''),
            'content': article_data.get('content', '') or article_data.get('summary', ''),
            'source': article_data.get('source', '腾讯新闻'),
            'published_at': article_data.get('time', ''),
            'url': article_data.get('url', ''),
            'author': article_data.get('author', ''),
            'api_source': 'TencentNews'
        }

class MockNewsAPI(NewsAPIClient):
    """模拟新闻API（用于测试）"""
    
    def __init__(self, api_key: str = "mock_key"):
        super().__init__(api_key)
    
    def fetch_news(self, query: str, days: int = 7) -> List[Dict[str, Any]]:
        """生成模拟新闻数据"""
        logger.info(f"生成模拟新闻数据，关键词: {query}")
        
        # 模拟新闻数据
        mock_articles = [
            {
                'title': f'{query}领域取得重大突破',
                'content': f'近日，在{query}领域，研究人员取得了重大突破。这项技术有望改变行业格局。',
                'source': '科技日报',
                'published_at': datetime.now().isoformat(),
                'url': 'https://example.com/news/1',
                'author': '张三',
                'api_source': 'MockAPI'
            },
            {
                'title': f'{query}市场前景分析',
                'content': f'专家表示，{query}市场在未来五年内将保持高速增长。投资者应关注相关机会。',
                'source': '财经新闻',
                'published_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'url': 'https://example.com/news/2',
                'author': '李四',
                'api_source': 'MockAPI'
            },
            {
                'title': f'{query}政策解读',
                'content': f'政府发布新的{query}相关政策，旨在促进行业健康发展。',
                'source': '政策研究',
                'published_at': (datetime.now() - timedelta(days=2)).isoformat(),
                'url': 'https://example.com/news/3',
                'author': '王五',
                'api_source': 'MockAPI'
            }
        ]
        
        return mock_articles
    
    def parse_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """直接返回模拟数据"""
        return article_data

class NewsAPIManager:
    """新闻API管理器"""
    
    def __init__(self, api_type: str = "newsapi", api_key: str = None):
        """
        初始化API管理器
        
        Args:
            api_type: API类型，可选值: "newsapi", "tencent", "mock"
            api_key: API密钥
        """
        self.api_type = api_type
        self.api_key = api_key
        
        # 创建API客户端
        if api_type == "newsapi":
            self.client = NewsAPIOfficial(api_key or "your_newsapi_key_here")
        elif api_type == "tencent":
            self.client = TencentNewsAPI(api_key or "your_tencent_key_here")
        elif api_type == "mock":
            self.client = MockNewsAPI()
        else:
            raise ValueError(f"不支持的API类型: {api_type}")
    
    def get_news(self, query: str = "科技", days: int = 7) -> List[Dict[str, Any]]:
        """获取新闻"""
        return self.client.fetch_news(query, days)
    
    def save_articles_to_file(self, articles: List[Dict[str, Any]], output_dir: Path) -> int:
        """保存文章到文件"""
        saved_count = 0
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, article in enumerate(articles, 1):
            try:
                # 创建文章内容
                content = f"标题: {article['title']}\n\n"
                content += f"来源: {article['source']}\n"
                content += f"作者: {article.get('author', '未知')}\n"
                content += f"发布时间: {article['published_at']}\n"
                content += f"API来源: {article.get('api_source', '未知')}\n"
                content += f"原文链接: {article['url']}\n\n"
                content += f"内容:\n{article['content']}"
                
                # 生成文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"article_{i:03d}_{timestamp}.txt"
                filepath = output_dir / filename
                
                # 保存文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                saved_count += 1
                logger.info(f"已保存第 {i} 篇文章: {filename}")
                
            except Exception as e:
                logger.error(f"保存文章失败: {e}")
        
        logger.info(f"成功保存 {saved_count}/{len(articles)} 篇文章")
        return saved_count
    
    def display_articles_summary(self, articles: List[Dict[str, Any]]):
        """显示文章摘要"""
        print(f"\n{'='*60}")
        print(f"新闻摘要 - 共 {len(articles)} 篇文章")
        print(f"{'='*60}")
        
        for i, article in enumerate(articles, 1):
            print(f"\n文章 {i}:")
            print(f"  标题: {article['title'][:50]}...")
            print(f"  来源: {article['source']}")
            print(f"  发布时间: {article['published_at'][:19]}")
            print(f"  API来源: {article.get('api_source', '未知')}")
            print(f"  内容预览: {article['content'][:100]}...")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='新闻API接入演示')
    parser.add_argument('--api-type', type=str, default='mock', 
                       choices=['newsapi', 'tencent', 'mock'],
                       help='API类型: newsapi, tencent, mock')
    parser.add_argument('--api-key', type=str, help='API密钥')
    parser.add_argument('--query', type=str, default='科技', help='搜索关键词')
    parser.add_argument('--days', type=int, default=7, help='获取最近几天的新闻')
    parser.add_argument('--output-dir', type=str, default='./data/news_demo',
                       help='输出目录')
    
    args = parser.parse_args()
    
    # 创建API管理器
    try:
        manager = NewsAPIManager(
            api_type=args.api_type,
            api_key=args.api_key
        )
        
        # 获取新闻
        print(f"使用 {args.api_type.upper()} API 获取新闻...")
        articles = manager.get_news(
            query=args.query,
            days=args.days
        )
        
        if not articles:
            print("未能获取到新闻文章")
            return
        
        # 显示摘要
        manager.display_articles_summary(articles)
        
        # 保存到文件
        output_dir = Path(args.output_dir)
        saved_count = manager.save_articles_to_file(articles, output_dir)
        
        print(f"\n{'='*60}")
        print(f"新闻获取完成！")
        print(f"API类型: {args.api_type}")
        print(f"关键词: {args.query}")
        print(f"获取文章数: {len(articles)}")
        print(f"保存文件数: {saved_count}")
        print(f"保存目录: {output_dir.absolute()}")
        print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        raise

def test_all_apis():
    """测试所有API"""
    print("测试所有新闻API...")
    
    test_queries = ["科技", "人工智能", "金融"]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"测试关键词: {query}")
        print(f"{'='*60}")
        
        # 测试模拟API
        try:
            mock_manager = NewsAPIManager(api_type="mock")
            mock_articles = mock_manager.get_news(query=query, days=1)
            print(f"模拟API: 获取到 {len(mock_articles)} 篇文章")
        except Exception as e:
            print(f"模拟API测试失败: {e}")
        
        # 提示用户如何配置真实API
        print("\n要使用真实API，请:")
        print("1. 注册NewsAPI账号: https://newsapi.org/register")
        print("2. 获取API密钥")
        print("3. 运行: python news_api_demo.py --api-type newsapi --api-key YOUR_KEY --query '科技'")

if __name__ == "__main__":
    # 运行演示
    main()
    
    # 或者运行测试
    # test_all_apis()