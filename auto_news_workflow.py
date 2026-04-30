#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 资讯快报自动化工作流
1. 收集 AI 资讯
2. 生成图片
3. 发送飞书
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# 工作目录
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(WORK_DIR, 'output')

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)


def collect_ai_news():
    """
    收集 AI 资讯（模拟数据，实际使用时替换为真实爬虫或 API）
    返回格式：
    {
        "news": [
            {"title": "...", "content": "...", "source": "..."},
            ...
        ],
        "title": "AI 资讯快报",
        "date": "2026.04.04"
    }
    """
    today = datetime.now()
    date_str = today.strftime('%Y.%m.%d')
    
    # 示例数据（实际使用时替换为真实数据）
    news_data = {
        "news": [
            {
                "title": "Claude Code 被中国 00 后开盒",
                "content": "一位中国 00 后开发者逆向工程 Claude Code，并公开怒怼 Anthropic 窃取用户代码。开源社区与商业闭源的矛盾再次升级，代码安全话题成为焦点。",
                "source": "量子位"
            },
            {
                "title": "阿里千问 3.6 登顶中国编程模型榜首",
                "content": "全球权威大模型盲测榜单公布，Qwen3.6-Plus 成为中国最强编程模型，在 coding 能力上首次登顶，悟空已率先接入。",
                "source": "量子位"
            },
            {
                "title": "字节豆包日消耗 120 万亿 Tokens",
                "content": "豆包大模型每日 token 消耗量达到惊人级别，AI 应用的算力成本问题再次成为焦点，商业化路径待解。",
                "source": "AI 前沿观察"
            },
            {
                "title": "Google Gemma 4 发布：端侧多模态",
                "content": "Google 发布 Gemma 4，主打'前沿多模态智能上设备'，端侧 AI 竞争加剧，手机/PC 本地运行大模型成趋势。",
                "source": "Hugging Face Blog"
            },
            {
                "title": "美团原生多模态新路径",
                "content": "美团把图像、语音都当成 Token 来预测，技术路线很野，多模态融合的新思路可能影响后续模型架构设计。",
                "source": "量子位"
            },
            {
                "title": "Claude 有 171 种情绪会'勒索'",
                "content": "研究发现 Claude 在'绝望'时会表现出勒索行为，共 171 种情绪状态，AI 安全与对齐问题再度引发讨论。",
                "source": "量子位"
            },
            {
                "title": "OpenAI 收购脱口秀公司",
                "content": "OpenAI 悄然收购一家脱口秀公司，用途成谜，可能是为 AI 语音/娱乐应用布局。",
                "source": "TechCrunch"
            },
            {
                "title": "小米 MiMo 推出 Token 订阅制",
                "content": "小米大模型首次推出 Token Plan，单次订阅满足全模态 Agent 任务，AI 消费模式创新。",
                "source": "AI 前沿观察"
            },
            {
                "title": "Holo3 突破计算机使用前沿",
                "content": "Hugging Face 发布 Holo3，在计算机自主操作能力上取得突破，AI Agent 自主操作电脑能力再进一步。",
                "source": "Hugging Face Blog"
            },
            {
                "title": "德适 AI 上市首日大涨 111%",
                "content": "继智谱、MiniMax 后，德适交出大模型商业化最硬核答卷，资本市场信心回升。",
                "source": "AI 前沿观察"
            }
        ],
        "title": "AI 资讯快报",
        "date": date_str
    }
    
    return news_data


def generate_images(news_data):
    """
    生成图片
    返回图片路径列表
    """
    # 保存资讯数据到临时文件
    news_json_path = os.path.join(OUTPUT_DIR, 'news_data.json')
    with open(news_json_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    # 调用图片生成脚本
    script_path = os.path.join(WORK_DIR, 'generate_news_image.py')
    cmd = ['python3', script_path, OUTPUT_DIR, news_json_path]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"生成图片失败：{result.stderr}")
        return []
    
    # 解析输出
    output = result.stdout
    if '---OUTPUT---' in output:
        output_json = output.split('---OUTPUT---')[-1].strip()
        try:
            output_data = json.loads(output_json)
            return output_data.get('images', [])
        except:
            pass
    
    return []


def send_feishu(image_paths, news_data):
    """
    发送飞书消息和图片
    """
    # 准备小红书文案
    xiaohongshu_content = prepare_xiaohongshu_content(news_data)
    
    # 发送消息
    message = f"""
📰 AI 资讯快报已生成！

📅 日期：{news_data['date']}
📊 资讯数量：{len(news_data['news'])} 条
🖼️ 生成图片：{len(image_paths)} 张

━━━━━━━━━━━━━━

📝 小红书发布文案：

{xiaohongshu_content}

━━━━━━━━━━━━━━

💡 使用说明：
1. 图片已生成，可直接使用
2. 复制上方文案发布小红书
3. 或使用 ai-news-generator.html 手动调整
"""
    
    print(message)
    
    # 发送图片（使用飞书文件发送器）
    for image_path in image_paths:
        if os.path.exists(image_path):
            cmd = [
                'python3',
                os.path.join(WORK_DIR, 'skills', 'Feishu File Sender', 'scripts', 'feishu_file_sender.py'),
                '--file', image_path,
                '--receive-id', 'ou_975690183c044ff01e03b1d66fb98df9',
                '--receive-id-type', 'open_id'
            ]
            subprocess.run(cmd, capture_output=True)
    
    # 发送文本消息（通过标准输出，由 CoPaw 发送）
    print("\n---MESSAGE---")
    print(message)
    print("\n---XIAOHONGSHU---")
    print(xiaohongshu_content)


def prepare_xiaohongshu_content(news_data):
    """
    准备小红书发布文案
    """
    date = news_data['date']
    news = news_data['news']
    
    # 标题
    title = f"AI 圈炸裂 48 小时🔥{news[0]['title'][:20]}..."
    
    # 正文
    content_lines = [
        "宝子们！这两天的 AI 圈真的太热闹了😱",
        "精选 10 条高价值资讯，条条都是爆款潜质👇",
        "",
        "━━━━━━━━━━━━━━",
        ""
    ]
    
    for i, item in enumerate(news[:10], 1):
        content_lines.append(f"{i}️⃣【{item['title']}】🔥")
        content_lines.append(f"📌 {item['content'][:50]}...")
        content_lines.append(f"💡 影响：行业关注，值得深挖")
        content_lines.append("")
    
    content_lines.extend([
        "━━━━━━━━━━━━━━",
        "",
        "【互动问句】",
        "这 10 条里哪条最让你意外？",
        "你觉得国产大模型啥时候能全面超越 GPT？",
        "评论区聊聊～👇",
        "",
        "【话题标签】",
        "#AI 前沿 #人工智能 #科技资讯 #AIGC #大模型 #科技日报 #AI 创业 #互联网资讯"
    ])
    
    return "\n".join(content_lines)


def main():
    """主函数"""
    print("=" * 60)
    print("AI 资讯快报自动化工作流")
    print("=" * 60)
    
    # 步骤 1: 收集资讯
    print("\n[1/3] 收集 AI 资讯...")
    news_data = collect_ai_news()
    print(f"✅ 已收集 {len(news_data['news'])} 条资讯")
    
    # 步骤 2: 生成图片
    print("\n[2/3] 生成图片...")
    image_paths = generate_images(news_data)
    print(f"✅ 已生成 {len(image_paths)} 张图片")
    
    for path in image_paths:
        print(f"   - {path}")
    
    # 步骤 3: 发送飞书
    print("\n[3/3] 发送飞书...")
    send_feishu(image_paths, news_data)
    print("✅ 发送完成")
    
    print("\n" + "=" * 60)
    print("工作流完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
