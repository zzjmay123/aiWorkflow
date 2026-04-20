#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报 - CDP 增强版（使用真实 Chrome 浏览器，携带登录态）
"""

import os
import sys
import json
import random
import time
from datetime import datetime
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

# CDP 配置（使用现有的 Pinchtab Chrome）
CDP_ENDPOINT = "http://localhost:9869"


def get_cdp_browser(playwright):
    """连接到现有 Chrome（CDP 模式）"""
    try:
        # 连接到现有 Chrome
        browser = playwright.chromium.connect_over_cdp(CDP_ENDPOINT)
        print("  ✅ 已连接到现有 Chrome（CDP 模式）")
        return browser
    except Exception as e:
        print(f"  ⚠️ CDP 连接失败：{e}，回退到独立浏览器模式")
        # 回退到独立浏览器
        return playwright.chromium.launch(
            headless=True,
            args=['--disable-gpu', '--no-sandbox']
        )


def fetch_news_cdp():
    """使用 CDP 模式抓取 AI 资讯"""
    news_items = []
    seen_titles = set()
    
    # 媒体配置
    sources = [
        {"name": "量子位", "url": "https://www.qbitai.com/", "link_pattern": "/202", "category": "科技"},
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/", "link_pattern": "/news", "category": "科技"},
        {"name": "36 氪", "url": "https://36kr.com/", "link_pattern": "/p/", "category": "科技"},
        {"name": "智东西", "url": "https://zhidx.com/", "link_pattern": "/p/", "category": "硬件"},
        {"name": "虎嗅", "url": "https://www.huxiu.com/", "link_pattern": "/article", "category": "科技"},
    ]
    
    with sync_playwright() as p:
        browser = get_cdp_browser(p)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        
        for source in sources:
            try:
                print(f"  📰 正在抓取 {source['name']}...")
                page.set_default_timeout(20000)
                page.goto(source["url"], wait_until='domcontentloaded')
                page.wait_for_timeout(3000)
                
                # 抓取链接
                links = page.query_selector_all(f'a[href*="{source["link_pattern"]}"]')
                collected = 0
                
                for link in links:
                    if collected >= 5:  # 每个源最多 5 条
                        break
                    
                    try:
                        title = link.inner_text().strip()
                        href = link.get_attribute('href')
                        
                        # 验证标题
                        if not title or len(title) < 8 or len(title) > 60:
                            continue
                        if title in seen_titles:
                            continue
                        if not any(kw in title for kw in ['AI', '智能', '大模型', '算法', '技术', '发布', '数据', '应用', '芯片', '机器人']):
                            continue
                        
                        # 构建 URL
                        full_url = source["url"].rstrip('/') + href if href and href.startswith('/') else href
                        
                        # 进入详情页抓取摘要（CDP 模式成功率高）
                        content = None
                        try:
                            page.goto(full_url, wait_until='domcontentloaded', timeout=15000)
                            page.wait_for_timeout(2000)
                            
                            # 抓取 meta description
                            meta_desc = page.query_selector('meta[name="description"]')
                            if meta_desc:
                                text = meta_desc.get_attribute('content')
                                if text and len(text) > 50 and title[:20] not in text:
                                    content = text[:200]
                            
                            # 抓取正文第一段
                            if not content:
                                for selector in ['article p:first-of-type', '.article-content p:first-child', 'p.summary']:
                                    el = page.query_selector(selector)
                                    if el:
                                        text = el.inner_text().strip()
                                        if text and len(text) > 50 and len(text) < 300 and title[:20] not in text:
                                            content = text
                                            break
                            
                            # 返回列表页
                            page.go_back()
                            page.wait_for_timeout(500)
                            
                        except Exception as e:
                            pass
                        
                        # 如果没有摘要，生成自然引导语
                        if not content:
                            keywords = ['技术', '方案', '产品', '发布', '突破', '进展', '趋势']
                            keyword = next((k for k in keywords if k in title), '进展')
                            templates = [
                                f"行业关注：{title[:40]}，点击查看详细{keyword}报道。",
                                f"热点追踪：{title[:40]}，了解更多行业{keyword}。",
                                f"深度解读：{title[:40]}，探索背后的技术逻辑与商业价值。",
                            ]
                            content = random.choice(templates)
                        
                        # 添加新闻
                        source_name = f"{source['name']}({source['category']})" if source.get('category') != '科技' else source['name']
                        
                        news_items.append({
                            "title": title,
                            "content": content,
                            "source": source_name,
                            "url": full_url if full_url else ""
                        })
                        seen_titles.add(title)
                        collected += 1
                        
                    except Exception as e:
                        continue
                
                print(f"    ✅ {source['name']} 抓取 {collected} 条")
                
            except Exception as e:
                print(f"    ⚠️ {source['name']} 抓取失败：{e}")
                continue
        
        browser.close()
    
    return news_items[:10]


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
    print("AI 资讯快报 - CDP 增强版")
    print("=" * 60)
    print()
    
    # [1/2] 抓取新闻
    print("[1/2] 抓取最新 AI 资讯（CDP 模式）...")
    news_items = fetch_news_cdp()
    print(f"  ✅ 抓取成功 {len(news_items)} 条")
    print()
    
    # [2/2] 生成文本内容
    print("[2/2] 生成文本内容...")
    
    paste_content = format_paste_content(news_items)
    copy_title, copy_body = generate_copy(news_items)
    
    # 保存为文件
    date_str = datetime.now().strftime('%Y%m%d')
    text_file = OUTPUT_DIR / f"AI 资讯快报_{date_str}_CDP.txt"
    
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
