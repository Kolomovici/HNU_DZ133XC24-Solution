"""
新闻API集成示例 - 将新闻API集成到现有词云项目中
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from news_api_demo import NewsAPIManager
from news_api_config import get_configured_api_key
from news_wordcloud import NewsWordCloudGenerator
from utils import save_json  # 导入save_json函数
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedNewsWordCloudGenerator(NewsWordCloudGenerator):
    """增强版新闻词云生成器，支持多种API"""
    
    def __init__(self, api_type: str = "mock", api_key: str = None):
        """初始化增强版生成器"""
        # 先调用父类初始化
        super().__init__(api_key=api_key)
        
        # 设置API类型
        self.api_type = api_type
        
        # 创建API管理器
        if not api_key and api_type != "mock":
            # 尝试从配置文件获取密钥
            api_key = get_configured_api_key(api_type)
        
        self.api_manager = NewsAPIManager(
            api_type=api_type,
            api_key=api_key
        )
        
        logger.info(f"初始化增强版新闻词云生成器，API类型: {api_type}")
    
    def fetch_news_from_api(self, query: str = "科技", days: int = 7):
        """
        从API获取新闻文章（重写父类方法）
        
        Args:
            query: 搜索关键词
            days: 获取最近几天的新闻
            
        Returns:
            新闻文章列表
        """
        logger.info(f"使用 {self.api_type} API 获取新闻，关键词: {query}")
        
        # 使用API管理器获取新闻
        articles = self.api_manager.get_news(query=query, days=days)
        
        if articles:
            # 转换为与父类兼容的格式
            formatted_articles = []
            for article in articles:
                formatted_article = {
                    'title': article.get('title', ''),
                    'content': article.get('content', ''),
                    'description': article.get('content', '')[:200] + '...' if article.get('content') else '',
                    'source': {'name': article.get('source', '未知来源')},
                    'publishedAt': article.get('published_at', ''),
                    'url': article.get('url', ''),
                    'author': article.get('author', '')
                }
                formatted_articles.append(formatted_article)
            
            # 缓存文章数据
            cache_data = {
                'query': query,
                'fetch_time': datetime.now().isoformat(),
                'articles': formatted_articles
            }
            save_json(cache_data, self.articles_cache)  # 使用导入的save_json函数
            
            logger.info(f"成功获取 {len(formatted_articles)} 篇新闻文章")
            return formatted_articles
        else:
            logger.warning("未能获取到新闻文章，尝试使用父类方法")
            return super().fetch_news_from_api(query, days)
    
    def run_enhanced_pipeline(self, query: str = "科技", use_cache: bool = True):
        """
        运行增强版新闻词云生成流程
        
        Args:
            query: 搜索关键词
            use_cache: 是否使用缓存
        """
        logger.info("开始增强版新闻词云生成流程...")
        
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
        
        logger.info("增强版新闻词云生成流程完成！")

def demo_integration():
    """演示集成功能"""
    print("新闻API集成演示")
    print("="*60)
    
    # 演示1: 使用模拟API
    print("\n1. 使用模拟API生成词云")
    print("-"*40)
    
    mock_generator = EnhancedNewsWordCloudGenerator(api_type="mock")
    mock_generator.run_enhanced_pipeline(query="人工智能", use_cache=False)
    
    # 演示2: 使用NewsAPI（如果已配置）
    print("\n2. 尝试使用NewsAPI（如果已配置）")
    print("-"*40)
    
    try:
        # 检查是否配置了NewsAPI密钥
        from news_api_config import APIKeyManager
        key_manager = APIKeyManager()
        newsapi_key = key_manager.get_key("newsapi")
        
        if newsapi_key:
            newsapi_generator = EnhancedNewsWordCloudGenerator(
                api_type="newsapi",
                api_key=newsapi_key
            )
            newsapi_generator.run_enhanced_pipeline(query="科技", use_cache=False)
        else:
            print("未配置NewsAPI密钥，跳过此演示")
            print("请运行 'python news_api_config.py --setup' 配置API密钥")
    
    except Exception as e:
        print(f"NewsAPI演示失败: {e}")
    
    # 演示3: 批量处理多个关键词
    print("\n3. 批量处理多个关键词")
    print("-"*40)
    
    keywords = ["人工智能", "大数据", "云计算", "区块链"]
    
    for keyword in keywords:
        print(f"\n处理关键词: {keyword}")
        generator = EnhancedNewsWordCloudGenerator(api_type="mock")
        generator.run_enhanced_pipeline(query=keyword, use_cache=False)

def compare_apis():
    """比较不同API的表现"""
    print("不同新闻API比较")
    print("="*60)
    
    test_query = "科技"
    
    # 测试模拟API
    print("\n1. 模拟API测试:")
    mock_manager = NewsAPIManager(api_type="mock")
    mock_articles = mock_manager.get_news(query=test_query)
    print(f"   获取文章数: {len(mock_articles)}")
    print(f"   文章示例: {mock_articles[0]['title'][:50]}...")
    
    # 测试NewsAPI（如果已配置）
    print("\n2. NewsAPI测试:")
    try:
        from news_api_config import get_configured_api_key
        newsapi_key = get_configured_api_key("newsapi")
        
        if newsapi_key:
            newsapi_manager = NewsAPIManager(
                api_type="newsapi",
                api_key=newsapi_key
            )
            newsapi_articles = newsapi_manager.get_news(query=test_query)
            print(f"   获取文章数: {len(newsapi_articles)}")
            if newsapi_articles:
                print(f"   文章示例: {newsapi_articles[0]['title'][:50]}...")
        else:
            print("   未配置API密钥")
    
    except Exception as e:
        print(f"   测试失败: {e}")
    
    print("\n结论:")
    print("- 模拟API: 适合开发和测试，无需网络连接")
    print("- NewsAPI: 提供真实新闻数据，需要API密钥")
    print("- 腾讯新闻API: 中文新闻覆盖更好，需要申请企业API")

def main():
    """主函数"""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='新闻API集成示例')
    parser.add_argument('--demo', action='store_true', help='运行集成演示')
    parser.add_argument('--compare', action='store_true', help='比较不同API')
    parser.add_argument('--api-type', type=str, default='mock', 
                       choices=['mock', 'newsapi', 'tencent'],
                       help='API类型')
    parser.add_argument('--query', type=str, default='科技', help='搜索关键词')
    parser.add_argument('--use-cache', action='store_true', help='使用缓存')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_integration()
    elif args.compare:
        compare_apis()
    else:
        # 运行单个流程
        print(f"使用 {args.api_type} API 生成词云")
        print(f"搜索关键词: {args.query}")
        print(f"使用缓存: {args.use_cache}")
        print("="*60)
        
        generator = EnhancedNewsWordCloudGenerator(api_type=args.api_type)
        generator.run_enhanced_pipeline(
            query=args.query,
            use_cache=args.use_cache
        )

if __name__ == "__main__":
    # 需要导入datetime
    from datetime import datetime
    
    main()