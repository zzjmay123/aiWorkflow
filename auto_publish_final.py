#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯全自动发布：生成文本 → 浏览器下载图片 → 发布小红书
【容错增强版】：自动重试、超时熔断、异常上报
"""

import asyncio
import json
import subprocess
import os
import sys
import signal
import random
from pathlib import Path
from datetime import datetime, timedelta

WORK_DIR = Path('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP')
HTML_PATH = 'file:///Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html?theme=techblue'
DOWNLOAD_DIR = WORK_DIR / 'output' / 'downloads'
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ================= 配置区 =================
MAX_RETRIES = 3              # 最大重试次数
STEP_TIMEOUT = 120           # 单步超时（秒）
GLOBAL_TIMEOUT = 300         # 全局超时（秒）
# ==========================================


def get_time_period():
    """根据当前时间判断是早上还是晚上"""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "早报"
    elif 12 <= hour < 18:
        return "午报"
    else:
        return "晚报"


def send_feishu_error(error_msg, step="未知步骤"):
    """发送错误通知到飞书"""
    print(f"\n🚨 错误通知：{step}")
    print(f"   {error_msg[:100]}...")
    
    try:
        message = f"❌ AI 资讯发布失败\n\n步骤：{step}\n错误：{error_msg[:200]}\n\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_script = WORK_DIR / 'send_copy_text.py'
        if send_script.exists():
            # 写入临时文件发送
            tmp_file = WORK_DIR / 'error_message.txt'
            with open(tmp_file, 'w', encoding='utf-8') as f:
                f.write(message)
            subprocess.run(['python3', str(send_script), str(tmp_file)], capture_output=True, timeout=10)
            print("✅ 错误通知已发送")
    except Exception as e:
        print(f"⚠️ 发送错误通知失败：{e}")


async def download_images_with_retry(paste_content, date_str):
    """带重试机制的图片下载"""
    for attempt in range(MAX_RETRIES):
        try:
            print(f"\n🔄 尝试 {attempt + 1}/{MAX_RETRIES}")
            return await download_images(paste_content, date_str, timeout=STEP_TIMEOUT)
        except asyncio.TimeoutError:
            print(f"⏰ 下载超时（{STEP_TIMEOUT}秒），正在重试...")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ 下载失败：{e}")
            if attempt < MAX_RETRIES - 1:
                print("   清理状态，准备重试...")
                # 清理可能残留的浏览器进程
                subprocess.run(['pkill', '-f', 'playwright'], capture_output=True)
                await asyncio.sleep(3)
            else:
                send_feishu_error(str(e), "图片下载")
                return []
    return []


async def download_images(paste_content, date_str, timeout=60):
    """使用 Playwright 自动下载图片（带超时保护）"""
    from playwright.async_api import async_playwright
    
    print("=" * 60)
    print("[1/3] 生成图片（浏览器下载）")
    print("=" * 60)
    
    image_files = []
    date_formatted = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:8]}"
    period = get_time_period()
    
    # 增加标题多样性，防止被判定为重复内容
    title_prefixes = ["AI", "科技", "全球", "前沿"]
    title_suffixes = ["早报", "速递", "头条", "前沿", "快讯"]
    
    # 根据时间段微调后缀，但保持随机性
    if period == "早报":
        suffix = random.choice(["早报", "晨间速递", "每日头条", "前沿早报"])
    elif period == "午报":
        suffix = random.choice(["午间速递", "午间头条", "午后前沿"])
    else:
        suffix = random.choice(["晚报", "晚间速递", "今日总结"])
        
    html_title = f"{random.choice(title_prefixes)} {suffix}"
    
    browser = None
    try:
        async with async_playwright() as p:
            # 启动浏览器（带超时）
            browser = await asyncio.wait_for(
                p.chromium.launch(headless=True),  # 改为 headless 提高稳定性
                timeout=30
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                accept_downloads=True
            )
            
            page = await context.new_page()
            
            # 导航（带超时）
            await asyncio.wait_for(
                page.goto(HTML_PATH, wait_until='domcontentloaded'),
                timeout=30
            )
            await asyncio.sleep(1)
            
            # 填充表单
            title_input = page.locator('#mainTitle')
            await title_input.fill(html_title)
            print(f"✅ 已更新标题：{html_title}")
            
            date_input = page.locator('#newsDate')
            await date_input.fill(date_formatted)
            print(f"✅ 已更新日期：{date_formatted}")
            
            textarea = page.locator('#pasteContent')
            await textarea.fill(paste_content)
            print(f"✅ 已粘贴内容（{len(paste_content)} 字）")
            await asyncio.sleep(1)
            
            # 等待解析
            await page.wait_for_selector('.news-list-item', timeout=10000)
            print("✅ 内容解析成功")
            
            # 获取总页数
            page_info = page.locator('#pageIndicator')
            page_text = await page_info.inner_text()
            import re
            match = re.search(r'第 \d+ / (\d+) 页', page_text)
            total_pages = int(match.group(1)) if match else 5
            print(f"📊 共 {total_pages} 页")
            
            # 监听下载
            downloads = []
            page.on('download', lambda d: downloads.append(d))
            
            # 触发下载
            await page.evaluate('downloadAll()')
            
            # 等待下载完成（动态等待）
            start_time = datetime.now()
            while len(downloads) < total_pages:
                if (datetime.now() - start_time).total_seconds() > timeout:
                    raise TimeoutError(f"下载超时：只下载了 {len(downloads)}/{total_pages} 张")
                await asyncio.sleep(0.5)
            
            # 保存文件
            for i, download in enumerate(downloads[:total_pages]):
                filename = f"AI 资讯快报_{date_str}_P{i+1}.png"
                save_path = DOWNLOAD_DIR / filename
                await download.save_as(str(save_path))
                image_files.append(save_path)
                file_size = save_path.stat().st_size / 1024
                print(f"  📥 {filename} ({file_size:.1f} KB)")
            
            print("✅ 图片生成完成")
            return image_files
            
    except Exception as e:
        print(f"❌ 图片生成失败：{e}")
        raise
    finally:
        if browser:
            await browser.close()


def get_xiaohongshu_title(date_str):
    """生成小红书标题（爆款风格）"""
    date_formatted = f"{date_str[4:6]}.{date_str[6:8]}"
    period = get_time_period()
    prefix = f"AI {period}"
    
    # 爆款标题库
    hot_titles = [
        "突破！全球 AI 最新大事件汇总",
        "警惕！AI 正在改变这些行业",
        "重磅！今天 AI 圈发生了这些大事",
        "干货！10 分钟看懂 AI 最新进展",
        "必看！AI 从业者不可错过的资讯",
        "深度！揭秘 AI 技术背后的真相",
    ]
    
    import random
    # 使用日期种子，确保同一天标题不变，但不同天随机
    random.seed(date_str)
    subtitle = random.choice(hot_titles)
    
    return f"{prefix} | {date_formatted} | {subtitle}"


def check_already_published(date_str):
    """检查今天是否已经发布过"""
    lock_file = Path("/tmp/xiaohongshu_publish_lock")
    if lock_file.exists():
        with open(lock_file, 'r', encoding='utf-8') as f:
            last_date = f.read().strip()
        if last_date == date_str:
            return True
    return False


def mark_published(date_str):
    """标记今天已发布"""
    lock_file = Path("/tmp/xiaohongshu_publish_lock")
    with open(lock_file, 'w', encoding='utf-8') as f:
        f.write(date_str)


def get_xiaohongshu_content(text_file):
    """提取小红书文案"""
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    copy_start = content.find('#AI 每日资讯')
    if copy_start != -1:
        body = content[copy_start:].strip()
        if "================================================" in body:
            body = body.split("================================================")[0].strip()
    else:
        body = ""
    
    today = datetime.now().strftime('%Y%m%d')
    title = get_xiaohongshu_title(today)
    
    return title, body


async def publish_with_retry(images, title, body, is_private=False):
    """带重试机制的发布"""
    for attempt in range(MAX_RETRIES):
        try:
            print(f"\n🔄 发布尝试 {attempt + 1}/{MAX_RETRIES}")
            return await publish_to_xiaohongshu(images, title, body, is_private, timeout=STEP_TIMEOUT)
        except Exception as e:
            print(f"❌ 发布失败：{e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(5)
            else:
                send_feishu_error(str(e), "小红书发布")
                return False
    return False


async def publish_to_xiaohongshu(images, title, body, is_private=False, timeout=120):
    """发布到小红书（带超时）"""
    print("\n" + "=" * 60)
    print("[2/3] 发布到小红书")
    print("=" * 60)
    
    if not images:
        raise ValueError("没有图片")
    
    # 设置 PYTHONPATH 以找到 xhs_cli 包
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path.home() / '.local' / 'pipx' / 'venvs' / 'xiaohongshu-cli' / 'lib' / 'python3.10' / 'site-packages') + ':' + env.get('PYTHONPATH', '')
    
    cmd = [
        'python3',
        '-m', 'xhs_cli.cli',
        'post',
        '--title', title,
        '--body', body
    ]
    
    for img in images[:5]:
        cmd.extend(['--images', str(img)])
    
    if is_private:
        cmd.append('--private')
    
    print(f"📤 发布命令:")
    print(f"   标题：{title}")
    print(f"   图片：{len(images)} 张")
    print(f"   模式：{'私密' if is_private else '公开'}")
    
    # 异步执行命令（带超时）
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )
    
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        
        if proc.returncode == 0:
            print("✅ 发布成功！")
            print(stdout.decode('utf-8'))
            return True
        else:
            error_msg = stderr.decode('utf-8')
            raise RuntimeError(f"发布失败：{error_msg}")
            
    except asyncio.TimeoutError:
        proc.kill()
        raise TimeoutError(f"发布超时（{timeout}秒）")


def send_feishu_notification(success, title, image_count):
    """发送飞书通知"""
    print("\n" + "=" * 60)
    print("[3/3] 发送飞书通知")
    print("=" * 60)
    
    if success:
        message = f"✅ AI 资讯发布成功！\n\n标题：{title}\n图片：{image_count} 张\n\n已发布到小红书"
    else:
        message = f"❌ AI 资讯发布失败\n\n标题：{title}\n\n请检查错误信息"
    
    try:
        send_script = WORK_DIR / 'send_copy_text.py'
        if send_script.exists():
            tmp_file = WORK_DIR / 'notification.txt'
            with open(tmp_file, 'w', encoding='utf-8') as f:
                f.write(message)
            subprocess.run(['python3', str(send_script), str(tmp_file)], capture_output=True, timeout=10)
            print("✅ 通知已发送")
    except Exception as e:
        print(f"⚠️ 通知发送失败：{e}")


async def main():
    """主流程（带全局超时保护）"""
    print("🚀 AI 资讯全自动发布流程（容错版）")
    print("=" * 60)
    
    # 全局超时保护
    try:
        await asyncio.wait_for(main_logic(), timeout=GLOBAL_TIMEOUT)
    except asyncio.TimeoutError:
        print(f"\n🚨 全局超时（{GLOBAL_TIMEOUT}秒），强制终止")
        send_feishu_error(f"流程超时（{GLOBAL_TIMEOUT}秒）", "全局控制")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(0)


async def main_logic():
    """实际业务逻辑"""
    
    # 🛑 模式调整：只发早报，不发晚报 (已临时关闭)
    # hour = datetime.now().hour
    # if hour >= 12:
    #     print("⚠️ 当前已切换为【早报模式】，跳过非早间发布。")
    #     print("   如需在晚间发布，请确认已修改发布策略。")
    #     return

    today = datetime.now().strftime('%Y%m%d')
    text_file = WORK_DIR / 'output' / 'text' / f'AI 资讯快报_{today}.txt'
    
    # 🧹 强制清理旧文件，确保每次抓取都是最新的
    if text_file.exists():
        print(f"🧹 清理旧文件，强制重新抓取...")
        text_file.unlink()
    
    print("❌ 文本文件不存在，尝试自动生成...")
    # 自动触发生成
    gen_script = WORK_DIR / 'ai_news_text_only.py'
    if gen_script.exists():
        result = subprocess.run(['python3', str(gen_script)], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ 自动生成失败")
            print(result.stderr)
            send_feishu_error("文本生成失败", "初始化")
            return
    else:
        print("❌ 生成脚本不存在")
        return
    
    # 防重复检查
    if check_already_published(today):
        print(f"⚠️ 今天 ({today}) 已经发布过，跳过")
        print("   如需重新发布，请删除 /tmp/xiaohongshu_publish_lock 文件")
        return
    
    print(f"📄 读取文件：{text_file.name}")
    
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start = content.find('=== 复制下方内容到生成器 ===')
    end = content.find('=== 复制结束 ===')
    
    if start != -1 and end != -1:
        paste_content = content[start:end].replace('=== 复制下方内容到生成器 ===\n', '').strip()
    else:
        start = content.find('【可粘贴内容】')
        end = content.find('【小红书文案】')
        paste_content = content[start:end].replace(
            '【可粘贴内容】（复制到 ai-news-generator.html）\n------------------------------------------------------------\n',
            ''
        ).strip()
        paste_content = paste_content.split('====')[0].split('----')[0].strip()
    
    title, body = get_xiaohongshu_content(text_file)
    date_str = today
    
    # [1/3] 下载图片（自动重试）
    images = await download_images_with_retry(paste_content, date_str)
    
    if not images:
        send_feishu_notification(False, title, 0)
        return
    
    # [2/3] 发布到小红书（自动重试）
    success = await publish_with_retry(images, title, body, is_private=False)
    
    # 标记已发布
    if success:
        mark_published(today)
    
    # [3/3] 发送通知
    send_feishu_notification(success, title, len(images))


if __name__ == "__main__":
    asyncio.run(main())
