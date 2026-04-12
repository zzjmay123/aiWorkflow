#!/bin/bash
# AI 资讯自动化工作流 - 一键安装脚本
# 自动安装所有依赖并配置环境

set -e  # 遇到错误立即退出

echo "=========================================="
echo " AI 资讯自动化工作流 - 安装脚本"
echo "=========================================="
echo ""

# 1. 检查 Python
echo "[1/5] 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ Python $PYTHON_VERSION 已安装"
else
    echo "❌ 未找到 Python 3，请先安装 Python 3.8+"
    exit 1
fi

# 2. 安装 Python 依赖
echo ""
echo "[2/5] 安装 Python 依赖..."
pip3 install -q -r requirements.txt
echo "✅ Python 依赖安装完成"

# 3. 安装 Playwright 浏览器
echo ""
echo "[3/5] 安装 Playwright 浏览器..."
playwright install chromium
echo "✅ Playwright 浏览器安装完成"

# 4. 安装 xiaohongshu-cli
echo ""
echo "[4/5] 安装小红书 CLI..."
if ! command -v pipx &> /dev/null; then
    echo "  安装 pipx..."
    pip3 install -q pipx
    pipx ensurepath
fi

if ! command -v xiaohongshu &> /dev/null; then
    echo "  安装 xiaohongshu-cli..."
    pipx install xiaohongshu-cli
    echo "✅ xiaohongshu-cli 安装完成"
else
    echo "✅ xiaohongshu-cli 已安装"
fi

# 5. 验证安装
echo ""
echo "[5/5] 验证安装..."
python3 scripts/ai_news_text_only.py --help > /dev/null 2>&1 && echo "✅ 脚本验证通过" || echo "⚠️  脚本验证失败"
xiaohongshu --version > /dev/null 2>&1 && echo "✅ 小红书 CLI 验证通过" || echo "⚠️  小红书 CLI 验证失败"

echo ""
echo "=========================================="
echo "🎉 安装完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 授权小红书：xiaohongshu auth login"
echo "2. 生成文本：python3 scripts/ai_news_text_only.py"
echo "3. 自动发布：python3 scripts/auto_publish_final.py"
echo ""
echo "详细文档：docs/01-安装指南.md"
echo ""
