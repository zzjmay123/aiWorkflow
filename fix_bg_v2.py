from PIL import Image, ImageDraw
import base64

# 1. 读取原始完美的背景图
img_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/design_assets/base_bg.png'
img = Image.open(img_path).convert("RGBA")
width, height = img.size

# 2. 定义需要抹除的文字区域 (根据 base_bg.png 的视觉位置估算)
# 日期 "2026.04.27" 和 "星期一" 位于标题下方
# 基于截图观察，大约在 y=200 到 y=280 之间，左侧区域
# 我们涂抹一个矩形覆盖这两个标签
# 坐标估算：
# y_start: 210
# y_end: 270
# x_start: 40
# x_end: 350 (覆盖整个可能的日期和星期宽度)

# 为了确保不破坏背景纹理，我们取该区域左侧边缘的像素颜色进行填充
# 或者使用 ImageDraw 的 floodfill 如果边界清晰，但矩形覆盖更稳妥

# 采样背景色：取 (10, 240) 处的像素，这应该是日期左侧的背景色
bg_color = img.getpixel((10, 240))
print(f"Sampled background color: {bg_color}")

# 创建绘图对象
draw = ImageDraw.Draw(img)

# 绘制矩形覆盖文字区域 (左, 上, 右, 下)
# 稍微扩大一点范围确保完全覆盖
draw.rectangle([30, 200, 380, 280], fill=bg_color)

# 保存
clean_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/design_assets/clean_bg_v2.png'
img.save(clean_path)
print(f"✅ Saved clean background to {clean_path}")

# 3. 转为 Base64 以便更新 HTML
with open(clean_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
    print(f"✅ Generated Base64 (length: {len(b64)})")
    
    # 写入一个临时文件供后续脚本读取
    with open('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/new_bg_b64.txt', 'w') as out:
        out.write(b64)
