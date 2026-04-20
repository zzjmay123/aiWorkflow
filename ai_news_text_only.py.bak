#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报 - 简化版（只生成文本内容）
每天定时执行，生成可粘贴到 HTML 生成器的文本内容
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 导入原有模块
sys.path.insert(0, str(Path(__file__).parent.absolute()))
from auto_news_browser import get_news_data, format_paste_content


# 配置
WORK_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = WORK_DIR / "output" / "text"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_copy(news_data):
    """生成小红书发布文案（优化版：链接集中放置）"""
    # 标题：取第一条新闻的前 20 字
    first_title = news_data['news'][0]['title'][:20]
    copy_title = f"AI 圈炸裂 48 小时🔥{first_title}..."
    
    copy_body = f"""宝子们！这两天的 AI 圈真的太热闹了😱
精选 10 条高价值资讯，条条都是爆款潜质👇

━━━━━━━━━━━━━━

"""
    
    # 收集链接（备用）
    links = []
    
    for i, news in enumerate(news_data['news'][:10], 1):
        title = news.get('title', '')
        content = news.get('content', '')
        url = news.get('url', '')
        
        copy_body += f"{i}️⃣【{title}】🔥\n"
        copy_body += f"📌 {content}...\n"
        
        # 链接直接放在正文里，方便点击
        if url:
            copy_body += f"🔗 原文：{url}\n"
            links.append(f"{i}. {title[:30]}... → {url}")
        
        copy_body += f"💡 影响：行业关注，值得深挖\n\n"
    
    # 添加链接汇总（简化版，方便需要时复制）
    if links:
        copy_body += """━━━━━━━━━━━━━━

📎 全部链接汇总（需要时复制）：
"""
        for link in links:
            copy_body += f"\n{link}"
    
    copy_body += """

━━━━━━━━━━━━━━

【互动问句】
这 10 条里哪条最让你意外？
你觉得 AI 会取代哪些工作？
评论区聊聊～👇

【话题标签】
#AI
#人工智能
#科技资讯
#AIGC
#大模型
#科技日报
#AI 创业
#互联网资讯
#AI 前沿
#黑科技
"""
    
    return copy_title, copy_body


def main():
    """主函数"""
    print("=" * 60)
    print("AI 资讯快报 - 文本生成")
    print("=" * 60)
    print()
    
    # [1/2] 抓取新闻
    print("[1/2] 抓取最新新闻...")
    news_data = get_news_data()
    print(f"  ✅ 抓取成功 {len(news_data['news'])} 条")
    print()
    
    # [2/2] 生成文本内容
    print("[2/2] 生成文本内容...")
    
    # 生成可粘贴内容
    paste_content = format_paste_content(news_data)
    
    # 生成小红书文案
    copy_title, copy_body = generate_copy(news_data)
    
    # 保存为文件
    date_str = news_data['date'].replace('.', '')
    text_file = OUTPUT_DIR / f"AI 资讯快报_{date_str}.txt"
    
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"AI 资讯快报 - {news_data['date']}\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("【可粘贴内容】（复制到 ai-news-generator.html）\n")
        f.write("-" * 60 + "\n")
        f.write(paste_content)
        f.write("\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("【小红书文案】\n")
        f.write("-" * 60 + "\n")
        f.write(f"标题：{copy_title}\n\n")
        f.write(f"正文：\n{copy_body}\n")
        f.write("=" * 60 + "\n")
    
    print(f"  ✅ 已保存：{text_file}")
    print()
    
    # 输出到控制台
    print("=" * 60)
    print("【可粘贴内容】（复制到 ai-news-generator.html）")
    print("=" * 60)
    print(paste_content)
    print()
    
    print("=" * 60)
    print("【小红书文案】")
    print("=" * 60)
    print(f"标题：{copy_title}\n")
    print(f"正文：\n{copy_body}")
    print("=" * 60)
    print()
    print("✅ 全部完成！")


if __name__ == '__main__':
    main()
