#!/usr/bin/env python3
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # 搜索"快乐马"
    print('搜索：快乐马')
    page.goto('https://www.google.com/search?q=快乐马+AI+新闻&hl=zh-CN', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(5000)
    
    # 抓取搜索结果
    results = page.query_selector_all('div.g')
    print(f'找到 {len(results)} 个结果\n')
    
    for i, r in enumerate(results[:10], 1):
        try:
            title_el = r.query_selector('h3')
            title = title_el.inner_text().strip() if title_el else '无标题'
            
            link_el = r.query_selector('a')
            href = link_el.get_attribute('href') if link_el else '无链接'
            
            snippet_el = r.query_selector('.VwiC3b')
            snippet = snippet_el.inner_text().strip()[:200] if snippet_el else '无摘要'
            
            print(f'{i}. {title}')
            print(f'   {href}')
            print(f'   {snippet}\n')
        except Exception as e:
            print(f'{i}. 抓取失败：{e}\n')
    
    browser.close()
