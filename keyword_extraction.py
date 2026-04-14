"""
关键词提取模块 - 中文文本关键词提取
"""

import jieba
import jieba.analyse
from collections import Counter
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import time
import json

# 版本信息
__version__ = "1.0.0"

# 默认配置
PROJECT_ROOT = Path(__file__).parent
DEFAULT_JIEBA_CONFIG = {
    'user_dict': str(PROJECT_ROOT / 'data' / 'user_dict.txt'),
    'stopwords_file': str(PROJECT_ROOT / 'data' / 'stopwords.txt')
}

# 日志设置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """清洗文本：去除多余空白、特殊字符，保留中文字符、数字、字母和常见标点"""
    if not text:
        return ""
    # 保留中文、英文、数字、常用标点
    text = re.sub(r'[^\u4e00-\u9fff\u3000-\u303f\w\s\.\,\!\?;:\(\)\[\]【】《》\"\'、，。！？；：（）]', '', text)
    # 合并空白
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def load_text_from_file(filepath: Path) -> Optional[str]:
    """从文件加载文本"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取文件失败 {filepath}: {e}")
        return None


def save_text_to_file(text: str, filepath: Path) -> bool:
    """保存文本到文件"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        logger.error(f"保存文件失败 {filepath}: {e}")
        return False


def create_stopwords_file(filepath: Path) -> None:
    """如果停用词文件不存在则创建默认的停用词文件"""
    if filepath.exists():
        return
    # 默认停用词集合
    default_stopwords = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
        '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '什么', '他', '她', '它', '我们', '你们', '他们', '它们',
        '这个', '那个', '这些', '那些', '这样', '那样', '这里', '那里', '怎么', '为什么', '可以', '觉得', '知道', '喜欢',
        '因为', '所以', '但是', '可是', '如果', '然后', '而且', '或者', '虽然', '然而', '因此', '于是', '并且', '不仅', '也',
        '又', '还', '更', '最', '非常', '十分', '特别', '相当', '比较', '可能', '可以', '应该', '需要', '已经', '正在',
        '还是', '还是', '为了', '对于', '关于', '作为', '通过', '根据', '按照', '除了', '比如', '例如', '等等', '等等', '等',
        '一般', '一些', '一切', '一个', '两种', '之后', '之前', '以前', '以后', '当时', '现在', '目前', '将来', '过去',
        '开始', '最后', '继续', '仍然', '始终', '终于', '结果', '原因', '方式', '方法', '问题', '情况', '时候', '时间',
        '地点', '东西', '事情', '人物', '方面', '水平', '程度', '范围', '过程', '活动', '关系', '状态', '发展', '变化',
        '影响', '作用', '意义', '价值', '特点', '优势', '缺点', '区别', '联系', '比较', '分析', '研究', '学习', '工作',
        '生活', '生产', '管理', '服务', '支持', '帮助', '建议', '意见', '需求', '供给', '市场', '经济', '社会', '文化',
        '历史', '科学', '技术', '教育', '医疗', '法律', '政治', '军事', '外交', '宗教', '艺术', '体育', '娱乐', '旅游',
        '交通', '通信', '能源', '环境', '资源', '人口', '民族', '国家', '城市', '农村', '企业', '组织', '机构', '部门',
        '系统', '数据', '信息', '网络', '平台', '产品', '服务', '项目', '计划', '方案', '策略', '政策', '制度', '机制',
        '模式', '方法', '技术', '工具', '设备', '材料', '资金', '资源', '能源', '人力', '物力', '财力', '权利', '义务',
        '责任', '权力', '利益', '冲突', '合作', '竞争', '发展', '改革', '开放', '创新', '创业', '投资', '融资', '消费',
        '生产', '分配', '交换', '流通', '存储', '运输', '销售', '采购', '库存', '质量', '成本', '价格', '利润', '效益',
        '效率', '效果', '结果', '目标', '任务', '职责', '角色', '身份', '地位', '层次', '等级', '顺序', '步骤', '阶段',
        '周期', '循环', '方向', '目标', '目的', '意图', '动机', '行为', '行动', '活动', '事件', '现象', '本质', '规律',
        '趋势', '变化', '矛盾', '统一', '对立', '平衡', '协调', '调整', '优化', '改善', '提升', '降低', '增加', '减少',
        '扩大', '缩小', '加强', '减弱', '加快', '减慢', '提高', '降低', '实现', '完成', '达到', '超过', '低于', '等于',
        '包含', '包括', '涉及', '有关', '相关', '不同', '相同', '类似', '一致', '差异', '区别', '联系', '影响', '依赖',
        '根据', '按照', '依照', '遵循', '遵守', '执行', '实施', '落实', '贯彻', '体现', '反映', '表现', '展示', '显示',
        '证明', '表明', '说明', '解释', '描述', '阐述', '论述', '讨论', '探讨', '研究', '分析', '总结', '归纳', '概括',
        '推断', '推测', '预测', '估计', '计算', '测量', '检验', '验证', '确认', '确定', '决定', '选择', '选取', '挑选',
        '收集', '整理', '归纳', '分类', '排序', '比较', '评估', '评价', '评分', '打分', '判断', '断定', '肯定', '否定',
        '同意', '反对', '支持', '质疑', '怀疑', '相信', '认为', '觉得', '感到', '感觉', '意识', '认识', '理解', '明白',
        '知道', '了解', '熟悉', '掌握', '运用', '使用', '利用', '采用', '采取', '实施', '执行', '操作', '处理', '加工',
        '制造', '生产', '创造', '发明', '发现', '探索', '寻找', '找到', '得到', '获得', '取得', '赢得', '收获', '积累',
        '增长', '发展', '进步', '提高', '提升', '加强', '增强', '扩大', '拓展', '延伸', '延长', '缩短', '减少', '降低',
        '减轻', '缓解', '消除', '解决', '处理', '应付', '应对', '面对', '避免', '防止', '预防', '阻止', '制止', '控制',
        '管理', '治理', '整顿', '清理', '清除', '排除', '驱逐', '赶走', '离开', '进入', '到达', '经过', '通过', '穿过',
        '越过', '跨过', '走过', '跑过', '跳过', '飞过', '游过', '爬过', '滚过', '滑过', '溜过', '漂过', '浮过', '沉过',
        '升起', '降落', '上升', '下降', '增加', '减少', '扩大', '缩小', '变长', '变短', '变宽', '变窄', '变高', '变低',
        '变深', '变浅', '变重', '变轻', '变硬', '变软', '变热', '变冷', '变干', '变湿', '变亮', '变暗', '变红', '变绿'
    }
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            for word in sorted(default_stopwords):
                f.write(word + '\n')
        logger.info(f"已创建默认停用词文件: {filepath}")
    except Exception as e:
        logger.error(f"创建停用词文件失败: {e}")


class KeywordExtractor:
    """关键词提取器"""

    def __init__(self, language='zh', min_word_length=2, max_word_length=5, stopwords_file=None):
        """初始化"""
        self.language = language
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length

        # 加载用户词典
        user_dict = Path(DEFAULT_JIEBA_CONFIG['user_dict'])
        if user_dict.exists():
            jieba.load_userdict(str(user_dict))
            logger.info(f"已加载用户词典: {user_dict}")

        # 停用词文件
        if stopwords_file:
            stopwords_path = Path(stopwords_file)
        else:
            stopwords_path = Path(DEFAULT_JIEBA_CONFIG['stopwords_file'])
        create_stopwords_file(stopwords_path)
        self.stopwords = self._load_stopwords(stopwords_path)

        # 测试文本
        self.test_texts = [
            "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
            "机器学习是人工智能的一个分支，它使用算法和统计模型使计算机系统能够在没有明确指令的情况下执行任务。",
            "深度学习是机器学习的一个子领域，它使用神经网络来模拟人脑的工作方式。",
            "自然语言处理是人工智能的一个重要方向，它研究如何让计算机理解和生成人类语言。",
            "计算机视觉是人工智能的另一个重要方向，它研究如何让计算机理解和分析图像和视频。"
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

    def extract_with_tfidf(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """使用TF-IDF提取关键词（基于sklearn）"""
        try:
            # 分词并去除停用词
            words = jieba.lcut(text)
            words = self._remove_stopwords(words)
            # 过滤单字符非中文
            words = [w for w in words if len(w) > 1 or '\u4e00' <= w <= '\u9fff']
            if not words:
                return []

            # 用空格连接成文档
            doc = ' '.join(words)
            vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
            tfidf_matrix = vectorizer.fit_transform([doc])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            return keyword_scores[:top_k]

        except Exception as e:
            logger.error(f"TF-IDF提取失败: {e}")
            return []

    def extract_with_textrank(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """使用TextRank算法提取关键词（jieba实现）"""
        try:
            keywords = jieba.analyse.textrank(
                text, topK=top_k, withWeight=True,
                allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'a')
            )
            return keywords
        except Exception as e:
            logger.error(f"TextRank提取失败: {e}")
            return []

    def extract_with_tfidf_jieba(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """使用jieba内置的TF-IDF提取关键词"""
        try:
            # 注意：jieba.analyse.extract_tags 的 allowPOS 参数在较新版本可能不支持，改用默认
            keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
            # 手动过滤词性（可选）
            return keywords
        except Exception as e:
            logger.error(f"jieba TF-IDF提取失败: {e}")
            return []

    def extract_keywords(self, text: str, method: str = 'tfidf_jieba',
                         top_k: int = 10) -> Dict[str, Any]:
        """提取关键词"""
        start_time = time.time()
        cleaned_text = clean_text(text)

        if method == 'tfidf':
            keywords = self.extract_with_tfidf(cleaned_text, top_k)
        elif method == 'textrank':
            keywords = self.extract_with_textrank(cleaned_text, top_k)
        elif method == 'tfidf_jieba':
            keywords = self.extract_with_tfidf_jieba(cleaned_text, top_k)
        else:
            raise ValueError(f"未知的提取方法: {method}")

        # 统计词频
        words = jieba.lcut(cleaned_text)
        words = self._remove_stopwords(words)
        word_freq = Counter(words)

        keyword_freqs = []
        for keyword, score in keywords:
            freq = word_freq.get(keyword, 0)
            keyword_freqs.append((keyword, score, freq))

        processing_time = time.time() - start_time

        return {
            'text_length': len(cleaned_text),
            'word_count': len(words),
            'unique_words': len(set(words)),
            'method': method,
            'keywords': keyword_freqs,
            'top_keywords': [k for k, _, _ in keyword_freqs[:5]],
            'processing_time': round(processing_time, 3)
        }

    def compare_methods(self, text: str, top_k: int = 10) -> Dict[str, Any]:
        """对比不同关键词提取方法"""
        methods = ['tfidf_jieba', 'textrank', 'tfidf']
        results = {}
        for method in methods:
            results[method] = self.extract_keywords(text, method, top_k)

        consistency = self._calculate_consistency(results, top_k)
        results['consistency'] = consistency
        return results

    def _calculate_consistency(self, results: Dict[str, Any], top_k: int) -> Dict[str, Any]:
        """计算方法间的一致性"""
        method_keys = {}
        for method, result in results.items():
            if method != 'consistency':
                keywords = [k for k, _, _ in result.get('keywords', [])]
                method_keys[method] = set(keywords[:top_k])

        methods = list(method_keys.keys())
        consistency_matrix = {}
        for i, m1 in enumerate(methods):
            for m2 in methods[i+1:]:
                set1 = method_keys[m1]
                set2 = method_keys[m2]
                intersection = len(set1 & set2)
                union = len(set1 | set2)
                similarity = intersection / union if union > 0 else 0.0
                consistency_matrix[f"{m1}_vs_{m2}"] = {
                    'similarity': round(similarity, 4),
                    'intersection': list(set1 & set2),
                    'unique_to_method1': list(set1 - set2),
                    'unique_to_method2': list(set2 - set1)
                }

        similarities = [v['similarity'] for v in consistency_matrix.values()]
        avg_similarity = np.mean(similarities) if similarities else 0.0

        return {
            'matrix': consistency_matrix,
            'average_similarity': round(avg_similarity, 4),
            'methods': methods
        }

    def extract_from_file(self, filepath: Path, method: str = 'tfidf_jieba',
                          top_k: int = 20) -> Dict[str, Any]:
        """从文件提取关键词"""
        text = load_text_from_file(filepath)
        if not text:
            return {}
        result = self.extract_keywords(text, method, top_k)
        result['file_info'] = {
            'filename': filepath.name,
            'file_size_bytes': filepath.stat().st_size,
            'text_length': len(text)
        }
        return result

    def batch_extract(self, directory: Path, method: str = 'tfidf_jieba',
                      top_k: int = 15) -> List[Dict[str, Any]]:
        """批量提取关键词"""
        results = []
        text_files = list(directory.glob('*.txt'))
        if not text_files:
            logger.warning(f"目录中没有找到文本文件: {directory}")
            return results

        logger.info(f"开始批量提取 {len(text_files)} 个文件的关键词...")
        for i, filepath in enumerate(text_files, 1):
            result = self.extract_from_file(filepath, method, top_k)
            if result:
                results.append(result)
                logger.info(f"已处理 {i}/{len(text_files)}: {filepath.name}")
        return results

    def generate_report(self, results: List[Dict[str, Any]], output_dir: Path) -> bool:
        """生成关键词提取报告"""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            # 详细报告
            report_lines = ["关键词提取报告", "=" * 60]
            for result in results:
                file_info = result.get('file_info', {})
                report_lines.append(f"\n文件: {file_info.get('filename', 'unknown')}")
                report_lines.append(f"文本长度: {result.get('text_length', 0)} 字符")
                report_lines.append(f"分词数量: {result.get('word_count', 0)}")
                report_lines.append(f"唯一词数: {result.get('unique_words', 0)}")
                report_lines.append(f"提取方法: {result.get('method', 'unknown')}")
                report_lines.append("\n关键词:")
                for keyword, score, freq in result.get('keywords', []):
                    report_lines.append(f"  {keyword}: 权重={score:.4f}, 词频={freq}")

            report_file = output_dir / 'keyword_extraction_report.txt'
            save_text_to_file('\n'.join(report_lines), report_file)

            # 摘要报告
            all_keywords = {}
            for result in results:
                keywords = result.get('keywords', [])
                for keyword, score, freq in keywords:
                    if keyword not in all_keywords:
                        all_keywords[keyword] = {'total_score': 0, 'total_freq': 0, 'doc_count': 0}
                    all_keywords[keyword]['total_score'] += score
                    all_keywords[keyword]['total_freq'] += freq
                    all_keywords[keyword]['doc_count'] += 1

            for kw in all_keywords:
                all_keywords[kw]['avg_score'] = all_keywords[kw]['total_score'] / len(results)

            sorted_keywords = sorted(all_keywords.items(), key=lambda x: x[1]['avg_score'], reverse=True)

            summary_lines = ["关键词提取摘要报告", "=" * 60, f"总文件数: {len(results)}", "\n总体关键词排名（前20）:"]
            for i, (kw, data) in enumerate(sorted_keywords[:20], 1):
                summary_lines.append(f"{i:2d}. {kw}: 平均权重={data['avg_score']:.4f}, "
                                     f"总词频={data['total_freq']}, 出现文档数={data['doc_count']}")

            summary_file = output_dir / 'keyword_summary_report.txt'
            save_text_to_file('\n'.join(summary_lines), summary_file)

            logger.info(f"报告已保存到: {output_dir}")
            return True
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return False

    def run_demo(self):
        """运行演示"""
        logger.info("开始关键词提取演示...")
        output_dir = PROJECT_ROOT / 'data' / 'keyword_extraction'
        output_dir.mkdir(parents=True, exist_ok=True)

        comparison_report = ["关键词提取方法对比报告", "=" * 60]
        for i, text in enumerate(self.test_texts, 1):
            comparison_report.append(f"\n测试文本 {i}:")
            comparison_report.append(f"内容: {text[:100]}...")
            comparison_report.append("-" * 40)

            results = self.compare_methods(text, top_k=10)
            for method, result in results.items():
                if method != 'consistency':
                    comparison_report.append(f"\n{method.upper()}方法:")
                    for j, (kw, score, freq) in enumerate(result.get('keywords', []), 1):
                        comparison_report.append(f"  {j:2d}. {kw:10s} 权重: {score:.4f} 词频: {freq}")

            consistency = results.get('consistency', {})
            comparison_report.append(f"\n方法间一致性: 平均相似度 = {consistency.get('average_similarity', 0)}")
            for pair, data in consistency.get('matrix', {}).items():
                comparison_report.append(f"  {pair}: 相似度={data.get('similarity', 0)}")
            comparison_report.append("\n" + "=" * 60)

        report_file = output_dir / 'method_comparison_report.txt'
        save_text_to_file('\n'.join(comparison_report), report_file)
        logger.info(f"演示完成！报告已保存到: {output_dir}")


def main():
    """主函数"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='关键词提取工具')
    parser.add_argument('--text', type=str, help='要分析的文本')
    parser.add_argument('--file', type=str, help='要分析的文本文件')
    parser.add_argument('--dir', type=str, help='要分析的目录（批量处理）')
    parser.add_argument('--method', type=str, default='tfidf_jieba',
                       choices=['tfidf', 'textrank', 'tfidf_jieba'],
                       help='提取方法')
    parser.add_argument('--top-k', type=int, default=10, help='提取前K个关键词')
    parser.add_argument('--output', type=str, help='输出目录')
    parser.add_argument('--compare', action='store_true', help='对比不同提取方法')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    parser.add_argument('--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--save', type=str, help='保存结果到JSON文件')
    parser.add_argument('--stopwords', type=str, help='自定义停用词文件')
    parser.add_argument('--language', type=str, default='zh', choices=['zh', 'en'], help='文本语言')

    args = parser.parse_args()

    if args.version:
        print(f"关键词提取工具 v{__version__}")
        return 0

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        extractor = KeywordExtractor(
            language=args.language,
            stopwords_file=args.stopwords
        )
    except Exception as e:
        logger.error(f"初始化提取器失败: {e}")
        return 1

    if args.demo:
        extractor.run_demo()
        return 0

    if args.text:
        if args.compare:
            results = extractor.compare_methods(args.text, args.top_k)
            print("\n关键词提取结果对比:")
            print("=" * 60)
            for method, result in results.items():
                if method != 'consistency':
                    print(f"\n{method.upper()}方法:")
                    for i, (kw, score, freq) in enumerate(result.get('keywords', []), 1):
                        print(f"  {i:2d}. {kw:10s} 权重: {score:.4f} 词频: {freq}")
            cons = results.get('consistency', {})
            print(f"\n方法间一致性: 平均相似度 = {cons.get('average_similarity', 0):.2%}")
            if args.save:
                with open(args.save, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
        else:
            result = extractor.extract_keywords(args.text, args.method, args.top_k)
            print(f"\n关键词提取结果 ({args.method}方法):")
            print("=" * 60)
            print(f"文本长度: {result.get('text_length', 0)} 字符")
            print(f"分词数量: {result.get('word_count', 0)}")
            print(f"唯一词数: {result.get('unique_words', 0)}")
            print(f"处理时间: {result.get('processing_time', 0)}秒")
            print("\n关键词:")
            for i, (kw, score, freq) in enumerate(result.get('keywords', []), 1):
                print(f"  {i:2d}. {kw:15s} 权重: {score:.4f} 词频: {freq}")
            if args.save:
                with open(args.save, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

    elif args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            logger.error(f"文件不存在: {filepath}")
            return 1
        result = extractor.extract_from_file(filepath, args.method, args.top_k)
        if not result:
            return 1
        print(f"\n文件关键词提取结果:")
        print("=" * 60)
        info = result.get('file_info', {})
        print(f"文件名: {info.get('filename')}")
        print(f"文本长度: {result.get('text_length')} 字符")
        print(f"分词数量: {result.get('word_count')}")
        print("\n关键词:")
        for i, (kw, score, freq) in enumerate(result.get('keywords', []), 1):
            print(f"  {i:2d}. {kw:15s} 权重: {score:.4f} 词频: {freq}")
        if args.save:
            with open(args.save, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

    elif args.dir:
        directory = Path(args.dir)
        if not directory.is_dir():
            logger.error(f"目录不存在: {directory}")
            return 1
        results = extractor.batch_extract(directory, args.method, args.top_k)
        if not results:
            logger.error("没有找到可处理的文件")
            return 1
        print(f"\n批量关键词提取完成，共处理 {len(results)} 个文件")
        if args.output:
            output_dir = Path(args.output)
            extractor.generate_report(results, output_dir)
        if args.save:
            with open(args.save, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())