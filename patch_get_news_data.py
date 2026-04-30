#!/usr/bin/env python3
"""
补丁：在 get_news_data 中注入 RSS 抓取逻辑
"""
import re

file_path = "/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/auto_news_browser.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找 get_news_data 中的特定位置进行注入
# 目标是在获取到 news_items 之后，return 之前。
# 我们可以利用 `return {` 之前的逻辑。

rss_logic_block = """
    # 🌍 [1.5] 抓取国际源 RSS (OpenAI, The Verge, TechCrunch)
    rss_keywords = ['AI', '人工智能', '大模型', 'GPT', 'OpenAI', '百度', '阿里', '腾讯', '华为', '自动驾驶', '机器人', '芯片', '算力', 'Sora', '文生视频', '多模态', 'Image', 'Model', 'Release']
    rss_sources = [
        ("https://openai.com/blog/rss.xml", "OpenAI 官方"),
        ("https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "The Verge AI"),
        ("https://techcrunch.com/category/artificial-intelligence/feed/", "TechCrunch AI"),
        ("https://hnrss.org/newest?q=ai", "Hacker News AI"),
    ]
    
    rss_items = []
    for rss_url, rss_name in rss_sources:
        try:
            # 调用之前补丁添加的 fetch_rss_news 函数
            items = fetch_rss_news(rss_url, rss_name, keywords=rss_keywords)
            rss_items.extend(items)
            print(f"    ✅ {rss_name} 抓取 {len(items)} 条")
        except Exception as e:
            print(f"    ❌ {rss_name} 抓取失败: {e}")
            
    # 合并新闻并去重
    seen_titles = set(n['title'] for n in news_items)
    for item in rss_items:
        if item['title'] not in seen_titles:
            news_items.append(item)
            seen_titles.add(item['title'])
            
    # 🌟 优先排序：GPT/OpenAI/Image 相关置顶
    priority_kw = ['gpt', 'openai', 'dall-e', 'image', 'model', 'release']
    priority_news = []
    other_news = []
    for n in news_items:
        if any(k in n['title'].lower() for k in priority_kw):
            priority_news.append(n)
        else:
            other_news.append(n)
    news_items = priority_news + other_news

"""

# 查找注入点：在 `except ... : ... backup ...` 之后，`return {` 之前。
# 我们可以匹配 `return {\n        "news": news_items,`

target_pattern = 'return {\n        "news": news_items,'

if target_pattern in content:
    # 检查是否已经插入过
    if "🌍 [1.5] 抓取国际源 RSS" not in content:
        # 注入
        content = content.replace(target_pattern, rss_logic_block + "\n    return {\n        \"news\": news_items,")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 成功在 get_news_data 中注入 RSS 逻辑！")
        
        # 验证语法
        import py_compile
        try:
            py_compile.compile(file_path, doraise=True)
            print("✅ 语法检查通过！")
        except Exception as e:
            print(f"❌ 语法错误: {e}")
    else:
        print("ℹ️ RSS 逻辑已存在。")
        import py_compile
        try:
            py_compile.compile(file_path, doraise=True)
            print("✅ 语法检查通过！")
        except Exception as e:
            print(f"❌ 语法错误: {e}")
else:
    print("❌ 未找到注入点 `return { \"news\": news_items,`")
    print("尝试寻找其他模式...")
    # Fallback: 尝试匹配 `date_str = today.strftime` 这种，但这太早了。
    # 还是直接报错比较好，让用户知道。
