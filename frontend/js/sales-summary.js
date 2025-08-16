// ฟังก์ชันโหลดข้อมูลสรุปยอดขาย
function loadSummaryData(filterType = null, monthValue = null, startDate = null, endDate = null) {
    console.log('loadSummaryData() called with filterType:', filterType);
    let apiUrl = '/api/sales-summary';
    
    // ถ้าเป็นการกรองตามเดือน ให้เรียก API แยก
    if (filterType === 'monthly' && monthValue) {
        const [year, month] = monthValue.split('-');
        apiUrl = `/api/sales-summary/monthly?year=${year}&month=${month}`;
    }
    // ถ้าเป็นการกรองตามช่วงวันที่กำหนดเอง
    else if (filterType === 'custom' && (startDate || endDate)) {
        const params = new URLSearchParams();
        if (startDate) params.append('startDate', startDate);
        if (endDate) params.append('endDate', endDate);
        apiUrl = `/api/sales-summary/custom?${params.toString()}`;
    }
    
    console.log('About to fetch API:', apiUrl);
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let totalSales = 0;
            let totalSessions = 0;
            let totalOrders = 0;
            
            if (filterType === 'monthly' && monthValue) {
                // ข้อมูลรายเดือน
                totalSales = data.total || 0;
                totalSessions = data.sessions || 0;
                totalOrders = data.orders || 0;
            } else if (filterType === 'custom') {
                // ข้อมูลช่วงวันที่กำหนดเอง
                totalSales = data.total || 0;
                totalSessions = data.sessions || 0;
                totalOrders = data.orders || 0;
            } else if (filterType) {
                // Calculate totals based on filter type
                if (filterType === 'today') {
                    totalSales = data.today.total;
                    totalSessions = data.today.sessions;
                    totalOrders = data.today.orders;
                } else if (filterType === 'week7') {
                    totalSales = data.week7.total;
                    totalSessions = data.week7.sessions;
                    totalOrders = data.week7.orders;
                } else if (filterType === 'month30') {
                    totalSales = data.month30.total;
                    totalSessions = data.month30.sessions;
                    totalOrders = data.month30.orders;
                } else if (filterType === 'allTime') {
                    totalSales = data.allTime.total;
                    totalSessions = data.allTime.sessions;
                    totalOrders = data.allTime.orders;
                }
            } else {
                // Calculate totals for all time (default view)
                totalSales = data.allTime.total;
                totalSessions = data.allTime.sessions;
                totalOrders = data.allTime.orders;
            }
            
            // Show summary section
            const summarySectionContainer = document.getElementById('summarySectionContainer');
            if (summarySectionContainer) {
                summarySectionContainer.style.display = 'block';
            }
            
            // Update the three summary cards (ไม่อัปเดต today-sales เพื่อป้องกันการเขียนทับจาก dashboard-enhanced.js)
            const totalSummaryEl = document.getElementById('totalSummary');
            const totalSessionsEl = document.getElementById('totalSessions');
            const totalOrdersEl = document.getElementById('totalOrders');
            
            if (totalSummaryEl) totalSummaryEl.textContent = formatCurrency(totalSales);
            if (totalSessionsEl) totalSessionsEl.textContent = totalSessions;
            if (totalOrdersEl) totalOrdersEl.textContent = totalOrders;
            
            // หมายเหตุ: ไม่อัปเดต today-sales element เพื่อให้ dashboard-enhanced.js จัดการเอง
            console.log('Updated sales summary cards (excluding today-sales):', formatCurrency(totalSales));
        })
        .catch(error => {
            console.error('Error loading sales summary:', error);
        });
}

// ฟังก์ชันจัดรูปแบบสกุลเงิน
function formatCurrency(amount) {
    return new Intl.NumberFormat('th-TH', {
        style: 'currency',
        currency: 'THB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}