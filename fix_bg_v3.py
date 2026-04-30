from PIL import Image, ImageDraw
import base64
import re
import shutil

# 1. Load base_bg.png
img_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/design_assets/base_bg.png'
img = Image.open(img_path).convert("RGBA")
width, height = img.size
draw = ImageDraw.Draw(img)

# 2. Define the area to clean (The old date badge area)
# Based on visual inspection of base_bg.png:
# The date badge "2026.04.27" is roughly at y=180 to y=220, x=40 to x=350.
# We will paint a larger rectangle to cover the entire row including the "Monday" text.
# Coordinates: [left, top, right, bottom]
# We'll cover from the left edge to about halfway across, and vertically around the date area.
# Estimated box: [0, 140, 450, 280]
clean_box = [0, 140, 450, 280]

# 3. Sample background color from a clean area
# We sample from the right side (x=500) at the same height (y=200) to get the background color.
bg_color = img.getpixel((500, 200))
print(f"Sampled background color: {bg_color}")

# 4. Paint over the old date badge
draw.rectangle(clean_box, fill=bg_color)

# 5. Save cleaned image
clean_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/design_assets/clean_bg_v3.png'
img.save(clean_path)
print(f"✅ Saved clean background to {clean_path}")

# 6. Encode to Base64
with open(clean_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
    print(f"✅ Generated Base64 (length: {len(b64)})")

# 7. Update HTML
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

# 8. Sync to workspace
shutil.copy(html_path, '/Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html')
print("✅ Synced to workspace")
