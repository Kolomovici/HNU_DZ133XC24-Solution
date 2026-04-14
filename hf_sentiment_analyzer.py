"""
Phi-2 情感分析器 - CPU优化版
使用提示工程通过文本生成进行情感分析
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json
import time
import hashlib
import pickle
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging
from datetime import datetime

# 设置日志
logger = logging.getLogger(__name__)


class Phi2SentimentAnalyzer:
    """Phi-2 情感分析器 - 基于提示工程的文本生成"""
    
    # 情感分析提示模板
    SENTIMENT_PROMPT = """分析以下文本的情感，只输出'正面'或'负面'。

文本：{text}
情感："""
    
    def __init__(self, model_name: str = "microsoft/phi-2", max_length: int = 512):
        """初始化分析器
        
        Args:
            model_name: Hugging Face模型名称，默认为 microsoft/phi-2
            max_length: 输入文本的最大长度（token数）
        """
        self.model_name = model_name
        self.max_length = max_length
        
        # 强制使用CPU
        self.device = "cpu"
        logger.info(f"使用设备: {self.device}")
        
        # 缓存配置
        self.cache_dir = Path("data/sentiment_cache")
        self.cache_ttl = 86400  # 24小时
        self.max_cache_size = 10000
        
        # 创建缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化模型组件
        self.tokenizer = None
        self.model = None
        
        # 加载模型
        self._load_model()
        
        logger.info(f"初始化 Phi-2 情感分析器: {model_name}")
    
    def _load_model(self):
        """加载 Phi-2 模型 - CPU优化版本"""
        try:
            logger.info(f"正在加载 Phi-2 模型: {self.model_name}")
            logger.info("注意：Phi-2 是一个 2.7B 参数模型，首次加载可能需要几分钟，请耐心等待...")
            
            # 使用 float32 确保 CPU 兼容性
            torch_dtype = torch.float32
            
            # 加载 tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                use_fast=True
            )
            
            # 设置 pad_token（Phi-2 没有默认的 pad_token）
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # 加载因果语言模型
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,  # 低内存模式
                trust_remote_code=True
            )
            
            # 将模型移到 CPU
            self.model.to(self.device)
            self.model.eval()  # 设置为评估模式
            
            logger.info("Phi-2 模型加载完成（CPU模式）")
            
        except Exception as e:
            logger.error(f"加载 Phi-2 模型失败: {e}")
            raise RuntimeError("无法加载 Phi-2 模型")
    
    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        content = f"{self.model_name}:{text}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从缓存加载数据"""
        cache_file = self._get_cache_path(cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            file_mtime = cache_file.stat().st_mtime
            if time.time() - file_mtime > self.cache_ttl:
                cache_file.unlink()
                return None
            
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            logger.debug(f"从缓存加载数据: {cache_key}")
            return cached_data
            
        except Exception as e:
            logger.warning(f"加载缓存失败 {cache_key}: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """保存数据到缓存"""
        try:
            cache_files = list(self.cache_dir.glob("*.pkl"))
            if len(cache_files) > self.max_cache_size:
                cache_files.sort(key=lambda x: x.stat().st_mtime)
                files_to_delete = cache_files[:len(cache_files) - self.max_cache_size + 1]
                for file in files_to_delete:
                    file.unlink()
            
            cache_file = self._get_cache_path(cache_key)
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"数据已缓存: {cache_key}")
            
        except Exception as e:
            logger.warning(f"保存缓存失败 {cache_key}: {e}")
    
    def _construct_prompt(self, text: str) -> str:
        """构建情感分析提示"""
        # 截断过长的文本，避免超出模型上下文窗口
        if len(text) > self.max_length:
            text_to_use = text[:self.max_length]
            logger.debug(f"文本过长，截取前{self.max_length}字符")
        else:
            text_to_use = text
        
        return self.SENTIMENT_PROMPT.format(text=text_to_use)
    
    def _parse_generated_output(self, generated_text: str) -> Optional[tuple]:
        """
        从生成的文本中解析情感标签和置信度
        
        Returns:
            (sentiment, confidence) 或 None
        """
        # 寻找 "正面" 或 "负面"
        pos_idx = generated_text.find("正面")
        neg_idx = generated_text.find("负面")
        
        if pos_idx == -1 and neg_idx == -1:
            # 尝试英文标签
            pos_idx = generated_text.find("positive")
            neg_idx = generated_text.find("negative")
            if pos_idx == -1 and neg_idx == -1:
                logger.warning(f"无法从生成文本中解析情感: {generated_text[:100]}")
                return None
        
        if pos_idx != -1 and (neg_idx == -1 or pos_idx < neg_idx):
            # 计算置信度：基于标签在生成文本中的位置权重
            confidence = 0.7 + (1.0 / (pos_idx + 1)) * 0.3
            confidence = min(confidence, 0.95)
            return ("positive", confidence)
        elif neg_idx != -1:
            confidence = 0.7 + (1.0 / (neg_idx + 1)) * 0.3
            confidence = min(confidence, 0.95)
            return ("negative", confidence)
        
        return None
    
    def analyze_sentiment(self, text: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        分析文本情感 - 使用 Phi-2 生成方式
        
        Args:
            text: 要分析的文本
            use_cache: 是否使用缓存
            
        Returns:
            情感分析结果
        """
        if not text or len(text.strip()) < 3:
            logger.warning("文本太短，无法进行情感分析")
            return None
        
        # 生成缓存键
        cache_key = self._get_cache_key(text)
        
        # 检查缓存
        if use_cache:
            cached_result = self._load_from_cache(cache_key)
            if cached_result:
                return cached_result
        
        logger.info(f"分析文本情感 (长度: {len(text)} 字符)")
        start_time = time.time()
        
        try:
            # 构建提示
            prompt = self._construct_prompt(text)
            
            # 对提示进行 tokenization
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length + 100
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 生成响应
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=20,           # 只需要生成少量 token
                    temperature=0.1,              # 低温度，使输出更确定
                    do_sample=False,              # 贪婪解码
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # 解码生成的文本
            generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
            generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            
            logger.debug(f"生成的文本: {generated_text}")
            
            # 解析情感结果
            parsed = self._parse_generated_output(generated_text)
            if parsed is None:
                logger.warning(f"无法解析 Phi-2 输出: {generated_text}")
                return None
            
            sentiment, confidence = parsed
            
            # 转换为 0-10 分制
            if sentiment == "positive":
                normalized_score = confidence * 10
            else:  # negative
                normalized_score = (1 - confidence) * 10
            
            # 提取关键词（简单分词）
            words = text.split()
            keywords = [word for word in words if len(word) > 1][:10]
            
            # 生成分析结果
            analysis_result = {
                'sentiment': sentiment,
                'score': round(normalized_score, 2),
                'keywords': keywords,
                'reason': f"Phi-2 生成情感标签，置信度 {confidence:.2%}",
                'text': text,
                'text_length': len(text),
                'analysis_time': datetime.now().isoformat(),
                'model': self.model_name,
                'device': self.device,
                'processing_time': round(time.time() - start_time, 3),
                'raw_output': generated_text  # 保留原始输出用于调试
            }
            
            # 缓存结果
            if use_cache:
                self._save_to_cache(cache_key, analysis_result)
            
            logger.info(f"情感分析完成: {sentiment} (分数: {analysis_result['score']})")
            return analysis_result
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return None
    
    def batch_analyze_sentiment(self, texts: List[str], 
                               batch_size: int = 4,  # Phi-2 较大，使用较小的批处理
                               use_cache: bool = True) -> List[Optional[Dict[str, Any]]]:
        """
        批量分析文本情感 - CPU优化版本
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小（Phi-2 建议 1-4）
            use_cache: 是否使用缓存
            
        Returns:
            分析结果列表
        """
        results = []
        total = len(texts)
        
        logger.info(f"开始批量情感分析，共 {total} 条文本")
        logger.info(f"批处理大小: {batch_size} (Phi-2 CPU优化)")
        
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            logger.info(f"处理批次 {batch_num}/{total_batches} ({len(batch)} 条)")
            
            batch_start_time = time.time()
            
            for j, text in enumerate(batch):
                idx = i + j + 1
                logger.debug(f"分析第 {idx}/{total} 条文本")
                
                result = self.analyze_sentiment(text, use_cache=use_cache)
                results.append(result)
            
            batch_time = time.time() - batch_start_time
            logger.debug(f"批次处理时间: {batch_time:.2f}秒")
            
            # 批次间延迟，避免CPU过载
            if i + batch_size < total:
                time.sleep(0.2)
        
        successful = sum(1 for r in results if r is not None)
        logger.info(f"批量情感分析完成，成功分析 {successful}/{total} 条")
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = None) -> Path:
        """
        保存分析结果
        
        Args:
            results: 分析结果列表
            filename: 输出文件名
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"phi2_sentiment_analysis_{timestamp}.json"
        
        output_dir = Path("data/sentiment_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        
        valid_results = [r for r in results if r is not None]
        save_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'model': self.model_name,
                'device': self.device,
                'total_results': len(results),
                'successful_results': len(valid_results)
            },
            'results': valid_results
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"分析结果已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
            return None
    
    def test_analysis(self):
        """测试分析功能"""
        print("=" * 60)
        print("测试 Phi-2 情感分析器 - CPU版")
        print("=" * 60)
        print(f"使用模型: {self.model_name}")
        print(f"使用设备: {self.device}")
        print("注意: Phi-2 是 2.7B 参数模型，首次运行需要下载约 5.4GB 模型文件")
        print("=" * 60)
        
        # 测试文本
        test_texts = [
            "这个产品真的很好用，我非常满意！质量优秀，价格合理，强烈推荐给大家！",
            "质量很差，完全不值这个价格。服务态度也不好，非常失望。",
            "产品一般般，没什么特别的感觉。能用，但不会推荐给朋友。",
            "这是我用过的最好的产品之一！功能强大，设计精美，用户体验极佳！",
            "糟糕的购物体验，产品有缺陷，客服也不解决问题。"
        ]
        
        print(f"测试 {len(test_texts)} 条文本的情感分析")
        
        results = []
        total_time = 0
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n{i}. 文本: {text[:40]}...")
            
            start_time = time.time()
            result = self.analyze_sentiment(text, use_cache=False)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            results.append(result)
            
            if result:
                sentiment = result['sentiment']
                score = result['score']
                
                if sentiment == "positive":
                    sentiment_display = f"\033[92m{sentiment}\033[0m"
                elif sentiment == "negative":
                    sentiment_display = f"\033[91m{sentiment}\033[0m"
                else:
                    sentiment_display = f"\033[93m{sentiment}\033[0m"
                
                print(f"   情感: {sentiment_display}")
                print(f"   分数: {score}/10")
                print(f"   关键词: {', '.join(result['keywords'][:3])}")
                print(f"   处理时间: {elapsed:.3f}秒")
            else:
                print("   分析失败")
        
        if any(results):
            output_path = self.save_results(results, "phi2_test_results.json")
            if output_path:
                print(f"\n测试结果已保存到: {output_path}")
        
        successful = sum(1 for r in results if r is not None)
        avg_time = total_time / len(test_texts) if test_texts else 0
        
        print(f"\n测试完成:")
        print(f"   成功分析: {successful}/{len(test_texts)} 条")
        print(f"   总耗时: {total_time:.2f}秒")
        print(f"   平均每条: {avg_time:.3f}秒")
        
        return successful > 0


def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        print("初始化 Phi-2 情感分析器...")
        print("使用 CPU 模式（需要约 5-6GB 可用内存）")
        
        # 创建分析器
        analyzer = Phi2SentimentAnalyzer(
            model_name="microsoft/phi-2"  # 使用 Microsoft 官方 Phi-2 模型
        )
        
        # 测试分析功能
        success = analyzer.test_analysis()
        
        if success:
            print("\n[SUCCESS] Phi-2 情感分析器测试通过！")
            print("\nPhi-2 模型特点:")
            print("1. 2.7B 参数，强大的语言理解能力")
            print("2. 使用提示工程进行情感分析")
            print("3. 在常识推理和语言理解基准测试中表现优异")
            print("\n可以开始使用以下功能：")
            print("1. analyze_sentiment(text) - 分析单条文本情感")
            print("2. batch_analyze_sentiment(texts) - 批量分析文本情感")
            print("3. save_results(results) - 保存分析结果")
        else:
            print("\n[WARNING] 测试存在问题")
            
    except Exception as e:
        print(f"\n[ERROR] 初始化失败: {e}")
        print("\n可能的解决方案：")
        print("1. 检查网络连接")
        print("2. 确保已安装 transformers: pip install transformers")
        print("3. 确保有足够的磁盘空间（Phi-2 模型需要约 5.4GB）")
        print("4. 确保有足够的内存（建议至少 8GB RAM）")
        print("5. 首次运行需要下载模型，请耐心等待")


if __name__ == "__main__":
    main()