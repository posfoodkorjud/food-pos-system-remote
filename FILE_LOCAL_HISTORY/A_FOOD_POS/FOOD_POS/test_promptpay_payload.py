#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.promptpay import PromptPayGenerator

def test_promptpay_payload():
    """ทดสอบการสร้าง PromptPay payload"""
    print("=== ทดสอบการสร้าง PromptPay Payload ===")
    
    promptpay_gen = PromptPayGenerator()
    
    # ทดสอบกับเบอร์โทร 0906016218 และจำนวน 100 บาท
    phone = "0906016218"
    amount = 100.0
    
    print(f"เบอร์โทร: {phone}")
    print(f"จำนวนเงิน: {amount} บาท")
    
    try:
        # สร้าง payload
        payload = promptpay_gen.generate_promptpay_payload(phone, amount, "phone")
        print(f"\nPromptPay Payload: {payload}")
        print(f"ความยาว Payload: {len(payload)} ตัวอักษร")
        
        # แยกวิเคราะห์ payload
        print("\n=== การวิเคราะห์ Payload ===")
        
        # Payload Format Indicator (00)
        pfi = payload[0:6]
        print(f"Payload Format Indicator: {pfi}")
        
        # Point of Initiation Method (01)
        pim = payload[6:12]
        print(f"Point of Initiation Method: {pim}")
        
        # Merchant Account Information (29)
        mai_start = payload.find('29')
        if mai_start != -1:
            mai_length = int(payload[mai_start+2:mai_start+4])
            mai = payload[mai_start:mai_start+4+mai_length]
            print(f"Merchant Account Information: {mai}")
        
        # Transaction Currency (53)
        tc_start = payload.find('5303')
        if tc_start != -1:
            tc = payload[tc_start:tc_start+6]
            print(f"Transaction Currency: {tc}")
        
        # Transaction Amount (54)
        ta_start = payload.find('54')
        if ta_start != -1 and payload[ta_start+2:ta_start+4].isdigit():
            ta_length = int(payload[ta_start+2:ta_start+4])
            ta = payload[ta_start:ta_start+4+ta_length]
            print(f"Transaction Amount: {ta}")
        
        # Country Code (58)
        cc_start = payload.find('5802')
        if cc_start != -1:
            cc = payload[cc_start:cc_start+6]
            print(f"Country Code: {cc}")
        
        # CRC (63)
        crc_start = payload.find('6304')
        if crc_start != -1:
            crc = payload[crc_start:crc_start+8]
            print(f"CRC: {crc}")
        
        # ตรวจสอบ CRC
        payload_without_crc = payload[:-4]
        calculated_crc = promptpay_gen._calculate_crc16(payload_without_crc)
        actual_crc = payload[-4:]
        print(f"\nCRC ที่คำนวณได้: {calculated_crc}")
        print(f"CRC ใน payload: {actual_crc}")
        print(f"CRC ถูกต้อง: {'✅' if calculated_crc == actual_crc else '❌'}")
        
        # ตัวอย่าง payload ที่ถูกต้องสำหรับเปรียบเทียบ
        print("\n=== เปรียบเทียบกับตัวอย่างมาตรฐาน ===")
        print("ตัวอย่าง PromptPay payload ที่ถูกต้อง:")
        print("00020101021229370016A000000677010111011066906016218530376454061005802TH6304xxxx")
        print(f"Payload ที่สร้าง:                    {payload}")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_promptpay_payload()