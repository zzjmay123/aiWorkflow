#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报 - 增强版（使用搜索引擎获取更丰富内容）
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请先安装 Playwright: pip3 install playwright")
    sys.exit(1)


# 配置
WORK_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = WORK_DIR / "output" / "text"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def search_ai_news():
    """使用搜索引擎获取最新 AI 资讯"""
    news_items = []
    seen_titles = set()
    
    # 搜索关键词
    search_queries = [
        "AI 人工智能 最新进展 2026",
        "大模型 技术突破 今天",
        "AI 创业 融资 新闻",
        "机器人 自动驾驶 AI 应用",
        "OpenAI Google 微软 AI 动态",
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-gpu', '--no-sandbox'])
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        for query in search_queries:
            try:
                page = context.new_page()
                page.set_default_timeout(20000)
                
                # 使用必应搜索（结果质量高）
                search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}&first=1"
                page.goto(search_url, wait_until='domcontentloaded')
                page.wait_for_timeout(3000)
                
                # 抓取搜索结果
                results = page.query_selector_all('li.b_algo')
                
                for result in results[:3]:  # 每个查询最多 3 条
                    try:
                        title_el = result.query_selector('h2 a')
                        snippet_el = result.query_selector('div.b_caption p')
                        
                        if title_el and snippet_el:
                            title = title_el.inner_text().strip()
                            snippet = snippet_el.inner_text().strip()
                            url = title_el.get_attribute('href')
                            
                            # 过滤和验证
                            if (len(title) > 10 and len(title) < 60 and 
                                title not in seen_titles and
                                any(kw in title for kw in ['AI', '智能', '大模型', '算法', '技术', '发布', '数据'])):
                                
                                # 提取来源
                                source = "综合搜索"
                                if 'qbitai.com' in url:
                                    source = "量子位"
                                elif 'jiqizhixin.com' in url:
                                    source = "机器之心"
                                elif '36kr.com' in url:
                                    source = "36 氪"
                                elif 'huxiu.com' in url:
                                    source = "虎嗅"
                                elif 'zhidx.com' in url:
                                    source = "智东西"
                                
                                news_items.append({
                                    "title": title,
                                    "content": snippet[:150] + "..." if len(snippet) > 150 else snippet,
                                    "source": source,
                                    "url": url
                                })
                                seen_titles.add(title)
                                
                                if len(news_items) >= 15:
                                    break
                    except:
                        continue
                
                page.close()
                
                if len(news_items) >= 15:
                    break
                    
            except Exception as e:
                print(f"  ⚠️ 搜索失败：{e}")
                continue
        
        browser.close()
    
    return news_items[:10]  # 只返回 10 条


def format_paste_content(news_items):
    """格式化成可粘贴内容"""
    lines = []
    for i, news in enumerate(news_items, 1):
        title = news.get('title', '')
        content = news.get('content', '')
        source = news.get('source', '未知')
        
        lines.append(f"{i}, {title}")
        lines.append(content)
        lines.append(f"来源：{source}")
        lines.append("")
    
    return "\n".join(lines)


def generate_copy(news_items):
    """生成小红书文案"""
    first_title = news_items[0]['title'][:20] if news_items else "AI 技术新突破"
    copy_title = f"AI 圈炸裂 48 小时🔥{first_title}..."
    
    copy_body = f"""宝子们！这两天的 AI 圈真的太热闹了😱
精选 10 条高价值资讯，条条都是爆款潜质👇

━━━━━━━━━━━━━━

"""
    
    links = []
    
    for i, news in enumerate(news_items[:10], 1):
        title = news.get('title', '')
        content = news.get('content', '')
        url = news.get('url', '')
        
        copy_body += f"{i}️⃣【{title}】🔥\n"
        copy_body += f"📌 {content}...\n"
        copy_body += f"💡 影响：行业关注，值得深挖\n\n"
        
        if url:
            links.append(f"{i}. {title[:30]}... → {url}")
    
    copy_body += """━━━━━━━━━━━━━━

🔗 原文链接汇总（复制到评论区）：
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
    print("AI 资讯快报 - 搜索引擎增强版")
    print("=" * 60)
    print()
    
    # [1/2] 搜索新闻
    print("[1/2] 搜索最新 AI 资讯...")
    news_items = search_ai_news()
    print(f"  ✅ 搜索成功 {len(news_items)} 条")
    print()
    
    # [2/2] 生成文本内容
    print("[2/2] 生成文本内容...")
    
    paste_content = format_paste_content(news_items)
    copy_title, copy_body = generate_copy(news_items)
    
    # 保存为文件
    date_str = datetime.now().strftime('%Y%m%d')
    text_file = OUTPUT_DIR / f"AI 资讯快报_{date_str}_search.txt"
    
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"AI 资讯快报 - {datetime.now().strftime('%Y.%m.%d')}\n")
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
