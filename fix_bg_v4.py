from PIL import Image, ImageDraw
import base64
import re
import shutil

# 1. Load base_bg.png (The original high-res screenshot)
img_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/design_assets/base_bg.png'
img = Image.open(img_path).convert("RGBA")
width, height = img.size
draw = ImageDraw.Draw(img)

# 2. Define areas to clean (Based on visual inspection of base_bg.png)
# We need to remove:
# - Title area (top left)
# - Date area (below title)
# - Card contents (middle)
# - Footer text (bottom right)

# We will use a solid color fill for rectangular areas that contain text.
# For areas with complex backgrounds (like the globe), we try to be careful, 
# but the globe is on the right, and text is mostly on the left/center.

# 2.1 Title Area: "科技前沿早报"
# Approx coords: [40, 60, 450, 140]
draw.rectangle([40, 60, 450, 140], fill=(245, 247, 254, 255))

# 2.2 Subtitle: "AI 每日精选..."
# Approx coords: [40, 145, 350, 170]
draw.rectangle([40, 145, 350, 170], fill=(245, 247, 254, 255))

# 2.3 Date Area: "2026.04.27" & "星期一"
# Approx coords: [40, 180, 350, 230]
draw.rectangle([40, 180, 350, 230], fill=(245, 247, 254, 255))

# 2.4 Card 1 Area: "01", Title, Content, Source
# Approx coords: [40, 260, 1200, 500]
# The cards are semi-transparent white, so we need to match the background gradient or just paint white/transparent.
# Since the background is a light gradient, painting with a sampled color is safer.
# Let's sample the background color from a clean area (e.g., right side, y=300)
bg_color = img.getpixel((1300, 300))
print(f"Sampled background color: {bg_color}")

draw.rectangle([40, 260, 1200, 500], fill=bg_color)

# 2.5 Card 2 Area: "02", Title, Content, Source
# Approx coords: [40, 520, 1200, 700]
draw.rectangle([40, 520, 1200, 700], fill=bg_color)

# 2.6 Footer text/watermark (bottom right corner)
# Approx coords: [900, 650, 1200, 700]
draw.rectangle([900, 650, 1200, 700], fill=bg_color)

# 3. Save cleaned image
clean_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/design_assets/clean_bg_v4.png'
img.save(clean_path)
print(f"✅ Saved clean background to {clean_path}")

# 4. Encode to Base64
with open(clean_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
    print(f"✅ Generated Base64 (length: {len(b64)})")

# 5. Update HTML
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

# 6. Sync to workspace
shutil.copy(html_path, '/Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html')
print("✅ Synced to workspace")
