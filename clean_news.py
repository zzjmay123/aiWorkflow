import re
import os

file_path = "output/text/AI 资讯快报_20260419.txt"

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 简单粗暴的文本处理：
# 找到 "[小红书文案]" 分割点
copy_start = content.find('[小红书文案]')
news_part = content[:copy_start] if copy_start != -1 else content
copy_part = content[copy_start:] if copy_start != -1 else ""

# 按空行分割新闻块
blocks = [b.strip() for b in news_part.split('\n\n') if b.strip()]

new_blocks = []
kept_count = 0
for block in blocks:
    # 跳过标题头
    if '复制下方内容' in block or '2026.04.19' in block:
        new_blocks.append(block)
        continue
    
    # 跳过包含旧闻关键词的
    if "Nature" in block or "龙虾" in block:
        print(f"🗑️  已过滤旧闻: {block[:20]}...")
        continue
    
    # 其他新闻保留
    new_blocks.append(block)
    kept_count += 1

# 重新编号
final_news = []
header = "AI 资讯快报 - 2026.04.19\n\n=== 复制下方内容到生成器 ===\n"
for i, block in enumerate(new_blocks):
    if "复制下方内容" in block or "2026.04.19" in block:
        continue
    
    # 提取内容并重新编号
    # 假设格式是 "数字、标题\n内容\n来源：xxx"
    lines = block.split('\n')
    if len(lines) >= 1 and '、' in lines[0]:
        # 去掉旧编号，加新编号
        title_line = lines[0]
        if title_line[0].isdigit():
            idx = title_line.find('、')
            if idx != -1:
                title_line = f"{i+1}、" + title_line[idx+1:]
        
        lines[0] = title_line
        final_news.append('\n'.join(lines))

# 拼接
final_content = header + '\n\n'.join(final_news) + '\n\n' + copy_part

# 保存
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"✅ 文件已更新，保留了 {kept_count} 条新闻。")
