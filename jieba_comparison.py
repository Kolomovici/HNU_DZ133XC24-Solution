"""
中文分词对比模块 - 使用结巴分词对比不同分词引擎的效果
"""

import jieba
import jieba.posseg as pseg
from collections import Counter
import time
from pathlib import Path
import logging
from typing import List, Tuple, Dict, Any

from config import JIEBA_CONFIG, PROJECT_ROOT
from utils import clean_text, load_text_from_file, save_text_to_file, create_stopwords_file

# 设置日志
logger = logging.getLogger(__name__)

class JiebaComparison:
    """结巴分词对比类"""
    
    def __init__(self):
        """初始化分词器"""
        # 加载用户词典
        user_dict = Path(JIEBA_CONFIG['user_dict'])
        if user_dict.exists():
            jieba.load_userdict(str(user_dict))
            logger.info(f"已加载用户词典: {user_dict}")
        
        # 创建停用词文件
        stopwords_file = Path(JIEBA_CONFIG['stopwords_file'])
        create_stopwords_file(stopwords_file)
        
        # 加载停用词
        self.stopwords = self._load_stopwords(stopwords_file)
        
        # 测试文本
        self.test_texts = [
            "自然语言处理是人工智能领域的一个重要方向。",
            "结巴分词是一款优秀的中文分词工具。",
            "今天天气真好，我们一起去公园散步吧！",
            "Python是一种广泛使用的高级编程语言。",
            "机器学习需要大量的数据和计算资源。"
        ]
    
    def _load_stopwords(self, stopwords_file: Path) -> set:
        """加载停用词"""
        stopwords = set()
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
    
    def _remove_stopwords(self, words: List[str]) -> List[str]:
        """移除停用词"""
        return [word for word in words if word not in self.stopwords]
    
    def cut_with_engine(self, text: str, engine: str = 'default') -> List[str]:
        """
        使用指定的分词引擎进行分词
        
        Args:
            text: 要分词的文本
            engine: 分词引擎 ('default', 'cut_all', 'search', 'pos')
            
        Returns:
            分词结果列表
        """
        text = clean_text(text)
        
        if engine == 'default':
            # 精确模式
            words = jieba.lcut(text)
        elif engine == 'cut_all':
            # 全模式
            words = jieba.lcut(text, cut_all=True)
        elif engine == 'search':
            # 搜索引擎模式
            words = jieba.lcut_for_search(text)
        elif engine == 'pos':
            # 词性标注
            words_with_pos = pseg.lcut(text)
            words = [f"{word}/{flag}" for word, flag in words_with_pos]
        else:
            raise ValueError(f"未知的分词引擎: {engine}")
        
        # 移除停用词（词性标注模式除外）
        if engine != 'pos':
            words = self._remove_stopwords(words)
        
        return words
    
    def compare_engines(self, text: str) -> Dict[str, Any]:
        """
        对比不同分词引擎的效果
        
        Args:
            text: 要分词的文本
            
        Returns:
            对比结果字典
        """
        results = {}
        
        engines = ['default', 'cut_all', 'search', 'pos']
        
        for engine in engines:
            start_time = time.time()
            words = self.cut_with_engine(text, engine)
            elapsed_time = time.time() - start_time
            
            results[engine] = {
                'words': words,
                'word_count': len(words),
                'unique_words': len(set(words)),
                'time_ms': round(elapsed_time * 1000, 2)
            }
            
            # 统计词频（词性标注模式除外）
            if engine != 'pos':
                word_freq = Counter(words)
                results[engine]['top_words'] = word_freq.most_common(10)
        
        return results
    
    def analyze_text_file(self, filepath: Path) -> Dict[str, Any]:
        """
        分析文本文件的分词效果
        
        Args:
            filepath: 文本文件路径
            
        Returns:
            分析结果
        """
        text = load_text_from_file(filepath)
        if not text:
            return {}
        
        # 截取前1000个字符进行分析
        sample_text = text[:1000] if len(text) > 1000 else text
        
        results = self.compare_engines(sample_text)
        
        # 添加文件信息
        results['file_info'] = {
            'filename': filepath.name,
            'file_size_bytes': filepath.stat().st_size,
            'text_length': len(text),
            'sample_length': len(sample_text)
        }
        
        return results
    
    def run_comparison(self, output_dir: Path = None):
        """
        运行分词对比
        
        Args:
            output_dir: 输出目录
        """
        if output_dir is None:
            output_dir = PROJECT_ROOT / 'data' / 'jieba_comparison'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("开始分词对比分析...")
        
        # 1. 测试预定义文本
        logger.info("\n1. 测试预定义文本:")
        for i, text in enumerate(self.test_texts, 1):
            logger.info(f"\n测试文本 {i}: {text}")
            results = self.compare_engines(text)
            
            for engine, data in results.items():
                logger.info(f"  {engine}模式:")
                logger.info(f"    分词数量: {data['word_count']}")
                logger.info(f"    唯一词数: {data['unique_words']}")
                logger.info(f"    耗时: {data['time_ms']}ms")
                
                if 'top_words' in data:
                    logger.info(f"    高频词: {data['top_words'][:5]}")
        
        # 2. 生成对比报告
        logger.info("\n2. 生成详细对比报告...")
        report = []
        
        for i, text in enumerate(self.test_texts, 1):
            results = self.compare_engines(text)
            
            report.append(f"测试文本 {i}: {text}")
            report.append("=" * 50)
            
            for engine, data in results.items():
                report.append(f"\n{engine.upper()}模式:")
                report.append(f"  分词数量: {data['word_count']}")
                report.append(f"  唯一词数: {data['unique_words']}")
                report.append(f"  耗时: {data['time_ms']}ms")
                
                if engine == 'pos':
                    report.append(f"  分词结果（前20个）: {' | '.join(data['words'][:20])}")
                else:
                    report.append(f"  高频词（前10）: {', '.join([f'{w}({c})' for w, c in data['top_words'][:10]])}")
            
            report.append("\n" + "=" * 50 + "\n")
        
        # 保存报告
        report_file = output_dir / 'comparison_report.txt'
        save_text_to_file('\n'.join(report), report_file)
        
        # 3. 性能测试
        logger.info("\n3. 性能测试:")
        performance_text = " ".join(self.test_texts * 10)  # 重复文本以增加长度
        performance_results = self.compare_engines(performance_text)
        
        perf_report = ["性能测试报告", "=" * 50]
        for engine, data in performance_results.items():
            perf_report.append(f"\n{engine.upper()}模式:")
            perf_report.append(f"  文本长度: {len(performance_text)} 字符")
            perf_report.append(f"  分词数量: {data['word_count']}")
            perf_report.append(f"  处理时间: {data['time_ms']}ms")
            perf_report.append(f"  处理速度: {len(performance_text)/data['time_ms']*1000:.2f} 字符/秒")
        
        perf_file = output_dir / 'performance_report.txt'
        save_text_to_file('\n'.join(perf_report), perf_file)
        
        logger.info(f"\n对比报告已保存到: {output_dir}")
        logger.info("分词对比完成！")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='结巴分词对比工具')
    parser.add_argument('--text', type=str, help='要分析的文本')
    parser.add_argument('--file', type=str, help='要分析的文本文件')
    parser.add_argument('--output', type=str, default=None, help='输出目录')
    
    args = parser.parse_args()
    
    # 创建分词对比实例
    comparator = JiebaComparison()
    
    if args.text:
        # 分析单个文本
        results = comparator.compare_engines(args.text)
        print(f"\n文本: {args.text}")
        for engine, data in results.items():
            print(f"\n{engine.upper()}模式:")
            print(f"  分词结果: {' | '.join(data['words'][:20])}")
            print(f"  分词数量: {data['word_count']}")
            print(f"  耗时: {data['time_ms']}ms")
    
    elif args.file:
        # 分析文本文件
        filepath = Path(args.file)
        if filepath.exists():
            results = comparator.analyze_text_file(filepath)
            print(f"\n文件分析结果: {filepath.name}")
            for engine, data in results.items():
                if engine != 'file_info':
                    print(f"\n{engine.upper()}模式:")
                    print(f"  分词数量: {data['word_count']}")
                    print(f"  耗时: {data['time_ms']}ms")
        else:
            print(f"文件不存在: {args.file}")
    
    else:
        # 运行完整的对比分析
        output_dir = Path(args.output) if args.output else None
        comparator.run_comparison(output_dir)

if __name__ == "__main__":
    main()