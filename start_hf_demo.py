"""
启动Hugging Face情感分析演示
展示使用预训练模型进行中文情感分析
"""

import sys
import os
from pathlib import Path
import time
import logging

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def check_environment():
    """检查环境"""
    print_header("环境检查")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("[WARNING] 建议使用Python 3.8或更高版本")
    
    # 检查必要包
    required_packages = [
        ("torch", "PyTorch"),
        ("transformers", "Hugging Face Transformers"),
        ("accelerate", "Accelerate"),
    ]
    
    all_installed = True
    for package, description in required_packages:
        try:
            if package == "torch":
                import torch
                print(f"[OK] {description} 版本: {torch.__version__}")
                if torch.cuda.is_available():
                    print(f"    CUDA可用: 是")
                    print(f"    GPU设备: {torch.cuda.get_device_name(0)}")
                else:
                    print(f"    CUDA可用: 否 (将使用CPU)")
            elif package == "transformers":
                import transformers
                print(f"[OK] {description} 版本: {transformers.__version__}")
            elif package == "accelerate":
                import accelerate
                print(f"[OK] {description} 版本: {accelerate.__version__}")
        except ImportError:
            print(f"[ERROR] 未安装 {description}")
            all_installed = False
    
    return all_installed

def run_hf_sentiment_demo():
    """运行Hugging Face情感分析演示"""
    print_header("Hugging Face情感分析演示")
    
    try:
        from hf_sentiment_analyzer import HFSentimentAnalyzer
        
        print("初始化情感分析器...")
        print("优先使用GPU 0，如果不可用则自动切换到CPU")
        
        # 创建分析器
        analyzer = HFSentimentAnalyzer(
            model_name="uer/roberta-base-finetuned-jd-binary-chinese",
            use_gpu=True
        )
        
        print("\n模型信息:")
        print(f"   模型名称: {analyzer.model_name}")
        print(f"   使用设备: {'GPU' if analyzer.device >= 0 else 'CPU'}")
        
        # 测试文本
        test_texts = [
            "这个手机真的很好用，拍照效果特别棒，运行速度也很快，非常满意！",
            "产品质量太差了，用了不到一个月就坏了，客服态度也不好，非常失望。",
            "产品还可以，对得起这个价格，但也没有什么特别突出的地方。",
            "这是我买过的最好的电子产品！性能强大，设计精美，用户体验完美！",
            "物流太慢了，等了整整一周才收到货，包装也有破损，体验很差。",
            "服务态度很好，解决问题很及时，产品使用起来也很方便。",
            "价格有点贵，但质量确实不错，考虑再买一个送给朋友。",
            "完全不推荐购买，问题很多，售后也不给解决。"
        ]
        
        print(f"\n准备分析 {len(test_texts)} 条测试文本...")
        print("第一次运行会下载模型，可能需要一些时间")
        print("下载完成后会缓存到本地，下次运行会更快")
        
        input("\n按 Enter 键开始分析...")
        
        results = []
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n{i}. 分析文本: {text[:50]}...")
            
            result = analyzer.analyze_sentiment(text, use_cache=False)
            results.append(result)
            
            if result:
                sentiment = result['sentiment']
                score = result['score']
                reason = result['reason']
                
                # 根据情感类型显示不同颜色
                if sentiment == "positive":
                    sentiment_display = f"\033[92m{sentiment}\033[0m"  # 绿色
                elif sentiment == "negative":
                    sentiment_display = f"\033[91m{sentiment}\033[0m"  # 红色
                else:
                    sentiment_display = f"\033[93m{sentiment}\033[0m"  # 黄色
                
                print(f"   情感: {sentiment_display}")
                print(f"   分数: {score}/10")
                print(f"   理由: {reason}")
                print(f"   处理时间: {result['processing_time']}秒")
            else:
                print("   [ERROR] 分析失败")
            
            time.sleep(0.5)  # 避免请求过快
        
        # 统计结果
        successful = sum(1 for r in results if r is not None)
        print(f"\n分析完成: {successful}/{len(test_texts)} 条成功分析")
        
        # 保存结果
        if successful > 0:
            output_path = analyzer.save_results(results, "demo_results.json")
            if output_path:
                print(f"\n分析结果已保存到: {output_path}")
        
        return successful > 0
        
    except Exception as e:
        print(f"[ERROR] 演示失败: {e}")
        return False

def run_batch_analysis_demo():
    """运行批量分析演示"""
    print_header("批量情感分析演示")
    
    try:
        from hf_sentiment_analyzer import HFSentimentAnalyzer
        
        print("创建批量分析器...")
        
        # 创建分析器（使用CPU以节省资源）
        analyzer = HFSentimentAnalyzer(use_gpu=False)
        
        # 生成批量测试数据
        print("生成测试数据...")
        batch_texts = []
        for i in range(1, 21):
            if i % 3 == 0:
                batch_texts.append(f"产品{i}: 质量很差，完全不推荐购买。")
            elif i % 3 == 1:
                batch_texts.append(f"产品{i}: 非常好用，物超所值，强烈推荐！")
            else:
                batch_texts.append(f"产品{i}: 一般般，没什么特别的感觉。")
        
        print(f"准备批量分析 {len(batch_texts)} 条文本...")
        print("使用批处理模式，提高分析效率")
        
        input("\n按 Enter 键开始批量分析...")
        
        start_time = time.time()
        results = analyzer.batch_analyze_sentiment(batch_texts, batch_size=8, use_cache=True)
        total_time = time.time() - start_time
        
        # 统计结果
        successful = sum(1 for r in results if r is not None)
        
        # 情感分布统计
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for result in results:
            if result:
                sentiment = result['sentiment']
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        print(f"\n批量分析完成!")
        print(f"   总文本数: {len(batch_texts)}")
        print(f"   成功分析: {successful}")
        print(f"   总耗时: {total_time:.2f}秒")
        print(f"   平均每条: {total_time/len(batch_texts):.3f}秒")
        
        print(f"\n情感分布:")
        for sentiment, count in sentiment_counts.items():
            percentage = count / successful * 100 if successful > 0 else 0
            print(f"   {sentiment}: {count} 条 ({percentage:.1f}%)")
        
        # 保存结果
        output_path = analyzer.save_results(results, "batch_results.json")
        if output_path:
            print(f"\n批量分析结果已保存到: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 批量分析演示失败: {e}")
        return False

def show_usage_guide():
    """显示使用指南"""
    print_header("使用指南")
    
    print("1. 基本使用:")
    print("   from hf_sentiment_analyzer import HFSentimentAnalyzer")
    print("   analyzer = HFSentimentAnalyzer(use_gpu=True)  # 优先使用GPU")
    print("   result = analyzer.analyze_sentiment('你的文本')")
    print("   print(f\"情感: {result['sentiment']}, 分数: {result['score']}\")")
    
    print("\n2. 批量分析:")
    print("   texts = ['文本1', '文本2', '文本3']")
    print("   results = analyzer.batch_analyze_sentiment(texts, batch_size=16)")
    
    print("\n3. 保存结果:")
    print("   analyzer.save_results(results, 'my_results.json')")
    
    print("\n4. 使用CPU模式:")
    print("   analyzer = HFSentimentAnalyzer(use_gpu=False)  # 强制使用CPU")
    
    print("\n5. 使用其他模型:")
    print("   analyzer = HFSentimentAnalyzer(")
    print("       model_name='bert-base-chinese',")
    print("       use_gpu=True")
    print("   )")

def main():
    """主函数"""
    print_header("Hugging Face中文情感分析工具")
    print("基于预训练模型的中文情感分析解决方案")
    print("优先使用GPU 0加速，自动降级到CPU")
    
    # 检查环境
    if not check_environment():
        print("\n[ERROR] 环境检查失败，请安装必要的包")
        print("运行: pip install torch transformers accelerate")
        return 1
    
    # 等待用户确认
    input("\n按 Enter 键开始演示...")
    
    # 运行演示
    demo_success = run_hf_sentiment_demo()
    
    if demo_success:
        input("\n按 Enter 键继续批量分析演示...")
        batch_success = run_batch_analysis_demo()
    else:
        batch_success = False
    
    # 显示使用指南
    if demo_success or batch_success:
        show_usage_guide()
    
    # 总结
    print_header("演示完成")
    
    if demo_success and batch_success:
        print("[SUCCESS] 所有演示成功完成！")
        print("\n下一步:")
        print("   1. 查看保存的结果文件")
        print("   2. 尝试分析自己的文本数据")
        print("   3. 集成到你的项目中")
        return 0
    elif demo_success:
        print("[PARTIAL] 基本演示成功，批量分析失败")
        return 1
    else:
        print("[ERROR] 演示失败")
        print("\n请检查:")
        print("   1. 网络连接是否正常")
        print("   2. 磁盘空间是否充足")
        print("   3. 内存是否足够")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n演示被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n演示发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)