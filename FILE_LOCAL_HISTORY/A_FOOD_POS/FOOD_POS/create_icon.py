#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Food POS System - Icon Creator
สร้างไอคอนสำหรับไฟล์ executable
"""

import os
from PIL import Image, ImageDraw, ImageFont
import io

def create_icon():
    """
    สร้างไอคอนสำหรับ Food POS System
    """
    try:
        # สร้างภาพขนาด 256x256 (ขนาดมาตรฐานสำหรับ ICO)
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # สีพื้นหลัง (gradient จากส้มเข้มไปส้มอ่อน)
        for y in range(size):
            color_ratio = y / size
            r = int(255 * (0.9 - color_ratio * 0.3))  # ส้มเข้ม -> ส้มอ่อน
            g = int(140 * (0.9 - color_ratio * 0.2))  # 
            b = int(0 * (1 - color_ratio * 0.1))      # 
            for x in range(size):
                img.putpixel((x, y), (r, g, b, 255))
        
        # วาดวงกลมพื้นหลัง
        circle_margin = 20
        circle_bbox = [circle_margin, circle_margin, size - circle_margin, size - circle_margin]
        draw.ellipse(circle_bbox, fill=(255, 165, 0, 255), outline=(255, 140, 0, 255), width=4)
        
        # วาดสัญลักษณ์จาน (วงกลมใหญ่)
        plate_margin = 60
        plate_bbox = [plate_margin, plate_margin, size - plate_margin, size - plate_margin]
        draw.ellipse(plate_bbox, fill=(255, 255, 255, 255), outline=(200, 200, 200, 255), width=3)
        
        # วาดอาหารบนจาน (วงกลมเล็กๆ หลายวง)
        food_colors = [
            (255, 100, 100, 255),  # แดง (มะเขือเทศ)
            (100, 255, 100, 255),  # เขียว (ผัก)
            (255, 255, 100, 255),  # เหลือง (ข้าว)
            (150, 100, 50, 255),   # น้ำตาล (เนื้อ)
        ]
        
        # วาดอาหารแบบสุ่ม
        import random
        random.seed(42)  # ใช้ seed เพื่อให้ได้ผลลัพธ์เหมือนเดิมทุกครั้ง
        
        for i in range(8):
            food_size = random.randint(15, 25)
            x = random.randint(plate_margin + 20, size - plate_margin - 20 - food_size)
            y = random.randint(plate_margin + 20, size - plate_margin - 20 - food_size)
            color = random.choice(food_colors)
            
            draw.ellipse([x, y, x + food_size, y + food_size], fill=color)
        
        # วาดส้อมและมีด (เส้นง่ายๆ)
        fork_x = size - 80
        fork_y = 80
        
        # ส้อม
        draw.line([fork_x, fork_y, fork_x, fork_y + 60], fill=(150, 150, 150, 255), width=4)
        for i in range(3):
            draw.line([fork_x - 6 + i * 6, fork_y, fork_x - 6 + i * 6, fork_y + 15], 
                     fill=(150, 150, 150, 255), width=2)
        
        # มีด
        knife_x = fork_x + 20
        knife_y = fork_y
        draw.line([knife_x, knife_y, knife_x, knife_y + 60], fill=(150, 150, 150, 255), width=4)
        draw.polygon([(knife_x - 8, knife_y), (knife_x + 8, knife_y), (knife_x, knife_y + 20)], 
                    fill=(200, 200, 200, 255))
        
        # เพิ่มเงา
        shadow_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        
        # เงาของวงกลมหลัก
        shadow_offset = 8
        shadow_circle = [circle_margin + shadow_offset, circle_margin + shadow_offset, 
                        size - circle_margin + shadow_offset, size - circle_margin + shadow_offset]
        shadow_draw.ellipse(shadow_circle, fill=(0, 0, 0, 50))
        
        # รวมเงากับภาพหลัก
        img = Image.alpha_composite(shadow_img, img)
        
        # บันทึกเป็นไฟล์ ICO
        # สร้างหลายขนาดสำหรับ ICO file
        sizes = [16, 32, 48, 64, 128, 256]
        icon_images = []
        
        for icon_size in sizes:
            resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # บันทึกเป็น ICO
        icon_images[0].save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
        
        # บันทึกเป็น PNG สำหรับดูตัวอย่าง
        img.save('icon_preview.png', format='PNG')
        
        print("✅ สร้างไอคอนเสร็จแล้ว!")
        print("   - icon.ico (สำหรับ executable)")
        print("   - icon_preview.png (สำหรับดูตัวอย่าง)")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างไอคอน: {e}")
        return False

def create_simple_icon():
    """
    สร้างไอคอนแบบง่าย (fallback)
    """
    try:
        size = 256
        img = Image.new('RGBA', (size, size), (255, 165, 0, 255))  # พื้นหลังสีส้ม
        draw = ImageDraw.Draw(img)
        
        # วาดตัวอักษร POS
        try:
            # ลองใช้ฟอนต์ระบบ
            font_size = 80
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # ใช้ฟอนต์เริ่มต้น
            font = ImageFont.load_default()
        
        # วาดข้อความ POS
        text = "POS"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        # เงาข้อความ
        draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0, 128))
        # ข้อความหลัก
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        # วาดกรอบ
        draw.rectangle([10, 10, size-10, size-10], outline=(255, 140, 0, 255), width=8)
        
        # บันทึกเป็น ICO
        sizes = [16, 32, 48, 64, 128, 256]
        icon_images = []
        
        for icon_size in sizes:
            resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        icon_images[0].save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
        img.save('icon_preview.png', format='PNG')
        
        print("✅ สร้างไอคอนแบบง่ายเสร็จแล้ว!")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างไอคอนแบบง่าย: {e}")
        return False

def main():
    """
    ฟังก์ชันหลัก
    """
    print("🎨 กำลังสร้างไอคอนสำหรับ Food POS System...")
    
    # ตรวจสอบ Pillow
    try:
        from PIL import Image
        print("✅ พบ Pillow library")
    except ImportError:
        print("⚠️  ไม่พบ Pillow library กำลังติดตั้ง...")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
            print("✅ ติดตั้ง Pillow เสร็จแล้ว")
        except:
            print("❌ ไม่สามารถติดตั้ง Pillow ได้")
            return False
    
    # ลองสร้างไอคอนแบบละเอียด
    if not create_icon():
        print("⚠️  ลองสร้างไอคอนแบบง่าย...")
        if not create_simple_icon():
            print("❌ ไม่สามารถสร้างไอคอนได้")
            return False
    
    return True

if __name__ == "__main__":
    if main():
        print("\n🎉 สร้างไอคอนเสร็จสมบูรณ์!")
    else:
        print("\n❌ ไม่สามารถสร้างไอคอนได้")
    
    input("กด Enter เพื่อออก...")