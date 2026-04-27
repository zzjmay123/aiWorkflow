#!/usr/bin/env python3
"""
脚本：为 auto_news_browser.py 添加 RSS 抓取功能
"""
import os
import re as re_mod

file_path = "/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/auto_news_browser.py"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"❌ 读取文件失败: {e}")
    exit(1)

changes_made = False

# 1. 添加 Imports
if "import xml.etree.ElementTree as ET" not in content:
    content = "import xml.etree.ElementTree as ET\n" + content
    changes_made = True

# 2. 添加 fetch_rss_news 函数 (如果不存在)
if "def fetch_rss_news(" not in content:
    rss_func = """
def fetch_rss_news(url, source_name, keywords=None):
    \"\"\"从 RSS 源抓取新闻（使用内置 xml.etree，无需 feedparser）\"\"\"
    news_items = []
    try:
        print(f"  📰 正在抓取 RSS 源：{source_name}...")
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
        res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code != 200:
            print(f"    ⚠️ 状态码：{res.status_code}")
            return news_items
            
        root = ET.fromstring(res.content)
        items = root.findall('.//item')
        
        count = 0
        for item in items:
            if count >= 3:  # 每个源最多抓 3 条
                break
                
            title_elem = item.find('title')
            link_elem = item.find('link')
            desc_elem = item.find('description')
            
            if title_elem is not None:
                title = title_elem.text.strip() if title_elem.text else ""
                link = link_elem.text if link_elem is not None else ""
                desc = desc_elem.text if desc_elem is not None else ""
                
                # 关键词过滤
                if keywords:
                    text_to_check = (title + " " + (desc or "")).lower()
                    if not any(kw.lower() in text_to_check for kw in keywords):
                        continue
                
                # 清理 HTML 标签
                clean_desc = re_mod.sub(r'<[^<]+>', '', desc) if desc else ""
                clean_desc = re_mod.sub(r'\s+', ' ', clean_desc).strip()
                
                # 核心词优先 (GPT, OpenAI 等)
                core_keywords = ['gpt', 'openai', 'dall-e', 'whisper', 'sora', 'model', 'ai', 'artificial intelligence']
                is_core = any(kw in title.lower() for kw in core_keywords)
                
                if is_core or (clean_desc and len(clean_desc) > 20):
                    if len(clean_desc) > 150:
                        clean_desc = clean_desc[:148] + "..."
                    elif not clean_desc:
                        clean_desc = f"【{source_name}】{title}"
                    
                    # 标记国际源
                    content_prefix = ""
                    if any(ord(c) > 127 for c in title):
                        pass # 有中文
                    else:
                        content_prefix = "（国际快讯）"

                    news_items.append({
                        "title": f"{content_prefix}{title}",
                        "content": clean_desc,
                        "source": source_name,
                        "category": "国际",
                        "url": link
                    })
                    count += 1
    except Exception as e:
        print(f"    ⚠️ RSS 抓取失败 {source_name}: {e}")
    return news_items

"""
    if "def get_news_data" in content:
        content = content.replace("def get_news_data", rss_func + "def get_news_data")
        changes_made = True

# 3. 更新关键词
old_keywords_line = "keywords = ['AI', '人工智能', '大模型', 'GPT', 'OpenAI', '百度', '阿里', '腾讯', '华为', '自动驾驶', '机器人', '芯片', '算力', 'Sora', '文生视频', '多模态']"
new_keywords_line = "keywords = ['AI', '人工智能', '大模型', 'GPT', 'OpenAI', '百度', '阿里', '腾讯', '华为', '自动驾驶', '机器人', '芯片', '算力', 'Sora', '文生视频', '多模态', 'Image', 'Model', 'Release']"

if old_keywords_line in content and new_keywords_line not in content:
    content = content.replace(old_keywords_line, new_keywords_line)
    changes_made = True

# 4. 在 get_news_data 中注入 RSS 调用逻辑
# 找到 `all_news.extend(real_news)` 并在其后插入 RSS 抓取
rss_block = """
    # [1.5] 🌍 抓取国际源 RSS (OpenAI, The Verge, TechCrunch)
    rss_sources = [
        ("https://openai.com/blog/rss.xml", "OpenAI 官方"),
        ("https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "The Verge AI"),
        ("https://techcrunch.com/category/artificial-intelligence/feed/", "TechCrunch AI"),
    ]
    
    for rss_url, rss_name in rss_sources:
        rss_news = fetch_rss_news(rss_url, rss_name, keywords=keywords)
        for item in rss_news:
            if item['title'] not in [n['title'] for n in all_news]:
                all_news.append(item)
"""

if "[1.5] 🌍 抓取国际源 RSS" not in content:
    if "all_news.extend(real_news)" in content:
        content = content.replace(
            "all_news.extend(real_news)", 
            "all_news.extend(real_news)\n" + rss_block
        )
        changes_made = True
    else:
        # Fallback: 找不到的话就不改了，避免破坏代码
        print("⚠️ 未找到注入点 `all_news.extend(real_news)`，跳过插入")

# 5. 优先排序逻辑
priority_block = """
    # 🌟 优先排序：包含 'GPT', 'OpenAI', 'Image' 的新闻置顶
    priority_keywords = ['gpt', 'openai', 'dall-e', 'image', 'model', 'release']
    priority_news = [n for n in all_news if any(k in n['title'].lower() for k in priority_keywords)]
    other_news = [n for n in all_news if not any(k in n['title'].lower() for k in priority_keywords)]
    all_news = priority_news + other_news

"""

if "priority_news = [n for n in all_news if any(k in n['title'].lower() for k in priority_keywords)]" not in content:
    if "return all_news[:20]" in content:
        content = content.replace("return all_news[:20]", priority_block + "    return all_news[:20]")
        changes_made = True

if changes_made:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 成功应用 RSS 补丁！")
    print("   - 添加了 fetch_rss_news 函数")
    print("   - 扩展了关键词列表")
    print("   - 添加了国际源抓取逻辑 (OpenAI, The Verge, TechCrunch)")
    print("   - 添加了新闻优先排序 (GPT/OpenAI/Image 置顶)")
    # Syntax check
    import py_compile
    try:
        py_compile.compile(file_path, doraise=True)
        print("✅ 语法检查通过！")
    except py_compile.PyCompileError as e:
        print(f"❌ 语法错误: {e}")
else:
    print("ℹ️ 脚本已是最新状态（或找不到修改点）。")
