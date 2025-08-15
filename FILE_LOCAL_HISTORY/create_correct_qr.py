#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def calculate_crc16(data):
    """Calculate CRC16 for EMV QR Code using CRC-CCITT"""
    crc = 0xFFFF
    for char in data:
        byte = ord(char)
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f"{crc:04X}"

def format_tag(tag, value):
    """Format EMV tag with length"""
    return f"{tag}{len(value):02d}{value}"

def generate_promptpay_payload(phone_number, amount=None):
    """Generate PromptPay QR code payload"""
    # Format phone number (remove leading 0, add 66)
    if phone_number.startswith('0'):
        formatted_phone = '66' + phone_number[1:]
    else:
        formatted_phone = phone_number
    
    # Build payload components
    payload_format = format_tag("00", "01")  # Payload Format Indicator
    poi_method = format_tag("01", "11")      # Point of Initiation Method (Static)
    
    # Merchant Account Information (Tag 29)
    aid = "A000000677010111"  # PromptPay AID
    merchant_aid = format_tag("00", aid)
    merchant_id = format_tag("01", formatted_phone)
    merchant_info = format_tag("29", merchant_aid + merchant_id)
    
    # Transaction details
    currency = format_tag("53", "764")      # Thai Baht
    country = format_tag("58", "TH")        # Thailand
    
    # Build payload without CRC
    payload_parts = [payload_format, poi_method, merchant_info, currency]
    
    # Add amount if specified
    if amount is not None:
        amount_str = f"{float(amount):.2f}"
        amount_tag = format_tag("54", amount_str)
        payload_parts.append(amount_tag)
    
    payload_parts.append(country)
    
    # Join all parts
    payload_without_crc = "".join(payload_parts)
    
    # Add CRC placeholder and calculate
    payload_with_crc_placeholder = payload_without_crc + "6304"
    crc = calculate_crc16(payload_without_crc + "6304")
    
    # Final payload
    final_payload = payload_without_crc + format_tag("63", crc)
    
    return final_payload

def analyze_payload(payload):
    """Analyze and display payload structure"""
    print(f"\nPayload: {payload}")
    print(f"Length: {len(payload)}")
    print("\nStructure:")
    
    i = 0
    while i < len(payload):
        if i + 4 > len(payload):
            break
            
        tag = payload[i:i+2]
        length = int(payload[i+2:i+4])
        
        if i + 4 + length > len(payload):
            break
            
        value = payload[i+4:i+4+length]
        
        print(f"  Tag {tag}: {value} (length: {length})")
        
        if tag == "29":  # Merchant info
            print("    Merchant Account Information:")
            j = 0
            while j < len(value):
                if j + 4 > len(value):
                    break
                sub_tag = value[j:j+2]
                sub_length = int(value[j+2:j+4])
                if j + 4 + sub_length > len(value):
                    break
                sub_value = value[j+4:j+4+sub_length]
                print(f"      Sub-tag {sub_tag}: {sub_value} (length: {sub_length})")
                j += 4 + sub_length
        
        i += 4 + length

if __name__ == "__main__":
    print("=== PromptPay QR Code Generator ===")
    
    # Test cases
    test_cases = [
        {"phone": "0812345678", "amount": None, "description": "Phone without amount"},
        {"phone": "0812345678", "amount": 100.00, "description": "Phone with 100 Baht"},
        {"phone": "0812345678", "amount": 50.50, "description": "Phone with 50.50 Baht"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}: {test['description']}")
        print(f"{'='*60}")
        
        payload = generate_promptpay_payload(test['phone'], test['amount'])
        analyze_payload(payload)
        
        # Validate CRC
        provided_crc = payload[-4:]
        data_without_crc = payload[:-4]
        calculated_crc = calculate_crc16(data_without_crc + "6304")
        
        print(f"\nCRC Validation:")
        print(f"  Provided: {provided_crc}")
        print(f"  Calculated: {calculated_crc}")
        print(f"  Valid: {'✅ Yes' if provided_crc == calculated_crc else '❌ No'}")
    
    print(f"\n{'='*60}")
    print("COMPARISON WITH CURRENT CODE")
    print(f"{'='*60}")
    
    # Compare with current implementation
    print("\nCurrent code structure (from backend/utils/promptpay.py):")
    print("- Uses hardcoded AID length: 0016")
    print("- Phone format: 66 + phone[1:] (removes leading 0)")
    print("- Amount format: {amount:.2f}")
    print("\nGenerated payload structure:")
    print("- Uses calculated AID length: 0016 (16 chars)")
    print("- Same phone format")
    print("- Same amount format")
    print("\nThe structures should be identical!")