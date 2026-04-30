#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报 - 人类行为模拟版（像真人一样浏览，绕过反爬）
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


def human_delay(min_sec=1, max_sec=3):
    """人类行为延迟（1-3 秒随机）"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def human_scroll(page):
    """模拟人类滚动页面"""
    # 随机滚动 1-3 次
    scroll_times = random.randint(1, 3)
    for _ in range(scroll_times):
        # 随机滚动距离（200-500 像素）
        scroll_y = random.randint(200, 500)
        page.evaluate(f"window.scrollBy(0, {scroll_y})")
        # 滚动后停顿
        time.sleep(random.uniform(0.3, 0.8))


def fetch_news_human_like():
    """像人类一样抓取新闻（慢速 + 随机行为）"""
    news_items = []
    seen_titles = set()
    
    # 媒体配置
    sources = [
        {"name": "量子位", "url": "https://www.qbitai.com/", "link_pattern": "/202", "category": "科技"},
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/", "link_pattern": "/news", "category": "科技"},
        {"name": "36 氪", "url": "https://36kr.com/", "link_pattern": "/p/", "category": "科技"},
        {"name": "智东西", "url": "https://zhidx.com/", "link_pattern": "/p/", "category": "硬件"},
        {"name": "虎嗅", "url": "https://www.huxiu.com/", "link_pattern": "/article", "category": "科技"},
        {"name": "钛媒体", "url": "https://www.tmtpost.com/", "link_pattern": "/article", "category": "科技"},
        {"name": "雷锋网", "url": "https://www.leiphone.com/", "link_pattern": "/news", "category": "科技"},
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-gpu',
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': random.randint(1200, 1920), 'height': random.randint(800, 1080)},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN'
        )
        
        # 隐藏自动化特征
        page = context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
        """)
        
        for i, source in enumerate(sources):
            if len(news_items) >= 15:
                break
            
            # 限制只抓取前 4 个媒体（节省时间）
            if i >= 4:
                break
            
            try:
                print(f"  📰 正在浏览 {source['name']}...")
                
                # 人类行为 1：打开页面前停顿
                human_delay(1, 3)
                
                page.set_default_timeout(30000)
                page.goto(source["url"], wait_until='domcontentloaded')
                
                # 人类行为 2：页面加载后等待（像真人阅读）
                human_delay(2, 4)
                
                # 人类行为 3：滚动页面（触发懒加载）
                human_scroll(page)
                
                # 人类行为 4：再次等待
                human_delay(2, 4)
                
                # 抓取链接
                links = page.query_selector_all(f'a[href*="{source["link_pattern"]}"]')
                print(f"    找到 {len(links)} 个链接")
                
                collected = 0
                for link in links:
                    if collected >= 3 or len(news_items) >= 15:
                        break
                    
                    try:
                        # 人类行为 5：点击前停顿
                        human_delay(1, 3)
                        
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
                        
                        # 人类行为 6：进入详情页（慢速）
                        try:
                            page.goto(full_url, wait_until='domcontentloaded', timeout=20000)
                            
                            # 人类行为 7：详情页等待（像真人阅读）
                            human_delay(2, 4)
                            
                            # 人类行为 8：详情页滚动
                            human_scroll(page)
                            
                            # 抓取 meta description
                            content = None
                            meta_desc = page.query_selector('meta[name="description"]')
                            if meta_desc:
                                text = meta_desc.get_attribute('content')
                                if text and len(text) > 50 and title[:20] not in text:
                                    content = text[:200]
                            
                            # 抓取正文第一段
                            if not content:
                                el = page.query_selector('article p:first-of-type')
                                if el:
                                    text = el.inner_text().strip()
                                    if text and len(text) > 50 and len(text) < 300 and title[:20] not in text:
                                        content = text
                            
                            # 人类行为 9：返回列表页（慢速）
                            page.go_back()
                            human_delay(2, 4)
                            
                        except Exception as e:
                            print(f"      ⚠️ 详情抓取失败，继续下一篇")
                            try:
                                page.goto(source["url"], wait_until='domcontentloaded', timeout=15000)
                                human_delay(2, 3)
                            except:
                                pass
                        
                        # 如果没有摘要，生成自然引导语
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
                        print(f"      ✅ {title[:30]}...")
                        
                    except Exception as e:
                        continue
                
                print(f"    ✅ {source['name']} 抓取 {collected} 条")
                
            except Exception as e:
                print(f"    ⚠️ {source['name']} 访问失败：{e}")
                continue
        
        browser.close()
    
    # 打乱顺序
    random.shuffle(news_items)
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
    print("AI 资讯快报 - 人类行为模拟版")
    print("=" * 60)
    print()
    
    # [1/2] 抓取新闻
    print("[1/2] 像人类一样浏览抓取（慢速，约需 3-5 分钟）...")
    start_time = time.time()
    news_items = fetch_news_human_like()
    elapsed = time.time() - start_time
    print(f"  ✅ 抓取成功 {len(news_items)} 条（耗时 {elapsed:.1f}秒）")
    print()
    
    # [2/2] 生成文本内容
    print("[2/2] 生成文本内容...")
    
    paste_content = format_paste_content(news_items)
    copy_title, copy_body = generate_copy(news_items)
    
    # 保存为文件
    date_str = datetime.now().strftime('%Y%m%d')
    text_file = OUTPUT_DIR / f"AI 资讯快报_{date_str}_human.txt"
    
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
