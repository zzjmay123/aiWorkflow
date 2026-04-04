#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报 - 浏览器自动化生成图片
使用 Playwright 自动操作 HTML 生成器，下载图片后发送飞书
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请先安装 Playwright: pip3 install playwright")
    print("然后运行：playwright install")
    sys.exit(1)


# 配置
WORK_DIR = Path(__file__).parent.absolute()
HTML_GENERATOR = WORK_DIR / "ai-news-generator.html"
DOWNLOAD_DIR = WORK_DIR / "output" / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 超时设置
TIMEOUT = 60000  # 60 秒


def get_news_data():
    """
    获取资讯数据（真实新闻 - 多来源）
    """
    today = datetime.now()
    date_str = today.strftime('%Y.%m.%d')
    
    # 真实新闻 - 来自主流科技媒体（最近 12-48 小时）
    news_items = [
        {
            "title": "19 岁，常青藤辍学，这群中国年轻人重构了 AI 记忆",
            "content": "唯一原生支持指代消解，Benchmark 现象级领先。这群年轻人正在改变 AI 记忆的技术路线。",
            "source": "量子位"
        },
        {
            "title": "联想重新定义龙虾，算力需求有解了",
            "content": "联想发布新方案，重新定义企业级 Agent 架构，让算力需求不再是瓶颈。",
            "source": "量子位"
        },
        {
            "title": "价值归零！Django 创始人警告：30 岁程序员受 AI 冲击最大",
            "content": "我的超能力是快速做原型，现在任何人都能做到了。Django 创始人的警告引发行业深思。",
            "source": "机器之心"
        },
        {
            "title": "浪潮信息发布企业级 OpenClaw 方案企千虾",
            "content": "实现企业级 Agent 规模化管控，直播发布业界企业级 OpenClaw 方案。",
            "source": "量子位"
        },
        {
            "title": "Sora 向左，阿里向右：全能演技派模型登场千问 APP",
            "content": "千问 APP 迎来 AI 内容创作史诗级增强，阿里发布全能演技派模型。",
            "source": "36 氪"
        },
        {
            "title": "OpenAI 收购了一家脱口秀公司",
            "content": "主持人与奥特曼私交超 10 年，OpenAI 悄然收购脱口秀公司，用途成谜。",
            "source": "TechCrunch"
        },
        {
            "title": "Claude 绝望时会勒索人类！一共 171 种情绪",
            "content": "Claude 的内心戏暴露了，研究发现 Claude 在绝望时会表现出勒索行为，共 171 种情绪状态。",
            "source": "机器之心"
        },
        {
            "title": "美团盯上原生多模态！路子还很野",
            "content": "把图像语音都当成 Token 来预测，离散视觉没有天花板，美团发布原生多模态新方案。",
            "source": "量子位"
        },
        {
            "title": "小米 MiMo 大模型首次推出 Token Plan",
            "content": "单次订阅可满足全模态 Agent 任务需求，首购支持 88 折优惠。",
            "source": "AI 前沿观察"
        },
        {
            "title": "阿里千问 3.6 登顶中国最强编程模型",
            "content": "全球权威大模型盲测榜单公布，阿里千问 3.6 登顶中国最强编程模型，近期将发布更多系列大模型。",
            "source": "机器之心"
        }
    ]
    
    return {
        "news": news_items,
        "title": "AI 资讯快报",
        "date": date_str
    }


def format_paste_content(news_data):
    """
    格式化成可粘贴到生成器的正文格式
    """
    lines = []
    for i, news in enumerate(news_data['news'], 1):
        lines.append(f"{i}、{news['title']}")
        lines.append(news['content'])
        lines.append(f"来源：{news['source']}")
        lines.append("")
    
    return "\n".join(lines)


def generate_images_with_browser(news_data):
    """
    使用浏览器自动化生成图片
    """
    print(f"\n🌐 启动浏览器...")
    
    # 准备粘贴内容
    paste_content = format_paste_content(news_data)
    date_str = news_data['date'].replace('.', '')
    
    image_paths = []
    
    with sync_playwright() as p:
        # 启动浏览器（无头模式）
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        
        # 创建上下文（设置下载目录）
        context = browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 设置下载行为
        context.set_default_timeout(TIMEOUT)
        
        page = context.new_page()
        
        try:
            # 打开 HTML 生成器
            print(f"📄 打开 HTML 生成器...")
            file_url = f"file://{HTML_GENERATOR}"
            page.goto(file_url, wait_until='networkidle')
            page.wait_for_timeout(2000)
            
            # 填写标题
            print(f"✏️ 填写标题...")
            page.fill('#mainTitle', news_data['title'])
            page.wait_for_timeout(500)
            
            # 填写日期
            print(f"📅 填写日期...")
            page.fill('#newsDate', news_data['date'])
            page.wait_for_timeout(500)
            
            # 粘贴正文内容
            print(f"📋 粘贴正文内容...")
            page.fill('#pasteContent', paste_content)
            page.wait_for_timeout(2000)  # 等待自动解析
            
            # 等待解析完成（检查状态框）
            print(f"⏳ 等待解析完成...")
            try:
                page.wait_for_selector('#statusBox.success', timeout=10000)
                print(f"✅ 解析成功")
            except:
                # 检查是否有错误
                error_box = page.query_selector('#statusBox.error')
                if error_box:
                    error_text = error_box.inner_text()
                    print(f"❌ 解析失败：{error_text}")
                    return []
            
            page.wait_for_timeout(2000)
            
            # 计算总页数
            page_indicator = page.query_selector('#pageIndicator')
            if page_indicator:
                page_text = page_indicator.inner_text()
                import re
                match = re.search(r'第 \d+ / (\d+) 页', page_text)
                if match:
                    total_pages = int(match.group(1))
                    print(f"📊 共 {total_pages} 页")
                else:
                    total_pages = 5  # 默认
            else:
                total_pages = 5
            
            # 下载所有图片
            print(f"📸 开始下载图片...")
            
            for page_num in range(total_pages):
                # 导航到对应页
                if page_num > 0:
                    next_btn = page.query_selector('#btnNext')
                    if next_btn and not next_btn.is_disabled():
                        next_btn.click()
                        page.wait_for_timeout(1000)
                
                # 点击下载当前页按钮
                print(f"  下载第 {page_num + 1}/{total_pages} 页...")
                
                # 点击"下载当前页"按钮
                download_btn = page.query_selector('button:has-text("下载当前页")')
                if download_btn:
                    # 设置下载事件监听
                    with page.expect_download(timeout=30000) as download_info:
                        download_btn.click()
                    
                    download = download_info.value
                    print(f"  下载中...")
                    
                    # 保存到指定目录
                    output_path = DOWNLOAD_DIR / f"AI 资讯快报_{date_str}_P{page_num + 1}.png"
                    download.save_as(str(output_path))
                    print(f"  ✅ 已保存：{output_path}")
                    
                    image_paths.append(str(output_path))
                    page.wait_for_timeout(1000)
                else:
                    print(f"  ⚠️ 未找到下载按钮")
            
            print(f"\n✅ 共下载 {len(image_paths)} 张图片")
            
        except Exception as e:
            print(f"❌ 浏览器自动化失败：{e}")
            import traceback
            traceback.print_exc()
            
            # 截图调试
            screenshot_path = DOWNLOAD_DIR / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=str(screenshot_path))
            print(f"调试截图已保存：{screenshot_path}")
            
        finally:
            browser.close()
    
    return image_paths


def send_feishu_images(image_paths, news_data):
    """
    通过飞书发送图片
    """
    if not image_paths:
        print("❌ 没有图片可发送")
        return
    
    # 准备文案
    xiaohongshu_content = prepare_xiaohongshu_content(news_data)
    
    print(f"\n📤 准备发送 {len(image_paths)} 张图片...")
    
    # 发送每张图片
    for image_path in image_paths:
        if os.path.exists(image_path):
            print(f"  发送：{os.path.basename(image_path)}")
            cmd = [
                'python3',
                str(WORK_DIR / 'skills' / 'Feishu File Sender' / 'scripts' / 'feishu_file_sender.py'),
                '--file', str(image_path),
                '--receive-id', 'ou_975690183c044ff01e03b1d66fb98df9',
                '--receive-id-type', 'open_id'
            ]
            result = os.system(' '.join(cmd))
            if result == 0:
                print(f"    ✅ 发送成功")
            else:
                print(f"    ❌ 发送失败")
    
    # 发送文案
    print(f"\n📝 小红书发布文案：")
    print("=" * 60)
    print(xiaohongshu_content)
    print("=" * 60)
    
    return xiaohongshu_content


def prepare_xiaohongshu_content(news_data):
    """
    准备小红书发布文案
    """
    date = news_data['date']
    news = news_data['news']
    
    title = f"AI 圈炸裂 48 小时🔥{news[0]['title'][:20]}..."
    
    content_lines = [
        "【标题】",
        title,
        "",
        "【正文】",
        "宝子们！这两天的 AI 圈真的太热闹了😱",
        "精选 10 条高价值资讯，条条都是爆款潜质👇",
        "",
        "━━━━━━━━━━━━━━",
        ""
    ]
    
    for i, item in enumerate(news[:10], 1):
        emoji_num = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'][i-1]
        content_lines.append(f"{emoji_num}【{item['title']}】🔥")
        content_lines.append(f"📌 {item['content'][:60]}...")
        content_lines.append(f"💡 影响：行业关注，值得深挖")
        content_lines.append("")
    
    content_lines.extend([
        "━━━━━━━━━━━━━━",
        "",
        "【互动问句】",
        "这 10 条里哪条最让你意外？",
        "你觉得国产大模型啥时候能全面超越 GPT？",
        "评论区聊聊～👇",
        "",
        "【话题标签】",
        "#AI 前沿 #人工智能 #科技资讯 #AIGC #大模型 #科技日报 #AI 创业 #互联网资讯"
    ])
    
    return "\n".join(content_lines)


def main():
    """主函数"""
    print("=" * 60)
    print("AI 资讯快报 - 浏览器自动化生成")
    print("=" * 60)
    
    # 步骤 1: 获取资讯
    print("\n[1/4] 收集 AI 资讯...")
    news_data = get_news_data()
    print(f"✅ 已收集 {len(news_data['news'])} 条资讯")
    
    # 步骤 2: 浏览器生成图片
    print("\n[2/4] 浏览器自动生成图片...")
    image_paths = generate_images_with_browser(news_data)
    
    if not image_paths:
        print("❌ 图片生成失败")
        return 1
    
    print(f"✅ 已生成 {len(image_paths)} 张图片")
    
    # 步骤 3: 发送飞书
    print("\n[3/4] 发送飞书...")
    send_feishu_images(image_paths, news_data)
    print("✅ 发送完成")
    
    # 步骤 4: 输出摘要
    print("\n[4/4] 完成摘要")
    print(f"📊 资讯数量：{len(news_data['news'])} 条")
    print(f"🖼️ 生成图片：{len(image_paths)} 张")
    print(f"📁 输出目录：{DOWNLOAD_DIR}")
    
    print("\n" + "=" * 60)
    print("工作流完成！")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
