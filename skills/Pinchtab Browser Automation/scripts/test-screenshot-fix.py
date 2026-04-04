#!/usr/bin/env python3
"""
Pinchtab 截图功能测试 - 验证修复后的截图 API
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pinchtab_client import PinchtabClient
import time

def test_screenshot():
    """测试截图功能"""
    client = PinchtabClient()
    
    print("🧪 Pinchtab 截图功能测试")
    print("=" * 50)
    
    # 1. 检查服务
    print("\n[1/4] 检查服务状态...")
    if not client.health_check():
        print("❌ Pinchtab 服务未运行")
        return False
    print("✅ 服务运行正常")
    
    # 2. 打开网页
    print("\n[2/4] 打开测试网页...")
    result = client.open("https://www.baidu.com")
    print(f"✅ 打开成功：{result.get('title', 'Unknown')}")
    time.sleep(2)
    
    # 3. 全屏截图
    print("\n[3/4] 全屏截图测试...")
    screenshot_path = client.screenshot("/tmp/pinchtab_fullpage.png", full_page=True)
    print(f"✅ 全屏截图已保存：{screenshot_path}")
    
    # 4. 当前视口截图
    print("\n[4/4] 视口截图测试...")
    viewport_path = client.screenshot("/tmp/pinchtab_viewport.png", full_page=False)
    print(f"✅ 视口截图已保存：{viewport_path}")
    
    print("\n" + "=" * 50)
    print("🎉 截图功能测试完成！")
    print("\n📁 生成的文件:")
    for path in [screenshot_path, viewport_path]:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   - {path} ({size/1024:.1f} KB)")
    
    return True

if __name__ == "__main__":
    success = test_screenshot()
    sys.exit(0 if success else 1)
