import sys
sys.path.append('C:\\Users\\KORJUD\\Desktop\\A_FOOD_POS4\\A_FOOD_POS\\FOOD_POS')

from backend.database import DatabaseManager
from datetime import date

db = DatabaseManager()
today = date.today().strftime('%Y-%m-%d')
print(f'วันนี้: {today}')

# ดึงข้อมูลออเดอร์วันนี้
orders = db.get_orders_by_date_range(today, today)
print(f'จำนวนออเดอร์ทั้งหมด: {len(orders)}')

# แสดงรายละเอียดออเดอร์
total_all = 0
total_non_rejected = 0
rejected_count = 0

for order in orders:
    order_id = order.get('order_id')
    status = order.get('status')
    amount = order.get('total_amount', 0)
    
    print(f'Order {order_id}: status={status}, amount={amount}')
    
    total_all += amount
    
    if status == 'rejected':
        rejected_count += 1
    else:
        total_non_rejected += amount

print(f'\n=== สรุป ===')
print(f'ยอดขายรวมทั้งหมด: {total_all} บาท')
print(f'ยอดขายรวม (ไม่รวม rejected): {total_non_rejected} บาท')
print(f'จำนวนออเดอร์ที่ rejected: {rejected_count}')
print(f'จำนวนออเดอร์ที่ไม่ rejected: {len(orders) - rejected_count}')