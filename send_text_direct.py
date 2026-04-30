#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接发送文本消息（不用文件）
"""
import json
import requests

# 读取配置
with open('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/agent.json', 'r') as f:
    config = json.load(f)

feishu = config['channels']['feishu']
APP_ID = feishu['app_id']
APP_SECRET = feishu['app_secret']

# 获取 token
url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
resp = requests.post(url, json={'app_id': APP_ID, 'app_secret': APP_SECRET})
token = resp.json()['tenant_access_token']
print(f"✅ 获取 token 成功")

# 读取文件内容
with open('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/output/text/AI 资讯快报_20260407.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 分两段发送
parts = content.split("【小红书文案】")
part1 = parts[0].strip()
part2 = "【小红书文案】" + parts[1] if len(parts) > 1 else ""

user_id = "ou_975690183c044ff01e03b1d66fb98df9"

# 发送消息
url = "https://open.feishu.cn/open-apis/im/v1/messages"
params = {"receive_id_type": "open_id"}
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print(f"📍 发送到：{user_id}")

print("📄 发送第 1 部分（可粘贴内容）...")
payload1 = {
    "receive_id": user_id,
    "msg_type": "text",
    "content": json.dumps({"text": part1[:1800]})
}
resp1 = requests.post(url, params=params, headers=headers, json=payload1)
result1 = resp1.json()
print(f"结果 1: {result1}")
if result1.get('code') == 0:
    print(f"✅ 消息 1 已发送：{result1['data']['message_id']}")

if part2:
    print("📄 发送第 2 部分（小红书文案）...")
    payload2 = {
        "receive_id": user_id,
        "msg_type": "text",
        "content": json.dumps({"text": part2[:1800]})
    }
    resp2 = requests.post(url, params=params, headers=headers, json=payload2)
    result2 = resp2.json()
    print(f"结果 2: {result2}")
    if result2.get('code') == 0:
        print(f"✅ 消息 2 已发送：{result2['data']['message_id']}")

print("\n✅ 发送完成！")
