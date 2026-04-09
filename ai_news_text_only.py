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
    """生成小红书发布文案（参考模板：极简清单体，防超长）"""
    date_str = datetime.now().strftime('%m.%d')
    
    # 标题：日期 + 核心词
    first_title = news_data['news'][0]['title'][:15]
    copy_title = f"📅 {date_str} | {first_title}..."
    
    # 标签放在最前面（参考模板）
    tags = "#AI 每日资讯  #人工智能前沿  #科技早知道  #AI 行业观察"
    copy_body = f"{tags}\n\n"
    
    # 序号 Emoji
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    links_list = []
    
    for i, news in enumerate(news_data['news'][:10]):
        title = news.get('title', '')
        url = news.get('url', '')
        
        # 截断过长标题
        if len(title) > 45:
            title = title[:43] + "..."
        
        emoji = emojis[i] if i < len(emojis) else f"{i+1}."
        copy_body += f"{emoji} {title}\n"
        
        if url:
            links_list.append(f"{i+1}. {url}")
    
    # 链接汇总（放在最后，不占用正文主体空间）
    if links_list:
        copy_body += f"\n📎 原文链接：\n" + "\n".join(links_list)
    
    # 固定结尾（参考模板）
    copy_body += f"""

⚡ AI 每日简报，及时、精选、有深度的 AI 资讯
每天几分钟，掌握全球智能浪潮。"""
    
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
