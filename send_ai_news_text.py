#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送 AI 资讯为飞书文本消息（链接可点击）
"""
import json
import requests
from pathlib import Path
from datetime import datetime

# 读取工作区配置
with open('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/agent.json', 'r') as f:
    config = json.load(f)

feishu = config['channels']['feishu']
APP_ID = feishu['app_id']
APP_SECRET = feishu['app_secret']

# 获取 token
def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    resp = requests.post(url, json=payload)
    data = resp.json()
    if data.get('code') != 0:
        raise Exception(f"获取 token 失败：{data}")
    return data['tenant_access_token']

# 发送文本消息
def send_text(token, user_id, text):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "open_id"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "receive_id": user_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    resp = requests.post(url, params=params, headers=headers, json=payload)
    result = resp.json()
    if result.get('code') != 0:
        raise Exception(f"发送失败：{result}")
    return result['data']['message_id']

# 读取最新的 AI 资讯文件
today = datetime.now()
date_str = today.strftime('%Y%m%d')
output_dir = Path('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/output/text')
latest_file = output_dir / f"AI 资讯快报_{date_str}.txt"

# 如果今天文件不存在，找最新的
if not latest_file.exists():
    files = sorted(output_dir.glob("AI 资讯快报_*.txt"), reverse=True)
    if files:
        latest_file = files[0]
        print(f"⚠️ 今日文件不存在，使用最新文件：{latest_file.name}")
    else:
        raise Exception("未找到任何 AI 资讯文件")

with open(latest_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 分割为可粘贴内容和小红书文案
parts = content.split("【小红书文案】")
paste_content = parts[0].replace("【可粘贴内容】（复制到 ai-news-generator.html）\n------------------------------------------------------------\n", "")
xiaohongshu_copy = "【小红书文案】" + parts[1] if len(parts) > 1 else ""

# 发送
token = get_token()
user_id = "ou_975690183c044ff01e03b1d66fb98df9"

print(f"📋 使用应用：{APP_ID}（运营--Jony）")
print(f"📍 发送到：{user_id}")
print(f"📄 读取文件：{latest_file.name}")

# 分 3 段发送（避免超长）
print("📄 发送第 1 部分（可粘贴内容）...")
msg1 = send_text(token, user_id, paste_content[:1800])
print(f"✅ 消息 1 已发送：{msg1}")

print("📄 发送第 2 部分（小红书文案）...")
msg2 = send_text(token, user_id, xiaohongshu_copy[:1800])
print(f"✅ 消息 2 已发送：{msg2}")

print("\n✅ 发送完成！飞书文本消息中的链接会自动变成可点击的超链接")
