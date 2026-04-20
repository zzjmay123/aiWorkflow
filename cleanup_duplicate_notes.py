#!/usr/bin/env python3
"""
删除今天重复发布的小红书笔记
"""

import subprocess
import json
from datetime import datetime

def get_notes():
    """获取所有笔记"""
    result = subprocess.run(
        ['python3', '-m', 'pipx', 'run', 'xiaohongshu-cli', 'my-notes', '--json'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if data.get('ok'):
            return data.get('data', {}).get('notes', [])
    return []


def delete_note(note_id):
    """删除指定笔记"""
    result = subprocess.run(
        ['python3', '-m', 'pipx', 'run', 'xiaohongshu-cli', 'delete', note_id],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def main():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"查找今天 ({today}) 发布的笔记...")
    
    notes = get_notes()
    today_notes = []
    
    for note in notes:
        note_time = note.get('time', '')
        if note_time.startswith(today):
            today_notes.append(note)
            print(f"  📝 {note_time} - {note.get('display_title', 'No Title')[:50]} - ID: {note.get('id')}")
    
    if len(today_notes) <= 1:
        print(f"\n✅ 今天只有 {len(today_notes)} 条笔记，无需删除")
        return
    
    print(f"\n⚠️  今天发布了 {len(today_notes)} 条笔记，将保留最新 1 条，删除其他 {len(today_notes)-1} 条")
    print()
    
    # 保留最新的（列表第一个）
    keep_note = today_notes[0]
    delete_notes = today_notes[1:]
    
    print(f"✅ 保留：{keep_note.get('time')} - {keep_note.get('display_title', 'No Title')[:50]}")
    print()
    
    for note in delete_notes:
        note_id = note.get('id')
        title = note.get('display_title', 'No Title')[:50]
        print(f"🗑️  删除：{note.get('time')} - {title}... ", end='')
        
        if delete_note(note_id):
            print("✅")
        else:
            print("❌")
    
    print(f"\n✅ 清理完成！保留 {len(today_notes)} 条中的 1 条")


if __name__ == "__main__":
    main()
