"""
新闻API配置管理
"""

import os
from pathlib import Path
from typing import Dict, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
NEWS_DATA_DIR = DATA_DIR / "news_data"
API_CONFIG_DIR = DATA_DIR / "api_configs"

# 创建必要的目录
for directory in [DATA_DIR, NEWS_DATA_DIR, API_CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class NewsAPIConfig:
    """新闻API配置类"""
    
    # 支持的API类型
    API_TYPES = {
        "newsapi": {
            "name": "NewsAPI.org",
            "base_url": "https://newsapi.org/v2",
            "endpoints": {
                "everything": "/everything",
                "top_headlines": "/top-headlines",
                "sources": "/sources"
            },
            "required_params": ["apiKey"],
            "optional_params": {
                "everything": ["q", "sources", "domains", "from", "to", "language", "sortBy", "pageSize", "page"],
                "top_headlines": ["country", "category", "sources", "q", "pageSize", "page"]
            },
            "rate_limit": 100,  # 每天请求限制
            "website": "https://newsapi.org",
            "registration_url": "https://newsapi.org/register",
            "pricing": "免费层: 100请求/天"
        },
        "tencent": {
            "name": "腾讯新闻API",
            "base_url": "https://api.news.qq.com",
            "endpoints": {
                "search": "/news/search",
                "hot": "/news/hot"
            },
            "required_params": ["key"],
            "optional_params": {
                "search": ["keyword", "num", "page", "sort"]
            },
            "rate_limit": 1000,  # 每天请求限制
            "website": "https://news.qq.com",
            "registration_url": "https://open.tencent.com/",
            "pricing": "需申请API密钥"
        },
        "baidu": {
            "name": "百度新闻搜索",
            "base_url": "https://news.baidu.com",
            "endpoints": {
                "search": "/news"
            },
            "required_params": [],
            "optional_params": {
                "search": ["word", "tn", "ie", "cl", "ct", "rn", "lm"]
            },
            "rate_limit": "未知",
            "website": "https://news.baidu.com",
            "registration_url": "无需注册",
            "pricing": "免费"
        },
        "mock": {
            "name": "模拟API",
            "base_url": "",
            "endpoints": {},
            "required_params": [],
            "optional_params": {},
            "rate_limit": "无限制",
            "website": "",
            "registration_url": "",
            "pricing": "免费"
        }
    }
    
    @classmethod
    def get_api_info(cls, api_type: str) -> Dict[str, Any]:
        """获取API信息"""
        if api_type not in cls.API_TYPES:
            raise ValueError(f"不支持的API类型: {api_type}")
        
        return cls.API_TYPES[api_type]
    
    @classmethod
    def list_available_apis(cls) -> list:
        """列出所有可用的API"""
        return list(cls.API_TYPES.keys())
    
    @classmethod
    def get_api_details(cls, api_type: str) -> str:
        """获取API详细信息"""
        info = cls.get_api_info(api_type)
        
        details = f"""
{info['name']} ({api_type})
{'='*50}
基本信息:
  - 基础URL: {info['base_url']}
  - 网站: {info['website']}
  - 注册地址: {info['registration_url']}
  - 价格: {info['pricing']}
  - 请求限制: {info['rate_limit']}

可用端点:
"""
        for endpoint, path in info['endpoints'].items():
            details += f"  - {endpoint}: {path}\n"
        
        details += f"""
必需参数: {', '.join(info['required_params'])}
"""
        
        for endpoint, params in info['optional_params'].items():
            if params:
                details += f"\n{endpoint}端点可选参数:\n"
                for param in params:
                    details += f"  - {param}\n"
        
        return details

class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self):
        self.config_file = API_CONFIG_DIR / "api_keys.json"
        self.keys = self._load_keys()
    
    def _load_keys(self) -> Dict[str, str]:
        """加载API密钥"""
        if self.config_file.exists():
            try:
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_keys(self):
        """保存API密钥"""
        import json
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.keys, f, ensure_ascii=False, indent=2)
    
    def set_key(self, api_type: str, api_key: str):
        """设置API密钥"""
        self.keys[api_type] = api_key
        self.save_keys()
        print(f"已保存 {api_type} API密钥")
    
    def get_key(self, api_type: str) -> str:
        """获取API密钥"""
        return self.keys.get(api_type, "")
    
    def remove_key(self, api_type: str):
        """移除API密钥"""
        if api_type in self.keys:
            del self.keys[api_type]
            self.save_keys()
            print(f"已移除 {api_type} API密钥")
    
    def list_keys(self):
        """列出所有API密钥"""
        if not self.keys:
            print("未配置任何API密钥")
            return
        
        print("已配置的API密钥:")
        for api_type, key in self.keys.items():
            masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            print(f"  {api_type}: {masked_key}")

def setup_newsapi():
    """设置NewsAPI配置"""
    print("\n设置 NewsAPI.org")
    print("="*50)
    
    config = NewsAPIConfig.get_api_info("newsapi")
    print(f"API名称: {config['name']}")
    print(f"网站: {config['website']}")
    print(f"注册地址: {config['registration_url']}")
    print(f"免费限制: {config['pricing']}")
    
    print("\n使用步骤:")
    print("1. 访问 https://newsapi.org/register 注册账号")
    print("2. 登录后获取API密钥")
    print("3. 将API密钥配置到系统中")
    
    api_key = input("\n请输入您的NewsAPI密钥 (直接回车跳过): ").strip()
    
    if api_key:
        key_manager = APIKeyManager()
        key_manager.set_key("newsapi", api_key)
        print("NewsAPI配置完成！")
    else:
        print("未配置NewsAPI密钥，将使用模拟API")

def setup_tencent_news():
    """设置腾讯新闻API配置"""
    print("\n设置 腾讯新闻API")
    print("="*50)
    
    config = NewsAPIConfig.get_api_info("tencent")
    print(f"API名称: {config['name']}")
    print(f"网站: {config['website']}")
    print(f"注册地址: {config['registration_url']}")
    
    print("\n注意: 腾讯新闻API需要申请企业API密钥")
    print("对于个人项目，建议使用NewsAPI或模拟API")
    
    api_key = input("\n请输入您的腾讯新闻API密钥 (直接回车跳过): ").strip()
    
    if api_key:
        key_manager = APIKeyManager()
        key_manager.set_key("tencent", api_key)
        print("腾讯新闻API配置完成！")
    else:
        print("未配置腾讯新闻API密钥")

def interactive_setup():
    """交互式配置向导"""
    print("新闻API配置向导")
    print("="*50)
    
    while True:
        print("\n请选择要配置的API:")
        print("1. NewsAPI.org (推荐)")
        print("2. 腾讯新闻API")
        print("3. 查看所有API信息")
        print("4. 查看已配置的密钥")
        print("5. 退出配置")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == "1":
            setup_newsapi()
        elif choice == "2":
            setup_tencent_news()
        elif choice == "3":
            print("\n所有可用的新闻API:")
            for api_type in NewsAPIConfig.list_available_apis():
                print(f"\n{NewsAPIConfig.get_api_details(api_type)}")
        elif choice == "4":
            key_manager = APIKeyManager()
            key_manager.list_keys()
        elif choice == "5":
            print("配置完成！")
            break
        else:
            print("无效选项，请重新选择")

def get_configured_api_key(api_type: str) -> str:
    """获取已配置的API密钥"""
    key_manager = APIKeyManager()
    return key_manager.get_key(api_type)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='新闻API配置管理')
    parser.add_argument('--setup', action='store_true', help='运行交互式配置向导')
    parser.add_argument('--list-apis', action='store_true', help='列出所有可用的API')
    parser.add_argument('--api-info', type=str, help='查看特定API的详细信息')
    parser.add_argument('--list-keys', action='store_true', help='列出已配置的API密钥')
    parser.add_argument('--set-key', nargs=2, metavar=('API_TYPE', 'API_KEY'), 
                       help='设置API密钥，例如: --set-key newsapi your_api_key')
    parser.add_argument('--remove-key', type=str, help='移除API密钥')
    
    args = parser.parse_args()
    
    if args.setup:
        interactive_setup()
    elif args.list_apis:
        print("所有可用的新闻API:")
        for api_type in NewsAPIConfig.list_available_apis():
            info = NewsAPIConfig.get_api_info(api_type)
            print(f"\n{api_type}: {info['name']}")
            print(f"  网站: {info['website']}")
            print(f"  价格: {info['pricing']}")
    elif args.api_info:
        try:
            print(NewsAPIConfig.get_api_details(args.api_info))
        except ValueError as e:
            print(f"错误: {e}")
    elif args.list_keys:
        key_manager = APIKeyManager()
        key_manager.list_keys()
    elif args.set_key:
        api_type, api_key = args.set_key
        key_manager = APIKeyManager()
        key_manager.set_key(api_type, api_key)
    elif args.remove_key:
        key_manager = APIKeyManager()
        key_manager.remove_key(args.remove_key)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()