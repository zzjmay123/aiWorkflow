from PIL import Image, ImageDraw
import base64
import re
import shutil

# 1. Load base_bg.png
img_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/design_assets/base_bg.png'
img = Image.open(img_path).convert("RGBA")
width, height = img.size
draw = ImageDraw.Draw(img)

# 2. Sample background color
# Sampling from bottom-left area which should be clean background
bg_color = img.getpixel((50, 1400))
print(f"Image Size: {width}x{height}")
print(f"Sampled background color: {bg_color}")

# 3. Define areas to clean (Coordinates based on 1086x1448)
# We paint with bg_color to remove text/cards, leaving space for HTML to render.

# 3.1 Header Area (Title, Subtitle, Date)
# Preserve the globe on the right (x > 650)
draw.rectangle([0, 0, 650, 380], fill=bg_color)

# 3.2 Card 1 Area
# Assuming cards span full width or mostly left.
# We paint the area where the card is.
draw.rectangle([0, 420, 1086, 780], fill=bg_color)

# 3.3 Card 2 Area
draw.rectangle([0, 820, 1086, 1180], fill=bg_color)

# 3.4 Footer Area
draw.rectangle([0, 1350, 1086, 1448], fill=bg_color)

# 4. Save cleaned image
clean_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/design_assets/clean_bg_v5.png'
img.save(clean_path)
print(f"✅ Saved clean background to {clean_path}")

# 5. Encode to Base64
with open(clean_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
    print(f"✅ Generated Base64 (length: {len(b64)})")

# 6. Update HTML
html_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/ai-news-generator.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r"url\('data:image/png;base64,.*?'\)"
match = re.search(pattern, html)
if match:
    old_full = match.group(0)
    new_full = f"url('data:image/png;base64,{b64}')"
    html = html.replace(old_full, new_full)
    print("✅ Replaced background image in HTML")
else:
    print("❌ Could not find base64 image in CSS")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# 7. Sync to workspace
shutil.copy(html_path, '/Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html')
print("✅ Synced to workspace")
