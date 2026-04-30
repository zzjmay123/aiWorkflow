#!/usr/bin/env python3
"""
智谱 GLM Coding Plan 自动抢购脚本
每天上午 10:00 限量放货，本脚本帮你拼手速

使用方式:
  python3 snap_up_codingplan.py              # 默认 Pro 套餐
  python3 snap_up_codingplan.py --plan lite   # Lite 套餐
  python3 snap_up_codingplan.py --plan max    # Max 套餐
  python3 snap_up_codingplan.py --now         # 立即执行（不等 10 点）
  python3 snap_up_codingplan.py --headed      # 显示浏览器窗口
"""

import argparse
import asyncio
import sys
import time
from datetime import datetime, timedelta
from playwright.async_api import async_playwright


# ============================================================
# 配置区 - 根据实际情况修改
# ============================================================

# 抢购页面 URL
PURCHASE_URL = "https://bigmodel.cn/pricing"

# 套餐名称映射（页面按钮文字，需要根据实际页面调整）
PLAN_SELECTORS = {
    "lite": {
        "card": "Lite",           # 套餐卡片上的文字标识
        "button_text": "开通",     # 购买按钮文字
    },
    "pro": {
        "card": "Pro",
        "button_text": "开通",
    },
    "max": {
        "card": "Max",
        "button_text": "开通",
    },
}

# 抢购目标时间
TARGET_HOUR = 10
TARGET_MINUTE = 0

# 提前多少秒开始准备页面
PREPARE_SECONDS = 120  # 提前 2 分钟打开页面

# 刷新间隔（秒）- 在 10:00 前刷新页面
REFRESH_INTERVAL = 2

# 抢购时点击间隔（毫秒）
CLICK_INTERVAL_MS = 50


# ============================================================
# 核心逻辑
# ============================================================

async def wait_until_target_time(plan: str, headed: bool = False, now: bool = False):
    """等待到目标时间，然后执行抢购"""
    
    target_time = datetime.now().replace(
        hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0
    )
    
    # 如果当前时间已经过了今天的目标时间，就等明天的
    if datetime.now() >= target_time and not now:
        target_time += timedelta(days=1)
        print(f"⏰ 今日 10:00 已过，已自动设置为明天 {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if now:
        print("⚡  立即执行模式，不等时间")
    else:
        wait_seconds = (target_time - datetime.now()).total_seconds()
        print(f"⏰ 抢购目标时间: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📦 目标套餐: {plan.upper()}")
        print(f"⏳ 等待 {wait_seconds:.0f} 秒...")
        
        # 倒计时
        prepare_time = target_time - timedelta(seconds=PREPARE_SECONDS)
        wait_to_prepare = (prepare_time - datetime.now()).total_seconds()
        
        if wait_to_prepare > 0:
            print(f"   还剩 {wait_to_prepare/60:.1f} 分钟开始准备页面...")
            print("   (你可以先休息，脚本会自动倒计时)")
            await asyncio.sleep(wait_to_prepare)
        else:
            print("   已经接近抢购时间，立即准备！")
        
        print(f"🚀 提前 {PREPARE_SECONDS} 秒打开页面准备...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # 使用用户数据目录，保持登录态
        # 注意：第一次运行需要先手动登录
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        print("🌐 正在打开抢购页面...")
        try:
            await page.goto(PURCHASE_URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"⚠️  页面加载超时: {e}")
            print("   可能是网络问题，继续尝试...")
        
        print("✅ 页面已打开")
        
        if not now:
            # 等待到目标时间，期间定期刷新
            time_left = (target_time - datetime.now()).total_seconds()
            while time_left > 5:
                await asyncio.sleep(REFRESH_INTERVAL)
                time_left = (target_time - datetime.now()).total_seconds()
                remaining = max(0, time_left)
                print(f"   ⏳ 倒计时 {remaining:.0f} 秒...")
                
                # 最后 30 秒开始高频刷新
                if remaining <= 30:
                    try:
                        await page.reload(wait_until="domcontentloaded", timeout=10000)
                    except:
                        pass
        
        # 🎯 开始抢购！
        print("\n" + "="*50)
        print("🎯🎯🎯 开始抢购！🎯🎯🎯")
        print("="*50)
        
        success = await snap_up(page, plan)
        
        if not success:
            print("\n❌ 抢购未成功，请手动检查页面状态")
            print("   你可以手动点击购买，浏览器窗口不会自动关闭")
            
            # 保持浏览器打开，让用户手动操作
            if headed:
                print("   浏览器窗口保持打开，完成后可手动关闭")
                await asyncio.sleep(300)  # 等 5 分钟
        
        await browser.close()
        
        if success:
            print("\n🎉 抢购流程已触发！请完成支付")


async def snap_up(page, plan: str) -> bool:
    """执行抢购操作"""
    
    plan_info = PLAN_SELECTORS[plan]
    max_retries = 30
    retry = 0
    
    while retry < max_retries:
        retry += 1
        print(f"\n🔄 第 {retry} 次尝试...")
        
        try:
            # 刷新页面获取最新状态
            if retry > 1:
                await page.reload(wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(0.5)
            
            # 方式1: 尝试点击套餐对应的购买按钮
            # 先尝试通过套餐名称定位
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.inner_text()
                if plan_info["button_text"] in text:
                    # 检查这个按钮是否属于目标套餐
                    parent = await btn.evaluate_handle(
                        "el => el.closest('.plan-card, .pricing-card, [class*=card], [class*=plan], [class*=pricing]')"
                    )
                    if parent:
                        parent_text = await parent.inner_text()
                        if plan_info["card"] in parent_text:
                            print(f"👉 找到 {plan.upper()} 套餐购买按钮: '{text}'")
                            await btn.click()
                            print("✅ 已点击购买按钮！")
                            await asyncio.sleep(1)
                            return await check_purchase_success(page)
            
            # 方式2: 如果没有找到，尝试通用选择器
            # 查找包含套餐名称的元素
            plan_elements = await page.query_selector_all(f"text={plan_info['card']}")
            for el in plan_elements:
                # 在这个元素附近找按钮
                parent = await el.evaluate_handle(
                    "el => el.closest('.plan-card, .pricing-card, [class*=card], [class*=plan]')"
                )
                if parent:
                    buy_btn = await parent.query_selector("button")
                    if buy_btn:
                        btn_text = await buy_btn.inner_text()
                        print(f"👉 找到按钮: '{btn_text}'")
                        try:
                            await buy_btn.click()
                            print("✅ 已点击！")
                            await asyncio.sleep(1)
                            return await check_purchase_success(page)
                        except:
                            pass
            
            # 方式3: 查找所有 "开通" / "立即购买" / "订阅" 按钮
            action_texts = ["开通", "立即购买", "订阅", "抢购", "购买"]
            for action_text in action_texts:
                btns = await page.query_selector_all(f"text={action_text}")
                if btns:
                    print(f"👉 尝试点击 '{action_text}' 按钮...")
                    await btns[0].click()
                    await asyncio.sleep(1)
                    if await check_purchase_success(page):
                        return True
            
            await asyncio.sleep(CLICK_INTERVAL_MS / 1000)
            
        except Exception as e:
            print(f"⚠️  操作异常: {e}")
            await asyncio.sleep(0.2)
    
    return False


async def check_purchase_success(page) -> bool:
    """检查是否成功进入支付流程"""
    try:
        url = page.url
        # 判断是否跳转到了支付/订单页面
        success_keywords = [
            "pay", "order", "checkout", "confirm", 
            "支付", "订单", "收银台", "确认"
        ]
        for keyword in success_keywords:
            if keyword.lower() in url.lower():
                print(f"🎉 似乎已进入支付页面: {url}")
                return True
        
        # 检查页面上是否有支付相关文字
        body_text = await page.inner_text("body")
        payment_indicators = ["支付宝", "微信", "支付金额", "确认支付", "收银台"]
        for indicator in payment_indicators:
            if indicator in body_text:
                print(f"🎉 页面出现支付相关内容: '{indicator}'")
                return True
        
        return False
    except:
        return False


def main():
    parser = argparse.ArgumentParser(description="智谱 GLM Coding Plan 抢购脚本")
    parser.add_argument("--plan", choices=["lite", "pro", "max"], default="pro",
                        help="目标套餐 (默认: pro)")
    parser.add_argument("--now", action="store_true",
                        help="立即执行，不等 10 点")
    parser.add_argument("--headed", action="store_true",
                        help="显示浏览器窗口（默认后台运行）")
    parser.add_argument("--url", type=str, default=None,
                        help="自定义抢购页面 URL")
    
    args = parser.parse_args()
    
    if args.url:
        global PURCHASE_URL
        PURCHASE_URL = args.url
    
    print("="*50)
    print("🔥 智谱 GLM Coding Plan 抢购脚本")
    print("="*50)
    print(f"📦 套餐: {args.plan.upper()}")
    print(f"🌐 页面: {PURCHASE_URL}")
    print()
    print("⚠️  注意事项:")
    print("   1. 首次运行需要先在浏览器中登录智谱账号")
    print("   2. 建议使用 --headed 参数首次运行，确认登录态")
    print("   3. 脚本会在 10:00 自动点击购买按钮")
    print("   4. 点击后需要手动完成支付")
    print()
    
    confirm = input("确认开始？(y/n): ")
    if confirm.lower() != "y":
        print("已取消")
        sys.exit(0)
    
    asyncio.run(wait_until_target_time(args.plan, args.headed, args.now))


if __name__ == "__main__":
    main()
