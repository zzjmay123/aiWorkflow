#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送小红书文案到飞书（文本消息格式，链接可点击）
"""

import json
import urllib.request
import urllib.error
from pathlib import Path

# 配置
WORK_DIR = Path(__file__).parent.absolute()
AGENT_FILE = WORK_DIR / "agent.json"

# 读取工作区配置
with open(AGENT_FILE, 'r', encoding='utf-8') as f:
    agent_config = json.load(f)

APP_ID = agent_config['channels']['feishu']['app_id']
APP_SECRET = agent_config['channels']['feishu']['app_secret']
RECEIVE_ID = "ou_975690183c044ff01e03b1d66fb98df9"


def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['tenant_access_token']


def send_text_message(text):
    """发送文本消息"""
    token = get_tenant_access_token()
    
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    
    # 飞书文本消息格式：content 是 JSON 字符串 {"text": "内容"}
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
    # 读取今日文案
    import glob
    text_files = glob.glob(str(WORK_DIR / "output" / "text" / "AI 资讯快报_*.txt"))
    if not text_files:
        print("❌ 未找到今日文案文件")
        return
    
    latest_file = max(text_files)
    print(f"📄 读取文件：{latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取小红书文案部分
    start = content.find("【小红书文案】")
    if start == -1:
        print("❌ 未找到小红书文案")
        return
    
    # 找到正文开始
    body_start = content.find("#AI 每日资讯", start)
    if body_start == -1:
        print("❌ 未找到文案正文")
        return
    
    # 提取到文件末尾
    copy_content = content[body_start:].strip()
    
    # 去掉末尾的分割线
    if "================================================" in copy_content:
        copy_content = copy_content.split("================================================")[0].strip()
    
    print(f"📝 文案长度：{len(copy_content)} 字")
    print()
    print("=" * 60)
    print(copy_content)
    print("=" * 60)
    print()
    
    # 发送
    print("📤 发送到飞书...")
    result = send_text_message(copy_content)
    
    if result.get('code') == 0:
        print(f"✅ 发送成功！message_id: {result.get('data', {}).get('message_id', 'unknown')}")
    else:
        print(f"❌ 发送失败：{result}")


if __name__ == "__main__":
    main()
