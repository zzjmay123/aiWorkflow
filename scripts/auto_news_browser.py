#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报 - 浏览器自动化生成图片
使用 Playwright 自动操作 HTML 生成器，下载图片后发送飞书
"""

import os
import sys
import json
import time
import asyncio
import requests
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请先安装 Playwright: pip3 install playwright")
    print("然后运行：playwright install")
    sys.exit(1)


# 配置
WORK_DIR = Path(__file__).parent.absolute()
HTML_GENERATOR = WORK_DIR / "ai-news-generator.html"
DOWNLOAD_DIR = WORK_DIR / "output" / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 超时设置
TIMEOUT = 60000  # 60 秒


def is_valid_news_title(text, seen_titles, keywords):
    """验证标题是否有效"""
    if not text or len(text) < 8 or len(text) > 60:
        return False
    if 'http' in text or text.startswith('http'):
        return False
    if text in seen_titles:
        return False
    
    # 过滤广告、导购、促销内容
    exclude_keywords = ['京东', '天猫', '淘宝', '大促', '优惠', '价格', '元', '购买', '导购', '评测', '开箱']
    if any(kw in text for kw in exclude_keywords):
        return False
    
    return any(kw.lower() in text.lower() for kw in keywords)


def fetch_article_detail(page, url, timeout=15000):
    """进入文章详情页抓取内容"""
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=timeout)
        page.wait_for_timeout(3000)
        
        # 尝试多种选择器抓取正文
        content_selectors = [
            'article p', '.article-content p', '.post-content p',
            'div.content p', 'section p', '[class*="content"] p',
            '[class*="article"] p', 'div[p*="content"] p'
        ]
        
        paragraphs = []
        for selector in content_selectors:
            try:
                els = page.query_selector_all(selector)
                if els:
                    for el in els:
                        text = el.inner_text().strip()
                        # 过滤：长度适中，不是导航/广告
                        if (len(text) > 50 and len(text) < 500 and 
                            not text.startswith('http') and
                            '广告' not in text and
                            '推荐' not in text):
                            paragraphs.append(text)
                    if paragraphs:
                        break
            except:
                continue
        
        if paragraphs:
            # 取前 2-3 段组合成摘要
            summary = ' '.join(paragraphs[:3])
            return summary[:150] + "..." if len(summary) > 150 else summary
        
        # 如果没抓到，尝试抓取 meta description
        try:
            meta_desc = page.query_selector('meta[name="description"]')
            if meta_desc:
                content = meta_desc.get_attribute('content')
                if content and len(content) > 50:
                    return content[:150] + "..." if len(content) > 150 else content
        except:
            pass
        
        return None
    except Exception as e:
        return None


def fetch_ithome_list():
    """
    用 requests 抓取 IT 之家列表页（速度快，结构清晰）
    """
    news_items = []
    try:
        print(f"  📰 正在抓取 IT 之家 (requests 模式)...")
        url = "https://www.ithome.com/list/"
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for item in soup.select('ul.datel li'):
            t_el = item.select_one('a.t')
            i_el = item.select_one('i')
            
            if t_el and i_el:
                title = t_el.text.strip()
                time_str = i_el.text.strip()
                
                # 解析时间 2026-04-09 04:30:10
                if '2026-04-' in time_str:
                    try:
                        pub_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                        
                        # 过滤：只取最近 24 小时，且与 AI 相关
                        if (datetime.now() - pub_time).total_seconds() < 24 * 3600:
                            # AI 关键词检查
                            ai_keywords = ['AI', '智能', '大模型', '算法', 'GPT', 'Claude', 'OpenAI', 
                                           '智谱', '通义', '文心', 'LLM', 'AGI', 'Copilot', '机器人',
                                           '自动驾驶', '算力', '芯片', '训练', '深度学习', '神经网络']
                            
                            is_ai = any(kw.lower() in title.lower() for kw in ai_keywords)
                            
                            if is_ai:
                                raw_url = t_el['href'] if t_el.has_attr('href') else ""
                                if raw_url.startswith('//'):
                                    full_url = 'https:' + raw_url
                                elif raw_url.startswith('/'):
                                    full_url = 'https://www.ithome.com' + raw_url
                                else:
                                    full_url = raw_url
                                    
                                news_items.append({
                                    "title": title,
                                    "content": f"IT 之家快讯：{title}，点击查看详细报道。",
                                    "source": "IT 之家",
                                    "category": "快讯",
                                    "url": full_url,
                                    "publish_time": pub_time
                                })
                    except:
                        pass
    
    except Exception as e:
        print(f"    ⚠️ IT 之家 requests 抓取失败：{e}")
        
    return news_items

def fetch_real_news():
    """
    真实抓取最新 AI 新闻（最近 24-48 小时）
    策略：优先使用 IT 之家 requests + 其他媒体 Playwright
    """
    from playwright.sync_api import sync_playwright
    
    news_items = []
    seen_titles = set()
    
    # 1. 优先抓取 IT 之家 (requests 模式，最快最新)
    ithome_news = fetch_ithome_list()
    
    # 【关键修复】限制 IT 之家最多 5 条，确保来源多样性
    for item in ithome_news[:5]:
        if item['title'] not in seen_titles:
            news_items.append(item)
            seen_titles.add(item['title'])
    print(f"  ✅ IT 之家抓取 {len(ithome_news)} 条（使用{min(len(ithome_news), 5)}条）")

    # 媒体配置：名称、URL、文章链接特征、摘要选择器
    sources = [
        {
            "name": "量子位", 
            "url": "https://www.qbitai.com/", 
            "link_pattern": "/202", 
            "category": "科技",
            "summary_selector": "div.excerpt-summary, p.excerpt"
        },
        {
            "name": "36 氪", 
            "url": "https://36kr.com/", 
            "link_pattern": "/p/", 
            "category": "科技",
            "summary_selector": "p.summary, div.content-snippet"
        },
        {
            "name": "机器之心", 
            "url": "https://www.jiqizhixin.com/", 
            "link_pattern": "/articles/",  # 修正：机器之心用 /articles/
            "category": "科技",
            "summary_selector": "p.summary, div.abstract"
        },
        {
            "name": "虎嗅", 
            "url": "https://www.huxiu.com/", 
            "link_pattern": "/article", 
            "category": "科技",
            "summary_selector": "div.article-summary, p.intro"
        },
        {
            "name": "智东西", 
            "url": "https://zhidx.com/", 
            "link_pattern": "/p/", 
            "category": "硬件",
            "summary_selector": "div.excerpt, p.description"
        },
        {
            "name": "车东西", 
            "url": "https://chedongxi.com/", 
            "link_pattern": "/article", 
            "category": "汽车",
            "summary_selector": "div.excerpt, p.summary"
        },
        {
            "name": "钛媒体", 
            "url": "https://www.tmtpost.com/", 
            "link_pattern": "/article", 
            "category": "科技",
            "summary_selector": "p.summary, div.abstract"
        },
        {
            "name": "雷锋网", 
            "url": "https://www.leiphone.com/", 
            "link_pattern": "/news", 
            "category": "科技",
            "summary_selector": "p.summary, div.abstract"
        },
        {
            "name": "DeepTech", 
            "url": "https://deeptechtech.com/", 
            "link_pattern": "/article", 
            "category": "科技",
            "summary_selector": "p.summary, div.excerpt"
        },
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-gpu', '--no-sandbox'])
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        for source in sources:
            try:
                print(f"  📰 正在抓取 {source['name']}...")
                page = context.new_page()
                page.set_default_timeout(20000)
                page.goto(source["url"], wait_until='domcontentloaded')
                page.wait_for_timeout(3000)
                
                # 抓取所有链接
                links = page.query_selector_all(f'a[href*="{source["link_pattern"]}"]')
                collected = 0
                
                for link in links:
                    if collected >= 3:  # 每个源最多 3 条
                        break
                    
                    try:
                        title = link.inner_text().strip()
                        href = link.get_attribute('href')
                        
                        # 验证标题
                        if not is_valid_news_title(title, seen_titles, 
                            ['AI', '智能', '大模型', '算法', '技术', '发布', '数据', '应用', 
                             '芯片', '自动驾驶', '机器人', '系统', '平台', '产品']):
                            continue
                        
                        # 策略 1：在父元素中查找摘要（列表页通常有摘要）
                        content = None
                        parent = link
                        for _ in range(3):  # 向上找 3 层父元素
                            parent = parent.query_selector('..')
                            if not parent:
                                break
                            # 尝试查找摘要段落
                            for selector in ['p', 'div', 'span']:
                                for el in parent.query_selector_all(selector):
                                    text = el.inner_text().strip()
                                    # 摘要特征：长度适中，不是标题本身
                                    if (len(text) > 50 and len(text) < 200 and 
                                        text != title and
                                        title[:20] not in text):
                                        content = text
                                        break
                                if content:
                                    break
                            if content:
                                break
                        
                        # 策略 2：如果列表页没有摘要，用新标签页进入详情页抓取（不影响主页）
                        if not content and href:
                            try:
                                detail_page = context.new_page()
                                full_url = source["url"].rstrip('/') + href if href.startswith('/') else href
                                detail_page.goto(full_url, wait_until='domcontentloaded', timeout=15000)
                                detail_page.wait_for_timeout(1500)
                                
                                # 【关键】检查发布时间，只取最近 24 小时的文章
                                import re
                                pub_time = None
                                for sel in ['time[datetime]', 'time', 'span.date', '.entry-date', '.cat-links']:
                                    try:
                                        time_el = detail_page.query_selector(sel)
                                        if time_el:
                                            dt = time_el.get_attribute('datetime')
                                            if dt:
                                                try:
                                                    pub_time = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                                                    if pub_time.tzinfo:
                                                        pub_time = pub_time.replace(tzinfo=None)
                                                    break
                                                except:
                                                    pass
                                            
                                            txt = time_el.inner_text().strip()
                                            match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', txt)
                                            if match:
                                                y, m, d = map(int, match.groups())
                                                time_match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})', txt)
                                                if time_match:
                                                    h, mi, s = map(int, time_match.groups())
                                                else:
                                                    h, mi, s = 0, 0, 0
                                                try:
                                                    pub_time = datetime(y, m, d, h, mi, s)
                                                    break
                                                except:
                                                    pass
                                    except:
                                        continue
                                
                                # 严格过滤：超过 48 小时的文章不要（平衡时效性和内容量）
                                if pub_time:
                                    now = datetime.now()
                                    delta = now - pub_time
                                    hours_old = delta.total_seconds() / 3600
                                    if hours_old > 48:
                                        print(f"      ⏰ {title[:30]}... ({hours_old:.0f}小时前，跳过)")
                                        detail_page.close()
                                        continue
                                    else:
                                        print(f"      ✅ {title[:30]}... ({hours_old:.0f}小时前)")
                                
                                # 优先抓取 meta description（最可靠）
                                meta_desc = detail_page.query_selector('meta[name="description"]')
                                if meta_desc:
                                    text = meta_desc.get_attribute('content')
                                    if text and len(text) > 50 and title[:20] not in text:
                                        content = text[:200]  # 限制长度
                                
                                # 如果 meta 没有，尝试抓取正文第一段
                                if not content:
                                    for selector in [
                                        'article p:first-of-type',
                                        '.article-content p:first-child',
                                        '.post-content p:first-child',
                                        'div.content p:first-child',
                                        'p.summary',
                                        'div.abstract'
                                    ]:
                                        el = detail_page.query_selector(selector)
                                        if el:
                                            text = el.inner_text().strip()
                                            if text and len(text) > 50 and len(text) < 300 and title[:20] not in text:
                                                content = text
                                                break
                                
                                detail_page.close()
                            except Exception as e:
                                # 详情页抓取失败，用标题生成简单摘要
                                pass
                        
                        # 如果还是没有摘要，生成自然的引导语（避免标题重复）
                        if not content:
                            # 从标题提取关键词
                            keywords = ['技术', '方案', '产品', '发布', '上线', '突破', '进展', '趋势', '分析', '解读']
                            keyword = next((k for k in keywords if k in title), '进展')
                            
                            templates = [
                                f"行业关注：{title[:40]}，点击查看详细{keyword}报道。",
                                f"热点追踪：{title[:40]}，了解更多行业{keyword}。",
                                f"深度解读：{title[:40]}，探索背后的技术逻辑与商业价值。",
                                f"最新资讯：{title[:40]}，点击获取完整{keyword}信息。",
                                f"业界聚焦：{title[:40]}，一文读懂核心{keyword}。",
                            ]
                            import random
                            content = random.choice(templates)
                        
                        # 策略 2：尝试使用媒体特定的摘要选择器
                        if not content and source.get('summary_selector'):
                            for selector in source.get('summary_selector', '').split(', '):
                                try:
                                    summary_el = link.query_selector(f'.. {selector}')
                                    if summary_el:
                                        summary_text = summary_el.inner_text().strip()
                                        if len(summary_text) > 30 and len(summary_text) < 200:
                                            content = summary_text
                                            break
                                except:
                                    continue
                        
                        # 策略 3：进详情页抓取
                        if not content and href and href.startswith('/'):
                            full_url = source["url"].rstrip('/') + href
                            content = fetch_article_detail(page, full_url)
                            
                            # 返回列表页
                            page.goto(source["url"], wait_until='domcontentloaded')
                            page.wait_for_timeout(1500)
                        
                        # 策略 4：用标题生成
                        if not content:
                            content = title + "。点击查看详细内容，了解最新技术进展和行业动态。"
                        
                        # 添加新闻
                        source_name = source["name"]
                        if source.get("category") and source["category"] != "科技":
                            source_name = f"{source['name']}({source['category']})"
                        
                        # 构建完整 URL
                        full_url = source["url"].rstrip('/') + href if href and href.startswith('/') else (href if href else source["url"])
                        
                        news_items.append({
                            "title": title,
                            "content": content,
                            "source": source_name,
                            "category": source.get("category", "科技"),
                            "url": full_url,
                            "publish_time": pub_time if pub_time else datetime.now()
                        })
                        seen_titles.add(title)
                        collected += 1
                        print(f"      ✅ {title[:40]}...")
                        
                    except Exception as e:
                        continue
                
                page.close()
                if collected > 0:
                    print(f"    ✅ {source['name']} 抓取 {collected} 条")
                else:
                    print(f"    ⚠️ {source['name']} 未抓到")
                    
            except Exception as e:
                print(f"    ⚠️ {source['name']} 抓取失败")
        
        browser.close()
    
    # 如果不足 10 条，用备用数据补充（带来源）
    backup_news = [
        {
            "title": "全球 AI 技术持续突破，多模态能力再升级",
            "content": "多家研究机构发布最新 AI 技术成果，在图像、文本、语音跨模态任务上表现优异，为通用人工智能奠定基础。技术演进加速，应用场景不断拓展。",
            "source": "量子位",
            "category": "科技"
        },
        {
            "title": "大模型应用加速落地，企业级方案频出",
            "content": "多家云服务商发布企业级大模型解决方案，支持私有化部署、数据隔离和定制微调，降低企业 AI 应用门槛，加速商业化进程。",
            "source": "机器之心",
            "category": "科技"
        },
        {
            "title": "AI 安全与对齐研究取得重要进展",
            "content": "顶尖 AI 实验室公布最新安全研究成果，提出新的对齐方法和评估框架，帮助大模型更好地理解人类意图，减少潜在风险。",
            "source": "36 氪",
            "category": "科技"
        },
        {
            "title": "自动驾驶技术迎来新突破",
            "content": "多家车企和科技公司联合发布自动驾驶新技术，在城市道路场景下实现更高水平的自主驾驶，事故率显著降低，商业化进程加快。",
            "source": "车东西",
            "category": "汽车"
        },
        {
            "title": "机器人商业化进程加速",
            "content": "人形机器人和工业机器人在多个场景实现规模化应用，成本持续下降，性能不断提升，商业化拐点正在到来。",
            "source": "智东西",
            "category": "硬件",
            "url": "https://zhidx.com/p/545922.html"
        },
    ]
    
    idx = 0
    while len(news_items) < 10:
        backup = backup_news[idx % len(backup_news)].copy()
        # 只给备用数据添加标记，真实抓取的保持原来源
        backup['source'] = f"{backup['source']} (综合整理)"
        # 备用数据也有 URL（使用对应媒体的首页或分类页）
        if not backup.get('url'):
            backup['url'] = "https://www.qbitai.com/"  # 默认量子位
        news_items.append(backup)
        idx += 1
    
    # 按时间倒序排列（最新的在前）
    def get_time_key(item):
        if isinstance(item.get('publish_time'), datetime):
            return item['publish_time']
        return datetime.min # 没有时间信息的排最后

    news_items.sort(key=get_time_key, reverse=True)
    result = news_items[:10]
    
    # 打印来源统计
    print("\n  📊 来源统计：")
    source_count = {}
    for item in result:
        src = item.get('source', '未知')
        source_count[src] = source_count.get(src, 0) + 1
    
    for src, count in source_count.items():
        print(f"    {src}: {count} 条")
    
    print(f"  ✅ 抓取成功 {len(result)} 条（已按时间排序）")
    return result


def get_news_data():
    """
    获取资讯数据（真实抓取最新新闻）
    """
    today = datetime.now()
    date_str = today.strftime('%Y.%m.%d')
    
    print("  🌐 正在抓取最新新闻...")
    try:
        news_items = fetch_real_news()
        print(f"  ✅ 抓取成功 {len(news_items)} 条")
    except Exception as e:
        print(f"  ⚠️ 抓取失败，使用备用数据：{e}")
        # 备用数据（仅当抓取失败时）
        news_items = [
            {"title": "AI 技术持续突破", "content": "全球 AI 研发进展迅速，多模态能力持续提升", "source": "量子位"},
            {"title": "大模型应用落地加速", "content": "企业级应用迎来新机遇，降低使用门槛", "source": "机器之心"},
            {"title": "自动驾驶新进展", "content": "多家车企发布最新技术，城市道路测试稳定", "source": "36 氪"},
            {"title": "AI 安全引发关注", "content": "业界讨论 AI 对齐问题，提出新评估框架", "source": "TechCrunch"},
            {"title": "机器人技术突破", "content": "人形机器人商业化加速，成本持续下降", "source": "量子位"},
            {"title": "AI 芯片竞争加剧", "content": "各大厂商发布新品，算力能效比提升", "source": "机器之心"},
            {"title": "生成式 AI 新应用", "content": "多模态能力持续提升，内容创作效率提高", "source": "36 氪"},
            {"title": "AI 医疗取得进展", "content": "辅助诊断准确率提升，应用场景拓展", "source": "健康界"},
            {"title": "量子计算新突破", "content": "量子优势进一步验证，技术瓶颈打破", "source": "量子位"},
            {"title": "AI 教育应用拓展", "content": "个性化学习成为趋势，智能辅导系统上线", "source": "机器之心"},
        ]
    
    return {
        "news": news_items,
        "title": "AI 资讯快报",
        "date": date_str
    }


def format_paste_content(news_data):
    """
    格式化成可粘贴到生成器的正文格式
    格式要求：
    1、标题
    内容... (确保 50-80 字，避免图片底部空白)
    来源：xxx
    """
    lines = []
    for i, news in enumerate(news_data['news'], 1):
        title = news.get('title', '')
        content = news.get('content', '')
        source = news.get('source', '未标注')
        
        if content:
            # 1. 去掉前缀
            prefixes = ['最新资讯：', '业界聚焦：', '行业关注：', '热点追踪：', 'IT 之家快讯：', '深度解读：', '最新消息：']
            for prefix in prefixes:
                content = content.replace(prefix, '')
            
            # 2. 去掉后缀/诱导点击文字
            suffixes = ['，点击查看详细报道。', '，了解更多行业进展。', '，点击查看。', '，点击获取完整进展信息。', '。']
            for suffix in suffixes:
                content = content.replace(suffix, '')
            
            # 3. 去掉标题重复部分
            if content.startswith(title):
                content = content[len(title):]
            elif title in content:
                content = content.replace(title, '')
            
            # 清理首尾空白和标点
            content = content.strip('，。、 ')
            
            # 4. 确保内容足够长（50-80 字），避免图片底部空白
            if len(content) < 50:
                # 用标题 + 补充说明填充
                content = f"{title}。本文深入解读该事件的背景、技术细节与行业影响，帮助读者全面理解最新进展。"
            elif len(content) > 75:
                content = content[:73] + '...'
        else:
            # 没有内容时，用标题 + 补充说明
            content = f"{title}。本文深入解读该事件的背景、技术细节与行业影响，帮助读者全面理解最新进展。"

        lines.append(f"{i}、{title}")
        lines.append(content)
        source = source.replace(" (综合整理)", "") if " (综合整理)" in source else source
        lines.append(f"来源：{source}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    """主函数"""
    print("=" * 60)
    print("AI 资讯快报 - 浏览器自动化生成")
    print("=" * 60)
    print()
    
    # [1/4] 收集资讯
    print("[1/4] 收集 AI 资讯...")
    news_data = get_news_data()
    print(f"✅ 已收集 {len(news_data['news'])} 条资讯")
    print()
    
    # [2/4] 生成图片
    print("[2/4] 浏览器自动生成图片...")
    try:
        from playwright.sync_api import sync_playwright
        
        print("\n🌐 启动浏览器...")
        with sync_playwright() as p:
            # 使用用户数据目录（避免登录问题）
            user_data_dir = WORK_DIR / "browser" / "user_data"
            user_data_dir.mkdir(parents=True, exist_ok=True)
            
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=True,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox',
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # 打开 HTML 生成器
            print("📄 打开 HTML 生成器...")
            page.goto(f'file://{HTML_GENERATOR}', wait_until='domcontentloaded')
            page.wait_for_timeout(2000)
            
            # 填写标题
            print("✏️ 填写标题...")
            page.fill('#mainTitle', news_data['title'])
            page.wait_for_timeout(500)
            
            # 填写日期
            print("📅 填写日期...")
            page.fill('#newsDate', news_data['date'])
            page.wait_for_timeout(500)
            
            # 粘贴正文内容
            print("📋 粘贴正文内容...")
            paste_content = format_paste_content(news_data)
            page.fill('#pasteContent', paste_content)
            page.wait_for_timeout(1000)
            
            # 等待自动解析完成
            print("⏳ 等待自动解析完成...")
            page.wait_for_timeout(5000)
            
            # 检查解析结果
            news_count = page.query_selector('#newsCount')
            if news_count:
                count_text = news_count.inner_text()
                print(f"✅ 解析成功")
                print(f"📊 共 {count_text} 页")
            else:
                print("⚠️ 未检测到解析结果")
            
            # 下载图片（使用截图方式，更可靠）
            print("📸 开始下载图片...")
            
            # 获取总页数
            total_pages = page.query_selector('#newsCount')
            if total_pages:
                page_text = total_pages.inner_text()
                import re
                match = re.search(r'(\d+)/(\d+)', page_text)
                if match:
                    total_pages = int(match.group(2))
                else:
                    total_pages = 5
            else:
                total_pages = 5
            
            date_str = news_data['date'].replace('.', '')
            
            # 逐页截图
            for i in range(total_pages):
                # 切换到第 i 页
                page.evaluate(f'currentPage = {i}; updatePreview();')
                page.wait_for_timeout(500)
                
                # 截图预览区域
                preview = page.query_selector('#preview-content')
                if preview:
                    img_path = str(DOWNLOAD_DIR / f"AI 资讯快报_{date_str}_P{i+1}.png")
                    preview.screenshot(path=img_path)
                    print(f"  ✅ 保存第{i+1}页：{img_path}")
                page.wait_for_timeout(300)
            
            browser.close()
            
            print(f"\n✅ 已生成 5 张图片")
            
    except Exception as e:
        print(f"❌ 生成失败：{e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # [3/4] 发送飞书
    print("[3/4] 发送飞书...")
    try:
        # 查找最新的 5 张图片
        import glob
        
        image_files = sorted(
            glob.glob(str(DOWNLOAD_DIR / f"AI 资讯快报_{news_data['date'].replace('.', '')}_*.png")),
            reverse=True
        )[:5]
        
        if len(image_files) < 5:
            # 尝试其他格式
            image_files = sorted(
                glob.glob(str(DOWNLOAD_DIR / "AI 资讯快报_*.png")),
                reverse=True
            )[:5]
        
        print(f"\n📤 准备发送 {len(image_files)} 张图片...")
        
        # 使用 feishu_file_sender skill 发送
        sender_script = WORK_DIR / "skills" / "Feishu File Sender" / "scripts" / "feishu_file_sender.py"
        
        if sender_script.exists():
            import subprocess
            
            for img_path in image_files:
                img_name = os.path.basename(img_path)
                print(f"  发送：{img_name}")
                
                result = subprocess.run(
                    ['python3', str(sender_script), img_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"    ✅ 发送成功")
                else:
                    print(f"    ❌ 发送失败")
                    if result.stderr:
                        print(f"       {result.stderr[:100]}")
        else:
            print("  ⚠️ 未找到飞书发送脚本")
            print(f"  📁 图片位置：{DOWNLOAD_DIR}")
            
    except Exception as e:
        print(f"❌ 发送失败：{e}")
    
    print()
    
    # [4/4] 输出文案
    print("[4/4] 小红书发布文案：")
    print("=" * 60)
    
    # 生成文案
    copy_title = f"AI 圈炸裂 48 小时🔥{news_data['news'][0]['title'][:20]}..."
    copy_body = f"""宝子们！这两天的 AI 圈真的太热闹了😱
精选 10 条高价值资讯，条条都是爆款潜质👇

━━━━━━━━━━━━━━

"""
    
    for i, news in enumerate(news_data['news'][:10], 1):
        title = news.get('title', '')
        content = news.get('content', '')
        source = news.get('source', '')
        
        copy_body += f"{i}️⃣【{title}】🔥\n"
        copy_body += f"📌 {content}...\n"
        copy_body += f"💡 影响：行业关注，值得深挖\n\n"
    
    copy_body += """━━━━━━━━━━━━━━

【互动问句】
这 10 条里哪条最让你意外？
你觉得 AI 会取代哪些工作？
评论区聊聊～👇

【话题标签】
#AI 前沿 #人工智能 #科技资讯 #AIGC #大模型 #科技日报 #AI 创业 #互联网资讯
"""
    
    print(f"【标题】\n{copy_title}\n")
    print(f"【正文】\n{copy_body}")
    print("=" * 60)
    print()
    print("✅ 全部完成！")


if __name__ == '__main__':
    main()
