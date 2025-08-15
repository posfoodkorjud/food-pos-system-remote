# -*- coding: utf-8 -*-
"""
PromptPay QR Code Generator สำหรับระบบ POS
"""

import qrcode
import base64
from io import BytesIO
from typing import Union

class PromptPayGenerator:
    """คลาสสำหรับสร้าง PromptPay QR Code"""
    
    def __init__(self):
        self.country_code = "TH"
        self.currency_code = "764"  # THB
    
    def _format_phone_number(self, phone: str) -> str:
        """
        จัดรูปแบบเบอร์โทรศัพท์สำหรับ PromptPay
        
        Args:
            phone: เบอร์โทรศัพท์
            
        Returns:
            เบอร์โทรศัพท์ที่จัดรูปแบบแล้ว
        """
        # ลบอักขระที่ไม่ใช่ตัวเลข
        phone = ''.join(filter(str.isdigit, phone))
        
        # ถ้าขึ้นต้นด้วย 0 ให้เปลี่ยนเป็น +66
        if phone.startswith('0'):
            phone = '66' + phone[1:]
        elif not phone.startswith('66'):
            phone = '66' + phone
            
        # เพิ่ม prefix '01' สำหรับ PromptPay
        return '01' + phone
    
    def _format_citizen_id(self, citizen_id: str) -> str:
        """
        จัดรูปแบบเลขบัตรประชาชนสำหรับ PromptPay
        
        Args:
            citizen_id: เลขบัตรประชาชน
            
        Returns:
            เลขบัตรประชาชนที่จัดรูปแบบแล้ว
        """
        # ลบอักขระที่ไม่ใช่ตัวเลข
        citizen_id = ''.join(filter(str.isdigit, citizen_id))
        
        # ตรวจสอบความยาว
        if len(citizen_id) != 13:
            raise ValueError("เลขบัตรประชาชนต้องมี 13 หลัก")
            
        return citizen_id
    
    def _calculate_crc16(self, data: str) -> str:
        """
        คำนวณ CRC16 สำหรับ PromptPay QR Code ตาม CRC-16/CCITT-FALSE
        
        Args:
            data: ข้อมูลที่จะคำนวณ CRC
            
        Returns:
            CRC16 ในรูปแบบ hex string
        """
        crc = 0xFFFF  # Initial value
        polynomial = 0x1021  # CRC-16/CCITT-FALSE polynomial
        
        for byte in data.encode('utf-8'):
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= 0xFFFF
        
        # No final XOR for CRC-16/CCITT-FALSE
        return f"{crc:04X}"
    
    def _format_amount(self, amount: float) -> str:
        """
        จัดรูปแบบจำนวนเงิน
        
        Args:
            amount: จำนวนเงิน
            
        Returns:
            จำนวนเงินในรูปแบบ string
        """
        # ถ้าเป็นจำนวนเต็ม ให้แสดงเป็นจำนวนเต็ม
        if amount == int(amount):
            return str(int(amount))
        else:
            return f"{amount:.2f}"
    
    def generate_promptpay_payload(self, identifier: str, amount: float = 0, identifier_type: str = "phone") -> str:
        """
        สร้าง PromptPay payload
        
        Args:
            identifier: เบอร์โทรศัพท์หรือเลขบัตรประชาชน
            amount: จำนวนเงิน (0 = ไม่ระบุจำนวน)
            identifier_type: ประเภท identifier ("phone" หรือ "citizen_id")
            
        Returns:
            PromptPay payload string
        """
        try:
            # จัดรูปแบบ identifier
            if identifier_type == "phone":
                formatted_id = self._format_phone_number(identifier)
                aid = "A000000677010111"  # PromptPay AID for mobile
            elif identifier_type == "citizen_id":
                formatted_id = self._format_citizen_id(identifier)
                aid = "A000000677010112"  # PromptPay AID for citizen ID
            else:
                raise ValueError("identifier_type ต้องเป็น 'phone' หรือ 'citizen_id'")
            
            # สร้าง payload
            payload = ""
            
            # Payload Format Indicator
            payload += "000201"
            
            # Point of Initiation Method (Static QR)
            payload += "010212" if amount > 0 else "010211"
            
            # Merchant Account Information
            merchant_info = f"0016{aid}01{len(formatted_id):02d}{formatted_id}"
            payload += f"29{len(merchant_info):02d}{merchant_info}"
            
            # Transaction Currency
            payload += f"5303{self.currency_code}"
            
            # Transaction Amount (ถ้ามี)
            if amount > 0:
                amount_str = self._format_amount(amount)
                payload += f"54{len(amount_str):02d}{amount_str}"
            
            # Country Code
            payload += f"5802{self.country_code}"
            
            # CRC16
            payload += "6304"
            crc = self._calculate_crc16(payload)
            payload += crc
            
            return payload
            
        except Exception as e:
            print(f"Error generating PromptPay payload: {e}")
            return ""
    
    def generate_qr(self, identifier: str, amount: float = 0, identifier_type: str = "phone") -> str:
        """
        สร้าง PromptPay QR Code
        
        Args:
            identifier: เบอร์โทรศัพท์หรือเลขบัตรประชาชน
            amount: จำนวนเงิน (0 = ไม่ระบุจำนวน)
            identifier_type: ประเภท identifier ("phone" หรือ "citizen_id")
            
        Returns:
            base64 string ของ PromptPay QR Code
        """
        try:
            # สร้าง payload
            payload = self.generate_promptpay_payload(identifier, amount, identifier_type)
            
            if not payload:
                return ""
            
            # สร้าง QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            qr.add_data(payload)
            qr.make(fit=True)
            
            # สร้างรูปภาพ
            img = qr.make_image(fill_color='black', back_color='white')
            
            # แปลงเป็น base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error generating PromptPay QR code: {e}")
            return ""
    
    def save_qr_to_file(self, identifier: str, amount: float, filename: str, identifier_type: str = "phone") -> bool:
        """
        สร้างและบันทึก PromptPay QR Code เป็นไฟล์
        
        Args:
            identifier: เบอร์โทรศัพท์หรือเลขบัตรประชาชน
            amount: จำนวนเงิน
            filename: ชื่อไฟล์ที่จะบันทึก
            identifier_type: ประเภท identifier
            
        Returns:
            True ถ้าบันทึกสำเร็จ, False ถ้าล้มเหลว
        """
        try:
            payload = self.generate_promptpay_payload(identifier, amount, identifier_type)
            
            if not payload:
                return False
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            qr.add_data(payload)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color='black', back_color='white')
            img.save(filename)
            
            return True
            
        except Exception as e:
            print(f"Error saving PromptPay QR code to file: {e}")
            return False
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        ตรวจสอบความถูกต้องของเบอร์โทรศัพท์
        
        Args:
            phone: เบอร์โทรศัพท์
            
        Returns:
            True ถ้าถูกต้อง, False ถ้าไม่ถูกต้อง
        """
        try:
            formatted = self._format_phone_number(phone)
            return len(formatted) >= 11 and formatted.startswith('66')
        except:
            return False
    
    def validate_citizen_id(self, citizen_id: str) -> bool:
        """
        ตรวจสอบความถูกต้องของเลขบัตรประชาชน
        
        Args:
            citizen_id: เลขบัตรประชาชน
            
        Returns:
            True ถ้าถูกต้อง, False ถ้าไม่ถูกต้อง
        """
        try:
            formatted = self._format_citizen_id(citizen_id)
            
            # ตรวจสอบ checksum
            if len(formatted) != 13:
                return False
            
            # คำนวณ checksum
            sum_digits = 0
            for i in range(12):
                sum_digits += int(formatted[i]) * (13 - i)
            
            checksum = (11 - (sum_digits % 11)) % 10
            
            return checksum == int(formatted[12])
            
        except:
            return False

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    generator = PromptPayGenerator()
    
    # ทดสอบเบอร์โทรศัพท์
    phone = "0812345678"
    amount = 150.50
    
    print(f"Testing phone: {phone}")
    print(f"Valid phone: {generator.validate_phone_number(phone)}")
    
    qr_code = generator.generate_qr(phone, amount, "phone")
    print(f"QR Code generated: {len(qr_code) > 0}")
    
    # ทดสอบเลขบัตรประชาชน
    citizen_id = "1234567890123"
    print(f"\nTesting citizen ID: {citizen_id}")
    print(f"Valid citizen ID: {generator.validate_citizen_id(citizen_id)}")
    
    # ทดสอบ payload
    payload = generator.generate_promptpay_payload(phone, amount, "phone")
    print(f"\nPayload: {payload[:50]}...")