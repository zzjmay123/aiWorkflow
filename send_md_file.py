#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送飞书文件消息（支持 md 文件）
"""
import json
import requests
from pathlib import Path

# 读取工作区配置
with open('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/agent.json', 'r') as f:
    config = json.load(f)

feishu = config['channels']['feishu']
APP_ID = feishu['app_id']
APP_SECRET = feishu['app_secret']

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    resp = requests.post(url, json=payload)
    data = resp.json()
    if data.get('code') != 0:
        raise Exception(f"获取 token 失败：{data}")
    return data['tenant_access_token']

def upload_file(token, file_path, file_type="stream"):
    """上传文件到飞书"""
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    file_name = Path(file_path).name
    # 确保文件名有正确的后缀
    if not file_name.endswith('.txt'):
        file_name = Path(file_path).stem + '.txt'
    
    with open(file_path, 'rb') as f:
        files = {
            "file": (file_name, f, "text/plain")  # 指定 MIME 类型为 txt
        }
        data = {"file_type": file_type}
        resp = requests.post(url, headers=headers, files=files, data=data)
    
    result = resp.json()
    if result.get('code') != 0:
        raise Exception(f"上传失败：{result}")
    
    print(f"上传返回：{result}")  # 调试
    file_key = result['data'].get('file_key') or result['data'].get('key')
    # 使用原始文件名（带.md 后缀）
    return file_key, file_name

def send_file_message(token, user_id, file_key, file_name):
    """发送文件消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "open_id"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "receive_id": user_id,
        "msg_type": "file",
        "content": json.dumps({
            "file_key": file_key,
            "file_name": file_name
        })
    }
    
    resp = requests.post(url, params=params, headers=headers, json=payload)
    result = resp.json()
    if result.get('code') != 0:
        raise Exception(f"发送失败：{result}")
    
    return result['data']['message_id']

# 主流程
print(f"📋 使用应用：{APP_ID}（运营--Jony）")

token = get_token()
print("✅ 获取 token 成功")

# 发送 txt 文件
txt_file = "/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/output/text/AI 资讯快报_20260407.txt"
user_id = "ou_975690183c044ff01e03b1d66fb98df9"

print(f"📤 上传文件：AI 资讯快报_20260407.txt")
file_key, file_name = upload_file(token, txt_file, file_type="stream")
print(f"✅ 上传成功，file_key: {file_key}")

print(f"📍 发送到：{user_id}")
msg_id = send_file_message(token, user_id, file_key, file_name)
print(f"✅ 发送成功！message_id: {msg_id}")

print("\n✅ 请检查飞书，应收到一个 txt 文件（显示为'运营--Jony'发送）")
