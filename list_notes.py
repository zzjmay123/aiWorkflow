#!/usr/bin/env python3
import subprocess
import json

result = subprocess.run(
    ['python3', '-m', 'pipx', 'run', 'xiaohongshu-cli', 'my-notes', '--json'],
    capture_output=True, text=True
)

data = json.loads(result.stdout)
notes = data.get('data', {}).get('notes', [])

print(f"共有 {len(notes)} 条笔记\n")
for i, note in enumerate(notes[:20], 1):
    title = note.get('display_title', 'No Title')[:60]
    time = note.get('time', 'Unknown')
    note_id = note.get('id', '')
    print(f"{i}. {time} - {title} - {note_id}")
