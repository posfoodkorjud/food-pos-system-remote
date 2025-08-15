# -*- coding: utf-8 -*-
"""
Data Models สำหรับระบบ POS ร้านอาหาร
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

class Table:
    """โมเดลสำหรับโต๊ะ"""
    def __init__(self, table_id: int, table_name: str = None):
        self.table_id = table_id
        self.table_name = table_name or f"โต๊ะ {table_id}"
        self.status = "available"  # available, occupied, calling, needs_checkout, waiting_payment, checkout, needs_clearing
        self.qr_code = None
        self.session_id = None
        self.created_at = datetime.now(timezone(timedelta(hours=7)))
        self.updated_at = datetime.now(timezone(timedelta(hours=7)))
    
    def to_dict(self) -> Dict:
        return {
            'table_id': self.table_id,
            'table_name': self.table_name,
            'status': self.status,
            'qr_code': self.qr_code,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MenuCategory:
    """โมเดลสำหรับหมวดหมู่เมนู"""
    def __init__(self, category_id: int, name: str, description: str = ""):
        self.category_id = category_id
        self.name = name
        self.description = description
        self.is_active = True
        self.created_at = datetime.now(timezone(timedelta(hours=7)))
    
    def to_dict(self) -> Dict:
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class MenuItem:
    """โมเดลสำหรับรายการเมนูอาหาร"""
    def __init__(self, item_id: int, name: str, price: float, category_id: int):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.category_id = category_id
        self.description = ""
        self.image_url = ""
        self.is_available = True
        self.preparation_time = 15  # นาที
        self.created_at = datetime.now(timezone(timedelta(hours=7)))
        self.updated_at = datetime.now(timezone(timedelta(hours=7)))
    
    def to_dict(self) -> Dict:
        return {
            'item_id': self.item_id,
            'name': self.name,
            'price': self.price,
            'category_id': self.category_id,
            'description': self.description,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'preparation_time': self.preparation_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class OrderItem:
    """โมเดลสำหรับรายการสั่งอาหาร"""
    def __init__(self, order_item_id: int, order_id: int, item_id: int, quantity: int, unit_price: float):
        self.order_item_id = order_item_id
        self.order_id = order_id
        self.item_id = item_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = quantity * unit_price
        self.customer_request = ""
        self.status = "pending"  # pending, preparing, ready, served
        self.created_at = datetime.now(timezone(timedelta(hours=7)))
    
    def to_dict(self) -> Dict:
        return {
            'order_item_id': self.order_item_id,
            'order_id': self.order_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'customer_request': self.customer_request,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Order:
    """โมเดลสำหรับออเดอร์"""
    def __init__(self, order_id: int, table_id: int, session_id: str):
        self.order_id = order_id
        self.table_id = table_id
        self.session_id = session_id
        self.status = "active"  # active, completed, cancelled
        self.total_amount = 0.0
        self.order_items: List[OrderItem] = []
        self.created_at = datetime.now(timezone(timedelta(hours=7)))
        self.updated_at = datetime.now(timezone(timedelta(hours=7)))
        self.completed_at = None
    
    def add_item(self, item: OrderItem):
        """เพิ่มรายการอาหารในออเดอร์"""
        self.order_items.append(item)
        self.calculate_total()
    
    def calculate_total(self):
        """คำนวณยอดรวม (ไม่รวมรายการที่ถูก reject)"""
        self.total_amount = sum(item.total_price for item in self.order_items if item.status != 'rejected')
        self.updated_at = datetime.now(timezone(timedelta(hours=7)))
    
    def to_dict(self) -> Dict:
        return {
            'order_id': self.order_id,
            'table_id': self.table_id,
            'session_id': self.session_id,
            'status': self.status,
            'total_amount': self.total_amount,
            'order_items': [item.to_dict() for item in self.order_items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class Receipt:
    """โมเดลสำหรับใบเสร็จ"""
    def __init__(self, receipt_id: int, order_id: int, table_id: int):
        self.receipt_id = receipt_id
        self.order_id = order_id
        self.table_id = table_id
        self.total_amount = 0.0
        self.payment_method = "promptpay"
        self.promptpay_qr = ""
        self.is_paid = False
        self.created_at = datetime.now(timezone(timedelta(hours=7)))
        self.paid_at = None
    
    def to_dict(self) -> Dict:
        return {
            'receipt_id': self.receipt_id,
            'order_id': self.order_id,
            'table_id': self.table_id,
            'total_amount': self.total_amount,
            'payment_method': self.payment_method,
            'promptpay_qr': self.promptpay_qr,
            'is_paid': self.is_paid,
            'created_at': self.created_at.isoformat(),
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }

class SystemConfig:
    """โมเดลสำหรับการตั้งค่าระบบ"""
    def __init__(self):
        self.restaurant_name = "ร้านอาหารนั่งชิลล์"
        self.restaurant_address = ""
        self.restaurant_phone = ""
        self.promptpay_id = ""
        self.promptpay_type = "phone"  # phone, citizen_id
        self.google_sheet_id = ""
        self.google_sheet_name = "ยอดขาย"
        self.domain_url = "http://localhost:5000"
        self.printer_name = ""
        self.tax_rate = 0.0
        self.service_charge = 0.0
        self.updated_at = datetime.now(timezone(timedelta(hours=7)))
    
    def to_dict(self) -> Dict:
        return {
            'restaurant_name': self.restaurant_name,
            'restaurant_address': self.restaurant_address,
            'restaurant_phone': self.restaurant_phone,
            'promptpay_id': self.promptpay_id,
            'promptpay_type': self.promptpay_type,
            'google_sheet_id': self.google_sheet_id,
            'google_sheet_name': self.google_sheet_name,
            'domain_url': self.domain_url,
            'printer_name': self.printer_name,
            'tax_rate': self.tax_rate,
            'service_charge': self.service_charge,
            'updated_at': self.updated_at.isoformat()
        }