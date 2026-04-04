#!/usr/bin/env python3
"""
Pinchtab 快速测试脚本
验证 Pinchtab 服务是否正常工作
"""

import sys
sys.path.insert(0, '/Users/zhouzhenjiang/.copaw/active_skills/Pinchtab Browser Automation/scripts')

from pinchtab_client import PinchtabClient
import time

def main():
    print("🧪 Pinchtab 快速测试")
    print("=" * 60)
    
    client = PinchtabClient()
    
    # 1. 健康检查
    print("\n[1/5] 健康检查...")
    if not client.health_check():
        print("❌ 失败：Pinchtab 服务未运行")
        print("💡 请运行：~/bin/pinchtab-start.sh")
        return False
    print("✅ 通过")
    
    # 2. 打开网页
    print("\n[2/5] 打开网页 (https://www.baidu.com)...")
    try:
        client.open("https://www.baidu.com")
        time.sleep(2)
        print("✅ 通过")
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False
    
    # 3. 获取快照
    print("\n[3/5] 获取页面快照...")
    try:
        snapshot = client.snapshot()
        title = snapshot.get('title', 'Unknown')
        print(f"✅ 通过 - 页面标题：{title}")
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False
    
    # 4. 截图
    print("\n[4/5] 截图测试...")
    try:
        path = client.screenshot("/tmp/pinchtab_test.png", full_page=True)
        print(f"✅ 通过 - 截图保存：{path}")
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False
    
    # 5. 查找元素
    print("\n[5/5] 查找元素测试...")
    try:
        search_ref = client.find_element(role="searchbox")
        if search_ref:
            print(f"✅ 通过 - 找到搜索框：{search_ref}")
        else:
            print("⚠️  未找到搜索框（可能页面结构变化）")
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！Pinchtab 工作正常")
    print("\n📚 使用方式:")
    print("   from pinchtab_client import PinchtabClient")
    print("   client = PinchtabClient()")
    print("   client.open('https://example.com')")
    print("   snapshot = client.snapshot()")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
