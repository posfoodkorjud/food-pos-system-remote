# -*- coding: utf-8 -*-
"""
QR Code Generator สำหรับระบบ POS
"""

import qrcode
import base64
from io import BytesIO
from PIL import Image

class QRGenerator:
    """คลาสสำหรับสร้าง QR Code"""
    
    def __init__(self):
        self.default_config = {
            'version': 1,
            'error_correction': qrcode.constants.ERROR_CORRECT_L,
            'box_size': 10,
            'border': 4,
        }
    
    def generate_qr(self, data: str, config: dict = None) -> str:
        """
        สร้าง QR Code และคืนค่าเป็น base64 string
        
        Args:
            data: ข้อมูลที่จะใส่ใน QR Code
            config: การตั้งค่า QR Code (optional)
            
        Returns:
            base64 string ของรูป QR Code
        """
        try:
            # ใช้การตั้งค่าเริ่มต้นหรือที่ส่งมา
            qr_config = config or self.default_config
            
            # สร้าง QR Code object
            qr = qrcode.QRCode(
                version=qr_config.get('version', 1),
                error_correction=qr_config.get('error_correction', qrcode.constants.ERROR_CORRECT_L),
                box_size=qr_config.get('box_size', 10),
                border=qr_config.get('border', 4),
            )
            
            # เพิ่มข้อมูล
            qr.add_data(data)
            qr.make(fit=True)
            
            # สร้างรูปภาพ
            img = qr.make_image(
                fill_color=qr_config.get('fill_color', 'black'),
                back_color=qr_config.get('back_color', 'white')
            )
            
            # แปลงเป็น base64 data URL
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return ""
    
    def generate_table_qr(self, table_id: int, domain: str) -> str:
        """
        สร้าง QR Code สำหรับโต๊ะ
        
        Args:
            table_id: หมายเลขโต๊ะ
            domain: โดเมนของเว็บไซต์
            
        Returns:
            base64 string ของ QR Code
        """
        url = f"{domain}/order?table={table_id}"
        return self.generate_qr(url)
    
    def save_qr_to_file(self, data: str, filename: str, config: dict = None) -> bool:
        """
        สร้างและบันทึก QR Code เป็นไฟล์
        
        Args:
            data: ข้อมูลที่จะใส่ใน QR Code
            filename: ชื่อไฟล์ที่จะบันทึก
            config: การตั้งค่า QR Code (optional)
            
        Returns:
            True ถ้าบันทึกสำเร็จ, False ถ้าล้มเหลว
        """
        try:
            qr_config = config or self.default_config
            
            qr = qrcode.QRCode(
                version=qr_config.get('version', 1),
                error_correction=qr_config.get('error_correction', qrcode.constants.ERROR_CORRECT_L),
                box_size=qr_config.get('box_size', 10),
                border=qr_config.get('border', 4),
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(
                fill_color=qr_config.get('fill_color', 'black'),
                back_color=qr_config.get('back_color', 'white')
            )
            
            img.save(filename)
            return True
            
        except Exception as e:
            print(f"Error saving QR code to file: {e}")
            return False
    
    def generate_batch_table_qrs(self, table_count: int, domain: str, save_path: str = None) -> dict:
        """
        สร้าง QR Code สำหรับหลายโต๊ะพร้อมกัน
        
        Args:
            table_count: จำนวนโต๊ะ
            domain: โดเมนของเว็บไซต์
            save_path: path สำหรับบันทึกไฟล์ (optional)
            
        Returns:
            dict ที่มี table_id เป็น key และ base64 QR code เป็น value
        """
        qr_codes = {}
        
        for table_id in range(1, table_count + 1):
            try:
                qr_code = self.generate_table_qr(table_id, domain)
                qr_codes[table_id] = qr_code
                
                # บันทึกเป็นไฟล์ถ้าระบุ path
                if save_path:
                    url = f"{domain}/order?table={table_id}"
                    filename = f"{save_path}/table_{table_id}_qr.png"
                    self.save_qr_to_file(url, filename)
                    
            except Exception as e:
                print(f"Error generating QR for table {table_id}: {e}")
                qr_codes[table_id] = ""
        
        return qr_codes

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    generator = QRGenerator()
    
    # ทดสอบสร้าง QR Code
    test_url = "https://example.com/order?table=1"
    qr_base64 = generator.generate_qr(test_url)
    print(f"QR Code length: {len(qr_base64)}")
    
    # ทดสอบสร้าง QR Code สำหรับโต๊ะ
    table_qr = generator.generate_table_qr(1)
    print(f"Table QR Code generated: {len(table_qr) > 0}")
    
    # ทดสอบสร้าง QR Code หลายโต๊ะ
    batch_qrs = generator.generate_batch_table_qrs(5)
    print(f"Generated QR codes for {len(batch_qrs)} tables")