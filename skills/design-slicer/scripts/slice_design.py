#!/usr/bin/env python3
"""
Design Image Slicer
-------------------
Slices a UI design image into reusable assets (Header, Card, Wave).
This script detects the white card area and extracts the surrounding elements.
"""

import os
import sys
from PIL import Image

def slice_design_image(image_path, output_dir):
    print(f"🔪 Starting slice for: {image_path}")
    
    if not os.path.exists(image_path):
        print("❌ Image not found.")
        return

    img = Image.open(image_path)
    w, h = img.size
    print(f"📐 Dimensions: {w}x{h}")

    os.makedirs(output_dir, exist_ok=True)

    # 1. Detect the White Card Area (Improved)
    # Scan the center column for the longest continuous segment of white pixels.
    
    best_start = -1
    best_end = -1
    max_len = 0
    
    current_start = -1
    current_len = 0
    
    for y in range(h):
        pixel = img.getpixel((w // 2, y))
        # White threshold
        is_white = all(c > 240 for c in pixel[:3])
        
        if is_white:
            if current_start == -1:
                current_start = y
            current_len += 1
        else:
            if current_len > max_len:
                max_len = current_len
                best_start = current_start
                best_end = current_start + current_len
            current_start = -1
            current_len = 0
            
    if current_len > max_len: # Check last segment
        best_start = current_start
        best_end = current_start + current_len
        
    if best_start != -1:
        card_top = best_start
        card_bottom = best_end
    else:
        # Fallback to rough estimation if detection fails
        card_top = int(h * 0.25)
        card_bottom = int(h * 0.85)
    
    # Refined bounds
    header_h = card_top
    wave_h = h - card_bottom

    print(f"📍 Detected Header Height: {header_h}")
    print(f"📍 Detected Card Y-Range: {card_top} - {card_bottom}")

    # 2. Slice Assets
    
    # A. Header (Background + Globe)
    header_img = img.crop((0, 0, w, header_h + 100)) # +100 for overlap
    header_img.save(os.path.join(output_dir, "header_bg.png"))
    
    # B. The Card (Template for news)
    card_img = img.crop((0, card_top, w, card_bottom))
    card_img.save(os.path.join(output_dir, "card_template.png"))
    
    # C. The Wave (Footer)
    wave_img = img.crop((0, card_bottom, w, h))
    wave_img.save(os.path.join(output_dir, "wave_footer.png"))
    
    # D. Full Background (The base)
    bg_img = img.copy()
    bg_img.save(os.path.join(output_dir, "base_bg.png"))

    print("✅ Slicing complete! Assets saved to:", output_dir)

if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else "input.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "./sliced_assets"
    slice_design_image(img, out)
