#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成闲鱼主图（9 张）
使用 Playwright 渲染 HTML 并截图
"""

import asyncio
import os
from playwright.async_api import async_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'screenshots')
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; padding: 0; background: #f0f0f0; font-family: 'PingFang SC', 'Heiti SC', 'Microsoft YaHei', sans-serif; }
        .slide {
            width: 1080px;
            height: 1920px;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            background: #ffffff;
        }
        .dark { background: #1a1a1a; color: #fff; }
        .red { background: #ff2442; color: #fff; }
        .blue { background: #007aff; color: #fff; }
        
        .header { padding: 120px 80px; text-align: center; }
        .title { font-size: 120px; font-weight: 900; margin: 0; line-height: 1.2; }
        .subtitle { font-size: 60px; margin-top: 40px; opacity: 0.8; }
        
        .content { flex: 1; padding: 0 80px; display: flex; flex-direction: column; justify-content: center; }
        .list-item { font-size: 56px; margin-bottom: 60px; display: flex; align-items: center; }
        .icon { margin-right: 40px; font-size: 64px; }
        
        .footer { padding: 80px; text-align: center; font-size: 48px; background: rgba(0,0,0,0.05); }
        
        .tag { display: inline-block; padding: 20px 60px; background: #ff2442; color: white; border-radius: 20px; font-size: 48px; margin: 20px; }
        .mock-terminal { background: #000; color: #0f0; padding: 60px; border-radius: 20px; font-family: monospace; font-size: 40px; margin: 40px; }
        .mock-phone { width: 500px; height: 1000px; background: #fff; border: 10px solid #333; border-radius: 60px; margin: 0 auto; overflow: hidden; display: flex; flex-direction: column; }
        .mock-phone-header { height: 120px; background: #ff2442; display: flex; align-items: center; justify-content: center; color: white; font-size: 40px; font-weight: bold; }
        .mock-phone-body { padding: 40px; font-size: 32px; color: #333; }
        
        .price-card { background: #fff; border-radius: 40px; padding: 60px; margin: 40px; text-align: center; border: 4px solid #eee; }
        .price { font-size: 140px; font-weight: 900; color: #ff2442; }
        .old-price { font-size: 60px; text-decoration: line-through; color: #999; }
    </style>
</head>
<body>

<!-- 图 1：封面 -->
<div class="slide dark">
    <div class="header">
        <div style="font-size: 200px; margin-bottom: 40px;">🔥</div>
        <h1 class="title" style="color: #ff2442;">AI 自媒体</h1>
        <h1 class="title">神器来了</h1>
    </div>
    <div class="content" style="align-items: center;">
        <div class="tag">自动抓取</div>
        <div class="tag">自动发文</div>
        <div class="tag">小红书风格</div>
    </div>
    <div class="footer" style="background: #ff2442;">
        每天省 3 小时，躺赚流量
    </div>
</div>

<!-- 图 2：功能列表 -->
<div class="slide">
    <div class="header">
        <h1 class="title" style="color: #000;">✨ 核心功能</h1>
    </div>
    <div class="content">
        <div class="list-item"><span class="icon">🕸️</span> 10+ 科技媒体自动抓取</div>
        <div class="list-item"><span class="icon">🎨</span> 小红书 3:4 风格图生成</div>
        <div class="list-item"><span class="icon">📱</span> 官方 CLI 一键发布</div>
        <div class="list-item"><span class="icon">⏰</span> 早晚报定时自动发</div>
        <div class="list-item"><span class="icon">📨</span> 飞书通知即时提醒</div>
    </div>
</div>

<!-- 图 3：运行效果 -->
<div class="slide dark">
    <div class="header">
        <h1 class="title">🚀 运行效果</h1>
    </div>
    <div class="content">
        <div class="mock-terminal">
            $ python auto_publish_final.py<br>
            <br>
            ✅ 已更新标题：AI 早报<br>
            ✅ 已粘贴内容（1190 字）<br>
            ✅ 内容解析成功<br>
            📊 共 5 页<br>
            📥 下载图片... 100%<br>
            <br>
            ✅ 发布成功!<br>
            🆔 69db2b3b...<br>
            ⭐ Score: 10
        </div>
    </div>
</div>

<!-- 图 4：小红书效果 -->
<div class="slide" style="background: #f8f8f8;">
    <div class="header">
        <h1 class="title" style="color: #ff2442;">📱 发布效果</h1>
    </div>
    <div class="content">
        <div class="mock-phone">
            <div class="mock-phone-header">AI 资讯快报</div>
            <div class="mock-phone-body">
                <div style="width: 100%; height: 300px; background: #eee; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; color: #999;">
                    图片区域
                </div>
                <div style="font-weight: bold; margin-bottom: 10px;">10 条 AI 大事件</div>
                <div>1️⃣ 高通前芯片工程师...</div>
                <div>2️⃣ 做人形机器人...</div>
                <div style="color: #ff2442; margin-top: 20px;">❤️ 1.2w 👀 5.6w</div>
            </div>
        </div>
    </div>
</div>

<!-- 图 5：图片生成器 -->
<div class="slide">
    <div class="header">
        <h1 class="title">🎨 图片生成器</h1>
    </div>
    <div class="content" style="align-items: center;">
        <div style="width: 800px; height: 1000px; border: 4px solid #000; border-radius: 20px; padding: 40px; background: white;">
            <div style="text-align: center; font-size: 60px; font-weight: bold; margin-bottom: 40px; border-bottom: 4px solid #000; padding-bottom: 20px;">AI 资讯快报</div>
            <div style="font-size: 40px; margin-bottom: 30px;">1. 新闻标题示例...</div>
            <div style="font-size: 30px; color: #666; padding: 0 20px;">内容摘要：这里是自动生成的摘要内容，排版精美。</div>
            <div style="margin-top: 40px; text-align: center; font-size: 30px; color: #999;">来源：智东西</div>
        </div>
        <div style="margin-top: 40px; font-size: 48px; color: #666;">自定义尺寸 / 颜色 / 布局</div>
    </div>
</div>

<!-- 图 6：安装流程 -->
<div class="slide blue">
    <div class="header">
        <h1 class="title">⚡ 5 分钟上手</h1>
    </div>
    <div class="content">
        <div class="list-item"><span class="icon">1️⃣</span> CoPaw Skill 一键拉取</div>
        <div class="list-item"><span class="icon">2️⃣</span> bash install.sh 自动装依赖</div>
        <div class="list-item"><span class="icon">3️⃣</span> xiaohongshu auth login 扫码</div>
        <div class="list-item"><span class="icon">4️⃣</span> 运行脚本，全自动搞定</div>
    </div>
    <div class="footer" style="background: rgba(255,255,255,0.2);">
        无需懂代码，有手就行！
    </div>
</div>

<!-- 图 7：交付内容 -->
<div class="slide">
    <div class="header">
        <h1 class="title">📦 交付清单</h1>
    </div>
    <div class="content">
        <div class="list-item">✅ 核心脚本×3 (抓取/生成/发布)</div>
        <div class="list-item">✅ 图片生成器×1 (HTML 可视化工具)</div>
        <div class="list-item">✅ 教程文档×3 (安装/配置/FAQ)</div>
        <div class="list-item">✅ 一键安装脚本×1 (自动环境配置)</div>
        <div class="list-item">✅ 持续更新 (Bug 修复/源维护)</div>
    </div>
</div>

<!-- 图 8：价格对比 -->
<div class="slide" style="background: #fff5f5;">
    <div class="header">
        <h1 class="title" style="color: #ff2442;">💰 价格对比</h1>
    </div>
    <div class="content">
        <div class="price-card">
            <div style="font-size: 40px; color: #666; margin-bottom: 20px;">自己开发</div>
            <div class="old-price">¥ 5000+</div>
            <div style="font-size: 40px; color: #999;">(时间成本)</div>
        </div>
        <div class="price-card" style="border-color: #ff2442; transform: scale(1.1);">
            <div style="font-size: 40px; color: #ff2442; margin-bottom: 20px; font-weight: bold;">🔥 买我的</div>
            <div class="price">¥ 399</div>
            <div style="font-size: 40px; color: #666;">(专业版 包安装)</div>
        </div>
    </div>
</div>

<!-- 图 9：售后承诺 -->
<div class="slide dark">
    <div class="header">
        <h1 class="title" style="color: #ff2442;">🛡️ 售后保障</h1>
    </div>
    <div class="content" style="align-items: center;">
        <div style="font-size: 80px; font-weight: bold; margin-bottom: 60px; color: #fff;">
            买得放心 用得安心
        </div>
        <div class="list-item" style="color: #fff;"><span class="icon">✅</span> 7 天无理由退款</div>
        <div class="list-item" style="color: #fff;"><span class="icon">✅</span> 30 天技术支持</div>
        <div class="list-item" style="color: #fff;"><span class="icon">✅</span> 终身免费更新</div>
        <div class="list-item" style="color: #fff;"><span class="icon">✅</span> 一对一远程安装</div>
    </div>
    <div class="footer" style="background: #ff2442; font-size: 60px; font-weight: bold;">
        立即抢购 限量早鸟价
    </div>
</div>

</body>
</html>
"""

async def main():
    print("🎨 开始生成闲鱼主图...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1080, "height": 1920})
        
        # 写入 HTML
        await page.set_content(HTML_CONTENT)
        await page.wait_for_load_state('networkidle')
        
        # 获取所有 slide
        slides = await page.query_selector_all('.slide')
        
        for i, slide in enumerate(slides):
            filename = f"listing-img-{i+1:02d}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # 截图
            await slide.screenshot(path=filepath)
            print(f"✅ 已生成：{filename}")
            
        await browser.close()
        print(f"\n🎉 全部完成！图片保存在：{OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())