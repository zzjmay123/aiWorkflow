#!/usr/bin/env python3
"""
Feishu File Sender for CoPaw
通过飞书 OpenAPI 上传并发送文件到飞书聊天
"""
import argparse
import json
import os
from pathlib import Path
from typing import Optional

import requests

# 飞书 API 端点
FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
FEISHU_UPLOAD_URL = "https://open.feishu.cn/open-apis/im/v1/files"
FEISHU_SEND_MSG_URL = "https://open.feishu.cn/open-apis/im/v1/messages"

# CoPaw 配置文件路径
COPAW_CONFIG = Path.home() / ".copaw" / "config.json"
# 当前工作区配置（优先使用）- 使用绝对路径
WORKSPACE_CONFIG = Path("/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/agent.json")


def load_copaw_config() -> dict:
    """加载 CoPaw 配置文件（优先使用工作区配置）"""
    # 优先使用当前工作区的 agent.json
    if WORKSPACE_CONFIG.exists():
        print(f"📋 使用工作区配置：{WORKSPACE_CONFIG}")
        return json.loads(WORKSPACE_CONFIG.read_text(encoding="utf-8"))
    
    # 回退到全局配置
    if not COPAW_CONFIG.exists():
        raise FileNotFoundError(f"CoPaw config not found: {COPAW_CONFIG}")
    print(f"📋 使用全局配置：{COPAW_CONFIG}")
    return json.loads(COPAW_CONFIG.read_text(encoding="utf-8"))


def get_feishu_credentials(config: dict) -> tuple[str, str]:
    """从 CoPaw 配置中获取飞书凭证"""
    feishu_config = config.get("channels", {}).get("feishu", {})
    if not feishu_config.get("enabled", False):
        raise RuntimeError("Feishu channel is not enabled in CoPaw config")
    
    app_id = feishu_config.get("app_id")
    app_secret = feishu_config.get("app_secret")
    
    if not app_id or not app_secret:
        raise RuntimeError("Missing app_id or app_secret in Feishu config")
    
    return app_id, app_secret


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """获取飞书 tenant_access_token"""
    resp = requests.post(
        FEISHU_TOKEN_URL,
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Get token failed: {data}")
    return data["tenant_access_token"]


def upload_file(token: str, file_path: Path, file_type: str) -> str:
    """上传文件到飞书，返回 file_key"""
    headers = {"Authorization": f"Bearer {token}"}
    with file_path.open("rb") as f:
        files = {"file": (file_path.name, f)}
        data = {
            "file_type": file_type,
            "file_name": file_path.name,
        }
        resp = requests.post(
            FEISHU_UPLOAD_URL,
            headers=headers,
            data=data,
            files=files,
            timeout=30,
        )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Upload failed: {data}")
    return data["data"]["file_key"]


def send_file_message(
    token: str,
    receive_id: str,
    receive_id_type: str,
    file_key: str,
) -> dict:
    """发送文件消息到飞书"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {"receive_id_type": receive_id_type}
    payload = {
        "receive_id": receive_id,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key}),
    }
    resp = requests.post(
        FEISHU_SEND_MSG_URL,
        headers=headers,
        params=params,
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Send message failed: {data}")
    return data


def infer_receive_id_type(receive_id: str, explicit: Optional[str]) -> str:
    """根据 receive_id 前缀推断 ID 类型"""
    if explicit:
        return explicit
    if receive_id.startswith("oc_"):
        return "chat_id"
    if receive_id.startswith("ou_"):
        return "open_id"
    if receive_id.startswith("on_"):
        return "user_id"
    return "chat_id"


def resolve_receive_id(cli_value: Optional[str]) -> str:
    """解析 receive_id，支持 CLI 参数和环境变量"""
    if cli_value:
        return cli_value
    
    # 尝试从环境变量读取（支持多种变量名）
    env_value = (
        os.getenv("COPAW_CHAT_ID")
        or os.getenv("FEISHU_CHAT_ID")
        or os.getenv("OPENCLAW_CHAT_ID")
    )
    if env_value:
        return env_value
    
    raise RuntimeError(
        "Missing receive_id. Provide --receive-id or set COPAW_CHAT_ID/FEISHU_CHAT_ID."
    )


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="CoPaw Feishu File Sender - 上传文件到飞书并发送"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="本地文件绝对路径"
    )
    parser.add_argument(
        "--receive-id",
        default=None,
        help="目标 chat_id 或 open_id（可选，默认从环境变量读取）"
    )
    parser.add_argument(
        "--receive-id-type",
        default=None,
        help="ID 类型：chat_id / open_id / user_id（可选，自动识别）"
    )
    parser.add_argument(
        "--file-type",
        default="stream",
        help="文件类型，默认 stream"
    )
    return parser.parse_args()


def main() -> None:
    """主函数"""
    args = parse_args()
    file_path = Path(args.file)
    
    # 检查文件是否存在
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # 加载 CoPaw 配置并获取飞书凭证
    config = load_copaw_config()
    app_id, app_secret = get_feishu_credentials(config)
    
    # 解析 receive_id
    receive_id = resolve_receive_id(args.receive_id)
    receive_id_type = infer_receive_id_type(receive_id, args.receive_id_type)
    
    print(f"📤 上传文件：{file_path.name}")
    print(f"📍 发送到：{receive_id} ({receive_id_type})")
    
    # 获取 token
    token = get_tenant_access_token(app_id, app_secret)
    
    # 上传文件
    file_key = upload_file(token, file_path, args.file_type)
    print(f"✅ 上传成功，file_key: {file_key}")
    
    # 发送消息
    result = send_file_message(token, receive_id, receive_id_type, file_key)
    print(f"✅ 发送成功！message_id: {result.get('data', {}).get('message_id')}")


if __name__ == "__main__":
    main()
