#!/usr/bin/env python3
from pathlib import Path
import time

downloads = Path.home() / 'Downloads'

# 找最近 5 分钟内的 PNG 文件
now = time.time()
five_min_ago = now - 300

recent_files = []
for f in downloads.glob('*.png'):
    mtime = f.stat().st_mtime
    if mtime > five_min_ago:
        recent_files.append((f, mtime))

if recent_files:
    print(f'✅ 找到 {len(recent_files)} 张新图片:')
    for f, mtime in sorted(recent_files, key=lambda x: x[1], reverse=True):
        t = time.strftime('%H:%M:%S', time.localtime(mtime))
        print(f'  {t} - {f.name} ({f.stat().st_size / 1024 / 1024:.2f} MB)')
else:
    print('❌ 未找到最近 5 分钟的图片')
