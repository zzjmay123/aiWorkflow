#!/usr/bin/env python3
"""
智谱 GLM Coding Plan 抢购脚本 - CDP 增强版
直接操控你已登录的 Chrome 浏览器，无需重新登录

前提:
  - Chrome 需要在 chrome://inspect/#remote-debugging 中开启远程调试
  - 或者启动 Chrome 时添加 --remote-debugging-port=9222

使用方式:
  python3 snap_up_cdp.py                    # 默认 Pro, 等待 10:00
  python3 snap_up_cdp.py --plan lite        # Lite 套餐
  python3 snap_up_cdp.py --now              # 立即执行
  python3 snap_up_cdp.py --port 9222        # 指定调试端口

注意: 如果 Chrome 未开启远程调试，先打开 chrome://version 查看配置文件路径，
      然后用命令行启动: 
      /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timedelta

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ 需要安装 playwright: pip install playwright && playwright install chromium")
    sys.exit(1)


# ============================================================
# 配置
# ============================================================

PURCHASE_URL = "https://bigmodel.cn/pricing"
TARGET_HOUR = 10
TARGET_MINUTE = 0
CDP_PORT = 9222


# ============================================================
# 核心逻辑
# ============================================================

async def find_cdp_targets(cdp_port):
    """列出 Chrome 所有已打开的标签页"""
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=5) as resp:
            targets = json.loads(resp.read())
        return targets
    except Exception as e:
        print(f"❌ 无法连接 Chrome CDP 端口 {cdp_port}: {e}")
        print("\n请先开启 Chrome 远程调试:")
        print("  方法1: 打开 chrome://inspect，勾选 'Allow remote debugging'")
        print(f"  方法2: 命令行启动 Chrome: --remote-debugging-port={cdp_port}")
        return []


async def wait_and_snap_up(plan="pro", now=False, headed=True):
    """主流程：等待时间 + 抢购"""
    
    target_time = datetime.now().replace(
        hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0
    )
    
    if datetime.now() >= target_time and not now:
        target_time += timedelta(days=1)
        print(f"⏰ 今日 10:00 已过，已设置为明天 {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if now:
        print("⚡ 立即执行模式")
    else:
        wait_seconds = (target_time - datetime.now()).total_seconds()
        print(f"⏰ 抢购目标: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📦 套餐: {plan.upper()}")
        print(f"⏳ 等待 {wait_seconds:.0f} 秒 ({wait_seconds/60:.1f} 分钟)")
        print("   倒计时期间你可以做别的事，脚本会自动倒计时")
        await asyncio.sleep(wait_seconds)
    
    print("\n🚀 开始连接你的 Chrome 浏览器...")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
            print("✅ 已连接 Chrome!")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return
        
        # 获取已有页面列表
        contexts = browser.contexts
        if not contexts:
            print("❌ 没有找到浏览器上下文")
            return
        
        context = contexts[0]
        pages = context.pages
        
        # 查找是否已有 pricing 页面
        pricing_page = None
        for pg in pages:
            if "bigmodel.cn" in pg.url:
                pricing_page = pg
                print(f"🔍 找到已打开的智谱页面: {pg.url}")
                break
        
        if not pricing_page:
            # 创建新标签页打开
            print("🌐 打开抢购页面...")
            pricing_page = await context.new_page()
            try:
                await pricing_page.goto(PURCHASE_URL, wait_until="domcontentloaded", timeout=30000)
                print("✅ 页面已打开")
            except Exception as e:
                print(f"⚠️ 页面加载超时: {e}")
                print("   请在浏览器中手动打开 bigmodel.cn/pricing")
        
        # 如果不立即执行，在接近 10 点时刷新
        if not now:
            # 最后 30 秒开始高频刷新
            print("   等待到 10:00...")
            while True:
                remaining = 60 - datetime.now().second
                if datetime.now().hour == TARGET_HOUR and datetime.now().minute == TARGET_MINUTE:
                    break
                if datetime.now().hour == TARGET_HOUR and datetime.now().minute > TARGET_MINUTE:
                    break
                await asyncio.sleep(min(remaining, 5))
        
        # 🎯 抢购!
        print("\n" + "="*50)
        print("🎯🎯🎯 开始抢购！🎯🎯🎯")
        print("="*50)
        
        await execute_snap_up(pricing_page, plan)
        
        print("\n✅ 抢购流程完成，请检查浏览器")


async def execute_snap_up(page, plan):
    """执行抢购点击"""
    
    plan_info = {
        "lite": {"text": "Lite", "keywords": ["Lite", "lite"]},
        "pro": {"text": "Pro", "keywords": ["Pro", "pro"]},
        "max": {"text": "Max", "keywords": ["Max", "max"]},
    }[plan]
    
    action_words = ["开通", "立即购买", "订阅", "抢购", "立即开通"]
    
    for attempt in range(50):
        print(f"\n🔄 第 {attempt+1} 轮...")
        
        try:
            # 刷新页面
            if attempt > 0:
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=10000)
                except:
                    pass
            
            await asyncio.sleep(0.3)
            
            # 策略1: 查找包含套餐名 + 开通按钮的卡片
            buttons = await page.query_selector_all("button")
            target_btn = None
            
            for btn in buttons:
                try:
                    text = await btn.inner_text()
                    if text.strip() not in action_words:
                        continue
                    
                    # 找到按钮的父级卡片
                    card_text = await btn.evaluate("""el => {
                        let p = el.parentElement;
                        let depth = 0;
                        while (p && depth < 6) {
                            const t = p.innerText || '';
                            if (t.length > 50 && t.length < 500) return t;
                            p = p.parentElement;
                            depth++;
                        }
                        return '';
                    }""")
                    
                    # 检查卡片是否包含目标套餐名
                    if any(kw in card_text for kw in plan_info["keywords"]):
                        target_btn = btn
                        print(f"👉 定位到 {plan.upper()} 套餐 '{text}' 按钮")
                        break
                except:
                    continue
            
            if target_btn:
                await target_btn.click()
                print(f"✅ 已点击！")
                await asyncio.sleep(1.5)
                
                # 检查是否成功
                current_url = page.url
                if any(kw in current_url.lower() for kw in ["pay", "order", "checkout", "收银台"]):
                    print(f"🎉 已进入支付页面: {current_url}")
                    return True
                
                body_text = await page.inner_text("body")
                if any(kw in body_text for kw in ["支付宝", "微信支付", "确认支付", "收银台"]):
                    print("🎉 页面出现支付选项！")
                    return True
            
            # 策略2: 如果没找到套餐特定的，尝试找任何可点击的按钮
            if not target_btn:
                for action in action_words:
                    try:
                        btns = await page.query_selector_all(f"text={action}")
                        if btns:
                            print(f"👉 尝试 '{action}' 按钮...")
                            await btns[0].click()
                            await asyncio.sleep(1)
                            if await check_payment_page(page):
                                return True
                    except:
                        pass
            
            await asyncio.sleep(0.2)
            
        except Exception as e:
            print(f"⚠️  异常: {e}")
            await asyncio.sleep(0.3)
    
    print("\n⚠️  达到最大尝试次数，请手动检查页面")
    return False


async def check_payment_page(page) -> bool:
    """检查是否进入支付页面"""
    try:
        url = page.url
        if any(kw in url.lower() for kw in ["pay", "order", "checkout", "收银台"]):
            print(f"🎉 已进入支付页面: {url}")
            return True
        body_text = await page.inner_text("body")
        if any(kw in body_text for kw in ["支付宝", "微信支付", "确认支付", "收银台"]):
            print("🎉 出现支付选项!")
            return True
        return False
    except:
        return False


def main():
    parser = argparse.ArgumentParser(description="智谱 GLM Coding Plan 抢购 (CDP 版)")
    parser.add_argument("--plan", choices=["lite", "pro", "max"], default="pro")
    parser.add_argument("--now", action="store_true", help="立即执行")
    parser.add_argument("--port", type=int, default=CDP_PORT, help="Chrome 调试端口")
    
    args = parser.parse_args()
    
    global CDP_PORT
    CDP_PORT = args.port
    
    print("="*50)
    print("🔥 智谱 GLM Coding Plan 抢购脚本 (CDP 增强版)")
    print("="*50)
    print(f"📦 套餐: {args.plan.upper()}")
    print(f"🌐 页面: {PURCHASE_URL}")
    print(f"🔌 CDP 端口: {CDP_PORT}")
    print()
    print("⚠️  使用前请确认:")
    print("   1. Chrome 已开启远程调试 (--remote-debugging-port)")
    print("   2. Chrome 中已登录智谱账号")
    print("   3. 抢购时需手动完成支付")
    print()
    
    # 先检查 CDP 是否可用
    targets = asyncio.get_event_loop().run_until_complete(find_cdp_targets(CDP_PORT))
    if not targets:
        print("\n💡 快速开启 Chrome 远程调试:")
        print(f'   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port={CDP_PORT}')
        sys.exit(1)
    
    print(f"✅ 已发现 {len(targets)} 个 Chrome 标签页")
    
    confirm = input("确认开始？(y/n): ")
    if confirm.lower() != "y":
        sys.exit(0)
    
    asyncio.run(wait_and_snap_up(args.plan, args.now))


if __name__ == "__main__":
    main()
