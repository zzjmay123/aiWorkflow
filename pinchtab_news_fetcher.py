#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报 - 使用 Pinchtab 抓取新闻
Pinchtab 可以绕过反爬虫，抓取详情页内容
"""

import requests
import time

class PinchtabClient:
    """Pinchtab 浏览器自动化客户端"""
    
    def __init__(self, base_url="http://localhost:9867"):
        self.base_url = base_url
    
    def health_check(self):
        """检查服务状态"""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            return resp.json().get("status") == "ok"
        except:
            return False
    
    def open(self, url):
        """打开网页"""
        resp = requests.post(f"{self.base_url}/navigate", 
                            json={"url": url}, timeout=30)
        return resp.json()
    
    def snapshot(self):
        """获取页面快照（无障碍树）"""
        resp = requests.get(f"{self.base_url}/snapshot", timeout=30)
        return resp.json()
    
    def screenshot(self, path="screenshot.png", full_page=False, ref=None):
        """截图"""
        data = {"full_page": full_page}
        if ref:
            data["ref"] = ref
        resp = requests.post(f"{self.base_url}/screenshot",
                            json=data, timeout=30)
        with open(path, 'wb') as f:
            f.write(resp.content)
        return path
    
    def click(self, ref):
        """点击元素"""
        resp = requests.post(f"{self.base_url}/click",
                            json={"ref": ref}, timeout=30)
        return resp.json()
    
    def type(self, ref, text):
        """输入文本"""
        resp = requests.post(f"{self.base_url}/type",
                            json={"ref": ref, "text": text}, timeout=30)
        return resp.json()
    
    def press_key(self, key):
        """按键盘"""
        resp = requests.post(f"{self.base_url}/press_key",
                            json={"key": key}, timeout=30)
        return resp.json()
    
    def wait_for(self, text=None, ref=None, timeout=5):
        """等待元素或文本出现"""
        data = {}
        if text:
            data["text"] = text
        if ref:
            data["ref"] = ref
        resp = requests.post(f"{self.base_url}/wait_for",
                            json=data, timeout=timeout+5)
        return resp.json()


def extract_text_from_snapshot(snapshot, max_length=150):
    """从快照中提取正文内容"""
    if not snapshot or 'tree' not in snapshot:
        return None
    
    paragraphs = []
    
    def traverse(node):
        if not isinstance(node, dict):
            return
        
        # 提取文本
        text = node.get('text', '').strip()
        role = node.get('role', '')
        
        # 过滤：段落文本，长度适中
        if (text and len(text) > 50 and len(text) < 300 and
            role in ['paragraph', 'text', 'generic'] and
            '广告' not in text and
            '推荐' not in text and
            '相关' not in text):
            paragraphs.append(text)
        
        # 递归子节点
        for child in node.get('children', []):
            traverse(child)
    
    # 遍历树
    for node in snapshot.get('tree', []):
        traverse(node)
    
    if paragraphs:
        # 取前 2-3 段
        content = ' '.join(paragraphs[:3])
        return content[:max_length] + "..." if len(content) > max_length else content
    
    return None


def fetch_news_with_pinchtap():
    """使用 Pinchtab 抓取新闻"""
    
    client = PinchtabClient()
    
    if not client.health_check():
        print("❌ Pinchtab 服务未运行")
        return None
    
    print("✅ Pinchtab 服务正常")
    
    news_items = []
    seen_titles = set()
    
    # 媒体列表
    sources = [
        {"name": "量子位", "url": "https://www.qbitai.com/", "category": "科技"},
        {"name": "智东西", "url": "https://zhidx.com/", "category": "硬件"},
    ]
    
    for source in sources:
        print(f"\n📰 正在抓取 {source['name']}...")
        
        try:
            # 1. 打开首页
            client.open(source["url"])
            time.sleep(3)
            
            # 2. 获取快照
            snapshot = client.snapshot()
            
            # 3. 提取文章链接（简化：手动找几个链接）
            # 这里我们用简单方式：直接构造已知文章 URL
            # 实际应该解析 snapshot 找链接
            
            # 示例：抓取量子位的文章
            if source["name"] == "量子位":
                # 从快照中找文章标题和链接
                articles = extract_articles_from_snapshot(snapshot, source["url"])
                
                for i, (title, article_url) in enumerate(articles[:3]):
                    if title in seen_titles:
                        continue
                    
                    print(f"  📄 文章 {i+1}: {title[:40]}...")
                    
                    # 4. 打开详情页
                    if article_url:
                        client.open(article_url)
                        time.sleep(3)
                        
                        # 5. 获取详情页快照
                        detail_snapshot = client.snapshot()
                        
                        # 6. 提取正文
                        content = extract_text_from_snapshot(detail_snapshot)
                        
                        if not content:
                            content = title + "。点击查看详细内容，了解最新技术进展和行业动态。"
                        
                        news_items.append({
                            "title": title,
                            "content": content,
                            "source": source["name"],
                            "category": source["category"]
                        })
                        seen_titles.add(title)
                        print(f"    ✅ 来源：{source['name']}, 内容长度：{len(content)}")
                    
                    # 返回首页继续下一篇
                    client.open(source["url"])
                    time.sleep(2)
            
            elif source["name"] == "智东西":
                articles = extract_articles_from_snapshot(snapshot, source["url"])
                
                for i, (title, article_url) in enumerate(articles[:3]):
                    if title in seen_titles:
                        continue
                    
                    print(f"  📄 文章 {i+1}: {title[:40]}...")
                    
                    if article_url:
                        client.open(article_url)
                        time.sleep(3)
                        
                        detail_snapshot = client.snapshot()
                        content = extract_text_from_snapshot(detail_snapshot)
                        
                        if not content:
                            content = title + "。点击查看详细内容，了解最新技术进展和行业动态。"
                        
                        news_items.append({
                            "title": title,
                            "content": content,
                            "source": f"{source['name']}({source['category']})",
                            "category": source["category"]
                        })
                        seen_titles.add(title)
                        print(f"    ✅ 来源：{source['name']}, 内容长度：{len(content)}")
                    
                    client.open(source["url"])
                    time.sleep(2)
        
        except Exception as e:
            print(f"    ⚠️ {source['name']} 抓取失败：{e}")
    
    return news_items


def extract_articles_from_snapshot(snapshot, base_url):
    """从快照中提取文章标题和链接"""
    articles = []
    
    if not snapshot or 'tree' not in snapshot:
        return articles
    
    def traverse(node):
        if not isinstance(node, dict):
            return
        
        text = node.get('text', '').strip()
        role = node.get('role', '')
        url = node.get('url', '')
        
        # 判断是否是文章标题
        if (text and len(text) > 10 and len(text) < 60 and
            url and url.startswith('/')):
            # 验证是否包含 AI 相关关键词
            if any(kw in text for kw in ['AI', '智能', '大模型', '算法', '技术', '发布', '数据', '应用', 
                                         '芯片', '自动驾驶', '机器人', '系统', '平台', '产品']):
                full_url = base_url.rstrip('/') + url
                articles.append((text, full_url))
        
        # 递归子节点
        for child in node.get('children', []):
            traverse(child)
    
    for node in snapshot.get('tree', []):
        traverse(node)
    
    return articles


if __name__ == "__main__":
    print("=" * 60)
    print("AI 资讯快报 - Pinchtab 新闻抓取测试")
    print("=" * 60)
    
    news_items = fetch_news_with_pinchtap()
    
    if news_items:
        print(f"\n✅ 共抓取 {len(news_items)} 条新闻\n")
        for i, news in enumerate(news_items, 1):
            print(f"{i}. {news['title']}")
            print(f"   来源：{news['source']}")
            print(f"   内容：{news['content'][:80]}...")
            print()
    else:
        print("\n❌ 抓取失败")
