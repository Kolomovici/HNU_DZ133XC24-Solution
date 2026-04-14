"""
字体下载脚本 - 自动下载中文字体文件
"""

import os
import sys
import requests
from pathlib import Path
import platform
import shutil

def download_font_from_url(url, filename):
    """从URL下载字体文件"""
    try:
        print(f"正在下载字体: {filename}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"字体下载成功: {filename}")
        return True
    except Exception as e:
        print(f"字体下载失败: {e}")
        return False

def copy_system_font(source_path, dest_path):
    """复制系统字体文件"""
    try:
        if os.path.exists(source_path):
            print(f"正在复制系统字体: {source_path}")
            shutil.copy2(source_path, dest_path)
            print(f"字体复制成功: {dest_path}")
            return True
        else:
            print(f"系统字体不存在: {source_path}")
            return False
    except Exception as e:
        print(f"字体复制失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("中文字体下载工具")
    print("=" * 60)
    
    # 创建fonts目录
    fonts_dir = Path("fonts")
    fonts_dir.mkdir(exist_ok=True)
    
    system = platform.system()
    print(f"检测到系统: {system}")
    
    success = False
    
    if system == "Windows":
        # Windows系统 - 尝试复制系统字体
        print("\n尝试从Windows系统复制SimHei字体...")
        
        # Windows系统字体路径
        windows_font_paths = [
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\msyh.ttc",  # 微软雅黑
            r"C:\Windows\Fonts\msyhbd.ttc",  # 微软雅黑粗体
        ]
        
        for font_path in windows_font_paths:
            dest_path = fonts_dir / "simhei.ttf"
            if copy_system_font(font_path, dest_path):
                success = True
                break
        
        if not success:
            print("\n系统字体复制失败，尝试从网络下载...")
            # 从GitHub下载SimHei字体
            font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
            dest_path = fonts_dir / "simhei.ttf"
            success = download_font_from_url(font_url, dest_path)
    
    elif system == "Darwin":  # macOS
        print("\nmacOS系统 - 下载中文字体...")
        # 下载思源黑体
        font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
        dest_path = fonts_dir / "SimHei.ttf"
        success = download_font_from_url(font_url, dest_path)
    
    else:  # Linux
        print("\nLinux系统 - 下载中文字体...")
        # 下载文泉驿微米黑
        font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
        dest_path = fonts_dir / "SimHei.ttf"
        success = download_font_from_url(font_url, dest_path)
    
    # 检查下载结果
    if success:
        print("\n" + "=" * 60)
        print("✅ 字体准备完成！")
        print(f"字体文件位置: {fonts_dir}")
        
        # 列出下载的字体文件
        font_files = list(fonts_dir.glob("*"))
        if font_files:
            print("已下载的字体文件:")
            for font_file in font_files:
                print(f"  - {font_file.name}")
        
        print("\n使用说明:")
        print("1. 字体已准备好，可以正常使用词云功能")
        print("2. 如果需要使用其他字体，请手动放入 fonts/ 目录")
        print("3. 可以在 config.py 中修改字体路径配置")
    else:
        print("\n" + "=" * 60)
        print("❌ 字体准备失败！")
        print("\n请手动下载中文字体:")
        print("1. 下载SimHei字体（黑体）")
        print("2. 将字体文件放入 fonts/ 目录")
        print("3. 确保文件名为 simhei.ttf 或 SimHei.ttf")
        print("\n字体下载地址:")
        print("- 思源黑体: https://github.com/googlefonts/noto-cjk")
        print("- 文泉驿微米黑: http://wenq.org/wqy2/index.cgi")
        print("\n或者使用系统已有字体:")
        if system == "Windows":
            print("复制: C:\\Windows\\Fonts\\simhei.ttf 到 fonts\\ 目录")
        elif system == "Darwin":
            print("macOS系统通常已安装中文字体")
        else:
            print("Linux系统安装: sudo apt-get install fonts-wqy-microhei")
    
    print("\n" + "=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序发生错误: {e}")
        sys.exit(1)