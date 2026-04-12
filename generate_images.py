#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成闲鱼主图（9 张）
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# 配置
OUTPUT_DIR = Path(__file__).parent / "assets" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 图片尺寸（闲鱼建议 1080x1920 竖屏）
WIDTH, HEIGHT = 1080, 1920

# 颜色配置
COLORS = {
    "bg_dark": (15, 23, 42),      # 深蓝黑背景
    "bg_light": (255, 255, 255),  # 白色背景
    "primary": (255, 68, 68),     # 小红书红
    "accent": (255, 193, 7),      # 黄色强调
    "text_white": (255, 255, 255),
    "text_dark": (33, 37, 41),
    "text_gray": (108, 117, 125),
    "success": (40, 167, 69),     # 绿色
    "border": (222, 226, 230),
}


def get_font(size):
    """获取中文字体"""
    # macOS
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/PingFang.ttc",
        "/Library/Fonts/PingFang.ttc",
    ]
    for path in font_paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    
    # Linux/Windows 兜底
    try:
        return ImageFont.truetype("SimHei", size)
    except:
        return ImageFont.load_default()


def draw_text_centered(draw, text, y, font_size, color, bold=False):
    """居中绘制文本"""
    font = get_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    draw.text((x, y), text, fill=color, font=font)
    return y + font_size + 10


def create_cover():
    """图 1：封面图（吸引点击）"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS["bg_dark"])
    draw = ImageDraw.Draw(img)
    
    # 背景渐变效果
    for i in range(HEIGHT):
        alpha = i / HEIGHT
        r = int(15 + (255 - 15) * alpha * 0.1)
        g = int(23 + (255 - 23) * alpha * 0.1)
        b = int(42 + (255 - 42) * alpha * 0.1)
        draw.line([(0, i), (WIDTH, i)], fill=(r, g, b))
    
    # 顶部 emoji
    draw.text((WIDTH//2 - 60, 150), "🔥📰", fill=COLORS["accent"], font=get_font(80))
    
    # 主标题
    font = get_font(72)
    text = "AI 自媒体神器"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    draw.text((x, 280), text, fill=COLORS["text_white"], font=font)
    
    # 副标题
    font = get_font(48)
    texts = [
        ("自动抓取 + 自动发布", COLORS["primary"]),
        ("每天省 3 小时", COLORS["accent"]),
        ("CoPaw Skill 一键安装", COLORS["text_white"]),
    ]
    y = 420
    for text, color in texts:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (WIDTH - text_width) // 2
        draw.text((x, y), text, fill=color, font=font)
        y += 70
    
    # 功能列表
    y = 700
    font = get_font(36)
    features = [
        "🕸️ 10+ 媒体自动抓取",
        "🎨 小红书风格图片",
        "📱 一键发布小红书",
        "⏰ 早晚报自动区分",
        "📨 飞书通知",
    ]
    for feature in features:
        bbox = draw.textbbox((0, 0), feature, font=font)
        text_width = bbox[2] - bbox[0]
        x = (WIDTH - text_width) // 2
        draw.text((x, y), feature, fill=COLORS["text_white"], font=font)
        y += 60
    
    # 底部标签
    y = 1100
    font = get_font(42)
    text = "科技资讯自动化工作流"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    draw.text((x, y), text, fill=COLORS["text_gray"], font=font)
    
    # 价格标签
    y = 1300
    font = get_font(60)
    text = "限时 ¥299 起"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    draw.text((x, y), text, fill=COLORS["primary"], font=font)
    
    # 底部提示
    font = get_font(32)
    text = "前 10 名早鸟价"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    draw.text((x, 1400), text, fill=COLORS["accent"], font=font)
    
    img.save(OUTPUT_DIR / "01-cover.png")
    print("✅ 图 1：封面图已生成")


def create_features():
    """图 2：功能展示"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS["bg_light"])
    draw = ImageDraw.Draw(img)
    
    # 标题
    y = draw_text_centered(draw, "✨ 核心功能", 80, 56, COLORS["text_dark"], bold=True)
    y += 40
    
    # 功能列表
    font = get_font(36)
    features = [
        ("🕸️ 智能抓取", "10+ 家科技媒体最新 AI 新闻\n量子位、36 氪、IT 之家、虎嗅..."),
        ("🎨 图片生成", "小红书风格图片生成器\n3:4 比例｜可自定义｜黑色主题"),
        ("📱 自动发布", "小红书官方 CLI，安全合规\n自动上传 5 张图片"),
        ("⏰ 定时发布", "支持 cron 定时执行\n早 8 点发 AI 早报，晚 8 点发 AI 晚报"),
        ("📨 飞书通知", "发布完成即时提醒\n工作摸鱼两不误"),
    ]
    
    for title, desc in features:
        y += 30
        # 功能框
        box_y = y
        draw.rounded_rectangle(
            [(60, y), (WIDTH-60, y+180)],
            radius=12,
            fill=(248, 249, 250),
            outline=COLORS["primary"],
            width=2
        )
        
        # 标题
        draw.text((100, y+20), title, fill=COLORS["text_dark"], font=get_font(40))
        
        # 描述
        desc_font = get_font(28)
        desc_y = y + 75
        for line in desc.split('\n'):
            draw.text((100, desc_y), line, fill=COLORS["text_gray"], font=desc_font)
            desc_y += 40
        
        y += 210
    
    img.save(OUTPUT_DIR / "02-features.png")
    print("✅ 图 2：功能展示已生成")


def create_terminal():
    """图 3：运行效果截图"""
    img = Image.new('RGB', (WIDTH, HEIGHT), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    
    # 终端标题栏
    draw.rectangle([(0, 0), (WIDTH, 50)], fill=(60, 60, 60))
    draw.text((20, 15), "Terminal", fill=(200, 200, 200), font=get_font(24))
    
    # 终端内容
    font = get_font(28)
    lines = [
        ("$ python scripts/auto_publish_final.py", (100, 100, 255)),
        ("", (255, 255, 255)),
        ("🚀 AI 资讯全自动发布流程", (255, 255, 255)),
        ("=" * 60, (100, 100, 100)),
        ("", (255, 255, 255)),
        ("📄 读取文件：AI 资讯快报_20260412.txt", (255, 255, 255)),
        ("", (255, 255, 255)),
        ("[1/3] 生成图片（浏览器下载）", (100, 200, 255)),
        ("✅ 已更新日期：2026.04.12", (40, 167, 69)),
        ("✅ 已粘贴内容（1190 字）", (40, 167, 69)),
        ("✅ 内容解析成功", (40, 167, 69)),
        ("📊 共 5 页", (255, 193, 7)),
        ("  📥 AI 资讯快报_20260412_P1.png", (200, 200, 200)),
        ("  📥 AI 资讯快报_20260412_P2.png", (200, 200, 200)),
        ("  📥 AI 资讯快报_20260412_P3.png", (200, 200, 200)),
        ("  📥 AI 资讯快报_20260412_P4.png", (200, 200, 200)),
        ("  📥 AI 资讯快报_20260412_P5.png", (200, 200, 200)),
        ("    ✅ AI 资讯快报_20260412_P1.png (187.9 KB)", (40, 167, 69)),
        ("    ✅ AI 资讯快报_20260412_P2.png (172.9 KB)", (40, 167, 69)),
        ("    ✅ AI 资讯快报_20260412_P3.png (169.4 KB)", (40, 167, 69)),
        ("    ✅ AI 资讯快报_20260412_P4.png (175.4 KB)", (40, 167, 69)),
        ("    ✅ AI 资讯快报_20260412_P5.png (189.0 KB)", (40, 167, 69)),
        ("", (255, 255, 255)),
        ("[2/3] 发布到小红书", (100, 200, 255)),
        ("✅ 发布成功！", (40, 167, 69)),
        ("笔记 ID: 69db2b3b000000001f005c60", (100, 200, 255)),
        ("", (255, 255, 255)),
        ("✅ 全部完成！", (40, 167, 69)),
    ]
    
    y = 100
    for text, color in lines:
        if text:
            draw.text((40, y), text, fill=color, font=font)
        y += 38
    
    img.save(OUTPUT_DIR / "03-terminal.png")
    print("✅ 图 3：运行效果已生成")


def create_install():
    """图 4：安装流程"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS["bg_light"])
    draw = ImageDraw.Draw(img)
    
    # 标题
    y = draw_text_centered(draw, "🚀 5 分钟上手", 80, 56, COLORS["text_dark"], bold=True)
    y += 60
    
    # 步骤
    font = get_font(40)
    steps = [
        ("1", "克隆仓库", "git clone ..."),
        ("2", "运行安装", "bash install.sh\n自动安装所有依赖"),
        ("3", "扫码授权", "xiaohongshu auth login\n小红书 App 扫码"),
        ("4", "运行脚本", "python scripts/xxx.py\n生成文本 + 发布"),
        ("5", "完成！", "开始自动发笔记\n每天省 3 小时"),
    ]
    
    for i, (num, title, desc) in enumerate(steps):
        y += 40
        
        # 步骤框
        box_y = y
        draw.rounded_rectangle(
            [(60, y), (WIDTH-60, y+200)],
            radius=16,
            fill=(248, 249, 250),
            outline=COLORS["primary"] if i < 3 else COLORS["success"],
            width=3
        )
        
        # 序号
        draw.ellipse([(100, y+20), (180, y+100)], fill=COLORS["primary"] if i < 3 else COLORS["success"])
        draw.text((120, y+35), num, fill=COLORS["text_white"], font=get_font(48))
        
        # 标题
        draw.text((220, y+35), title, fill=COLORS["text_dark"], font=font)
        
        # 描述
        desc_font = get_font(28)
        desc_y = y + 95
        for line in desc.split('\n'):
            draw.text((220, desc_y), line, fill=COLORS["text_gray"], font=desc_font)
            desc_y += 40
        
        y += 230
    
    img.save(OUTPUT_DIR / "04-install.png")
    print("✅ 图 4：安装流程已生成")


def create_price():
    """图 5：价格对比"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS["bg_dark"])
    draw = ImageDraw.Draw(img)
    
    # 标题
    y = draw_text_centered(draw, "💰 价格对比", 80, 56, COLORS["text_white"], bold=True)
    y += 80
    
    # 价格卡片
    cards = [
        ("自己开发", "¥5000+", "时间成本\n至少 1 周开发\n后续维护", COLORS["text_gray"]),
        ("找外包", "¥3000+", "一次性费用\n沟通成本高\n质量不稳定", COLORS["text_gray"]),
        ("买我的", "¥399", "专业版全包\n5 分钟上手\n30 天售后", COLORS["primary"]),
    ]
    
    for i, (title, price, desc, color) in enumerate(cards):
        x = 80 + i * 320
        card_y = y
        
        # 卡片背景
        fill_color = (40, 40, 60) if i < 2 else (255, 68, 68, 100)
        draw.rounded_rectangle(
            [(x, card_y), (x+300, card_y+450)],
            radius=16,
            fill=fill_color if i < 2 else (60, 30, 30),
            outline=color,
            width=3
        )
        
        # 标题
        draw.text((x+150, card_y+30), title, fill=color, font=get_font(36), anchor="mm")
        
        # 价格
        draw.text((x+150, card_y+120), price, fill=COLORS["text_white"], font=get_font(56), anchor="mm")
        
        # 描述
        desc_font = get_font(26)
        desc_y = card_y + 220
        for line in desc.split('\n'):
            draw.text((x+150, desc_y), line, fill=COLORS["text_white"], font=desc_font, anchor="mm")
            desc_y += 45
    
    # 底部提示
    y += 520
    draw_text_centered(draw, "省下的时间接 2 个私活就回本了！", y, 40, COLORS["accent"])
    
    img.save(OUTPUT_DIR / "05-price.png")
    print("✅ 图 5：价格对比已生成")


def create_delivery():
    """图 6：交付内容"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS["bg_light"])
    draw = ImageDraw.Draw(img)
    
    # 标题
    y = draw_text_centered(draw, "📦 交付内容", 80, 56, COLORS["text_dark"], bold=True)
    y += 60
    
    # 交付列表
    font = get_font(36)
    items = [
        ("✅", "核心脚本×3", "ai_news_text_only.py\nauto_news_browser.py\nauto_publish_final.py", COLORS["success"]),
        ("✅", "图片生成器×1", "ai-news-generator.html\n浏览器打开即用\n可自定义样式", COLORS["success"]),
        ("✅", "教程文档×3", "安装指南 + 配置说明 + 常见问题\n小白也能看懂", COLORS["success"]),
        ("✅", "安装脚本×1", "bash install.sh\n一键安装所有依赖", COLORS["success"]),
        ("✅", "持续更新", "新闻源维护\nBug 修复\n功能升级", COLORS["success"]),
    ]
    
    for icon, title, desc, color in items:
        y += 30
        
        # 项目框
        draw.rounded_rectangle(
            [(60, y), (WIDTH-60, y+160)],
            radius=12,
            fill=(248, 249, 250),
            outline=color,
            width=2
        )
        
        # 图标
        draw.text((100, y+20), icon, fill=color, font=get_font(48))
        
        # 标题
        draw.text((180, y+25), title, fill=COLORS["text_dark"], font=get_font(40))
        
        # 描述
        desc_font = get_font(26)
        desc_y = y + 80
        for line in desc.split('\n'):
            draw.text((180, desc_y), line, fill=COLORS["text_gray"], font=desc_font)
            desc_y += 35
        
        y += 180
    
    img.save(OUTPUT_DIR / "06-delivery.png")
    print("✅ 图 6：交付内容已生成")


def create_warranty():
    """图 7：售后保障"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS["bg_dark"])
    draw = ImageDraw.Draw(img)
    
    # 标题
    y = draw_text_centered(draw, "🛡️ 售后保障", 80, 56, COLORS["text_white"], bold=True)
    y += 80
    
    # 保障列表
    font = get_font(40)
    items = [
        ("✅", "7 天无理由退款", "不影响二次销售", COLORS["success"]),
        ("✅", "30 天技术支持", "专业版起", COLORS["success"]),
        ("✅", "终身免费更新", "新闻源维护 + Bug 修复", COLORS["success"]),
        ("✅", "远程安装服务", "专业版起", COLORS["success"]),
        ("✅", "问题响应时间<2 小时", "工作时间", COLORS["success"]),
    ]
    
    for icon, title, desc, color in items:
        y += 40
        
        # 项目框
        draw.rounded_rectangle(
            [(60, y), (WIDTH-60, y+140)],
            radius=12,
            fill=(40, 40, 60),
            outline=color,
            width=2
        )
        
        # 图标
        draw.text((100, y+20), icon, fill=color, font=get_font(48))
        
        # 标题
        draw.text((180, y+25), title, fill=COLORS["text_white"], font=font)
        
        # 描述
        draw.text((180, y+85), desc, fill=COLORS["text_gray"], font=get_font(28))
        
        y += 150
    
    img.save(OUTPUT_DIR / "07-warranty.png")
    print("✅ 图 7：售后保障已生成")


def create_targets():
    """图 8：适用人群"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS["bg_light"])
    draw = ImageDraw.Draw(img)
    
    # 标题
    y = draw_text_centered(draw, "🎯 适用人群", 80, 56, COLORS["text_dark"], bold=True)
    y += 60
    
    # 适用人群
    font = get_font(36)
    targets = [
        ("✅", "AI/科技自媒体从业者", "每天需要发内容\n但没时间找素材", COLORS["success"]),
        ("✅", "小红书批量运营者", "多账号管理\n需要自动化工具", COLORS["success"]),
        ("✅", "想日更但没时间的", "内容创作者\n效率提升 3 倍", COLORS["success"]),
        ("✅", "有 CoPaw/OpenClaw 环境的", "想提效的开发者\n一键安装", COLORS["success"]),
        ("❌", "完全不懂电脑的小白", "建议先学基础\n或买专业版包安装", COLORS["primary"]),
    ]
    
    for icon, title, desc, color in targets:
        y += 30
        
        # 项目框
        fill = (240, 255, 240) if icon == "✅" else (255, 240, 240)
        draw.rounded_rectangle(
            [(60, y), (WIDTH-60, y+160)],
            radius=12,
            fill=fill,
            outline=color,
            width=2
        )
        
        # 图标
        draw.text((100, y+20), icon, fill=color, font=get_font(48))
        
        # 标题
        draw.text((180, y+25), title, fill=COLORS["text_dark"], font=get_font(38))
        
        # 描述
        desc_font = get_font(26)
        desc_y = y + 80
        for line in desc.split('\n'):
            draw.text((180, desc_y), line, fill=COLORS["text_gray"], font=desc_font)
            desc_y += 35
        
        y += 170
    
    img.save(OUTPUT_DIR / "08-targets.png")
    print("✅ 图 8：适用人群已生成")


def create_bonus():
    """图 9：限时福利"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS["bg_dark"])
    draw = ImageDraw.Draw(img)
    
    # 背景装饰
    for i in range(0, HEIGHT, 100):
        draw.line([(0, i), (WIDTH, i)], fill=(40, 40, 60), width=1)
    
    # 标题
    y = draw_text_centered(draw, "🎉 限时福利", 80, 56, COLORS["accent"], bold=True)
    y += 20
    draw_text_centered(draw, "前 10 名专享", y, 40, COLORS["primary"])
    y += 80
    
    # 福利列表
    font = get_font(40)
    bonuses = [
        ("🎁", "早鸟价 ¥299", "原价¥399", COLORS["primary"]),
        ("📖", "送《小红书运营手册》", "电子版", COLORS["accent"]),
        ("💰", "送《自媒体变现指南》", "实战经验", COLORS["accent"]),
        ("🔄", "终身免费更新", "新闻源维护 + 功能升级", COLORS["success"]),
    ]
    
    for icon, title, desc, color in bonuses:
        y += 40
        
        # 福利框
        draw.rounded_rectangle(
            [(60, y), (WIDTH-60, y+140)],
            radius=16,
            fill=(40, 40, 60),
            outline=color,
            width=3
        )
        
        # 图标
        draw.text((100, y+20), icon, fill=color, font=get_font(56))
        
        # 标题
        draw.text((200, y+30), title, fill=COLORS["text_white"], font=font)
        
        # 描述
        draw.text((200, y+90), desc, fill=COLORS["text_gray"], font=get_font(28))
        
        y += 150
    
    # 倒计时提示
    y += 60
    draw_text_centered(draw, "⏰ 名额有限，先到先得！", y, 44, COLORS["primary"])
    
    # 行动号召
    y += 100
    draw.rounded_rectangle(
        [(100, y), (WIDTH-100, y+100)],
        radius=50,
        fill=COLORS["primary"],
        outline=COLORS["text_white"],
        width=3
    )
    draw_text_centered(draw, "💬 有任何问题欢迎私信咨询！", y+25, 40, COLORS["text_white"])
    
    img.save(OUTPUT_DIR / "09-bonus.png")
    print("✅ 图 9：限时福利已生成")


def main():
    """生成所有主图"""
    print("=" * 60)
    print("生成闲鱼主图（9 张）")
    print("=" * 60)
    print()
    
    create_cover()      # 图 1：封面
    create_features()   # 图 2：功能
    create_terminal()   # 图 3：运行效果
    create_install()    # 图 4：安装流程
    create_price()      # 图 5：价格对比
    create_delivery()   # 图 6：交付内容
    create_warranty()   # 图 7：售后保障
    create_targets()    # 图 8：适用人群
    create_bonus()      # 图 9：限时福利
    
    print()
    print("=" * 60)
    print(f"✅ 全部完成！图片保存在：{OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
