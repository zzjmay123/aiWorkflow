#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报 - 优化选择器版（修复链接匹配问题）
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


def fetch_news_fixed_selectors():
    """使用修复后的选择器抓取新闻"""
    news_items = []
    seen_titles = set()
    seen_urls = set()
    
    # 媒体配置 - 使用实际有效的 pattern
    sources = [
        {"name": "量子位", "url": "https://www.qbitai.com/", "link_pattern": "/202", "category": "科技"},
        {"name": "智东西", "url": "https://zhidx.com/", "link_pattern": "zhidx.com/p/", "category": "硬件", "base": "https://zhidx.com"},
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/", "link_pattern": "/articles/", "category": "科技"},
        {"name": "DeepTech", "url": "https://www.deep-tech.cn/", "link_pattern": "/article", "category": "科技"},
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-gpu', '--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            viewport={'width': 1536, 'height': 864},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        for source in sources:
            if len(news_items) >= 15:
                break
            
            try:
                print(f"  📰 正在抓取 {source['name']}...")
                
                page.goto(source["url"], wait_until='domcontentloaded', timeout=20000)
                page.wait_for_timeout(2000)
                page.evaluate("window.scrollBy(0, 600)")
                page.wait_for_timeout(1000)
                
                # 查找所有链接
                all_links = page.query_selector_all('a[href]')
                collected = 0
                skipped = 0
                
                for link in all_links:
                    if collected >= 8 or len(news_items) >= 15:
                        break
                    
                    # 限制跳过次数（避免遍历太多无效链接）
                    if skipped > 100:
                        break
                    
                    try:
                        href = link.get_attribute('href') or ''
                        
                        # 检查是否匹配 pattern
                        if source["link_pattern"] not in href:
                            skipped += 1
                            continue
                        
                        # 跳过已抓取的 URL（防止重复）
                        if href in seen_urls:
                            skipped += 1
                            continue
                        
                        # 跳过分类页、标签页
                        if any(skip in href for skip in ['/category', '/tag', '/topic', 'javascript', '#']):
                            skipped += 1
                            continue
                        
                        title = link.inner_text().strip()
                        
                        # 验证标题
                        if not title or len(title) < 8 or len(title) > 60:
                            skipped += 1
                            continue
                        if title in seen_titles:
                            skipped += 1
                            continue
                        if not any(kw in title for kw in ['AI', '智能', '大模型', '算法', '技术', '发布', '数据', '应用', '芯片', '机器人', '科技']):
                            skipped += 1
                            continue
                        
                        # 构建完整 URL
                        if href.startswith('/'):
                            full_url = source.get('base', source["url"]).rstrip('/') + href
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                        
                        # 尝试抓取摘要（简化：只用 meta description）
                        content = None
                        try:
                            page.goto(full_url, wait_until='domcontentloaded', timeout=12000)
                            page.wait_for_timeout(1000)
                            
                            # 量子位专用选择器
                            if 'qbitai.com' in full_url:
                                content_el = page.query_selector('.content')
                                if content_el:
                                    text = content_el.inner_text().strip()
                                    # 提取第一段有效内容（跳过标题、作者、图片）
                                    lines = [l.strip() for l in text.split('\n') if len(l) > 50 and not l.startswith('<') and '来源：' not in l]
                                    if lines:
                                        content = lines[0][:200]
                            
                            # 通用：meta description
                            if not content:
                                meta_desc = page.query_selector('meta[name="description"]')
                                if meta_desc:
                                    text = meta_desc.get_attribute('content')
                                    if text and len(text) > 50 and title[:20] not in text:
                                        content = text[:200]
                            
                            page.go_back()
                            page.wait_for_timeout(500)
                            
                        except:
                            pass
                        
                        # 生成引导语
                        if not content:
                            keywords = ['技术', '方案', '产品', '发布', '突破', '进展', '趋势']
                            keyword = next((k for k in keywords if k in title), '进展')
                            templates = [
                                f"行业关注：{title[:40]}，点击查看详细{keyword}报道。",
                                f"热点追踪：{title[:40]}，了解更多行业{keyword}。",
                                f"深度解读：{title[:40]}，探索背后的技术逻辑与商业价值。",
                                f"最新资讯：{title[:40]}，点击获取完整{keyword}信息。",
                            ]
                            content = random.choice(templates)
                        
                        source_name = f"{source['name']}({source['category']})" if source.get('category') != '科技' else source['name']
                        
                        news_items.append({
                            "title": title,
                            "content": content,
                            "source": source_name,
                            "url": full_url
                        })
                        seen_titles.add(title)
                        seen_urls.add(href)
                        collected += 1
                        
                    except:
                        continue
                
                if collected > 0:
                    print(f"    ✅ {source['name']} 抓取 {collected} 条（跳过 {skipped} 条）")
                else:
                    print(f"    ⚠️ {source['name']} 无有效链接（跳过 {skipped} 条）")
                
            except Exception as e:
                print(f"    ⚠️ {source['name']} 访问失败")
                continue
        
        browser.close()
    
    random.shuffle(news_items)
    return news_items[:10]


def format_paste_content(news_items):
    lines = []
    for i, news in enumerate(news_items, 1):
        lines.append(f"{i}, {news.get('title', '')}")
        lines.append(news.get('content', ''))
        lines.append(f"来源：{news.get('source', '未知')}")
        lines.append("")
    return "\n".join(lines)


def generate_copy(news_items):
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
    print("=" * 60)
    print("AI 资讯快报 - 优化选择器版")
    print("=" * 60)
    print()
    
    print("[1/2] 抓取最新 AI 资讯...")
    start_time = time.time()
    news_items = fetch_news_fixed_selectors()
    elapsed = time.time() - start_time
    print(f"  ✅ 抓取成功 {len(news_items)} 条（耗时 {elapsed:.1f}秒）")
    print()
    
    print("[2/2] 生成文本内容...")
    
    paste_content = format_paste_content(news_items)
    copy_title, copy_body = generate_copy(news_items)
    
    date_str = datetime.now().strftime('%Y%m%d')
    text_file = OUTPUT_DIR / f"AI 资讯快报_{date_str}_fixed.txt"
    
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"AI 资讯快报 - {datetime.now().strftime('%Y.%m.%d')}\n")
        f.write("=" * 60 + "\n\n")
        f.write("【可粘贴内容】（复制到 ai-news-generator.html）\n")
        f.write("-" * 60 + "\n")
        f.write(paste_content)
        f.write("\n\n")
        f.write("=" * 60 + "\n")
        f.write("【小红书文案】\n")
        f.write("-" * 60 + "\n")
        f.write(f"标题：{copy_title}\n\n")
        f.write(f"正文：\n{copy_body}\n")
        f.write("=" * 60 + "\n")
    
    print(f"  ✅ 已保存：{text_file}")
    print()
    print("=" * 60)
    print("【可粘贴内容】")
    print("=" * 60)
    print(paste_content)
    print()
    print("=" * 60)
    print("【小红书文案】")
    print("=" * 60)
    print(f"标题：{copy_title}\n")
    print(f"正文：\n{copy_body}")
    print("=" * 60)


if __name__ == '__main__':
    main()
