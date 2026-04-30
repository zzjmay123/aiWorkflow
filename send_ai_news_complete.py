#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送 AI 资讯完整内容到飞书（两部分：可粘贴内容 + 小红书文案）
"""

import json
import urllib.request
from pathlib import Path
from datetime import datetime

# 配置
WORK_DIR = Path(__file__).parent.absolute()
AGENT_FILE = WORK_DIR / "agent.json"
RECEIVE_ID = "ou_975690183c044ff01e03b1d66fb98df9"

# 读取工作区配置
with open(AGENT_FILE, 'r', encoding='utf-8') as f:
    agent_config = json.load(f)

APP_ID = agent_config['channels']['feishu']['app_id']
APP_SECRET = agent_config['channels']['feishu']['app_secret']


def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['tenant_access_token']


def send_text_message(text, prefix=""):
    """发送文本消息"""
    token = get_tenant_access_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    content_json = json.dumps({"text": text}, ensure_ascii=False)
    payload = {
        "receive_id": RECEIVE_ID,
        "msg_type": "text",
        "content": content_json
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result


def main():
    # 查找今日文件
    output_dir = WORK_DIR / "output" / "text"
    today = datetime.now().strftime('%Y%m%d')
    text_file = output_dir / f"AI 资讯快报_{today}.txt"
    
    if not text_file.exists():
        print(f"❌ 未找到今日文件：{text_file}")
        return
    
    print(f"📄 读取文件：{text_file.name}")
    
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割内容
    parts = content.split("【小红书文案】")
    paste_content = parts[0].replace(
        "============================================================\nAI 资讯快报 - 2026.04.11\n============================================================\n\n【可粘贴内容】（复制到 ai-news-generator.html）\n------------------------------------------------------------\n", 
        ""
    ).strip()
    
    xiaohongshu_copy = ""
    if len(parts) > 1:
        # 提取小红书文案正文
        copy_start = parts[1].find("#AI 每日资讯")
        if copy_start != -1:
            xiaohongshu_copy = parts[1][copy_start:].strip()
            # 去掉末尾分割线
            if "================================================" in xiaohongshu_copy:
                xiaohongshu_copy = xiaohongshu_copy.split("================================================")[0].strip()
    
    # 发送第 1 部分：可粘贴内容
    print("📤 发送第 1 部分（可粘贴内容 - 用于生成图片）...")
    result1 = send_text_message(paste_content, "【可粘贴内容】")
    if result1.get('code') == 0:
        print(f"✅ 第 1 部分已发送：{result1.get('data', {}).get('message_id', 'unknown')}")
    else:
        print(f"❌ 第 1 部分发送失败：{result1}")
    
    # 发送第 2 部分：小红书文案
    print("📤 发送第 2 部分（小红书文案 - 直接发布）...")
    result2 = send_text_message(xiaohongshu_copy, "【小红书文案】")
    if result2.get('code') == 0:
        print(f"✅ 第 2 部分已发送：{result2.get('data', {}).get('message_id', 'unknown')}")
    else:
        print(f"❌ 第 2 部分发送失败：{result2}")
    
    print()
    print("✅ 发送完成！")
    print("   - 第 1 部分：可粘贴到 ai-news-generator.html 生成图片")
    print("   - 第 2 部分：小红书文案，可直接发布")


if __name__ == "__main__":
    main()
