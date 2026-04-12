#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯全自动发布：生成文本 → 浏览器下载图片 → 发布小红书
"""

import asyncio
import json
import subprocess
from pathlib import Path
from datetime import datetime

WORK_DIR = Path('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP')
HTML_PATH = 'file:///Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html'
DOWNLOAD_DIR = Path.home() / 'Downloads'


def get_time_period():
    """根据当前时间判断是早上还是晚上"""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "早报"
    elif 12 <= hour < 18:
        return "午报"
    else:
        return "晚报"


async def download_images(paste_content, date_str):
    """使用 Playwright 自动下载图片"""
    from playwright.async_api import async_playwright
    
    print("=" * 60)
    print("[1/3] 生成图片（浏览器下载）")
    print("=" * 60)
    
    image_files = []
    
    # 格式化日期为 YYYY.MM.DD
    date_formatted = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:8]}"
    
    # 获取时段（早报/晚报）
    period = get_time_period()
    html_title = f"AI {period}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        # 关键配置：允许下载
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            accept_downloads=True
        )
        
        page = await context.new_page()
        
        await page.goto(HTML_PATH)
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(1)
        
        # 【修复 1】更新标题和日期
        title_input = await page.query_selector('#newsTitle')
        if title_input:
            await title_input.fill(html_title)
            print(f"✅ 已更新标题：{html_title}")
        
        date_input = await page.query_selector('#newsDate')
        if date_input:
            await date_input.fill(date_formatted)
            print(f"✅ 已更新日期：{date_formatted}")
            await asyncio.sleep(0.5)
        
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
        page_info = await page.query_selector('#pageIndicator')
        total_pages = 5  # 默认
        if page_info:
            page_text = await page_info.inner_text()
            import re
            match = re.search(r'第 \d+ / (\d+) 页', page_text)
            if match:
                total_pages = int(match.group(1))
                print(f"📊 共 {total_pages} 页")
        
        # 【修复 2】使用 downloadAll() 函数一次性下载
        print(f"  调用 downloadAll() 下载全部 {total_pages} 张图片...")
        
        # 监听下载事件
        downloads = []
        def handle_download(download):
            downloads.append(download)
            print(f"  📥 {download.suggested_filename}")
        
        page.on('download', handle_download)
        
        # 调用 downloadAll
        await page.evaluate('downloadAll()')
        
        # 等待所有下载完成（每张图间隔 500ms）
        await asyncio.sleep(total_pages * 0.7)
        
        # 保存文件
        for i, download in enumerate(downloads[:total_pages]):
            filename = f"AI 资讯快报_{date_str}_P{i+1}.png"
            save_path = DOWNLOAD_DIR / filename
            await download.save_as(str(save_path))
            image_files.append(save_path)
            
            file_size = save_path.stat().st_size / 1024
            print(f"    ✅ {filename} ({file_size:.1f} KB)")
        
        await browser.close()
    
    return image_files


def get_xiaohongshu_title(date_str):
    """生成小红书标题（格式：AI 早报/晚报 | 日期 | 引流说明）"""
    # 格式化为 MM.DD
    date_formatted = f"{date_str[4:6]}.{date_str[6:8]}"
    
    # 判断时段
    period = get_time_period()
    prefix = f"AI {period}"
    
    # 标题格式：AI 早报/晚报 | 时间日期 | 简单的引流说明
    # 引流说明要简洁有吸引力，每天轮换
    titles = [
        "AI 圈热点速递",
        "10 条 AI 大事件",
        "AI 人必看",
        "今日 AI 风向标",
        "AI 前沿动态"
    ]
    
    # 根据日期选择一个（每天轮换）
    import hashlib
    hash_val = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    subtitle = titles[hash_val % len(titles)]
    
    title = f"{prefix} | {date_formatted} | {subtitle}"
    
    return title


def check_already_published(date_str):
    """检查今天是否已经发布过（防重复）"""
    lock_file = Path("/tmp/xiaohongshu_publish_lock")
    
    if lock_file.exists():
        with open(lock_file, 'r') as f:
            last_date = f.read().strip()
        if last_date == date_str:
            return True
    return False


def mark_published(date_str):
    """标记今天已发布"""
    lock_file = Path("/tmp/xiaohongshu_publish_lock")
    with open(lock_file, 'w') as f:
        f.write(date_str)


def get_xiaohongshu_content(text_file):
    """提取小红书文案"""
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题（备用，如果不需要自定义标题）
    title_start = content.find('标题：📅')
    if title_start != -1:
        title_line = content[title_start:title_start+100].split('\n')[0]
        default_title = title_line.replace('标题：', '').strip()
    else:
        default_title = f"📅 {datetime.now().strftime('%m.%d')} AI 日报"
    
    # 提取正文
    copy_start = content.find('#AI 每日资讯')
    if copy_start != -1:
        body = content[copy_start:].strip()
        if "================================================" in body:
            body = body.split("================================================")[0].strip()
    else:
        body = ""
    
    # 使用标准标题格式
    today = datetime.now().strftime('%Y%m%d')
    title = get_xiaohongshu_title(today)
    
    return title, body


async def publish_to_xiaohongshu(images, title, body, is_private=False):
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
    for img in images[:5]:
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


def send_feishu_notification(success, title, image_count):
    """发送飞书通知"""
    print()
    print("=" * 60)
    print("[3/3] 发送飞书通知")
    print("=" * 60)
    
    if success:
        message = f"✅ AI 资讯发布成功！\n\n标题：{title}\n图片：{image_count} 张\n\n已发布到小红书"
    else:
        message = f"❌ AI 资讯发布失败\n\n标题：{title}\n\n请检查错误信息"
    
    # 调用飞书发送脚本
    send_script = WORK_DIR / 'send_copy_text.py'
    if send_script.exists():
        subprocess.run(['python3', str(send_script)], capture_output=True)
        print("✅ 通知已发送")
    else:
        print("⚠️ 飞书通知脚本不存在")


async def main():
    """主流程"""
    print("🚀 AI 资讯全自动发布流程")
    print("=" * 60)
    print()
    
    # 读取今日文本
    today = datetime.now().strftime('%Y%m%d')
    text_file = WORK_DIR / 'output' / 'text' / f'AI 资讯快报_{today}.txt'
    
    if not text_file.exists():
        print("❌ 文本文件不存在，请先生成")
        print(f"   运行：python3 ai_news_text_only.py")
        return
    
    # 【防重复发布】检查今天是否已经发布过
    if check_already_published(today):
        print(f"⚠️ 今天 ({today}) 已经发布过，跳过")
        print("   如需重新发布，请删除 /tmp/xiaohongshu_publish_lock 文件")
        return
    
    print(f"📄 读取文件：{text_file.name}")
    
    # 提取可粘贴内容
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start = content.find('=== 复制下方内容到生成器 ===')
    end = content.find('=== 复制结束 ===')
    
    if start != -1 and end != -1:
        paste_content = content[start:end].replace('=== 复制下方内容到生成器 ===\n', '').strip()
    else:
        # 兼容旧格式
        start = content.find('【可粘贴内容】')
        end = content.find('【小红书文案】')
        paste_content = content[start:end].replace(
            '【可粘贴内容】（复制到 ai-news-generator.html）\n------------------------------------------------------------\n',
            ''
        ).strip()
        # 移除末尾可能的分隔线
        paste_content = paste_content.split('====')[0].split('----')[0].strip()
    
    # 提取小红书文案
    title, body = get_xiaohongshu_content(text_file)
    
    # [1/3] 下载图片
    date_str = datetime.now().strftime('%Y%m%d')
    images = await download_images(paste_content, date_str)
    
    if not images:
        send_feishu_notification(False, title, 0)
        return
    
    # [2/3] 发布到小红书
    success = await publish_to_xiaohongshu(images, title, body, is_private=False)
    
    # 标记已发布
    if success:
        mark_published(today)
    
    # [3/3] 发送通知
    send_feishu_notification(success, title, len(images))


if __name__ == "__main__":
    asyncio.run(main())
