import base64
import re
import shutil

# 1. 完整编码 clean_bg.png
clean_bg_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/design_assets/clean_bg.png'
with open(clean_bg_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
print(f"✅ Encoded clean_bg.png (Length: {len(b64)})")

# 2. 更新 HTML
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
    print(" Could not find base64 image in CSS")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# 3. 同步到工作区
shutil.copy(html_path, '/Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html')
print("✅ Synced to workspace")
