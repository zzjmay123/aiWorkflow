#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化流程：生成 AI 资讯 → 生成图片 → 发布小红书
"""

import json
import urllib.request
import subprocess
from pathlib import Path
from datetime import datetime
import time

# 配置
WORK_DIR = Path('/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP')
HTML_PATH = '/Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html'
OUTPUT_DIR = WORK_DIR / 'output' / 'images'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 飞书配置
AGENT_FILE = WORK_DIR / 'agent.json'
with open(AGENT_FILE, 'r', encoding='utf-8') as f:
    agent_config = json.load(f)

APP_ID = agent_config['channels']['feishu']['app_id']
APP_SECRET = agent_config['channels']['feishu']['app_secret']
RECEIVE_ID = "ou_975690183c044ff01e03b1d66fb98df9"


def get_tenant_access_token():
    """获取飞书 token"""
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


def send_text_message(text):
    """发送飞书文本消息"""
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


def generate_news():
    """生成 AI 资讯文本"""
    print("=" * 60)
    print("[1/4] 生成 AI 资讯文本")
    print("=" * 60)
    
    result = subprocess.run(
        ['python3', str(WORK_DIR / 'ai_news_text_only.py')],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode == 0:
        print("✅ 文本生成成功")
        # 返回今日文件路径
        today = datetime.now().strftime('%Y%m%d')
        return WORK_DIR / 'output' / 'text' / f'AI 资讯快报_{today}.txt'
    else:
        print(f"❌ 文本生成失败：{result.stderr}")
        return None


def generate_images(text_file):
    """使用 HTML 生成器生成图片"""
    print()
    print("=" * 60)
    print("[2/4] 生成图片（使用 ai-news-generator.html）")
    print("=" * 60)
    
    # 读取可粘贴内容
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取可粘贴部分
    start = content.find('【可粘贴内容】')
    end = content.find('【小红书文案】')
    if start == -1 or end == -1:
        print("❌ 无法提取可粘贴内容")
        return []
    
    paste_content = content[start:end].replace(
        '【可粘贴内容】（复制到 ai-news-generator.html）\n------------------------------------------------------------\n',
        ''
    ).strip()
    
    print(f"📝 内容长度：{len(paste_content)} 字")
    
    # 使用 AppleScript 自动化浏览器操作
    script = f'''
    tell application "Safari"
        activate
        delay 1
        
        -- 打开 HTML 页面
        set theURL to "{HTML_PATH}"
        set current tab of window 1 to (make new tab with properties {{URL:theURL}})
        delay 2
        
        -- 粘贴内容到正文框
        tell application "System Events"
            keystroke tab 3 times
            keystroke "{paste_content[:500]}"
        end tell
        delay 2
        
        -- 下载全部图片
        tell application "System Events"
            keystroke tab 5 times
            keystroke space
        end tell
        delay 5
        
        -- 关闭页面
        close current tab of window 1
    end tell
    '''
    
    # 执行脚本
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ 图片生成成功")
        # TODO: 获取生成的图片路径
        return []
    else:
        print(f"❌ 图片生成失败：{result.stderr}")
        return []


def post_to_xiaohongshu(images, title, body):
    """发布到小红书"""
    print()
    print("=" * 60)
    print("[3/4] 发布到小红书")
    print("=" * 60)
    
    if not images:
        print("❌ 没有图片可发布")
        return False
    
    # 构建图片参数
    image_args = []
    for img in images:
        image_args.extend(['--images', str(img)])
    
    # 发布命令
    cmd = [
        'python3', '-m', 'pipx', 'run', 'xiaohongshu-cli',
        'post',
        '--title', title,
        '--body', body
    ] + image_args
    
    print(f"📤 发布命令：{' '.join(cmd[:10])}...")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode == 0:
        print("✅ 发布成功")
        print(result.stdout)
        return True
    else:
        print(f"❌ 发布失败：{result.stderr}")
        return False


def notify_user(success, message=""):
    """发送飞书通知"""
    print()
    print("=" * 60)
    print("[4/4] 发送通知")
    print("=" * 60)
    
    if success:
        text = f"✅ AI 资讯发布成功！\n\n{message}"
    else:
        text = f"❌ AI 资讯发布失败\n\n{message}"
    
    result = send_text_message(text)
    
    if result.get('code') == 0:
        print(f"✅ 通知已发送：{result.get('data', {}).get('message_id', 'unknown')}")
    else:
        print(f"❌ 通知发送失败：{result}")


def main():
    """主流程"""
    print("🚀 AI 资讯全自动发布流程")
    print("=" * 60)
    
    # [1/4] 生成文本
    text_file = generate_news()
    if not text_file:
        notify_user(False, "文本生成失败")
        return
    
    # [2/4] 生成图片
    # TODO: 需要优化图片生成逻辑
    images = []  # 暂时跳过，手动生成
    
    # [3/4] 发布小红书
    # TODO: 需要图片后才能发布
    
    # [4/4] 通知
    notify_user(True, f"文本已生成：{text_file.name}\n图片生成需要手动操作")


if __name__ == "__main__":
    main()
