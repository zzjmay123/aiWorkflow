---
name: design-slicer
description: |
  将用户提供的 UI 设计稿截图自动切片为可用的前端素材（背景、卡片、装饰元素）。
  当用户提供一张设计图并要求“还原”、“切图”或“生成素材”时使用。
metadata:
  author: Agent
  version: "1.0.0"
---

# Design Slicer Skill

## 功能
自动分析 UI 截图，识别布局结构（Header, Content Card, Footer），并切分出独立的素材文件，用于后续的 HTML/CSS 100% 还原。

## 用法
1. 确认用户已上传图片或提供了图片路径。
2. 运行脚本：
   ```bash
   python skills/design-slicer/scripts/slice_design.py <image_path> <output_dir>
   ```
3. 将切出的素材（`header_bg.png`, `card_template.png`, `wave_footer.png`）同步到工作区。
4. 更新 `ai-news-generator.html` 引用这些素材。
5. **提交代码**：`git add . && git commit -m "feat: update design assets from slice" && git push`。

## 资产说明
- **header_bg.png**: 包含顶部背景、光晕、地球等装饰。
- **card_template.png**: 中间的白色卡片主体（用于动态填充文字）。
- **wave_footer.png**: 底部的波浪纹理。
