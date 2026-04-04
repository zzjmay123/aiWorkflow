---
name: feishu-file-sender
description: 飞书文件发送器 — 为 CoPaw 补齐飞书渠道文件投递能力，通过飞书 OpenAPI 上传并发送 agent 生成的本地文件
license: MIT
compatibility: copaw
metadata:
  version: "2.0.0"
  tags: [feishu, file, upload, im, messaging, openapi, copaw]
  author: wen-ai (adapted for CoPaw)
  copaw:
    emoji: "📎"
    requires:
      bins: [python3]
      config:
        - ~/.copaw/config.json
---

# Feishu File Sender | 飞书文件发送器 (CoPaw 版)

CoPaw agent 在本地生成文件，但飞书渠道只支持文本消息，没有文件投递能力。本 skill 通过直接调用飞书 OpenAPI（上传 + 发送）补齐这一底层能力，使生成的文件能回传到聊天中。

## 快速开始 | Quick Start

```bash
python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/report.xlsx \
  --receive-id oc_xxx
```

## 使用方法 | Usage

```bash
python3 scripts/feishu_file_sender.py \
  --file <文件绝对路径> \
  --receive-id <chat_id|open_id> \
  --receive-id-type <chat_id|open_id|user_id>
```

### 参数说明 | Arguments

- `--file`（必填）：本地文件绝对路径
- `--receive-id`（可选）：目标 chat_id 或 open_id。若省略，脚本会读取 `COPAW_CHAT_ID` 或 `FEISHU_CHAT_ID` 环境变量
- `--receive-id-type`（可选）：若省略，将根据前缀自动识别：
  - `oc_` → chat_id
  - `ou_` → open_id
  - `on_` → user_id
- `--file-type`（可选）：飞书上传的文件类型，默认 `stream`

## 工作原理 | How It Works

1. 从 `~/.copaw/config.json` 读取飞书 appId/appSecret
2. 调用飞书 **上传文件** API 获取 `file_key`
3. 调用飞书 **发送消息** API 发送文件

## 配置说明 | Configuration

飞书凭证存储在 `~/.copaw/config.json`：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "app_id": "cli_xxxxxxxxxxxxx",
      "app_secret": "xxxxxxxxxxxxxxxxxxxxxxxxx"
    }
  }
}
```

## 环境变量 | Environment Variables

- `COPAW_CHAT_ID`：默认发送的飞书群组 chat_id
- `FEISHU_CHAT_ID`：备选环境变量名

## 错误处理 | Error Handling

- **缺少凭证** → 确保 `channels.feishu` 存在于 `~/.copaw/config.json`，且 enabled=true
- **机器人不在群内（230002）** → 将机器人加入目标群或换一个群
- **缺少 receive_id** → 传入 `--receive-id` 或设置 `COPAW_CHAT_ID` 环境变量
- **HTTP 错误** → 查看飞书错误返回中的 `log_id` 进行排查

## 安全说明 | Security

本技能会从本机 CoPaw 配置中读取飞书凭证（`~/.copaw/config.json`）：

- `channels.feishu.app_id`
- `channels.feishu.app_secret`

这些凭证仅用于获取 tenant access token 并发送文件。技能不会存储或向其他地方传输凭证。

## 使用示例 | Examples

### 发送到指定群组

```bash
python3 scripts/feishu_file_sender.py \
  --file /Users/zhouzhenjiang/.copaw/output/report.xlsx \
  --receive-id oc_1234567890
```

### 使用环境变量（推荐）

```bash
export COPAW_CHAT_ID="oc_1234567890"
python3 scripts/feishu_file_sender.py \
  --file /Users/zhouzhenjiang/.copaw/output/report.xlsx
```

### 发送 PDF 文件

```bash
python3 scripts/feishu_file_sender.py \
  --file /Users/zhouzhenjiang/.copaw/output/analysis.pdf \
  --receive-id ou_84a5749d2edf80845c9a5915c6677c75 \
  --receive-id-type open_id
```

## 备注 | Notes

- 本技能专为 **CoPaw** 设计，自动从 `~/.copaw/config.json` 读取配置
- 建议通过入站 `chat_id` 发送到 **当前聊天**
- 文件类型支持：stream（默认）、image、video、audio、doc 等

## 随附脚本 | Bundled Script

- `scripts/feishu_file_sender.py`

## 变更日志 | Changelog

- **v2.0.0** - 适配 CoPaw，从 `~/.copaw/config.json` 读取配置
- **v1.0.9** - 初始版本（OpenClaw）
