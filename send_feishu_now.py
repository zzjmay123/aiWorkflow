#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用当前工作区配置发送飞书文件
"""
import json
import base64
import requests
from pathlib import Path

# 读取工作区配置
with open('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/agent.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

feishu = config['channels']['feishu']
APP_ID = feishu['app_id']
APP_SECRET = feishu['app_secret']

# 获取 token
def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    resp = requests.post(url, json=payload)
    data = resp.json()
    if data.get('code') != 0:
        raise Exception(f"获取 token 失败：{data}")
    return data['tenant_access_token']

# 上传文件
def upload_file(token, file_path):
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    with open(file_path, 'rb') as f:
        files = {
            "image": (Path(file_path).name, f)
        }
        data = {"image_type": "message"}
        resp = requests.post(url, headers=headers, files=files, data=data)
        result = resp.json()
        if result.get('code') != 0:
            raise Exception(f"上传失败：{result}")
        return result['data']['image_key']

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

# 主流程
print(f"📋 使用应用：{APP_ID}")
print("📤 准备发送 AI 资讯快报...")

token = get_token()
print("✅ 获取 token 成功")

# 发送今天的文件
import glob
files = glob.glob("/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/output/text/AI 资讯快报_*.txt")
if not files:
    print("❌ 没有找到今天的资讯文件！")
    exit(1)
file_path = sorted(files)[-1] # 取最新的
print(f"📂 找到文件：{file_path}")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 分两段发送（避免太长）
parts = content.split("【小红书文案】")
part1 = parts[0].strip()
part2 = "【小红书文案】" + parts[1] if len(parts) > 1 else ""

user_id = "ou_975690183c044ff01e03b1d66fb98df9"

print(f"📍 发送到：{user_id}")
print("📄 发送第 1 部分（可粘贴内容）...")
msg1 = send_text(token, user_id, part1[:1800] + "...")
print(f"✅ 消息 1 已发送：{msg1}")

if part2:
    print("📄 发送第 2 部分（小红书文案）...")
    msg2 = send_text(token, user_id, part2[:1800])
    print(f"✅ 消息 2 已发送：{msg2}")

print("\n✅ 全部发送完成！")
