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
    date_str = datetime.now().strftime('%Y-%m-%d')
    date_short = datetime.now().strftime('%m.%d')
    
    # 判断时段（早报/晚报）
    hour = datetime.now().hour
    if 6 <= hour < 12:
        period = "早报"
    elif 12 <= hour < 18:
        period = "午报"
    else:
        period = "晚报"
    
    # 爆款标题库（增加点击率）
    hot_titles = [
        f"突破！全球 AI 最新大事件汇总",
        f"警惕！AI 正在改变这些行业",
        f"重磅！今天 AI 圈发生了这些大事",
        f"干货！10 分钟看懂 AI 最新进展",
        f"必看！AI 从业者不可错过的资讯",
        f"深度！揭秘 AI 技术背后的真相",
    ]
    
    # 随机选择一个标题，避免每天重复
    import random
    copy_title = f"AI {period} | {date_short} | {random.choice(hot_titles)}"
    
    # 标签放在最前面（每个标签单独一行，小红书才能识别）
    tags = "#AI 每日资讯\n#人工智能前沿\n#科技早知道\n#AI 行业观察"
    copy_body = f"{tags}\n\n"
    
    # 序号 Emoji
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '']
    
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
    
    # 链接汇总（放在最后，每个链接单独一行）
    if links_list:
        copy_body += f"\n📎 原文链接：\n" + "\n".join(links_list)
    
    # 固定结尾（根据时段调整）
    copy_body += f"""

⚡ AI {period}，及时、精选、有深度的 AI 资讯
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
        f.write(f"AI 资讯快报 - {news_data['date']}\n\n")
        
        # 可粘贴内容（干净无分隔线）
        f.write("=== 复制下方内容到生成器 ===\n")
        f.write(paste_content.strip() + "\n")
        f.write("=== 复制结束 ===\n\n")
        
        # 小红书文案
        f.write("[小红书文案]\n")
        f.write(f"标题：{copy_title}\n\n")
        f.write(f"正文：\n{copy_body}\n")
    
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
