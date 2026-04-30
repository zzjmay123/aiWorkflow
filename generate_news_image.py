#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报图片生成器 - 完整版
根据输入的资讯内容生成小红书风格的图片，支持批量生成
"""

import sys
import os
import json
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("请先安装 PIL: pip3 install Pillow")
    sys.exit(1)


def get_font(font_path, size):
    """获取字体，如果系统字体不可用则使用默认字体"""
    font_paths = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/PingFang SC.ttc',
        '/Library/Fonts/PingFang.ttc',
        '/Library/Fonts/STHeiti Light.ttc',
        '/Library/Fonts/STHeiti Bold.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        'C:\\Windows\\Fonts\\simhei.ttf',
        'C:\\Windows\\Fonts\\msyh.ttc',
    ]
    
    selected_path = font_path
    if not selected_path or not os.path.exists(selected_path):
        for fp in font_paths:
            if os.path.exists(fp):
                selected_path = fp
                break
    
    try:
        if selected_path and os.path.exists(selected_path):
            return ImageFont.truetype(selected_path, size)
        else:
            return ImageFont.load_default()
    except:
        return ImageFont.load_default()


def wrap_text(draw, text, max_width, font, max_lines=None):
    """文本自动换行"""
    lines = []
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        words = paragraph.split(' ')
        current_line = ''
        
        for word in words:
            test_line = current_line + word + ' '
            if draw.textlength(test_line, font=font) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + ' '
        
        if current_line:
            lines.append(current_line.strip())
        
        if max_lines and len(lines) >= max_lines:
            break
    
    return lines[:max_lines] if max_lines else lines


def create_news_image(news_items, title, date, output_path, page_num=1, total_pages=1):
    """
    生成资讯快报图片
    
    Args:
        news_items: 资讯列表，每项包含 title, content, source
        title: 主标题
        date: 日期
        output_path: 输出文件路径
        page_num: 当前页码
        total_pages: 总页数
    """
    # 图片尺寸
    width = 1080
    height = 1440
    
    # 创建图片
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 边框
    border_width = 10
    draw.rectangle([0, 0, width-1, height-1], outline='black', width=border_width)
    
    # 加载字体
    font_title = get_font(None, 72)
    font_date = get_font(None, 36)
    font_num = get_font(None, 24)
    font_news_title = get_font(None, 32)
    font_news_content = get_font(None, 26)
    font_source = get_font(None, 22)
    font_page = get_font(None, 20)
    
    # 边距
    margin_left = 70
    margin_right = 70
    margin_top = 60
    
    # 绘制标题
    draw.text((width/2, margin_top), title, fill='black', font=font_title, anchor='mm')
    
    # 标题下划线
    line_y = margin_top + 50
    draw.line([(margin_left, line_y), (width - margin_right, line_y)], fill='black', width=4)
    
    # 日期（黑底白字）
    date_y = line_y + 25
    date_bg_width = 280
    date_bg_height = 50
    date_bg_left = (width - date_bg_width) / 2
    draw.rectangle([
        date_bg_left, date_y,
        date_bg_left + date_bg_width, date_y + date_bg_height
    ], fill='black')
    draw.text((width/2, date_y + date_bg_height/2), date, fill='white', font=font_date, anchor='mm')
    
    # 资讯内容起始位置
    content_start_y = date_y + date_bg_height + 40
    
    # 可用高度
    available_height = height - content_start_y - 80
    
    # 绘制每条资讯
    num_items = len(news_items)
    for i, news in enumerate(news_items):
        # 每条资讯的高度
        item_height = available_height / num_items
        item_y = content_start_y + i * item_height
        
        # 资讯卡片背景
        card_margin = 10
        card_rect = [
            margin_left, item_y + card_margin,
            width - margin_right, item_y + item_height - card_margin
        ]
        draw.rectangle(card_rect, outline='black', width=2)
        
        # 编号标签
        num_bg_width = 50
        num_bg_height = 30
        num_bg_left = margin_left + 20
        num_bg_top = item_y + card_margin + 20
        draw.rectangle([
            num_bg_left, num_bg_top,
            num_bg_left + num_bg_width, num_bg_top + num_bg_height
        ], fill='black')
        draw.text((num_bg_left + num_bg_width/2, num_bg_top + num_bg_height/2), 
                 str((page_num - 1) * 2 + i + 1), fill='white', font=font_num, anchor='mm')
        
        # 资讯标题
        news_title_y = num_bg_top + num_bg_height/2
        draw.text((num_bg_left + num_bg_width + 20, news_title_y), 
                 news['title'], fill='black', font=font_news_title, anchor='lm')
        
        # 资讯内容
        content_y = news_title_y + 40
        content_text = news['content']
        
        # 自动换行
        max_width = width - margin_left - num_bg_width - 100
        lines = wrap_text(draw, content_text, max_width, font_news_content, max_lines=5)
        
        line_spacing = 32
        for line in lines:
            draw.text((num_bg_left + num_bg_width + 20, content_y), 
                     line, fill='#333333', font=font_news_content, anchor='lt')
            content_y += line_spacing
        
        # 来源
        if news.get('source'):
            source_y = item_y + item_height - card_margin - 35
            source_text = f"来源：{news['source']}"
            source_bg_width = draw.textlength(source_text, font=font_source) + 24
            source_bg_left = margin_left + 20
            source_bg_top = source_y - 5
            draw.rectangle([
                source_bg_left, source_bg_top,
                source_bg_left + source_bg_width, source_bg_top + 28
            ], fill='#f0f0f0')
            draw.text((source_bg_left + 12, source_bg_top + 11), 
                     source_text, fill='#666666', font=font_source, anchor='lt')
    
    # 页码
    page_text = f"第 {page_num} / {total_pages} 页"
    page_text_width = draw.textlength(page_text, font=font_page)
    draw.text((width/2, height - 40), page_text, fill='#999999', font=font_page, anchor='mm')
    
    # 保存图片
    img.save(output_path, 'PNG', quality=95)
    print(f"图片已保存：{output_path}")
    return output_path


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法：python generate_news_image.py <输出目录> <资讯 JSON 文件>")
        print("或：python generate_news_image.py <输出目录> <资讯 JSON 字符串>")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    news_data_arg = sys.argv[2]
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 解析资讯数据
    try:
        # 尝试从文件读取
        if os.path.exists(news_data_arg):
            with open(news_data_arg, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
        else:
            # 尝试解析 JSON 字符串
            news_data = json.loads(news_data_arg)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误：{e}")
        sys.exit(1)
    
    # 提取数据
    news_items = news_data.get('news', [])
    title = news_data.get('title', 'AI 资讯快报')
    date = news_data.get('date', datetime.now().strftime('%Y.%m.%d'))
    
    if not news_items:
        print("没有资讯内容")
        sys.exit(1)
    
    # 每 2 条资讯生成 1 张图片
    items_per_page = 2
    total_pages = (len(news_items) + items_per_page - 1) // items_per_page
    
    print(f"共 {len(news_items)} 条资讯，将生成 {total_pages} 张图片")
    
    # 生成图片
    output_paths = []
    for page in range(total_pages):
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(news_items))
        page_items = news_items[start_idx:end_idx]
        
        # 生成文件名
        date_str = date.replace('.', '')
        output_path = os.path.join(output_dir, f"AI 资讯快报_{date_str}_P{page+1}.png")
        
        # 生成图片
        create_news_image(
            news_items=page_items,
            title=title,
            date=date,
            output_path=output_path,
            page_num=page + 1,
            total_pages=total_pages
        )
        
        output_paths.append(output_path)
    
    # 输出所有图片路径（JSON 格式）
    print("\n---OUTPUT---")
    print(json.dumps({
        'images': output_paths,
        'total_pages': total_pages,
        'total_items': len(news_items)
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
