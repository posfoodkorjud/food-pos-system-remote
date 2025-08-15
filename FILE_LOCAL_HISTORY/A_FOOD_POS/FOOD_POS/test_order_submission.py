import requests
import json

# ทดสอบการส่งข้อมูลออเดอร์ที่มีตัวเลือกพิเศษ
def test_order_with_special_options():
    url = 'http://localhost:5000/api/orders'
    
    # ข้อมูลทดสอบ - สั่งข้าวกะเพราหมูสับ พร้อมไข่ดาว
    order_data = {
        'table_id': 1,
        'items': [{
            'item_id': 859,  # ข้าวกะเพราหมูสับ
            'quantity': 1,
            'price': 69,  # ราคารวมไข่ดาว (59 + 10)
            'selected_option': 'ไข่ดาว (+10฿)',
            'note': 'ทดสอบหมายเหตุ'
        }]
    }
    
    print("=== ทดสอบการส่งข้อมูลออเดอร์ ===")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=order_data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ การส่งข้อมูลสำเร็จ!")
            else:
                print(f"❌ เกิดข้อผิดพลาด: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")

if __name__ == '__main__':
    test_order_with_special_options()