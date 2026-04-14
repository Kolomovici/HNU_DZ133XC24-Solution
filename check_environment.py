"""
环境检查脚本 - 验证运行环境是否准备就绪
"""

import sys
import os
import platform
from pathlib import Path
import subprocess

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    print(f"  Python版本: {sys.version}")
    
    if version.major == 3 and version.minor >= 8:
        print(f"  ✅ Python版本符合要求 (3.8+)")
        return True
    else:
        print(f"  ❌ Python版本过低，需要3.8或更高版本")
        return False

def check_pip_packages():
    """检查必要的pip包"""
    print("\n检查必要的Python包...")
    
    required_packages = [
        'jieba',
        'wordcloud',
        'matplotlib',
        'numpy',
        'pandas',
        'requests',
        'beautifulsoup4',
        'snownlp',
        'pypinyin',
        'PIL',
        'scikit-learn',
        'opencc'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
                package_name = 'Pillow'
            elif package == 'opencc':
                __import__('opencc')
                package_name = 'opencc-python-reimplemented'
            else:
                __import__(package)
                package_name = package
            
            print(f"  ✅ {package_name} 已安装")
        except ImportError:
            print(f"  ❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n  缺少以下包: {', '.join(missing_packages)}")
        print(f"  请运行: pip install -r requirements.txt")
        return False
    else:
        print(f"  ✅ 所有必要的Python包已安装")
        return True

def check_directories():
    """检查必要的目录"""
    print("\n检查必要的目录...")
    
    required_dirs = [
        'data',
        'data/comments',
        'data/news_articles',
        'data/wordclouds',
        'data/keyword_extraction',
        'data/jieba_comparison',
        'fonts'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ 目录存在: {dir_path}")
        else:
            print(f"  ⚠️  目录不存在: {dir_path}")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n  缺少以下目录:")
        for dir_path in missing_dirs:
            print(f"    - {dir_path}")
        print(f"\n  可以运行以下命令创建:")
        print(f"    mkdir {' '.join(missing_dirs)}")
        return False
    else:
        print(f"  ✅ 所有必要的目录已存在")
        return True

def check_fonts():
    """检查字体文件"""
    print("\n检查中文字体文件...")
    
    fonts_dir = Path("fonts")
    if not fonts_dir.exists():
        print(f"  ❌ fonts目录不存在")
        return False
    
    font_files = list(fonts_dir.glob("*"))
    if not font_files:
        print(f"  ❌ fonts目录中没有字体文件")
        print(f"  请运行: python download_fonts.py 或 .\\setup_fonts.ps1")
        return False
    
    # 检查常见的字体文件
    common_fonts = ['simhei.ttf', 'SimHei.ttf', 'msyh.ttc', 'simsun.ttc', 'NotoSansSC-Regular.otf']
    found_fonts = []
    
    for font_file in font_files:
        if font_file.name in common_fonts:
            found_fonts.append(font_file.name)
    
    if found_fonts:
        print(f"  ✅ 找到中文字体文件: {', '.join(found_fonts)}")
        return True
    else:
        print(f"  ⚠️  找到字体文件，但可能不是标准中文字体:")
        for font_file in font_files:
            print(f"    - {font_file.name}")
        print(f"\n  建议使用标准中文字体，可以运行: python download_fonts.py")
        return True  # 仍然返回True，因为可能有其他字体可用

def check_config():
    """检查配置文件"""
    print("\n检查配置文件...")
    
    config_file = Path("config.py")
    if not config_file.exists():
        print(f"  ❌ config.py文件不存在")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键配置
        checks = [
            ('PROJECT_ROOT', '项目根目录配置'),
            ('DATA_DIR', '数据目录配置'),
            ('DEFAULT_FONT', '默认字体配置'),
            ('JIEBA_CONFIG', '结巴分词配置')
        ]
        
        all_ok = True
        for key, description in checks:
            if key in content:
                print(f"  ✅ {description} 存在")
            else:
                print(f"  ⚠️  {description} 可能缺失")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"  ❌ 读取配置文件失败: {e}")
        return False

def check_sample_data():
    """检查示例数据"""
    print("\n检查示例数据...")
    
    sample_file = Path("data/sample_article.txt")
    if sample_file.exists():
        print(f"  ✅ 示例数据文件存在: {sample_file}")
        return True
    else:
        print(f"  ⚠️  示例数据文件不存在")
        print(f"  可以手动创建或使用工具生成数据")
        return True  # 不是必须的

def run_quick_test():
    """运行快速测试"""
    print("\n运行快速功能测试...")
    
    test_commands = [
        ("分词测试", "python -c \"import jieba; print('✅ 结巴分词导入成功')\""),
        ("关键词提取测试", "python -c \"from keyword_extraction import KeywordExtractor; print('✅ 关键词提取模块导入成功')\""),
        ("情感分析测试", "python -c \"from text_sentiment import TextSentimentAnalyzer; print('✅ 文本情感分析模块导入成功')\""),
    ]
    
    all_passed = True
    
    for test_name, command in test_commands:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {test_name} 通过")
            else:
                print(f"  ❌ {test_name} 失败: {result.stderr}")
                all_passed = False
        except Exception as e:
            print(f"  ❌ {test_name} 异常: {e}")
            all_passed = False
    
    return all_passed

def main():
    """主函数"""
    print("=" * 70)
    print("中文文本处理与分析工具 - 环境检查")
    print("=" * 70)
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"系统架构: {platform.machine()}")
    print("=" * 70)
    
    checks = [
        ("Python版本", check_python_version),
        ("Python包", check_pip_packages),
        ("目录结构", check_directories),
        ("字体文件", check_fonts),
        ("配置文件", check_config),
        ("示例数据", check_sample_data),
        ("功能测试", run_quick_test)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n[{check_name}]")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"  ❌ 检查过程中发生错误: {e}")
            results.append((check_name, False))
    
    # 显示检查结果摘要
    print("\n" + "=" * 70)
    print("检查结果摘要")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{check_name:15} {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计检查: {len(results)} 项")
    print(f"通过: {passed} 项")
    print(f"失败: {failed} 项")
    
    if failed == 0:
        print("\n🎉 所有检查通过！环境准备就绪。")
        print("\n下一步建议:")
        print("1. 运行完整测试: python test_all_modules.py")
        print("2. 运行演示: python start_demo.py")
        print("3. 查看使用指南: 阅读 USAGE_GUIDE.md")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 项检查失败，请根据上面的提示解决问题。")
        print("\n常见问题解决:")
        print("1. 安装依赖包: pip install -r requirements.txt")
        print("2. 设置字体: python download_fonts.py 或 .\\setup_fonts.ps1")
        print("3. 创建目录: 手动创建缺失的目录")
        print("\n详细指南请查看 INSTALLATION_GUIDE.md")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n检查过程中发生错误: {e}")
        sys.exit(1)