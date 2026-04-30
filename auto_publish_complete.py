#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯全自动发布：生成文本 → Playwright 截图 → 发布小红书
"""

import asyncio
import json
import subprocess
from pathlib import Path
from datetime import datetime

WORK_DIR = Path('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP')
HTML_PATH = 'file:///Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html'
OUTPUT_DIR = WORK_DIR / 'output' / 'images'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def generate_screenshots(paste_content, date_str):
    """使用 Playwright 截图"""
    from playwright.async_api import async_playwright
    
    print("=" * 60)
    print("[1/3] 生成图片（Playwright 截图）")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        await page.goto(HTML_PATH)
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(1)
        
        # 粘贴内容
        textarea = await page.query_selector('textarea[placeholder*="粘贴资讯正文"]')
        if textarea:
            await textarea.fill(paste_content)
            print(f"✅ 已粘贴内容（{len(paste_content)} 字）")
            await asyncio.sleep(2)
        
        # 等待解析
        try:
            await page.wait_for_selector('.news-list-item', timeout=10000)
            print("✅ 内容解析成功")
        except:
            print("❌ 内容解析失败")
            await browser.close()
            return []
        
        await asyncio.sleep(1)
        
        # 获取总页数
        page_info = await page.query_selector('.page-info')
        if page_info:
            page_text = await page_info.inner_text()
            import re
            match = re.search(r'第 \d+ / (\d+) 页', page_text)
            if match:
                total_pages = int(match.group(1))
                print(f"📊 共 {total_pages} 页")
        
        total_pages = 5  # 默认
        
        # 逐页截图
        image_files = []
        for i in range(total_pages):
            # 切换到第 i 页
            next_btn = await page.query_selector('button[aria-label="下一页"]')
            if i > 0 and next_btn:
                await next_btn.click()
                await asyncio.sleep(0.5)
            
            # 截图预览区域
            preview = await page.query_selector('#preview-content')
            if preview:
                image_path = OUTPUT_DIR / f"AI 资讯快报_{date_str}_P{i+1}.png"
                await preview.screenshot(path=str(image_path), type='png', scale='device')
                image_files.append(image_path)
                print(f"  ✅ 第 {i+1} 页：{image_path.name}")
                await asyncio.sleep(0.3)
        
        await browser.close()
        return image_files


def get_xiaohongshu_content(text_file):
    """提取小红书文案"""
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    title_start = content.find('标题：📅')
    if title_start != -1:
        title_line = content[title_start:title_start+100].split('\n')[0]
        title = title_line.replace('标题：', '').strip()
    else:
        today = datetime.now().strftime('%m.%d')
        title = f"📅 {today} AI 日报"
    
    # 提取正文
    copy_start = content.find('#AI 每日资讯')
    if copy_start != -1:
        body = content[copy_start:].strip()
        if "================================================" in body:
            body = body.split("================================================")[0].strip()
    else:
        body = ""
    
    return title, body


async def publish_to_xiaohongshu(images, title, body, is_private=True):
    """发布到小红书"""
    print()
    print("=" * 60)
    print("[2/3] 发布到小红书")
    print("=" * 60)
    
    if not images:
        print("❌ 没有图片")
        return False
    
    # 构建命令
    cmd = [
        'python3', '-m', 'pipx', 'run', 'xiaohongshu-cli',
        'post',
        '--title', title,
        '--body', body
    ]
    
    # 添加图片
    for img in images[:5]:  # 最多 5 张
        cmd.extend(['--images', str(img)])
    
    if is_private:
        cmd.append('--private')
    
    print(f"📤 发布命令:")
    print(f"   标题：{title}")
    print(f"   图片：{len(images)} 张")
    print(f"   模式：{'私密' if is_private else '公开'}")
    print()
    
    # 执行
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        print("✅ 发布成功！")
        print(result.stdout)
        return True
    else:
        print("❌ 发布失败")
        print(result.stderr)
        return False


def notify_user(success, message):
    """发送飞书通知"""
    print()
    print("=" * 60)
    print("[3/3] 发送通知")
    print("=" * 60)
    
    # TODO: 实现飞书通知
    print(f"{'✅' if success else '❌'} {message}")


async def main():
    """主流程"""
    print("🚀 AI 资讯全自动发布流程")
    print("=" * 60)
    print()
    
    # 生成文本
    today = datetime.now().strftime('%Y%m%d')
    text_file = WORK_DIR / 'output' / 'text' / f'AI 资讯快报_{today}.txt'
    
    if not text_file.exists():
        print("❌ 文本文件不存在，请先生成")
        return
    
    print(f"📄 读取文件：{text_file.name}")
    
    # 提取可粘贴内容
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start = content.find('【可粘贴内容】')
    end = content.find('【小红书文案】')
    paste_content = content[start:end].replace(
        '【可粘贴内容】（复制到 ai-news-generator.html）\n------------------------------------------------------------\n',
        ''
    ).strip()
    
    # 提取小红书文案
    title, body = get_xiaohongshu_content(text_file)
    
    # [1/3] 生成图片
    date_str = datetime.now().strftime('%Y%m%d')
    images = await generate_screenshots(paste_content, date_str)
    
    if not images:
        notify_user(False, "图片生成失败")
        return
    
    # [2/3] 发布到小红书（先私密测试）
    success = await publish_to_xiaohongshu(images, title, body, is_private=True)
    
    # [3/3] 通知
    notify_user(success, f"{'发布成功' if success else '发布失败'}")


if __name__ == "__main__":
    asyncio.run(main())
