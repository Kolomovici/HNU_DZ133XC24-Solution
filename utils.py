"""
工具函数模块 - 提供跨平台兼容的工具函数
"""

import os
import sys
import logging
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import platform

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """设置跨平台环境"""
    system = platform.system()
    
    # 设置编码
    if system == "Windows":
        import locale
        locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    
    # 设置路径分隔符
    os.environ['PATH_SEPARATOR'] = os.pathsep
    
    logger.info(f"运行在 {system} 系统上")

def clean_text(text: str) -> str:
    """
    清理文本，移除特殊字符和多余空格
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 移除URL
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # 移除特殊字符，保留中文、英文、数字和基本标点
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？；：、（）《》【】"\'.,!?;:()\[\]{}]', '', text)
    
    # 移除多余空格和换行
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def save_text_to_file(text: str, filepath: Path) -> bool:
    """
    保存文本到文件，确保UTF-8编码
    
    Args:
        text: 要保存的文本
        filepath: 文件路径
        
    Returns:
        是否保存成功
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.info(f"文本已保存到: {filepath}")
        return True
    except Exception as e:
        logger.error(f"保存文件失败 {filepath}: {e}")
        return False

def load_text_from_file(filepath: Path) -> Optional[str]:
    """
    从文件加载文本，自动处理编码
    
    Args:
        filepath: 文件路径
        
    Returns:
        文本内容或None
    """
    try:
        # 尝试UTF-8编码
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # 尝试GBK编码（中文Windows常用）
            with open(filepath, 'r', encoding='gbk') as f:
                return f.read()
        except Exception as e:
            logger.error(f"加载文件失败 {filepath}: {e}")
            return None
    except Exception as e:
        logger.error(f"加载文件失败 {filepath}: {e}")
        return None

def save_json(data: Dict[str, Any], filepath: Path) -> bool:
    """
    保存数据为JSON文件
    
    Args:
        data: 要保存的数据
        filepath: 文件路径
        
    Returns:
        是否保存成功
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON数据已保存到: {filepath}")
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败 {filepath}: {e}")
        return False

def load_json(filepath: Path) -> Optional[Dict[str, Any]]:
    """
    从JSON文件加载数据
    
    Args:
        filepath: 文件路径
        
    Returns:
        数据字典或None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载JSON文件失败 {filepath}: {e}")
        return None

def get_file_list(directory: Path, extension: str = None) -> List[Path]:
    """
    获取目录中的文件列表
    
    Args:
        directory: 目录路径
        extension: 文件扩展名（可选）
        
    Returns:
        文件路径列表
    """
    if not directory.exists():
        return []
    
    files = []
    for item in directory.iterdir():
        if item.is_file():
            if extension is None or item.suffix.lower() == extension.lower():
                files.append(item)
    
    return sorted(files)

def create_stopwords_file(stopwords_file: Path):
    """
    创建默认的停用词文件
    
    Args:
        stopwords_file: 停用词文件路径
    """
    if stopwords_file.exists():
        return
    
    default_stopwords = [
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要',
        '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '它', '我们', '你们', '他们', '她们',
        '它们', '这个', '那个', '这些', '那些', '什么', '怎么', '为什么', '哪里', '谁', '几', '多少', '一些', '一点',
        '非常', '特别', '比较', '更', '最', '太', '真', '真的', '可以', '可能', '能够', '应该', '必须', '需要', '想要',
        '希望', '喜欢', '爱', '恨', '讨厌', '觉得', '认为', '知道', '了解', '明白', '记得', '忘记', '开始', '结束',
        '继续', '停止', '做', '作', '为', '因为', '所以', '但是', '然而', '而且', '或者', '如果', '那么', '虽然', '即使',
        '无论', '不管', '只有', '只要', '除非', '除了', '关于', '对于', '根据', '通过', '按照', '由于', '为了', '使得',
        '以及', '等等', '例如', '比如', '譬如', '诸如', '之类', '之类', '之类', '之类', '之类', '之类'
    ]
    
    save_text_to_file('\n'.join(default_stopwords), stopwords_file)
    logger.info(f"已创建默认停用词文件: {stopwords_file}")

def check_font_file(font_path: Path) -> bool:
    """
    检查字体文件是否存在
    
    Args:
        font_path: 字体文件路径
        
    Returns:
        字体文件是否存在
    """
    if font_path.exists():
        logger.info(f"找到字体文件: {font_path}")
        return True
    else:
        logger.warning(f"字体文件不存在: {font_path}")
        logger.info("请下载中文字体文件（如SimHei.ttf）到 fonts/ 目录")
        return False

def get_platform_info() -> Dict[str, str]:
    """
    获取平台信息
    
    Returns:
        平台信息字典
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }

# 初始化环境
setup_environment()