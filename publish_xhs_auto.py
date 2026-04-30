#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布小红书笔记（PNG 转 JPG + 调用 xhs-cli）
"""
import os
import glob
from PIL import Image
from datetime import datetime

def convert_png_to_jpg(png_path):
    """将 PNG 转为 JPG（去除透明度，压缩体积）"""
    img = Image.open(png_path).convert('RGB')
    jpg_path = png_path.replace('.png', '.jpg')
    img.save(jpg_path, 'JPEG', quality=95)
    print(f"✅ 转换完成：{jpg_path}")
    return jpg_path

def main():
    # 查找最近生成的图片（假设在 downloads 或指定目录）
    # 这里你可以根据实际情况修改路径
    search_path = os.path.expanduser("~/Downloads/AI资讯*.png")
    png_files = glob.glob(search_path)
    
    if not png_files:
        print("❌ 未找到图片文件")
        return
    
    # 找最新的图片
    latest_png = max(png_files, key=os.path.getctime)
    print(f"🖼️ 找到图片：{latest_png}")
    
    # 转换
    jpg_path = convert_png_to_jpg(latest_png)
    
    # 调用 xhs post
    # 注意：这里需要你的 ai_news_text_only.py 生成的文案
    # 实际使用时，应该从 txt 文件读取文案
    print(f"\n🚀 准备发布...")
    print(f"请手动运行以下命令发布（或集成到脚本中）：")
    print(f"xhs post --title '今日 AI 日报' --images '{jpg_path}' --body '你的文案内容'")

if __name__ == "__main__":
    main()
