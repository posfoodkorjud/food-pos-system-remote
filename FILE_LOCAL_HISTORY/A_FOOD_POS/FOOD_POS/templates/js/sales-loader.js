// Sales Loader - โหลดยอดขายทันทีเมื่อหน้าเว็บโหลด
console.log('=== SALES LOADER SCRIPT LOADED ===');

// ฟังก์ชันโหลดยอดขาย
function loadSalesDataImmediate() {
    console.log('=== LOADING SALES DATA IMMEDIATELY ===');
    
    fetch('/api/sales-summary', {
        method: 'GET',
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    })
    .then(response => {
        console.log('Sales API Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Sales API call result:', data);
        
        if (data.success) {
            // อัปเดตยอดขายวันนี้
            if (data.today && data.today.total !== undefined) {
                const todaySalesEl = document.getElementById('today-sales');
                if (todaySalesEl) {
                    const newValue = `฿${(data.today.total || 0).toLocaleString()}`;
                    console.log('Updating today sales to:', newValue);
                    todaySalesEl.textContent = newValue;
                } else {
                    console.log('today-sales element not found');
                }
            }
            
            // อัปเดตยอดขายสัปดาห์
            if (data.week7 && data.week7.total !== undefined) {
                const weekSalesEl = document.getElementById('week-sales');
                if (weekSalesEl) {
                    const newValue = `฿${(data.week7.total || 0).toLocaleString()}`;
                    console.log('Updating week sales to:', newValue);
                    weekSalesEl.textContent = newValue;
                }
            }
            
            // อัปเดตยอดขายเดือน
            if (data.month30 && data.month30.total !== undefined) {
                const monthSalesEl = document.getElementById('month-sales');
                if (monthSalesEl) {
                    const newValue = `฿${(data.month30.total || 0).toLocaleString()}`;
                    console.log('Updating month sales to:', newValue);
                    monthSalesEl.textContent = newValue;
                }
            }
            
            // อัปเดตจำนวนลูกค้าทั้งหมด
            if (data.allTime && data.allTime.total !== undefined) {
                const totalCustomersEl = document.getElementById('total-customers');
                if (totalCustomersEl) {
                    const newValue = (data.allTime.total || 0).toLocaleString();
                    console.log('Updating total customers to:', newValue);
                    totalCustomersEl.textContent = newValue;
                }
            }
            
            console.log('=== SALES DATA UPDATE COMPLETED ===');
        } else {
            console.error('Sales API returned success: false');
        }
    })
    .catch(error => {
        console.error('Sales API call error:', error);
    });
}

// เรียกใช้ทันทีเมื่อ DOM โหลดเสร็จ
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadSalesDataImmediate);
} else {
    // DOM โหลดเสร็จแล้ว เรียกทันที
    loadSalesDataImmediate();
}

// เรียกใช้อีกครั้งหลังจาก 1 วินาที เพื่อให้แน่ใจ
setTimeout(loadSalesDataImmediate, 1000);

console.log('=== SALES LOADER SCRIPT SETUP COMPLETED ===');