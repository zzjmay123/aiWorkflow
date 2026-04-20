#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用 chat_id 发送文件到当前对话
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

print(f"📋 使用应用：{APP_ID}")

# 获取 token
url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
resp = requests.post(url, json={'app_id': APP_ID, 'app_secret': APP_SECRET})
data = resp.json()
if data.get('code') != 0:
    raise Exception(f"获取 token 失败：{data}")
token = data['tenant_access_token']
print("✅ Token 获取成功")

# 上传文件
file_path = '/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/output/text/AI 资讯快报_20260407.txt'
url = 'https://open.feishu.cn/open-apis/im/v1/files'
headers = {'Authorization': f'Bearer {token}'}

with open(file_path, 'rb') as f:
    files = {'file': ('AI 资讯快报_20260407.txt', f, 'text/plain')}
    resp = requests.post(url, headers=headers, files=files, data={'file_type': 'stream'})
    result = resp.json()
    if result.get('code') != 0:
        raise Exception(f"上传失败：{result}")
    file_key = result['data']['file_key']
    print(f"✅ 上传成功：{file_key}")

# 用当前 session 发送
session_id = '6fb98df9'
url = f'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id'
headers['Content-Type'] = 'application/json'
payload = {
    'receive_id': session_id,
    'msg_type': 'file',
    'content': json.dumps({'file_key': file_key})
}

resp = requests.post(url, headers=headers, json=payload)
result = resp.json()
print(f'发送结果：{result}')

if result.get('code') == 0:
    print(f'✅ 发送成功！message_id: {result["data"]["message_id"]}')
else:
    print(f'❌ 发送失败：{result}')
    # 尝试用 open_id 发送
    print('\n尝试用 open_id 发送...')
    user_id = 'ou_975690183c044ff01e03b1d66fb98df9'
    url = f'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'
    payload['receive_id'] = user_id
    resp = requests.post(url, headers=headers, json=payload)
    result = resp.json()
    print(f'发送结果：{result}')
    if result.get('code') == 0:
        print(f'✅ 发送成功！message_id: {result["data"]["message_id"]}')
    else:
        print(f'❌ 发送失败：{result}')
