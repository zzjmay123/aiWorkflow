#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自动发布流程：生成文本 → 截图 → 发布小红书
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
import time

# 配置
WORK_DIR = Path('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP')
HTML_PATH = '/Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html'
OUTPUT_DIR = WORK_DIR / 'output' / 'images'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 读取今日文案
today = datetime.now().strftime('%Y%m%d')
text_file = WORK_DIR / 'output' / 'text' / f'AI 资讯快报_{today}.txt'

if not text_file.exists():
    print("❌ 文本文件不存在，先生成文本")
    subprocess.run(['python3', str(WORK_DIR / 'ai_news_text_only.py')])

# 读取文案
with open(text_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取可粘贴内容
start = content.find('【可粘贴内容】')
end = content.find('【小红书文案】')
paste_content = content[start:end].replace(
    '【可粘贴内容】（复制到 ai-news-generator.html）\n------------------------------------------------------------\n',
    ''
).strip()

# 提取小红书文案
copy_start = content.find('#AI 每日资讯', end)
if copy_start != -1:
    xiaohongshu_copy = content[copy_start:].strip()
    if "================================================" in xiaohongshu_copy:
        xiaohongshu_copy = xiaohongshu_copy.split("================================================")[0].strip()
else:
    xiaohongshu_copy = ""

# 提取标题
title_start = content.find('标题：📅')
if title_start != -1:
    title_line = content[title_start:title_start+100].split('\n')[0]
    xiaohongshu_title = title_line.replace('标题：', '').strip()
else:
    xiaohongshu_title = f"📅 {today} AI 日报"

print("=" * 60)
print("📋 准备发布内容")
print("=" * 60)
print(f"标题：{xiaohongshu_title}")
print(f"文案长度：{len(xiaohongshu_copy)} 字")
print(f"可粘贴内容长度：{len(paste_content)} 字")
print()

# 使用 Python 脚本控制浏览器截图
screenshot_script = f'''
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import time

async def main():
    paste_content = """{paste_content[:500]}"""  # 简化版，实际需要完整内容
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={{"width": 1920, "height": 1080}})
        page = await context.new_page()
        
        await page.goto('file:///Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html')
        await page.wait_for_load_state('networkidle')
        
        # 粘贴内容
        await page.fill('textarea[placeholder*="粘贴资讯正文"]', paste_content)
        await asyncio.sleep(2)
        
        # 等待解析
        await page.wait_for_selector('.news-list-item', timeout=10000)
        await asyncio.sleep(1)
        
        # 截图预览区域
        preview = await page.query_selector('#preview-content')
        if preview:
            await preview.screenshot(path='/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/output/images/test.png')
            print("✅ 截图成功")
        else:
            print("❌ 未找到预览区域")
        
        await browser.close()

asyncio.run(main())
'''

print(" 准备截图...")
# TODO: 执行截图脚本

# 发布到小红书
print()
print("=" * 60)
print("📤 发布到小红书")
print("=" * 60)

# 检查图片
image_files = list(OUTPUT_DIR.glob('*.png'))
if image_files:
    print(f"找到 {len(image_files)} 张图片")
    
    # 构建发布命令
    cmd = [
        'python3', '-m', 'pipx', 'run', 'xiaohongshu-cli',
        'post',
        '--title', xiaohongshu_title,
        '--body', xiaohongshu_copy
    ]
    
    # 添加图片（最多 5 张）
    for img in sorted(image_files)[:5]:
        cmd.extend(['--images', str(img)])
    
    print(f"发布命令：{' '.join(cmd[:8])}...")
    
    # 询问是否发布
    print()
    print("⚠️  即将发布到小红书，是否继续？")
    print("   图片数：", len(image_files))
    print("   标题：", xiaohongshu_title)
    print("   文案：", len(xiaohongshu_copy), "字")
else:
    print("❌ 未找到图片，无法发布")
