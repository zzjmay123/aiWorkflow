#!/usr/bin/env python3
"""
Pinchtab 通用客户端 - 供其他技能调用
提供简单的网页采集功能
"""

import requests
import time
from typing import List, Dict, Optional

PINCHTAB_BASE = "http://localhost:9867"

class PinchtabClient:
    """Pinchtab 浏览器自动化客户端"""
    
    def __init__(self, base_url=PINCHTAB_BASE):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self, timeout=5) -> bool:
        """检查服务是否运行"""
        try:
            resp = self.session.get(f"{self.base_url}/health", timeout=timeout)
            return resp.json().get("status") == "ok"
        except Exception as e:
            print(f"❌ 服务检查失败：{e}")
            return False
    
    def open(self, url: str, timeout=30) -> Dict:
        """打开网页"""
        try:
            resp = self.session.post(
                f"{self.base_url}/navigate",
                json={"url": url},
                timeout=timeout
            )
            result = resp.json()
            print(f"📄 打开页面：{result.get('title', 'Unknown')[:50]}")
            return result
        except Exception as e:
            print(f"❌ 打开页面失败：{e}")
            return {}
    
    def snapshot(self, timeout=30) -> Dict:
        """获取页面快照（无障碍树）"""
        try:
            resp = self.session.get(f"{self.base_url}/snapshot", timeout=timeout)
            return resp.json()
        except Exception as e:
            print(f"❌ 获取快照失败：{e}")
            return {}
    
    def screenshot(self, path: str, full_page=False, timeout=30) -> str:
        """截图"""
        try:
            resp = self.session.post(
                f"{self.base_url}/screenshot",
                json={"full_page": full_page},
                timeout=timeout
            )
            with open(path, 'wb') as f:
                f.write(resp.content)
            print(f"📸 截图已保存：{path}")
            return path
        except Exception as e:
            print(f"❌ 截图失败：{e}")
            return ""
    
    def click(self, ref: str, timeout=10) -> Dict:
        """点击元素"""
        try:
            resp = self.session.post(
                f"{self.base_url}/click",
                json={"ref": ref},
                timeout=timeout
            )
            return resp.json()
        except Exception as e:
            print(f"❌ 点击失败：{e}")
            return {}
    
    def type(self, ref: str, text: str, timeout=10) -> Dict:
        """输入文本"""
        try:
            resp = self.session.post(
                f"{self.base_url}/type",
                json={"ref": ref, "text": text},
                timeout=timeout
            )
            return resp.json()
        except Exception as e:
            print(f"❌ 输入失败：{e}")
            return {}
    
    def extract_text_elements(self, snapshot: Dict, min_length=20, max_length=200, 
                             min_depth=5, max_depth=12, exclude_keywords=None) -> List[Dict]:
        """
        从快照中提取文本元素
        
        Args:
            snapshot: Pinchtab 快照
            min_length: 最小文本长度
            max_length: 最大文本长度
            min_depth: 最小深度
            max_depth: 最大深度
            exclude_keywords: 排除的关键词列表
        
        Returns:
            提取的元素列表
        """
        if exclude_keywords is None:
            exclude_keywords = [
                'ICP', '公网安备', 'Copyright', '版权所有',
                '首页', '更多', '关于', '联系', '广告', '登录', '注册'
            ]
        
        elements = []
        nodes = snapshot.get('nodes', [])
        
        for node in nodes:
            role = node.get('role', '')
            name = node.get('name', '').strip()
            depth = node.get('depth', 0)
            
            # 查找 heading 或 link 元素
            if role in ['heading', 'link', 'StaticText'] and name:
                # 过滤条件
                if (len(name) >= min_length and len(name) <= max_length and
                    depth >= min_depth and depth <= max_depth and
                    not any(kw in name for kw in exclude_keywords)):
                    
                    elements.append({
                        'text': name,
                        'role': role,
                        'ref': node.get('ref', ''),
                        'depth': depth
                    })
        
        return elements
    
    def wait(self, seconds=2):
        """等待"""
        time.sleep(seconds)


def check_pinchtab_service() -> bool:
    """检查 Pinchtab 服务是否可用"""
    client = PinchtabClient()
    if not client.health_check():
        print("❌ Pinchtab 服务未运行")
        print("💡 请先启动服务：~/bin/pinchtab-start.sh")
        return False
    print("✅ Pinchtab 服务正常")
    return True


# 使用示例
if __name__ == "__main__":
    # 检查服务
    if not check_pinchtab_service():
        exit(1)
    
    # 创建客户端
    client = PinchtabClient()
    
    # 打开网页
    client.open("https://www.qbitai.com")
    client.wait(3)
    
    # 获取快照
    snapshot = client.snapshot()
    
    # 提取元素
    elements = client.extract_text_elements(snapshot)
    
    print(f"\n📊 提取到 {len(elements)} 个元素:")
    for i, elem in enumerate(elements[:10], 1):
        print(f"{i}. [{elem['role']}] {elem['text'][:50]}")
