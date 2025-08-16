// Admin Panel JavaScript
console.log('=== admin.js loaded successfully ===');

// Global variables
let currentSection = 'dashboard';
let tables = [];
let menuCategories = [];
let menuItems = [];
let orders = [];
let notifications = [];
let selectedTableId = null;
let lastOrderCount = 0;
let notificationSound = null;
let currentCategory = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadTables();
    loadMenuCategories();
    loadMenuItems();
    loadOrders();
    loadSettings();
    
    // Load dashboard data if on dashboard page
    if (typeof loadDashboard === 'function') {
        loadDashboard();
    }
    
    // ล้าง localStorage และ processedNotifications เมื่อโหลดหน้าใหม่
    localStorage.removeItem('newNotification');
    processedNotifications.clear();
    
    // Load existing notifications
    checkForNewNotifications();
    
    // Setup notification sound
    setupNotificationSound();
    
    // Setup auto-refresh with order checking (ลบการเรียก checkForNewNotifications ออกจาก checkForNewOrders)
    setInterval(checkForNewOrders, 5000); // Check every 5 seconds
    setInterval(refreshData, 30000); // Refresh all data every 30 seconds
    
    // เริ่มต้น notification polling แยกต่างหาก
    startNotificationPolling();
    
    // Setup form handlers
    setupFormHandlers();
    
    // Check server status
    checkServerStatus();
});

// Utility Functions
function showLoading(show = true) {
    const spinner = document.getElementById('loading-spinner');
    if (show) {
        spinner.classList.remove('d-none');
        spinner.style.display = 'block';
    } else {
        spinner.classList.add('d-none');
        spinner.style.display = 'none';
        // ลบ backdrop ที่อาจค้างอยู่
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        // ลบ class modal-open จาก body
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }
}

function hideLoading() {
    showLoading(false);
}

function showAlert(message, type = 'info') {
    // Convert to modal notification
    showNotificationModal(message, type);
}

// ฟังก์ชัน modal ใหม่สำหรับการแจ้งเตือน
function showNotificationModal(message, type = 'info') {
    // กำหนดสีและไอคอนตามประเภท
    let headerClass, iconClass, title;
    
    switch(type) {
        case 'success':
            headerClass = 'bg-success text-white';
            iconClass = 'fas fa-check-circle text-success';
            title = 'สำเร็จ!';
            break;
        case 'error':
        case 'danger':
            headerClass = 'bg-danger text-white';
            iconClass = 'fas fa-exclamation-triangle text-danger';
            title = 'เกิดข้อผิดพลาด!';
            break;
        case 'warning':
            headerClass = 'bg-warning text-dark';
            iconClass = 'fas fa-exclamation-triangle text-warning';
            title = 'คำเตือน!';
            break;
        default:
            headerClass = 'bg-info text-white';
            iconClass = 'fas fa-info-circle text-info';
            title = 'แจ้งเตือน';
    }
    
    // สร้าง modal element
    const modalHtml = `
        <div class="modal fade" id="adminNotificationModal" tabindex="-1" aria-labelledby="adminNotificationModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header ${headerClass}">
                        <h5 class="modal-title" id="adminNotificationModalLabel">
                            <i class="${iconClass.split(' ')[0]} ${iconClass.split(' ')[1]} me-2"></i>${title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-3">
                            <i class="${iconClass}" style="font-size: 3rem;"></i>
                        </div>
                        <h4>${message}</h4>
                        <p class="text-muted">หน้าต่างนี้จะปิดอัตโนมัติใน <span id="adminNotificationCountdown">3</span> วินาที</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่า (ถ้ามี)
    const existingModal = document.getElementById('adminNotificationModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal เข้าไปใน body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('adminNotificationModal'));
    modal.show();
    
    // นับถอยหลัง 3 วินาที
    let countdown = 3;
    const countdownElement = document.getElementById('adminNotificationCountdown');
    
    const countdownInterval = setInterval(() => {
        countdown--;
        if (countdownElement) {
            countdownElement.textContent = countdown;
        }
        
        if (countdown <= 0) {
            clearInterval(countdownInterval);
            modal.hide();
            
            // ลบ modal ออกจาก DOM หลังจากปิด
            setTimeout(() => {
                const modalElement = document.getElementById('adminNotificationModal');
                if (modalElement) {
                    modalElement.remove();
                }
            }, 300);
        }
    }, 1000);
}

function formatCurrency(amount) {
    return `฿${parseFloat(amount).toFixed(2)}`;
}

// formatDateTime function is now imported from date-config.js

// Navigation
function showSection(sectionName, event = null) {
    console.log('showSection() called with:', sectionName);
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.add('d-none');
    });
    
    // Show selected section
    document.getElementById(`${sectionName}-section`).classList.remove('d-none');
    
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to clicked nav link or find the corresponding nav link
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        // Find the nav link for this section and make it active
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            if (link.getAttribute('onclick') && link.getAttribute('onclick').includes(`'${sectionName}'`)) {
                link.classList.add('active');
            }
        });
    }
    currentSection = sectionName;
    
    // Load section-specific data
    switch(sectionName) {
        case 'dashboard':
            console.log('=== Dashboard case reached ===');
            // Load dashboard data if the function exists
            if (typeof loadDashboard === 'function') {
        console.log('loadDashboard function exists, calling it');
        loadDashboard();
        
        // ตั้งค่า interval สำหรับ dashboard (ทุก 30 วินาที)
        if (dashboardInterval) {
            clearInterval(dashboardInterval);
        }
        dashboardInterval = setInterval(() => {
            if (currentSection === 'dashboard') {
                loadDashboard();
            }
        }, 30000);
    } else {
        console.log('loadDashboard function does not exist');
    }
            break;
        case 'tables':
            // หยุด dashboard interval เมื่อเปลี่ยนไปส่วนอื่น
            if (dashboardInterval) {
                clearInterval(dashboardInterval);
                dashboardInterval = null;
            }
            refreshTables();
            break;
        case 'menu':
            // หยุด dashboard interval เมื่อเปลี่ยนไปส่วนอื่น
            if (dashboardInterval) {
                clearInterval(dashboardInterval);
                dashboardInterval = null;
            }
            refreshMenu();
            loadOptionTypes(); // Load option types when menu section is shown
            break;
        case 'orders':
            // หยุด dashboard interval เมื่อเปลี่ยนไปส่วนอื่น
            if (dashboardInterval) {
                clearInterval(dashboardInterval);
                dashboardInterval = null;
            }
            refreshOrders();
            break;
        case 'settings':
            // หยุด dashboard interval เมื่อเปลี่ยนไปส่วนอื่น
            if (dashboardInterval) {
                clearInterval(dashboardInterval);
                dashboardInterval = null;
            }
            loadSettings();
            break;
    }
}

// Dashboard Functions
let salesChart = null;
let categoryChart = null;
let dashboardInterval = null;
let isDashboardLoading = false;

async function loadDashboard() {
    console.log('loadDashboard() called');
    
    // ป้องกันการเรียกใช้ซ้ำขณะกำลังโหลด
    if (isDashboardLoading) {
        console.log('Dashboard is already loading, skipping...');
        return;
    }
    
    isDashboardLoading = true;
    
    try {
        showLoading();
        await Promise.all([
            loadSalesSummary(),
            loadSalesChart(),
            loadTopItems(),
            loadCategoryChart()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showAlert('เกิดข้อผิดพลาดในการโหลดข้อมูลแดชบอร์ด', 'danger');
    } finally {
        hideLoading();
        isDashboardLoading = false;
    }
}

let isSalesSummaryLoading = false;

async function loadSalesSummary() {
    console.log('=== loadSalesSummary() called ===');
    
    // ป้องกันการเรียกใช้ซ้ำขณะกำลังโหลด
    if (isSalesSummaryLoading) {
        console.log('Sales summary is already loading, skipping...');
        return;
    }
    
    isSalesSummaryLoading = true;
    
    try {
        console.log('Fetching /api/sales-summary...');
        
        // เพิ่มการรอเพื่อให้แน่ใจว่าเซิร์ฟเวอร์พร้อม
        const response = await fetch('/api/sales-summary', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Sales summary data received:', data);
        
        if (data.success && data.data) {
            console.log('Updating sales summary with valid data...');
            
            const summary = data.data;
            
            // Update summary cards - ใช้โครงสร้างข้อมูลจาก API ที่ถูกต้อง
            const todaySalesEl = document.getElementById('today-sales');
            const weekSalesEl = document.getElementById('week-sales');
            const monthSalesEl = document.getElementById('month-sales');
            const totalCustomersEl = document.getElementById('total-customers');
            
            // หมายเหตุ: ไม่อัปเดต today-sales element เพื่อป้องกันการขัดแย้งกับ dashboard-enhanced.js
            // dashboard-enhanced.js จะจัดการ today-sales element เอง
            console.log('=== SKIPPING TODAY SALES UPDATE (handled by dashboard-enhanced.js) ===');
            console.log('Data.today.total:', summary.today.total);
            
            if (weekSalesEl) {
                const newValue = `฿${(summary.week.total || 0).toLocaleString()}`;
                console.log('Updating week sales:', newValue);
                weekSalesEl.textContent = newValue;
            }
            
            if (monthSalesEl) {
                const newValue = `฿${(summary.month.total || 0).toLocaleString()}`;
                console.log('Updating month sales:', newValue);
                monthSalesEl.textContent = newValue;
            }
            
            // หมายเหตุ: ไม่อัปเดต today-orders, total-orders, total-customers เพื่อป้องกันการขัดแย้งกับ dashboard-enhanced.js
            // dashboard-enhanced.js จะจัดการ elements เหล่านี้เอง
            console.log('=== SKIPPING ORDERS/CUSTOMERS UPDATE (handled by dashboard-enhanced.js) ===');
            console.log('Data.today.orders:', summary.today.orders);
            console.log('Data.total.total:', summary.total.total);
            
            // Update additional stats
            
            console.log('Sales summary updated successfully');
        } else {
            console.error('Invalid data structure received:', data);
        }
    } catch (error) {
        console.error('Error loading sales summary:', error);
        // ไม่แสดงค่า 0 เมื่อเกิด error เพื่อป้องกันการกระพริบ
        // แทนที่จะแสดงข้อความ error หรือเก็บค่าเดิมไว้
        console.log('Keeping existing values due to API error');
    } finally {
        isSalesSummaryLoading = false;
    }
}

async function loadSalesChart(days = 7) {
    try {
        const response = await fetch(`/api/sales-chart?days=${days}`);
        const data = await response.json();
        
        if (data.success) {
            updateSalesChart(data.data);
        } else {
            // สร้างข้อมูลจำลองหาก API ไม่สำเร็จ
            createDummyChartData(days);
        }
    } catch (error) {
        console.error('Error loading sales chart:', error);
        // สร้างข้อมูลจำลองหาก API ล้มเหลว
        createDummyChartData(days);
    }
}

function createDummyChartData(days = 7) {
    const dummyData = {
        labels: [],
        sales: []
    };
    
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dummyData.labels.push(date.toLocaleDateString('th-TH', { timeZone: 'Asia/Bangkok', month: 'short', day: 'numeric' }));
        dummyData.sales.push(Math.random() * 5000 + 1000); // ข้อมูลจำลองระหว่าง 1000-6000
    }
    
    updateSalesChart(dummyData);
}

function updateSalesChart(data) {
    const ctx = document.getElementById('salesChart').getContext('2d');
    
    if (salesChart) {
        salesChart.destroy();
    }
    
    // ตรวจสอบว่ามีข้อมูลหรือไม่
    if (!data || !data.labels || !data.sales) {
        console.error('Invalid chart data provided');
        return;
    }
    
    salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'ยอดขาย (฿)',
                data: data.sales,
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '฿' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

async function loadTopItems() {
    try {
        const response = await fetch('/api/top-items?limit=5');
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            displayTopItems(data.data);
        } else {
            // Show dummy data
            const dummyItems = [
                { name: 'ข้าวผัดกุ้ง', quantity: 25, total: 3750 },
                { name: 'ต้มยำกุ้ง', quantity: 20, total: 3200 },
                { name: 'ผัดไทย', quantity: 18, total: 2700 },
                { name: 'ส้มตำ', quantity: 15, total: 1800 },
                { name: 'แกงเขียวหวาน', quantity: 12, total: 2400 }
            ];
            displayTopItems(dummyItems);
        }
    } catch (error) {
        console.error('Error loading top items:', error);
        document.getElementById('top-items-list').innerHTML = '<p class="text-muted text-center">ไม่สามารถโหลดข้อมูลได้</p>';
    }
}

function displayTopItems(items) {
    const container = document.getElementById('top-items-list');
    
    container.innerHTML = items.map((item, index) => `
        <div class="top-item">
            <div class="item-rank">${index + 1}</div>
            <div class="item-info">
                <div class="item-name">${item.name}</div>
                <div class="item-sales">ขายได้ ${item.quantity} จาน</div>
            </div>
            <div class="item-amount">฿${(item.total || item.sales || 0).toLocaleString()}</div>
        </div>
    `).join('');
}

async function loadCategoryChart() {
    try {
        const response = await fetch('/api/category-chart');
        const data = await response.json();
        
        if (data.success) {
            updateCategoryChart(data.data);
        } else {
            // Show dummy data
            const dummyData = [
                { category: 'อาหารหลัก', total: 15000 },
                { category: 'เครื่องดื่ม', total: 8000 },
                { category: 'ของหวาน', total: 5000 },
                { category: 'อาหารทานเล่น', total: 3000 }
            ];
            updateCategoryChart(dummyData);
        }
    } catch (error) {
        console.error('Error loading category chart:', error);
        // Show dummy data on error
        const dummyData = [
            { category: 'อาหารหลัก', total: 15000 },
            { category: 'เครื่องดื่ม', total: 8000 },
            { category: 'ของหวาน', total: 5000 },
            { category: 'อาหารทานเล่น', total: 3000 }
        ];
        updateCategoryChart(dummyData);
    }
}

function updateCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    const colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'];
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.category),
            datasets: [{
                data: data.map(item => item.total),
                backgroundColor: colors.slice(0, data.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ฿${value.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Chart update function for period change
function changeSalesChartPeriod() {
    const days = parseInt(document.getElementById('chart-period').value);
    loadSalesChart(days);
}

// Server Status
async function checkServerStatus() {
    try {
        console.log('Checking server status...');
        const response = await fetch('/api/status');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        const statusElement = document.getElementById('server-status');
        const statusIcon = statusElement.previousElementSibling;
        
        if (data.success) {
            statusElement.textContent = 'เซิร์ฟเวอร์ออนไลน์';
            statusIcon.className = 'fas fa-circle text-success me-1';
            console.log('Server status updated to online');
        } else {
            throw new Error('Server error: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Server status check failed:', error);
        const statusElement = document.getElementById('server-status');
        const statusIcon = statusElement.previousElementSibling;
        
        statusElement.textContent = 'เซิร์ฟเวอร์ออฟไลน์';
        statusIcon.className = 'fas fa-circle text-danger me-1';
    }
}

// Tables Management
async function loadTables() {
    try {
        // เพิ่ม cache busting parameter เพื่อป้องกันการ cache
        const timestamp = new Date().getTime();
        const response = await fetch(`/api/tables?_t=${timestamp}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // API ส่งข้อมูลเป็น array โดยตรง
        tables = Array.isArray(data) ? data : [];
        
        // โหลดข้อมูลรายการอาหารสำหรับแต่ละโต๊ะที่มี session_id
        for (let table of tables) {
            if (table.session_id) {
                try {
                    const orderResponse = await fetch(`/api/tables/${table.table_id}/orders?session_id=${table.session_id}&_t=${timestamp}`);
                    if (orderResponse.ok) {
                        const orderData = await orderResponse.json();
                        if (orderData.success && orderData.data.orders) {
                            table.order_count = orderData.data.orders.length;
                        } else {
                            table.order_count = 0;
                        }
                    } else {
                        table.order_count = 0;
                    }
                } catch (orderError) {
                    console.error(`Error loading orders for table ${table.table_id}:`, orderError);
                    table.order_count = 0;
                }
            } else {
                table.order_count = 0;
            }
        }
        
        renderTables();
    } catch (error) {
        console.error('Error loading tables:', error);
        showAlert('ไม่สามารถโหลดข้อมูลโต๊ะได้ กรุณารีเฟรชหน้าเว็บ', 'danger');
        tables = []; // เคลียร์ข้อมูลโต๊ะเมื่อเกิดข้อผิดพลาด
        renderTables(); // แสดงหน้าว่างเมื่อไม่มีข้อมูล
    }
}

function renderTables() {
    const container = document.getElementById('tables-grid');
    if (!container) {
        console.error('Element with id "tables-grid" not found');
        return;
    }
    container.innerHTML = '';
    
    // แสดงโต๊ะทั้งหมด
    tables.forEach(table => {
        const col = document.createElement('div');
        col.className = 'col-md-4 col-sm-6 col-12';
        
        const statusClass = getTableStatusClass(table.status);
        const statusText = getTableStatusText(table.status);
        
        col.innerHTML = `
            <div class="table-card ${statusClass}">
                <div onclick="showTableDetail(${table.table_id})" style="cursor: pointer;">
                    <div class="table-number">โต๊ะ ${table.table_id}</div>
                    <div class="table-status">${statusText}</div>
                    ${table.current_order_id ? `<div class="table-info">Order #${table.current_order_id}</div>` : ''}
                    ${table.last_activity ? `<div class="table-info">${formatDateTime(table.last_activity)}</div>` : ''}
                </div>
                <div class="table-actions mt-2">
                    ${table.status === 'available' ? 
                        `<button class="btn btn-sm btn-success" onclick="event.stopPropagation(); startTableSession(${table.table_id})" title="สร้าง QR Code">
                            <i class="fas fa-qrcode me-1"></i>สร้าง QR
                        </button>` :
                        `<button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); showTableQR(${table.table_id})" title="แสดง QR Code">
                            <i class="fas fa-qrcode"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="event.stopPropagation(); printTableQR(${table.table_id})" title="พิมพ์ QR Code">
                            <i class="fas fa-print"></i>
                        </button>
                        ${table.session_id && table.order_count > 0 ? 
                            `<button class="btn btn-sm btn-warning" onclick="event.stopPropagation(); showTableDetail(${table.table_id})" title="ตรวจสอบ">
                                ตรวจสอบ
                            </button>` :
                            `<button class="btn btn-sm btn-danger" onclick="event.stopPropagation(); closeTableSession(${table.table_id})" title="ปิดเซสชั่น">
                                ปิดเซสชั่น
                            </button>`
                        }`
                    }
                </div>
            </div>
        `;
        
        container.appendChild(col);
    });
}

function getTableStatusClass(status) {
    switch(status) {
        case 'available': return 'available';
        case 'occupied': return 'occupied';
        case 'needs_checkout': return 'needs-checkout';
        case 'waiting_payment': return 'waiting-payment';
        case 'needs_clearing': return 'needs-clearing';
        case 'calling': return 'calling';
        default: return 'available';
    }
}

function getTableStatusText(status) {
    switch(status) {
        case 'available': return 'ว่าง';
        case 'occupied': return 'มีลูกค้า';
        case 'needs_checkout': return 'รอเช็คบิล';
        case 'waiting_payment': return 'รอชำระเงิน';
        case 'needs_clearing': return 'รอเคลียร์โต๊ะ';
        case 'calling': return 'เรียกพนักงาน';
        default: return 'ไม่ทราบสถานะ';
    }
}

// ฟังก์ชันสำหรับแสดงรายละเอียดโต๊ะ (ใช้ modal เดียว)
async function showTableDetail(tableId) {
    try {
        showLoading(true);
        
        // ค้นหาข้อมูลโต๊ะเพื่อดึง session_id
        const table = tables.find(t => t.table_id === tableId);
        const session_id = table ? table.session_id : null;
        
        // เพิ่ม session_id เป็น query parameter เสมอ แม้จะเป็น null หรือ undefined
        // เพื่อให้ backend รู้ว่าต้องการดึงข้อมูลตาม session_id ปัจจุบันเท่านั้น
        const url = `/api/tables/${tableId}/orders?session_id=${session_id}`;
            
        console.log('Fetching table details with URL:', url);
        console.log('Current session_id:', session_id);
            
        const response = await fetch(url);
        const data = await response.json();
        
        // สร้างข้อมูลโต๊ะพื้นฐาน ไม่ว่า API จะสำเร็จหรือไม่
        let tableData = {
            table_id: tableId,
            table_name: `โต๊ะ ${tableId}`,
            status: table ? table.status : 'occupied',
            session_id: session_id,
            total_amount: 0,
            order_count: 0,
            orders: []
        };
        
        // ถ้า API สำเร็จ ใช้ข้อมูลจาก API แทน
        if (data.success) {
            tableData = data.data;
        } else {
            console.warn('API returned error:', data.error || 'Unknown error');
            // ไม่ throw error เพื่อให้แสดง modal ได้
        }
        
        // Debug: แสดงข้อมูลที่ได้รับจาก API
        console.log('Table data to display:', tableData);
        console.log('Table status:', tableData.status);
        
        // สร้างเนื้อหาสำหรับ modal
        let contentHtml = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <h6><i class="fas fa-table me-2"></i>${tableData.table_name}</h6>
                    <p class="mb-1"><strong>สถานะ:</strong> <span class="badge bg-${getStatusBadgeColor(tableData.status)}">${getTableStatusText(tableData.status)}</span></p>
                    ${tableData.session_id ? `<p class="mb-1"><strong>Session ID:</strong> ${tableData.session_id}</p>` : ''}
                </div>
                <div class="col-md-6 text-end">
                    <h5 class="text-primary"><strong>ยอดรวม: ฿${(tableData.total_amount !== undefined && tableData.total_amount !== null) ? tableData.total_amount.toFixed(2) : '0.00'}</strong></h5>
                    <p class="mb-0 text-muted">รายการทั้งหมด: ${tableData.order_count || 0} รายการ</p>
                </div>
            </div>
        `;
        
        if (tableData.orders && tableData.orders.length > 0) {
            contentHtml += `
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>เมนู</th>
                                <th class="text-center">สถานะ</th>
                                <th class="text-center">จำนวน</th>
                                <th class="text-end">ราคา</th>
                                <th class="text-end">รวม</th>
                                <th>หมายเหตุ</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            tableData.orders.forEach(order => {
                const statusClass = order.item_status === 'completed' ? 'completed-order' : '';
                const statusBadge = getItemStatusBadge(order.item_status);
                
                // Parse customer_request to show spice level in parentheses with menu name
                let menuDisplay = order.menu_name;
                let notesDisplay = '-';
                
                if (order.customer_request) {
                    const parts = order.customer_request.split(' | ');
                    
                    // แยกตัวเลือก spice และ addon
                    const spiceOptions = parts.filter(part => 
                        part.includes('เผ็ด') || part.includes('หวาน') || part.includes('ปกติ')
                    );
                    const addonOptions = parts.filter(part => 
                        part.includes('ไข่') || part.includes('เพิ่ม')
                    ).filter(part => !part.includes('ไม่เพิ่ม')); // กรอง "ไม่เพิ่ม" ออก
                    
                    // รวม spice options เข้ากับชื่อเมนูในวงเล็บ
                    if (spiceOptions.length > 0) {
                        menuDisplay = `${order.menu_name} <span class="${getCustomerRequestClass(spiceOptions[0])}">(${spiceOptions[0]})</span>`;
                    }
                    
                    // แสดง addon options เป็นรายการด้านล่าง (same style as main order list)
                    if (addonOptions.length > 0) {
                        const addonList = addonOptions.map(option => `<div class="text-muted small">- ${option}</div>`).join('');
                        menuDisplay += `<br>${addonList}`;
                    }
                    
                    notesDisplay = '-';
                }
                
                // Handle price display for rejected items
                let priceDisplay, totalDisplay;
                if (order.item_status === 'rejected') {
                    // Show strikethrough original price and 0.00 for rejected items
                    const originalPrice = (order.price !== undefined && order.price !== null) ? order.price.toFixed(2) : '0.00';
                    const originalTotal = (order.total !== undefined && order.total !== null) ? order.total.toFixed(2) : '0.00';
                    priceDisplay = `<span style="text-decoration: line-through; color: #6c757d;">฿${originalPrice}</span><br><span style="color: #dc3545; font-weight: bold;">฿0.00</span>`;
                    totalDisplay = `<span style="text-decoration: line-through; color: #6c757d;">฿${originalTotal}</span><br><span style="color: #dc3545; font-weight: bold;">฿0.00</span>`;
                } else {
                    // Normal price display for other statuses
                    priceDisplay = `฿${(order.price !== undefined && order.price !== null) ? order.price.toFixed(2) : '0.00'}`;
                    totalDisplay = `฿${(order.total !== undefined && order.total !== null) ? order.total.toFixed(2) : '0.00'}`;
                }
                
                contentHtml += `
                    <tr class="${statusClass}">
                        <td>${menuDisplay}</td>
                        <td class="text-center">${statusBadge}</td>
                        <td class="text-center">${order.quantity}</td>
                        <td class="text-end">${priceDisplay}</td>
                        <td class="text-end">${totalDisplay}</td>
                        <td class="text-muted small">${notesDisplay}</td>
                    </tr>
                `;
            });
            
            contentHtml += `
                        </tbody>
                        <tfoot>
                            <tr class="table-active">
                                <th colspan="4" class="text-end">ยอดรวมทั้งหมด:</th>
                                <th class="text-end">฿${(tableData.total_amount !== undefined && tableData.total_amount !== null) ? tableData.total_amount.toFixed(2) : '0.00'}</th>
                                <th></th>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            `;
        } else {
            contentHtml += `
                <div class="text-center py-4">
                    <i class="fas fa-utensils fa-3x text-muted mb-3"></i>
                    <p class="text-muted">ยังไม่มีรายการสั่งอาหาร</p>
                </div>
            `;
        }
        
        // แสดงเนื้อหาใน modal
        const tableDetailsContent = document.getElementById('table-details-content');
        if (tableDetailsContent) {
            tableDetailsContent.innerHTML = contentHtml;
        }
        
        // สร้างปุ่มตามสถานะโต๊ะ
        let actionButtons = '';
        
        // Debug: แสดงเงื่อนไขในการแสดงปุ่มเช็คบิล
        console.log('Condition for checkout button:', { 
            status: tableData.status, 
            isOccupied: tableData.status === 'occupied',
            hasOrders: tableData.orders && tableData.orders.length > 0,
            ordersLength: tableData.orders ? tableData.orders.length : 0
        });
        
        // ลบปุ่มเพิ่มรายการออกตามความต้องการของผู้ใช้
        
        // ปุ่มแก้ไขเมนู - แสดงเมื่อโต๊ะมีสถานะ occupied และมีรายการสั่งอาหาร
        if (tableData.status === 'occupied' && tableData.orders && tableData.orders.length > 0) {
            actionButtons += `
                <button type="button" class="btn btn-primary me-2" onclick="editTableMenu(${tableId})">
                    <i class="fas fa-edit me-1"></i>แก้ไขเมนู
                </button>
            `;
        }
        
        // ปุ่มเช็คบิล - แสดงเมื่อโต๊ะมีสถานะ occupied และมีรายการสั่งอาหาร
        if (tableData.status === 'occupied' && tableData.orders && tableData.orders.length > 0) {
            // ตรวจสอบว่ามีรายการที่มีสถานะ 'pending' (รอดำเนินการ) หรือ 'accepted' (รับแล้ว) หรือไม่
            const hasPendingOrAcceptedItems = tableData.orders.some(order => 
                order.item_status === 'pending' || order.item_status === 'accepted'
            );
            
            if (hasPendingOrAcceptedItems) {
                // ถ้ามีรายการที่ยังไม่เสร็จ ให้แสดงปุ่มเป็นสีเทาและปิดใช้งาน
                actionButtons += `
                    <button type="button" class="btn btn-secondary me-2" disabled title="ไม่สามารถเช็คบิลได้ เนื่องจากยังมีรายการที่รอดำเนินการหรือรับแล้ว">
                        <i class="fas fa-receipt me-1"></i>เช็คบิล
                    </button>
                `;
            } else {
                // ถ้าไม่มีรายการที่ยังไม่เสร็จ ให้แสดงปุ่มปกติ
                actionButtons += `
                    <button type="button" class="btn btn-warning me-2" onclick="checkoutTable(${tableId})">
                        <i class="fas fa-receipt me-1"></i>เช็คบิล
                    </button>
                `;
            }
        }
        
        // ปุ่มชำระเงินแล้ว - แสดงเมื่อโต๊ะมีสถานะ waiting_payment
        if (tableData.status === 'waiting_payment') {
            actionButtons += `
                <button type="button" class="btn btn-success me-2" onclick="completePayment(${tableId})">
                    <i class="fas fa-check me-1"></i>ชำระเงินแล้ว
                </button>
            `;
        }
        
        // ปุ่มเคลียร์โต๊ะแล้ว - แสดงเมื่อโต๊ะมีสถานะ needs_clearing
        if (tableData.status === 'needs_clearing') {
            actionButtons += `
                <button type="button" class="btn btn-info me-2 btn-clear-table" onclick="clearTable(${tableId})">
                    <i class="fas fa-broom me-1"></i>เคลียร์โต๊ะแล้ว
                </button>
            `;
        }
        
        // ปุ่มเคลียร์โต๊ะ - แสดงเมื่อโต๊ะมีสถานะ checkout
        if (tableData.status === 'checkout') {
            actionButtons += `
                <button type="button" class="btn btn-primary me-2" onclick="clearTable(${tableId})">
                    <i class="fas fa-broom me-1"></i>เคลียร์โต๊ะ
                </button>
            `;
        }
        
        // เพิ่มปุ่มพิมพ์ใบเสร็จเสมอเมื่อโต๊ะมีสถานะ waiting_payment, needs_clearing, หรือ checkout
        console.log('[DEBUG] showTableDetail: Receipt data exists:', !!window.receiptData, 'Session ID exists:', !!tableData.session_id);
        // ตรวจสอบว่ามีการกดปุ่มเช็คบิลแล้วหรือไม่ (มีข้อมูล receiptData หรือสถานะเป็น waiting_payment, needs_clearing, checkout)
        if (window.receiptData || tableData.status === 'waiting_payment' || tableData.status === 'needs_clearing' || tableData.status === 'checkout') {
            console.log('[DEBUG] showTableDetail: Adding print receipt button');
            actionButtons += `
                <button type="button" class="btn btn-info me-2" onclick="printReceipt(${tableId})">
                    <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                </button>
            `;
        } else {
            console.log('[DEBUG] showTableDetail: Adding disabled print receipt button');
            actionButtons += `
                <button type="button" class="btn btn-secondary me-2" disabled title="ต้องกดเช็คบิลก่อน">
                    <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                </button>
            `;
        }
        
        const tableActionButtons = document.getElementById('table-action-buttons');
        if (tableActionButtons) {
            tableActionButtons.innerHTML = actionButtons;
        }
        
        // แสดง modal
        const modal = new bootstrap.Modal(document.getElementById('tableDetailsModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading table details:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันสำหรับเปลี่ยนสถานะความพร้อมของเมนู
async function toggleMenuAvailability(itemId, isAvailable) {
    try {
        // หาข้อมูลเมนูจาก menuItems array
        const menuItem = menuItems.find(item => item.item_id === itemId);
        if (!menuItem) {
            throw new Error('ไม่พบข้อมูลเมนู');
        }
        
        const response = await fetch(`/api/menu/items/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: menuItem.name,
                price: menuItem.price,
                category_id: menuItem.category_id,
                description: menuItem.description || '',
                image_url: menuItem.image_url || null,
                preparation_time: menuItem.preparation_time || 15,
                food_option_type: menuItem.food_option_type || 'none',
                is_available: isAvailable
            })
        });
        
        const data = await response.json();
        console.log('API response:', data);
        
        if (data.success) {
            // อัปเดตข้อมูลในหน่วยความจำ
            const menuItem = menuItems.find(item => item.item_id === itemId);
            if (menuItem) {
                menuItem.is_available = isAvailable;
            }
            
            // อัปเดต label ข้างๆ toggle switch
            const toggleLabel = document.querySelector(`input[onchange*="${itemId}"]`).parentElement.nextElementSibling;
            if (toggleLabel) {
                toggleLabel.textContent = isAvailable ? 'พร้อมให้บริการ' : 'ไม่พร้อมให้บริการ';
                // อัปเดต CSS class
                toggleLabel.className = `toggle-label ${isAvailable ? 'available' : 'unavailable'}`;
            }
            
            // อัปเดตจำนวนเมนูที่พร้อมและไม่พร้อมให้บริการ
            updateMenuCounts();
            
            showAlert(`${isAvailable ? 'เปิด' : 'ปิด'}การให้บริการเมนูสำเร็จ`, 'success');
        } else {
            throw new Error(data.error || 'ไม่สามารถอัปเดตสถานะได้');
        }
    } catch (error) {
        console.error('Error toggling menu availability:', error);
        showAlert('เกิดข้อผิดพลาด: ' + error.message, 'error');
        
        // คืนค่า toggle switch กลับเป็นเดิม
        const toggleInput = document.querySelector(`input[onchange*="${itemId}"]`);
        if (toggleInput) {
            toggleInput.checked = !isAvailable;
        }
    }
}

// Bind functions to window object for onclick access
// Use the clearTable function that accepts tableId parameter
window.clearTable = async function(tableId) {
    // ค้นหาข้อมูลโต๊ะเพื่อดึงสถานะปัจจุบัน
    const table = tables.find(t => t.table_id === tableId);
    const status = table ? table.status : null;
    
    // ถ้าสถานะเป็น needs_clearing ไม่ต้องแสดงกล่องยืนยัน
    if (status !== 'needs_clearing' && !confirm('คุณต้องการเคลียร์โต๊ะนี้หรือไม่?')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`/api/tables/${tableId}/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('เคลียร์โต๊ะสำเร็จ', 'success');
            
            // ปิด modal ถ้ามี
            const modal = bootstrap.Modal.getInstance(document.getElementById('tableDetailsModal'));
            if (modal) modal.hide();
            
            // รีเฟรชข้อมูลโต๊ะ
            await loadTables();
        } else {
            throw new Error(data.error || 'ไม่สามารถเคลียร์โต๊ะได้');
        }
        
    } catch (error) {
        console.error('Error clearing table:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
};
window.showTableDetail = showTableDetail;
window.completePayment = completePayment;
window.printReceipt = printReceipt;


// Global variable สำหรับเก็บข้อมูลออเดอร์ที่กำลังแก้ไข
let currentEditingOrders = [];
let currentEditingTableId = null;

// ฟังก์ชันสำหรับแก้ไขเมนูโต๊ะ
async function editTableMenu(tableId) {
    console.log('=== editTableMenu called with tableId:', tableId);
    try {
        showLoading(true);
        
        // ค้นหาข้อมูลโต๊ะเพื่อดึง session_id
        const table = tables.find(t => t.table_id === tableId);
        const session_id = table ? table.session_id : null;
        
        // ดึงข้อมูลออเดอร์ปัจจุบันของโต๊ะ
        const response = await fetch(`/api/tables/${tableId}/orders?session_id=${session_id}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'ไม่สามารถดึงข้อมูลออเดอร์ได้');
        }
        
        // เก็บข้อมูลออเดอร์ปัจจุบันไว้ในตัวแปร global
        currentEditingOrders = data.data && data.data.orders ? [...data.data.orders] : [];
        currentEditingTableId = tableId;
        
        // แสดงหน้าแก้ไขเมนู
        showEditMenuInterface(tableId);
        
    } catch (error) {
        console.error('Error opening edit menu:', error);
        showAlert('เกิดข้อผิดพลาดในการเปิดหน้าแก้ไขเมนู', 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันแสดงหน้าแก้ไขเมนู
function showEditMenuInterface(tableId) {
    let contentHtml = `
        <div class="edit-menu-container">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6><i class="fas fa-edit me-2"></i>แก้ไขรายการสั่งอาหาร - โต๊ะ ${tableId}</h6>
                <button type="button" class="btn btn-success btn-sm" onclick="showAddMenuModal()">
                    <i class="fas fa-plus me-1"></i>เพิ่มรายการ
                </button>
            </div>
            
            <div id="edit-orders-list">
                <!-- รายการออเดอร์จะแสดงที่นี่ -->
            </div>
            
            <div class="mt-3 p-3 bg-light rounded">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">ยอดรวมทั้งหมด:</h5>
                    <h5 class="mb-0 text-primary" id="edit-total-amount">฿0.00</h5>
                </div>
            </div>
        </div>
    `;
    
    // แสดงเนื้อหาใน modal
    const tableDetailsContent = document.getElementById('table-details-content');
        if (tableDetailsContent) {
            tableDetailsContent.innerHTML = contentHtml;
        }
    
    // อัปเดตรายการออเดอร์
    updateEditOrdersList();
    
    // เปลี่ยนปุ่มใน footer
    const actionButtons = `
        <button type="button" class="btn btn-secondary me-2" onclick="showTableDetail(${tableId})">
            <i class="fas fa-times me-1"></i>ยกเลิก
        </button>
        <button type="button" class="btn btn-primary" onclick="saveMenuChanges(${tableId})">
            <i class="fas fa-save me-1"></i>บันทึกการเปลี่ยนแปลง
        </button>
    `;
    console.log('=== Setting action buttons HTML:', actionButtons);
    document.getElementById('table-action-buttons').innerHTML = actionButtons;
    console.log('=== Action buttons element after setting:', document.getElementById('table-action-buttons'));
}

// ฟังก์ชันอัปเดตรายการออเดอร์ในหน้าแก้ไข
function updateEditOrdersList() {
    const container = document.getElementById('edit-orders-list');
    let html = '';
    let totalAmount = 0;
    
    if (currentEditingOrders.length === 0) {
        html = `
            <div class="text-center py-4">
                <i class="fas fa-utensils fa-3x text-muted mb-3"></i>
                <p class="text-muted">ยังไม่มีรายการสั่งอาหาร</p>
                <button type="button" class="btn btn-primary" onclick="showAddMenuModal()">
                    <i class="fas fa-plus me-1"></i>เพิ่มรายการแรก
                </button>
            </div>
        `;
    } else {
        html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>เมนู</th>
                            <th class="text-center">สถานะ</th>
                            <th class="text-center">จำนวน</th>
                            <th class="text-end">ราคา</th>
                            <th class="text-end">รวม</th>
                            <th>หมายเหตุ</th>
                            <th class="text-center">จัดการ</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        currentEditingOrders.forEach((order, index) => {
            const itemTotal = (order.price || 0) * (order.quantity || 0);
            const orderStatus = order.item_status || order.status || 'pending';
            
            // Only add to total if not rejected
            if (orderStatus !== 'rejected') {
                totalAmount += itemTotal;
            }
            
            // Get status badge for the order
            const statusBadge = getItemStatusBadge(orderStatus);
            
            // Price display logic for rejected items
            let priceDisplay, totalDisplay;
            if (orderStatus === 'rejected') {
                priceDisplay = `<span style="text-decoration: line-through; color: #6c757d;">฿${(order.price || 0).toFixed(2)}</span><br><strong style="color: #dc3545;">฿0.00</strong>`;
                totalDisplay = `<span style="text-decoration: line-through; color: #6c757d;">฿${itemTotal.toFixed(2)}</span><br><strong style="color: #dc3545;">฿0.00</strong>`;
            } else {
                priceDisplay = `฿${(order.price || 0).toFixed(2)}`;
                totalDisplay = `฿${itemTotal.toFixed(2)}`;
            }
            
            // Parse customer_request to move special options from notes to under menu name (same as table details)
            let menuDisplay = order.menu_name || order.name;
            let notesDisplay = '-';
            
            if (order.customer_request) {
                if (order.customer_request.includes(' | ')) {
                    const parts = order.customer_request.split(' | ');
                    
                    // แยก spice options และ addon options
                    const spicePart = parts[0] ? parts[0].trim() : '';
                    const allParts = parts[1] ? parts[1].split(',').map(part => part.trim()) : [];
                    const spiceOptions = allParts.filter(part => 
                        part.includes('เผ็ด') || part.includes('หวาน') || part.includes('ปกติ')
                    );
                    const addonOptions = allParts.filter(part => 
                        part.includes('ไข่') || part.includes('เพิ่ม')
                    ).filter(part => !part.includes('ไม่เพิ่ม')); // กรอง "ไม่เพิ่ม" ออก
                    
                    // รวม spice level จากส่วนแรกเข้ากับชื่อเมนูในวงเล็บ
                    if (spicePart && (spicePart.includes('เผ็ด') || spicePart.includes('หวาน') || spicePart.includes('ปกติ'))) {
                        menuDisplay = `${order.menu_name || order.name} <span class="${getCustomerRequestClass(spicePart)}">(${spicePart})</span>`;
                    } else if (spiceOptions.length > 0) {
                        menuDisplay = `${order.menu_name || order.name} <span class="${getCustomerRequestClass(spiceOptions[0])}">(${spiceOptions[0]})</span>`;
                    }
                    
                    // แสดง addon options เป็นรายการด้านล่าง
                    if (addonOptions.length > 0) {
                        const addonList = addonOptions.map(option => `<div class="text-muted small">- ${option}</div>`).join('');
                        menuDisplay += `<br>${addonList}`;
                    }
                    
                    // Keep notes column empty for admin to edit later
                    notesDisplay = '-';
                } else {
                    // If no separator, check if entire request is spice level
                    const trimmedRequest = order.customer_request.trim();
                    if (trimmedRequest.includes('เผ็ด') || trimmedRequest.includes('หวาน') || trimmedRequest.includes('ปกติ')) {
                        menuDisplay = `${order.menu_name || order.name} <span class="${getCustomerRequestClass(trimmedRequest)}">(${trimmedRequest})</span>`;
                    } else {
                        // Show as addon option below menu name
                        menuDisplay = `${order.menu_name || order.name}<br><div class="text-muted small">- ${trimmedRequest}</div>`;
                    }
                    notesDisplay = '-';
                }
            }
            
            html += `
                <tr>
                    <td>
                        ${menuDisplay}
                    </td>
                    <td class="text-center">
                        ${statusBadge}
                    </td>
                    <td class="text-center">
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-outline-secondary btn-sm" 
                                    onclick="decreaseOrderQuantity(${index})" 
                                    ${order.quantity <= 1 ? 'disabled' : ''}>
                                <i class="fas fa-minus"></i>
                            </button>
                            <span class="btn btn-outline-secondary btn-sm disabled">${order.quantity}</span>
                            <button type="button" class="btn btn-outline-secondary btn-sm" 
                                    onclick="increaseOrderQuantity(${index})">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </td>
                    <td class="text-end">${priceDisplay}</td>
                    <td class="text-end">${totalDisplay}</td>
                    <td class="text-muted small">${notesDisplay}</td>
                    <td class="text-center">
                        <button type="button" class="btn btn-danger btn-sm" 
                                onclick="removeOrderItem(${index})" 
                                title="ลบรายการ">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
    }
    
    container.innerHTML = html;
    
    // อัปเดตยอดรวม
    const totalElement = document.getElementById('edit-total-amount');
    if (totalElement) {
        totalElement.textContent = `฿${totalAmount.toFixed(2)}`;
    }
}

// ฟังก์ชันเพิ่มจำนวนรายการ
function increaseOrderQuantity(index) {
    if (currentEditingOrders[index]) {
        currentEditingOrders[index].quantity += 1;
        updateEditOrdersList();
    }
}

// ฟังก์ชันลดจำนวนรายการ
function decreaseOrderQuantity(index) {
    if (currentEditingOrders[index] && currentEditingOrders[index].quantity > 1) {
        currentEditingOrders[index].quantity -= 1;
        updateEditOrdersList();
    }
}

// ฟังก์ชันลบรายการ
function removeOrderItem(index) {
    console.log('=== removeOrderItem called ===');
    console.log('Index:', index);
    console.log('currentEditingOrders:', currentEditingOrders);
    
    if (!currentEditingOrders || !Array.isArray(currentEditingOrders)) {
        console.error('currentEditingOrders is not defined or not an array');
        showAlert('ข้อมูลรายการไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง', 'error');
        return;
    }
    
    if (index < 0 || index >= currentEditingOrders.length) {
        console.error('Invalid index:', index);
        showAlert('ไม่พบรายการที่ต้องการลบ', 'error');
        return;
    }
    
    if (confirm('คุณต้องการลบรายการนี้หรือไม่?')) {
        console.log('User confirmed deletion');
        const removedItem = currentEditingOrders.splice(index, 1);
        console.log('Removed item:', removedItem);
        console.log('currentEditingOrders after removal:', currentEditingOrders);
        updateEditOrdersList();
        showAlert('ลบรายการเรียบร้อยแล้ว', 'success');
    }
}

// ฟังก์ชันแก้ไขหมายเหตุพิเศษ
function editCustomerRequest(index) {
    if (!currentEditingOrders[index]) {
        showAlert('ไม่พบรายการที่ต้องการแก้ไข', 'error');
        return;
    }
    
    const currentRequest = currentEditingOrders[index].customer_request || '';
    const menuName = currentEditingOrders[index].menu_name || currentEditingOrders[index].name;
    
    // สร้าง modal สำหรับแก้ไขหมายเหตุ
    const modalHtml = `
        <div class="modal fade" id="editCustomerRequestModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">แก้ไขหมายเหตุพิเศษ</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label"><strong>เมนู:</strong> ${menuName}</label>
                        </div>
                        <div class="mb-3">
                            <label for="customerRequestInput" class="form-label">หมายเหตุพิเศษ:</label>
                    <textarea class="form-control" id="customerRequestInput" rows="3" 
                                      placeholder="เช่น ไม่ใส่ผัก, เผ็ดน้อย, ไม่ใส่น้ำตาล...">${currentRequest}</textarea>
                            <div class="form-text">สามารถระบุความต้องการพิเศษสำหรับรายการนี้ได้</div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="button" class="btn btn-primary" onclick="saveCustomerRequest(${index})">บันทึก</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่าถ้ามี
    const existingModal = document.getElementById('editCustomerRequestModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal ใหม่
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('editCustomerRequestModal'));
    modal.show();
    
    // Focus ที่ textarea
    setTimeout(() => {
        const textarea = document.getElementById('customerRequestInput');
        if (textarea) {
            textarea.focus();
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);
        }
    }, 500);
}

// ฟังก์ชันบันทึกหมายเหตุพิเศษ
function saveCustomerRequest(index) {
    if (!currentEditingOrders[index]) {
        showAlert('ไม่พบรายการที่ต้องการแก้ไข', 'error');
        return;
    }
    
    const textarea = document.getElementById('customerRequestInput');
    if (!textarea) {
        showAlert('ไม่พบช่องกรอกหมายเหตุ', 'error');
        return;
    }
    
    const newRequest = textarea.value.trim();
    
    // อัปเดตหมายเหตุในรายการ
    currentEditingOrders[index].customer_request = newRequest;
    
    // อัปเดตรายการแสดงผล
    updateEditOrdersList();
    
    // ปิด modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('editCustomerRequestModal'));
    if (modal) {
        modal.hide();
    }
    
    // แสดงข้อความแจ้งเตือน
    const menuName = currentEditingOrders[index].menu_name || currentEditingOrders[index].name;
    if (newRequest) {
        showAlert(`อัปเดตหมายเหตุสำหรับ ${menuName} เรียบร้อยแล้ว`, 'success');
    } else {
        showAlert(`ลบหมายเหตุสำหรับ ${menuName} เรียบร้อยแล้ว`, 'success');
    }
}

// ฟังก์ชันแสดง modal เพิ่มรายการเมนู
async function showAddMenuModal() {
    try {
        // ดึงข้อมูลเมนูทั้งหมด
        const response = await fetch('/api/menu/items');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API Response:', data);
        
        // ตรวจสอบรูปแบบ response
        let menuItems = [];
        if (data.success && data.data) {
            menuItems = data.data;
        } else if (Array.isArray(data.data)) {
            menuItems = data.data;
        } else if (Array.isArray(data)) {
            menuItems = data;
        } else {
            throw new Error('รูปแบบข้อมูลไม่ถูกต้อง');
        }
        
        if (menuItems.length === 0) {
            throw new Error('ไม่พบรายการเมนูในระบบ');
        }
        
        // สร้าง modal สำหรับเลือกเมนู
        let modalHtml = `
            <div class="modal fade" id="addMenuModal" tabindex="-1" style="z-index: 1060;">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">เพิ่มรายการอาหาร</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
        `;
        
        menuItems.forEach(item => {
            modalHtml += `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card h-100">
                        <div class="card-body">
                            <h6 class="card-title">${item.name}</h6>
                            <p class="card-text text-muted small">${item.description || ''}</p>
                            <p class="card-text"><strong>฿${(item.price || 0).toFixed(2)}</strong></p>
                            <button type="button" class="btn btn-primary btn-sm w-100" 
                                    onclick="addMenuItemToOrder(${item.item_id}, '${item.name}', ${item.price})">
                                <i class="fas fa-plus me-1"></i>เพิ่ม
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        modalHtml += `
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ปิด</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // ลบ modal เก่าถ้ามี
        const existingModal = document.getElementById('addMenuModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // เพิ่ม modal ใหม่
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // แสดง modal
        const modal = new bootstrap.Modal(document.getElementById('addMenuModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error showing add menu modal:', error);
        showAlert('เกิดข้อผิดพลาดในการดึงข้อมูลเมนู', 'danger');
    }
}

// ฟังก์ชันโหลดตัวเลือกพิเศษแบบ dynamic สำหรับ admin
async function loadDynamicSpecialOptionsForAdmin(container) {
    try {
        const response = await fetch('/api/option-values?option_type=addon');
        const result = await response.json();
        
        if (result.success && result.data) {
            const rowContainer = container.querySelector('#specialOptionsRow');
            if (rowContainer) {
                rowContainer.innerHTML = '';
                
                // สร้างตัวเลือกจากข้อมูล API
                result.data.forEach((option, index) => {
                    const colDiv = document.createElement('div');
                    colDiv.className = 'col-6';
                    
                    const inputId = `addon${index}`;
                    const priceText = option.additional_price > 0 ? ` (+${option.additional_price}฿)` : '';
                    
                    colDiv.innerHTML = `
                        <input type="checkbox" class="btn-check" name="addonOptions" id="${inputId}" value="${option.name}" data-price="${option.additional_price}">
                        <label class="btn btn-outline-success w-100" for="${inputId}">${option.name}${priceText}</label>
                    `;
                    
                    rowContainer.appendChild(colDiv);
                    
                    // ตั้งค่าเริ่มต้นให้ "ไม่เพิ่ม" ถูกเลือก
                    if (option.name === 'ไม่เพิ่ม') {
                        setTimeout(() => {
                            const checkbox = document.getElementById(inputId);
                            if (checkbox) {
                                checkbox.checked = true;
                            }
                        }, 50);
                    }
                });
                
                // เพิ่มลอจิกการจัดการตัวเลือก
                setTimeout(() => {
                    setupAdminSpecialOptionsLogic();
                }, 100);
            }
        }
    } catch (error) {
        console.error('Error loading dynamic special options for admin:', error);
    }
}

// ฟังก์ชันจัดการลอจิกตัวเลือกพิเศษสำหรับ admin
function setupAdminSpecialOptionsLogic() {
    const addonCheckboxes = document.querySelectorAll('input[name="addonOptions"]');
    let noAdditionCheckbox = null;
    
    // หา checkbox "ไม่เพิ่ม"
    addonCheckboxes.forEach(checkbox => {
        if (checkbox.value === 'ไม่เพิ่ม') {
            noAdditionCheckbox = checkbox;
        }
    });
    
    if (!noAdditionCheckbox) return;
    
    // ฟังก์ชันตรวจสอบและจัดการการเลือก "ไม่เพิ่ม" อัตโนมัติ
    function checkAndSetNoAddition() {
        const otherCheckboxes = Array.from(addonCheckboxes).filter(cb => cb.value !== 'ไม่เพิ่ม');
        const hasOtherSelection = otherCheckboxes.some(cb => cb.checked);
        
        if (!hasOtherSelection && !noAdditionCheckbox.checked) {
            noAdditionCheckbox.checked = true;
        }
    }
    
    addonCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.value === 'ไม่เพิ่ม') {
                // ถ้าเลือก "ไม่เพิ่ม" ให้ยกเลิกตัวเลือกอื่นทั้งหมด
                if (this.checked) {
                    addonCheckboxes.forEach(otherCheckbox => {
                        if (otherCheckbox.value !== 'ไม่เพิ่ม') {
                            otherCheckbox.checked = false;
                        }
                    });
                }
            } else {
                // ถ้าเลือกตัวเลือกอื่น ให้ยกเลิก "ไม่เพิ่ม"
                if (this.checked && noAdditionCheckbox.checked) {
                    noAdditionCheckbox.checked = false;
                }
                
                // ถ้ายกเลิกตัวเลือกอื่น ให้ตรวจสอบว่าต้องเลือก "ไม่เพิ่ม" หรือไม่
                if (!this.checked) {
                    setTimeout(checkAndSetNoAddition, 10);
                }
            }
        });
    });
    
    // ตรวจสอบเริ่มต้น
    setTimeout(checkAndSetNoAddition, 50);
}

// ฟังก์ชันเพิ่มรายการเมนูลงในออเดอร์
async function addMenuItemToOrder(menuId, menuName, price) {
    console.log('=== addMenuItemToOrder called ===');
    console.log('menuId:', menuId, 'menuName:', menuName, 'price:', price);
    console.log('currentEditingTableId:', currentEditingTableId);
    console.log('currentEditingOrders:', currentEditingOrders);
    
    // ตรวจสอบว่าอยู่ในโหมดแก้ไขเมนูหรือไม่
    if (!currentEditingTableId) {
        showAlert('กรุณาเข้าสู่โหมดแก้ไขเมนูก่อน โดยการกดปุ่ม "แก้ไขเมนู" ในการ์ดโต๊ะ', 'warning');
        return;
    }
    
    // แสดง modal สำหรับเลือก customer_request ทุกครั้ง
    showAddMenuItemModal(menuId, menuName, price);
}


// ฟังก์ชันแสดง modal สำหรับเพิ่มรายการใหม่พร้อมหมายเหตุ
function showAddMenuItemModal(menuId, menuName, price) {
    // ค้นหาข้อมูลเมนูจาก menuItems array
    const menuItem = menuItems.find(item => item.item_id === menuId || item.id === menuId);
    const foodOptionType = menuItem ? menuItem.food_option_type : 'none';
    
    console.log('Menu item found:', menuItem);
    console.log('Food option type:', foodOptionType);
    
    // สร้างส่วนตัวเลือกตาม food_option_type
    let optionsHtml = '';
    
    // แยกตัวเลือกที่เลือกไว้ (คั่นด้วย comma)
    const selectedOptions = foodOptionType ? foodOptionType.split(',').map(opt => opt.trim()) : [];
    
    // ระดับความเผ็ด
    if (selectedOptions.includes('spice')) {
        optionsHtml += `
        <div class="mb-4">
            <h6 class="mb-3">ระดับความเผ็ด (เลือกได้อย่างเดียว)</h6>
            <div class="row g-2">
                <div class="col-4">
                    <input type="radio" class="btn-check" name="spiceLevel" id="spiceMild" value="เผ็ดน้อย">
                    <label class="btn btn-outline-warning w-100" for="spiceMild">เผ็ดน้อย</label>
                </div>
                <div class="col-4">
                    <input type="radio" class="btn-check" name="spiceLevel" id="spiceNormal" value="เผ็ดปกติ">
                    <label class="btn btn-outline-warning w-100" for="spiceNormal">เผ็ดปกติ</label>
                </div>
                <div class="col-4">
                    <input type="radio" class="btn-check" name="spiceLevel" id="spiceHot" value="เผ็ดมาก">
                    <label class="btn btn-outline-warning w-100" for="spiceHot">เผ็ดมาก</label>
                </div>
            </div>
        </div>`;
    }
    
    // ระดับความหวาน
    if (selectedOptions.includes('sweet')) {
        optionsHtml += `
        <div class="mb-4">
            <h6 class="mb-3">ระดับความหวาน (เลือกได้ 1 รายการ)</h6>
            <div class="row g-2">
                <div class="col-4">
                    <input type="radio" class="btn-check" name="sweetnessLevel" id="sweetLess" value="หวานน้อย">
                    <label class="btn btn-outline-info w-100" for="sweetLess">หวานน้อย</label>
                </div>
                <div class="col-4">
                    <input type="radio" class="btn-check" name="sweetnessLevel" id="sweetNormal" value="หวานปกติ">
                    <label class="btn btn-outline-info w-100" for="sweetNormal">หวานปกติ</label>
                </div>
                <div class="col-4">
                    <input type="radio" class="btn-check" name="sweetnessLevel" id="sweetMore" value="หวานมาก">
                    <label class="btn btn-outline-info w-100" for="sweetMore">หวานมาก</label>
                </div>
            </div>
        </div>`;
    }
    
    // ตัวเลือกพิเศษ (Dynamic Loading)
    if (selectedOptions.includes('special')) {
        optionsHtml += `
        <div class="mb-4" id="specialOptionsContainer">
            <h6 class="mb-3">ตัวเลือกพิเศษ (เลือกได้หลายตัวเลือก)</h6>
            <div class="row g-2" id="specialOptionsRow">
                <!-- Dynamic content will be loaded here -->
            </div>
        </div>`;
    }
    
    // สร้าง modal สำหรับเพิ่มรายการใหม่
    const modalHtml = `
        <div class="modal fade" id="addMenuItemModal" tabindex="-1" style="z-index: 1070;">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">เพิ่มรายการอาหาร</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label"><strong>เมนู:</strong> ${menuName}</label>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>ราคา:</strong> ฿${price.toFixed(2)}</label>
                        </div>
                        <div class="mb-3">
                            <label for="newItemQuantity" class="form-label">จำนวน:</label>
                            <div class="input-group" style="max-width: 150px;">
                                <button class="btn btn-outline-secondary" type="button" onclick="changeNewItemQuantity(-1)">-</button>
                                <input type="number" class="form-control text-center" id="newItemQuantity" value="1" min="1" readonly>
                                <button class="btn btn-outline-secondary" type="button" onclick="changeNewItemQuantity(1)">+</button>
                            </div>
                        </div>
                        
                        ${optionsHtml}
                        
                        <div class="mb-3">
                            <label for="newItemCustomerRequest" class="form-label">หมายเหตุเพิ่มเติม (ไม่บังคับ):</label>
                            <textarea class="form-control" id="newItemCustomerRequest" rows="2" 
                                      placeholder="หมายเหตุพิเศษอื่นๆ..."></textarea>
                            <div class="form-text">สามารถระบุความต้องการพิเศษเพิ่มเติมได้</div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="button" class="btn btn-primary" onclick="confirmAddMenuItem(${menuId}, '${menuName}', ${price})">เพิ่มรายการ</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่าถ้ามี
    const existingModal = document.getElementById('addMenuItemModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal ใหม่
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // ปิด modal เลือกเมนูก่อน
    const addMenuModal = bootstrap.Modal.getInstance(document.getElementById('addMenuModal'));
    if (addMenuModal) {
        addMenuModal.hide();
    }
    
    // แสดง modal ใหม่
    const modal = new bootstrap.Modal(document.getElementById('addMenuItemModal'));
    modal.show();
    
    // โหลดตัวเลือกพิเศษแบบ dynamic หลังจากแสดง modal
    if (selectedOptions.includes('special')) {
        setTimeout(() => {
            const specialContainer = document.getElementById('specialOptionsContainer');
            if (specialContainer) {
                loadDynamicSpecialOptionsForAdmin(specialContainer);
            }
        }, 100);
    }
}

// ฟังก์ชันเปลี่ยนจำนวนในการเพิ่มรายการใหม่
function changeNewItemQuantity(change) {
    const quantityInput = document.getElementById('newItemQuantity');
    if (quantityInput) {
        let currentValue = parseInt(quantityInput.value) || 1;
        currentValue += change;
        if (currentValue < 1) currentValue = 1;
        quantityInput.value = currentValue;
    }
}

// ฟังก์ชันยืนยันการเพิ่มรายการใหม่
async function confirmAddMenuItem(menuId, menuName, price) {
    const quantityInput = document.getElementById('newItemQuantity');
    const customerRequestInput = document.getElementById('newItemCustomerRequest');
    
    const quantity = parseInt(quantityInput?.value) || 1;
    const additionalNotes = customerRequestInput?.value.trim() || '';
    
    // รวบรวมข้อมูลจากตัวเลือกต่างๆ
    const spiceLevel = document.querySelector('input[name="spiceLevel"]:checked')?.value || '';
    const sweetnessLevel = document.querySelector('input[name="sweetnessLevel"]:checked')?.value || '';
    const addonOptions = Array.from(document.querySelectorAll('input[name="addonOptions"]:checked')).map(cb => cb.value);
    
    // สร้าง customer_request ตามรูปแบบเดียวกับหน้าลูกค้า
    let customerRequest = '';
    
    // เพิ่มระดับความเผ็ดหรือความหวาน (ถ้ามี)
    if (spiceLevel || sweetnessLevel) {
        const levels = [spiceLevel, sweetnessLevel].filter(level => level).join(', ');
        customerRequest = levels;
    }
    
    // เพิ่มตัวเลือกพิเศษ (ถ้ามี)
    if (addonOptions.length > 0) {
        if (customerRequest) {
            customerRequest += ' | ' + addonOptions.join(', ');
        } else {
            customerRequest = addonOptions.join(', ');
        }
    }
    
    // เพิ่มหมายเหตุเพิ่มเติม (ถ้ามี)
    if (additionalNotes) {
        if (customerRequest) {
            customerRequest += ' | ' + additionalNotes;
        } else {
            customerRequest = additionalNotes;
        }
    }
    
    try {
        showLoading(true);
        
        // ค้นหาข้อมูลโต๊ะเพื่อดึง session_id
        const table = tables.find(t => t.table_id === currentEditingTableId);
        const session_id = table ? table.session_id : null;
        
        if (!session_id) {
            throw new Error('ไม่พบ session_id ของโต๊ะ');
        }
        
        // เตรียมข้อมูลสำหรับส่งไปยัง API
        const orderData = {
            table_id: currentEditingTableId,
            session_id: session_id,
            items: [{
                item_id: menuId,
                quantity: quantity,
                price: price,
                customer_request: customerRequest
            }]
        };
        
        // ส่งข้อมูลไปยัง API
        const response = await fetch('http://localhost:5000/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // ตรวจสอบว่ามีรายการนี้อยู่แล้วหรือไม่
            const existingIndex = currentEditingOrders.findIndex(order => 
                (order.menu_id === menuId || order.id === menuId) && 
                order.customer_request === customerRequest);
            
            if (existingIndex !== -1) {
                // ถ้ามีแล้วและ customer_request เหมือนกัน เพิ่มจำนวน
                currentEditingOrders[existingIndex].quantity += quantity;
            } else {
                // ถ้ายังไม่มีหรือ customer_request ต่างกัน เพิ่มรายการใหม่
                currentEditingOrders.push({
                    menu_id: menuId,
                    menu_name: menuName,
                    name: menuName,
                    price: price,
                    quantity: quantity,
                    customer_request: customerRequest,
                    item_status: 'pending'
                });
            }
            
            // อัปเดตรายการ
            updateEditOrdersList();
            
            // ปิด modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addMenuItemModal'));
            if (modal) {
                modal.hide();
            }
            
            // แสดงข้อความแจ้งเตือน
            let message = `เพิ่ม ${menuName}`;
            if (quantity > 1) {
                message += ` จำนวน ${quantity} รายการ`;
            }
            if (customerRequest) {
            message += ` (${customerRequest})`;
            }
            message += ` เรียบร้อยแล้ว`;
            
            showAlert(message, 'success');
        } else {
            throw new Error(data.error || 'ไม่สามารถเพิ่มรายการได้');
        }
        
    } catch (error) {
        console.error('Error adding menu item:', error);
        showAlert('เกิดข้อผิดพลาดในการเพิ่มรายการ: ' + error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันบันทึกการเปลี่ยนแปลง
async function saveMenuChanges(tableId) {
    console.log('=== saveMenuChanges called with tableId:', tableId);
    console.log('=== currentEditingOrders:', currentEditingOrders);
    
    try {
        showLoading(true);
        
        // ค้นหาข้อมูลโต๊ะเพื่อดึง session_id
        const table = tables.find(t => t.table_id === tableId);
        const session_id = table ? table.session_id : null;
        
        if (!session_id) {
            throw new Error('ไม่พบ session_id ของโต๊ะ');
        }
        
        // ตรวจสอบว่ามีการเปลี่ยนแปลงจริงหรือไม่
        // หมายเหตุ: ไม่ควรข้ามการบันทึกแม้ว่า currentEditingOrders จะว่าง
        // เพราะอาจเป็นการลบรายการทั้งหมด ซึ่งก็เป็นการเปลี่ยนแปลงที่ถูกต้อง
        
        // ถ้าไม่มีรายการใดๆ ให้ส่งข้อมูลว่างไปยัง API เพื่อล้างออเดอร์
        const ordersToSend = currentEditingOrders || [];
        
        // เตรียมข้อมูลสำหรับส่งไปยัง API
        const updateData = {
            session_id: session_id,
            orders: ordersToSend.map(order => {
                const price = parseFloat(order.price) || 0;
                const quantity = parseInt(order.quantity) || 0;
                const total_price = price * quantity;
                
                console.log('Processing order item:', {
                    menu_id: order.menu_id || order.id,
                    quantity: quantity,
                    price: price,
                    total_price: total_price,
                    original_order: order
                });
                
                return {
                    menu_id: order.menu_id || order.id,
                    quantity: quantity,
                    price: price,
                    total_price: total_price,
                    customer_request: order.customer_request || '',
                    status: order.item_status || order.status || 'pending'
                };
            })
        };
        
        console.log('Saving menu changes:', updateData);
        
        const response = await fetch(`http://localhost:5000/api/tables/${tableId}/update-orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('บันทึกการเปลี่ยนแปลงเรียบร้อยแล้ว', 'success');
            
            // อัปเดตข้อมูลโต๊ะเฉพาะโต๊ะที่แก้ไขเพื่อให้ได้ session_id ใหม่
            const tableResponse = await fetch(`http://localhost:5000/api/tables/${tableId}`);
            const tableData = await tableResponse.json();
            
            if (tableData.success) {
                // อัปเดตข้อมูลโต๊ะในตัวแปร tables
                const tableIndex = tables.findIndex(t => t.table_id === tableId);
                if (tableIndex !== -1) {
                    tables[tableIndex] = tableData.data;
                }
            }
            
            // แสดงรายละเอียดโต๊ะด้วยข้อมูลที่อัปเดตแล้ว
            await showTableDetail(tableId);
        } else {
            throw new Error(data.error || 'ไม่สามารถบันทึกการเปลี่ยนแปลงได้');
        }
        
    } catch (error) {
        console.error('Error saving menu changes:', error);
        showAlert('เกิดข้อผิดพลาดในการบันทึกการเปลี่ยนแปลง: ' + error.message, 'danger');
    } finally {
        showLoading(false);
    }
}























// ฟังก์ชันสำหรับเช็คบิล
async function checkoutTable(tableId) {
    try {
        showLoading(true);
        
        // ค้นหาข้อมูลโต๊ะเพื่อดึง session_id
        const table = tables.find(t => t.table_id === tableId);
        const session_id = table ? table.session_id : null;
        
        console.log('Checkout table with session_id:', session_id);
        
        const response = await fetch(`/api/tables/${tableId}/checkout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: session_id
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('เช็คบิลสำเร็จ โต๊ะอยู่ในสถานะรอชำระเงิน', 'success');
            
            // บันทึกข้อมูลใบเสร็จไว้ใช้ในการพิมพ์
            if (data.data && data.data.orders && data.data.orders.length > 0) {
                window.receiptData = data.data;
                console.log('Receipt data saved:', window.receiptData);
                
                // ตรวจสอบว่ามีข้อมูลที่จำเป็นครบถ้วนหรือไม่
                if (!window.receiptData.table_id) {
                    window.receiptData.table_id = tableId;
                }
                
                // ไม่ต้องตั้งค่า created_at ใหม่ เพื่อให้ใช้วันที่จาก API checkout
                // if (!window.receiptData.created_at) {
                //     window.receiptData.created_at = new Date().toISOString();
                // }
                
                // คำนวณยอดรวมถ้าไม่มีข้อมูล (ไม่รวมรายการที่ถูก reject)
                if (!window.receiptData.total_amount) {
                    window.receiptData.total_amount = window.receiptData.orders.reduce((sum, order) => {
                        const status = order.status || order.item_status || 'completed';
                        if (status === 'rejected') return sum; // ไม่นับรายการที่ถูกยกเลิก
                        const price = parseFloat(order.price || order.unit_price || 0);
                        const quantity = parseInt(order.quantity || 1);
                        return sum + (price * quantity);
                    }, 0);
                }
                
                // เปลี่ยนปุ่มพิมพ์ใบเสร็จจากปุ่มที่ถูก disable เป็นปุ่มที่กดได้
                const actionButtons = document.getElementById('table-action-buttons');
                const disabledPrintButton = Array.from(actionButtons.children).find(btn => 
                    btn.classList.contains('btn-secondary') && btn.innerHTML.includes('พิมพ์ใบเสร็จ'));
                    
                if (disabledPrintButton) {
                    const printButton = document.createElement('button');
                    printButton.type = 'button';
                    printButton.className = 'btn btn-info me-2';
                    printButton.innerHTML = '<i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ';
                    printButton.onclick = () => printReceipt(tableId);
                    actionButtons.replaceChild(printButton, disabledPrintButton);
                    console.log('Replaced disabled print button with active one');
                }
            } else {
                console.warn('Checkout API returned success but no valid receipt data');
                showAlert('ไม่พบข้อมูลรายการอาหารสำหรับใบเสร็จ', 'warning');
            }
            
            // อัปเดตสถานะบิลเป็น 'checked' สำหรับทุก order ใน session
            if (data.data && data.data.orders && data.data.orders.length > 0) {
                try {
                    for (const order of data.data.orders) {
                        if (order.order_id) {
                            const billStatusResponse = await fetch(`http://localhost:5000/api/orders/${order.order_id}/bill-status`, {
                                method: 'PUT',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ bill_status: 'checked' })
                            });
                            
                            if (billStatusResponse.ok) {
                                console.log(`Bill status updated to checked for order ${order.order_id}`);
                            }
                        }
                    }
                } catch (billError) {
                    console.error('Error updating bill status:', billError);
                }
            }
            
            // รีเฟรชข้อมูลโต๊ะและแสดงรายละเอียดใหม่ (ไม่ปิด modal)
            await loadTables();
            await showTableDetail(tableId);
            
            // เพิ่มปุ่มพิมพ์ใบเสร็จหลังจากเช็คบิลสำเร็จ
            const actionButtons = document.getElementById('table-action-buttons');
            
            // ตรวจสอบว่ามีปุ่มพิมพ์ใบเสร็จอยู่แล้วหรือไม่
            const existingPrintButton = Array.from(actionButtons.children).find(btn => 
                btn.innerHTML.includes('พิมพ์ใบเสร็จ'));
                
            if (!existingPrintButton) {
                const printButton = document.createElement('button');
                printButton.type = 'button';
                printButton.className = 'btn btn-info me-2';
                printButton.innerHTML = '<i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ';
                printButton.onclick = () => printReceipt(tableId);
                actionButtons.appendChild(printButton);
                console.log('Added print receipt button');
            }
        } else {
            throw new Error(data.error || 'ไม่สามารถเช็คบิลได้');
        }
    } catch (error) {
        console.error('Error checking out table:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันสำหรับชำระเงินเสร็จสิ้น
async function completePayment(tableId) {
    try {
        // แสดง loading พร้อมข้อความที่ชัดเจน
        showLoading(true);
        
        // เพิ่ม timeout เพื่อป้องกันการรอนานเกินไป
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // timeout 10 วินาที
        
        const response = await fetch(`/api/tables/${tableId}/payment-complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // แสดงข้อความสำเร็จทันที
            showAlert('✅ ชำระเงินเสร็จสิ้น โต๊ะอยู่ในสถานะรอเคลียร์โต๊ะ', 'success');
            
            // ปิด modal และรีเฟรชข้อมูล
            const modal = bootstrap.Modal.getInstance(document.getElementById('tableDetailsModal'));
            if (modal) modal.hide();
            
            // รีเฟรชข้อมูลโต๊ะ
            loadTables();
        } else {
            throw new Error(data.error || 'ไม่สามารถอัปเดตสถานะการชำระเงินได้');
        }
    } catch (error) {
        console.error('Error completing payment:', error);
        
        if (error.name === 'AbortError') {
            showAlert('⚠️ การดำเนินการใช้เวลานานเกินไป กรุณาลองใหม่อีกครั้ง', 'warning');
        } else {
            showAlert(`❌ เกิดข้อผิดพลาด: ${error.message}`, 'danger');
        }
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันสำหรับพิมพ์ใบเสร็จ
// ฟังก์ชันรวมสำหรับพิมพ์ใบเสร็จ - รองรับทั้งการพิมพ์ครั้งแรกและการพิมพ์ซ้ำ
async function printReceipt(identifier, isReprint = false) {
    try {
        console.log('Printing receipt for:', identifier, 'isReprint:', isReprint);
        console.log('Current receipt data:', window.receiptData);
        showLoading(true);
        
        // ถ้าเป็นการพิมพ์ซ้ำ (identifier คือ orderId)
        if (isReprint) {
            // ดึงข้อมูลใบเสร็จจาก API
            const response = await fetch(`/api/orders/${identifier}`);
            const data = await response.json();
            
            if (!data.success || !data.data.table_id) {
                throw new Error(data.error || 'ไม่สามารถดึงข้อมูลใบเสร็จได้');
            }
            
            // ตั้งค่า receiptData ให้เหมือนกับที่ checkoutTable ทำ
            window.receiptData = {
                tableId: data.data.table_id,
                table_id: data.data.table_id,
                order_id: data.data.order_id,  // เพิ่ม order_id
                orders: data.data.items || [],
                totalAmount: data.data.total_amount || 0,
                total_amount: data.data.total_amount || 0,
                arrivalTime: data.data.created_at,
                checkoutTime: data.data.completed_at || new Date().toLocaleString('sv-SE', { timeZone: 'Asia/Bangkok' }).replace(' ', 'T') + '.000Z',
                created_at: data.data.completed_at || new Date().toLocaleString('sv-SE', { timeZone: 'Asia/Bangkok' }).replace(' ', 'T') + '.000Z',
                session_created_at: data.data.created_at,
                checkout_at: data.data.completed_at || new Date().toLocaleString('sv-SE', { timeZone: 'Asia/Bangkok' }).replace(' ', 'T') + '.000Z'
            };
            
            // ใช้ tableId สำหรับการประมวลผลต่อไป
            const tableId = data.data.table_id;
            return await printReceipt(tableId, false); // เรียกตัวเองแบบไม่ใช่ reprint
        }
        
        // การพิมพ์ปกติ (identifier คือ tableId)
        const tableId = identifier;
        
        // ตรวจสอบว่ามีการกดปุ่มเช็คบิลแล้วหรือไม่
        const table = tables.find(t => t.table_id === tableId);
        if (!window.receiptData && table && table.status !== 'waiting_payment' && table.status !== 'needs_clearing' && table.status !== 'checkout') {
            throw new Error('กรุณากดปุ่มเช็คบิลก่อนพิมพ์ใบเสร็จ');
        }
        
        // ตรวจสอบว่ามีข้อมูลใบเสร็จที่ถูกต้องหรือไม่
        if (!window.receiptData || !window.receiptData.orders || window.receiptData.orders.length === 0) {
            console.log('No valid receipt data found, fetching from API...');
            // ถ้าไม่มีข้อมูลใบเสร็จ ให้ดึงข้อมูลจาก API
            const table = tables.find(t => t.table_id === tableId);
            const session_id = table ? table.session_id : null;
            
            console.log('Table info:', table);
            console.log('Session ID:', session_id);
            
            if (!session_id) {
                throw new Error('ไม่พบ session_id สำหรับโต๊ะนี้ ไม่สามารถพิมพ์ใบเสร็จได้');
            }
            
            // ลองดึงข้อมูลจาก API checkout ก่อน
            try {
                const checkoutResponse = await fetch(`http://localhost:5000/api/tables/${tableId}/checkout`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: session_id
                    })
                });
                
                const checkoutData = await checkoutResponse.json();
                console.log('Checkout API response:', checkoutData);
                
                if (checkoutData.success) {
                    // แปลงข้อมูลเวลาให้อยู่ในรูปแบบที่ถูกต้อง
                    let arrivalTime = null;
                    let checkoutTime = null;
                    
                    if (checkoutData.data.session_created_at) {
                        const arrivalDate = new Date(checkoutData.data.session_created_at);
                        const year = arrivalDate.getFullYear();
                        const month = String(arrivalDate.getMonth() + 1).padStart(2, '0');
                        const day = String(arrivalDate.getDate()).padStart(2, '0');
                        const hours = String(arrivalDate.getHours()).padStart(2, '0');
                        const minutes = String(arrivalDate.getMinutes()).padStart(2, '0');
                        const seconds = String(arrivalDate.getSeconds()).padStart(2, '0');
                        arrivalTime = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
                    }
                    
                    if (checkoutData.data.checkout_at) {
                        const checkoutDate = new Date(checkoutData.data.checkout_at);
                        const year = checkoutDate.getFullYear();
                        const month = String(checkoutDate.getMonth() + 1).padStart(2, '0');
                        const day = String(checkoutDate.getDate()).padStart(2, '0');
                        const hours = String(checkoutDate.getHours()).padStart(2, '0');
                        const minutes = String(checkoutDate.getMinutes()).padStart(2, '0');
                        const seconds = String(checkoutDate.getSeconds()).padStart(2, '0');
                        checkoutTime = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
                    }
                    
                    window.receiptData = {
                        ...checkoutData.data,
                        arrivalTime: arrivalTime,
                        checkoutTime: checkoutTime
                    };
                    console.log('Created receipt data from checkout API:', window.receiptData);
                    return await printReceipt(tableId); // เรียกฟังก์ชันตัวเองอีกครั้งหลังจากได้ข้อมูลแล้ว
                }
            } catch (checkoutError) {
                console.error('Error fetching from checkout API:', checkoutError);
                // ถ้าไม่สำเร็จ ให้ลองดึงข้อมูลจาก orders API แทน
            }
            
            // ดึงข้อมูลโต๊ะและออเดอร์
            const response = await fetch(`http://localhost:5000/api/tables/${tableId}/orders?session_id=${session_id}`);
            const data = await response.json();
            console.log('Orders API response:', data);
            
            if (!data.success) {
                throw new Error('ไม่สามารถดึงข้อมูลใบเสร็จได้');
            }
            
            if (!data.data.orders || data.data.orders.length === 0) {
                throw new Error('ไม่พบรายการอาหารสำหรับโต๊ะนี้');
            }
            
            // แปลงข้อมูลเวลาให้อยู่ในรูปแบบที่ถูกต้อง
            let arrivalTime = null;
            let checkoutTime = null;
            
            if (data.data.session_created_at) {
                const arrivalDate = new Date(data.data.session_created_at);
                const year = arrivalDate.getFullYear();
                const month = String(arrivalDate.getMonth() + 1).padStart(2, '0');
                const day = String(arrivalDate.getDate()).padStart(2, '0');
                const hours = String(arrivalDate.getHours()).padStart(2, '0');
                const minutes = String(arrivalDate.getMinutes()).padStart(2, '0');
                const seconds = String(arrivalDate.getSeconds()).padStart(2, '0');
                arrivalTime = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
            }
            
            if (data.data.checkout_at) {
                const checkoutDate = new Date(data.data.checkout_at);
                const year = checkoutDate.getFullYear();
                const month = String(checkoutDate.getMonth() + 1).padStart(2, '0');
                const day = String(checkoutDate.getDate()).padStart(2, '0');
                const hours = String(checkoutDate.getHours()).padStart(2, '0');
                const minutes = String(checkoutDate.getMinutes()).padStart(2, '0');
                const seconds = String(checkoutDate.getSeconds()).padStart(2, '0');
                checkoutTime = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
            }
            
            window.receiptData = {
                table_id: tableId,
                session_id: session_id,
                order_id: data.data.order_id,  // เพิ่ม order_id
                orders: data.data.orders,
                total_amount: data.data.total_amount,
                created_at: data.data.created_at,
                session_created_at: data.data.session_created_at,
                checkout_at: data.data.checkout_at,
                arrivalTime: arrivalTime,
                checkoutTime: checkoutTime
            };
            console.log('Created receipt data from orders API:', window.receiptData);
        }
        
        // สร้างหน้าต่างใหม่สำหรับพิมพ์ใบเสร็จ
        const printWindow = window.open('', '_blank');
        
        if (!printWindow) {
            throw new Error('ไม่สามารถเปิดหน้าต่างพิมพ์ได้ โปรดอนุญาตให้เว็บไซต์เปิดหน้าต่างใหม่');
        }
        
        // ตรวจสอบและปรับรูปแบบข้อมูลใบเสร็จให้ถูกต้อง
        const receiptData = window.receiptData;
        console.log('Using receipt data for printing:', receiptData);
        
        // ตรวจสอบว่ามีข้อมูลใบเสร็จหรือไม่
        if (!receiptData) {
            throw new Error('ไม่พบข้อมูลใบเสร็จ');
        }
        
        // ตรวจสอบว่ามีข้อมูลออเดอร์หรือไม่
        if (!receiptData.orders || receiptData.orders.length === 0) {
            throw new Error('ไม่พบรายการอาหารในใบเสร็จ');
        }
        
        // ตรวจสอบว่ามีข้อมูลโต๊ะหรือไม่
        if (!receiptData.table_id) {
            receiptData.table_id = tableId; // ใช้ tableId ที่ส่งเข้ามาถ้าไม่มีในข้อมูลใบเสร็จ
        }
        
        // ดึงข้อมูลร้านจาก localStorage
        const restaurantName = localStorage.getItem('restaurant_name') || 'ร้านอาหาร A-FOOD';
        const restaurantAddress = localStorage.getItem('restaurant_address') || 'สงขลา หาดใหญ่';
        const restaurantPhone = localStorage.getItem('restaurant_phone') || '02-xxx-xxxx';
        const restaurantTel = `โทร. ${restaurantPhone}`;
        
        // ตรวจสอบและกำหนดวันที่ใบเสร็จ
        let receiptDate;
        try {
            receiptDate = new Date(receiptData.created_at || new Date()).toLocaleString('th-TH', {
                timeZone: 'Asia/Bangkok',
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }).replace(/-/g, '/');
        } catch (error) {
            console.warn('Error formatting receipt date:', error);
            receiptDate = new Date().toLocaleString('th-TH', {
                timeZone: 'Asia/Bangkok',
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }).replace(/-/g, '/'); // ใช้วันที่ปัจจุบันถ้าแปลงวันที่ไม่สำเร็จ
        }
        
        // สร้าง HTML สำหรับใบเสร็จ
        let receiptHtml = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>ใบเสร็จ - โต๊ะ ${receiptData.table_id}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
                <style>
                    body {
                        font-family: 'Sarabun', Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background: white;
                    }
                    .receipt {
                        max-width: 80mm;
                        margin: 0 auto;
                        padding: 10px;
                        border: 1px solid #ddd;
                    }
                    .receipt-header {
                        text-align: center;
                        margin-bottom: 20px;
                    }
                    .receipt-title {
                        font-size: 18px;
                        font-weight: bold;
                        margin-bottom: 5px;
                    }
                    .receipt-info {
                        margin-bottom: 15px;
                        font-size: 14px;
                    }
                    .receipt-table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 15px;
                        font-size: 10px;
                        table-layout: fixed;
                    }
                    .receipt-table th, .receipt-table td {
                        padding: 2px;
                        text-align: left;
                        border-bottom: 1px dashed #ddd;
                        white-space: normal;
                        overflow: hidden;
                        line-height: 1.2;
                        max-height: 2.4em;
                        word-wrap: break-word;
                    }
                    .receipt-table th:nth-child(1), .receipt-table td:nth-child(1) {
                        width: 35%;
                        text-align: left;
                    }
                    .receipt-table th:nth-child(2), .receipt-table td:nth-child(2) {
                        width: 15%;
                        text-align: center;
                    }
                    .receipt-table th:nth-child(3), .receipt-table td:nth-child(3) {
                        width: 10%;
                        text-align: center;
                        white-space: nowrap;
                    }
                    .receipt-table th:nth-child(4), .receipt-table td:nth-child(4) {
                        width: 20%;
                        text-align: right;
                    }
                    .receipt-table th:nth-child(5), .receipt-table td:nth-child(5) {
                        width: 20%;
                        text-align: center;
                        font-size: 8px;
                    }
                    .receipt-total {
                        text-align: right;
                        font-weight: bold;
                        margin-top: 10px;
                        font-size: 16px;
                    }
                    .receipt-footer {
                        text-align: center;
                        margin-top: 20px;
                        font-size: 14px;
                    }
                    .qr-code {
                        text-align: center;
                        margin: 15px 0;
                    }
                    @media print {
                        body {
                            padding: 0;
                            margin: 0;
                        }
                        .receipt {
                            width: 100%;
                            border: none;
                        }
                        .no-print {
                            display: none;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="receipt">
                    <div class="receipt-header">
                        <div class="receipt-title">${restaurantName}</div>
                        <div>${restaurantAddress}</div>
                        <div>${restaurantTel}</div>
                    </div>
                    
                    <div class="receipt-info">
                        <div>ใบเสร็จรับเงิน${receiptData.order_id ? ` : Order ID No.${String(receiptData.order_id).padStart(4, '0')}` : ''}</div>
                        <div>โต๊ะ: ${receiptData.table_id}</div>
                        <div>วันที่: ${receiptDate}</div>
                        ${receiptData.arrivalTime ? `<div>เวลาที่มาถึง: ${receiptData.arrivalTime}</div>` : ''}
                        ${receiptData.checkoutTime ? `<div>เวลาเช็คบิล: ${receiptData.checkoutTime}</div>` : ''}
                    </div>
                    
                    <table class="receipt-table">
                        <thead>
                            <tr>
                                <th>เมนู</th>
                                <th>ราคา</th>
                                <th>จำนวน</th>
                                <th>รวม</th>
                                <th>หมายเหตุ</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        // เพิ่มรายการอาหาร
        if (receiptData.orders && receiptData.orders.length > 0) {
            // เรียงลำดับรายการอาหารตามชื่อ
            const sortedOrders = [...receiptData.orders].sort((a, b) => {
                const nameA = (a.menu_name || a.menu_item_name || a.name || '').toLowerCase();
                const nameB = (b.menu_name || b.menu_item_name || b.name || '').toLowerCase();
                return nameA.localeCompare(nameB);
            });
            
            // รวมรายการที่ซ้ำกัน
            const groupedOrders = {};
            
            sortedOrders.forEach(order => {
                // ตรวจสอบรูปแบบข้อมูลและปรับให้ถูกต้อง
                const menuName = order.item_name || order.menu_name || order.menu_item_name || order.name || 'รายการอาหาร';
                const quantity = order.quantity || 1;
                const price = order.price || (order.total ? order.total / quantity : 0);
                const total = order.total || order.total_price || (price * quantity) || 0;
                const status = order.status || order.item_status || 'completed';
                
                // ดึง addon options จาก customer_request (ส่วนที่ 2)
                let specialOptions = '';
                if (order.customer_request) {
                    if (order.customer_request.includes(' | ')) {
                        const parts = order.customer_request.split(' | ');
                        if (parts.length >= 2 && parts[1] !== 'ไม่เพิ่ม') {
                            specialOptions = parts[1] || ''; // addon options อยู่ในส่วนที่ 2
                        }
                    }
                }
                
                // สร้างคีย์ที่รวมชื่อเมนู สถานะ และตัวเลือกพิเศษ
                const orderKey = `${menuName}_${status}_${specialOptions}`;
                
                if (!groupedOrders[orderKey]) {
                    groupedOrders[orderKey] = {
                        menuName,
                        price,
                        quantity: 0,
                        total: 0,
                        status,
                        specialOptions
                    };
                }
                
                // เพิ่มจำนวนและยอดรวม (ไม่รวมรายการที่ถูก reject)
                groupedOrders[orderKey].quantity += quantity;
                if (status !== 'rejected') {
                    groupedOrders[orderKey].total += parseFloat(total);
                }
            });
            
            // แสดงรายการที่รวมแล้ว
            Object.values(groupedOrders).forEach(item => {
                const unitPrice = item.status === 'rejected' ? 0 : (item.price || (item.total / item.quantity));
                const statusText = item.status === 'rejected' ? 'ยกเลิก' : '';
                const itemTotal = item.status === 'rejected' ? '฿0.00' : `฿${parseFloat(item.total).toFixed(2)}`;
                
                // แสดงชื่อเมนูพร้อมตัวเลือกพิเศษ (ถ้ามี)
                let displayName = item.menuName;
                if (item.specialOptions && item.specialOptions.trim() !== '') {
                    displayName += `<br><small style="color: #666;">(${item.specialOptions})</small>`;
                }
                
                receiptHtml += `
                    <tr>
                        <td>${displayName}</td>
                        <td>฿${parseFloat(unitPrice).toFixed(2)}</td>
                        <td>${item.quantity}</td>
                        <td>${itemTotal}</td>
                        <td>${statusText}</td>
                    </tr>
                `;
                
                console.log('Added grouped order item:', item);
            });
        }
        
        receiptHtml += `
                        </tbody>
                    </table>
                    
                    <div class="receipt-total">
                        ยอดรวมทั้งหมด: ฿${(() => {
                            // คำนวณยอดรวมจากรายการอาหารที่ไม่ถูกยกเลิก
                            if (!receiptData.total_amount) {
                                const calculatedTotal = receiptData.orders.reduce((sum, order) => {
                                    const status = order.status || order.item_status || 'completed';
                                    if (status === 'rejected') return sum; // ไม่นับรายการที่ถูกยกเลิก
                                    const price = parseFloat(order.total || order.total_price || order.price || 0);
                                    const quantity = parseInt(order.quantity || 1);
                                    return sum + (price * quantity);
                                }, 0);
                                return calculatedTotal.toFixed(2);
                            }
                            // คำนวณยอดรวมใหม่โดยไม่นับรายการที่ถูกยกเลิก
                            const adjustedTotal = receiptData.orders.reduce((sum, order) => {
                                const status = order.status || order.item_status || 'completed';
                                if (status === 'rejected') return sum;
                                const price = parseFloat(order.total || order.total_price || order.price || 0);
                                const quantity = parseInt(order.quantity || 1);
                                return sum + (price * quantity);
                            }, 0);
                            return adjustedTotal.toFixed(2);
                        })()}
                    </div>
                    

                    
                    ${(() => {
                        const promptpayNumber = localStorage.getItem('promptpay_number') || '0906016218';
                        const totalAmount = (() => {
                            if (!receiptData.total_amount) {
                                return receiptData.orders.reduce((sum, order) => {
                                    const status = order.status || order.item_status || 'completed';
                                    if (status === 'rejected') return sum;
                                    const price = parseFloat(order.total || order.total_price || order.price || 0);
                                    const quantity = parseInt(order.quantity || 1);
                                    return sum + (price * quantity);
                                }, 0);
                            }
                            return receiptData.orders.reduce((sum, order) => {
                                const status = order.status || order.item_status || 'completed';
                                if (status === 'rejected') return sum;
                                const price = parseFloat(order.total || order.total_price || order.price || 0);
                                const quantity = parseInt(order.quantity || 1);
                                return sum + (price * quantity);
                            }, 0);
                        })();
                        
                        if (promptpayNumber && totalAmount > 0) {
                            return `
                            <div class="qr-code">
                                <div>สแกนเพื่อชำระเงิน</div>
                                <div id="promptpay-qr-container"></div>
                                <script>
                                    // สร้าง PromptPay QR Code ที่ถูกต้อง
                                    const qrContainer = document.getElementById('promptpay-qr-container');
                                    
                                    // เรียก API เพื่อสร้าง PromptPay QR Code
                                    fetch('/api/promptpay/generate-qr', {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json'
                                        },
                                        body: JSON.stringify({
                                            amount: ${totalAmount.toFixed(2)}
                                        })
                                    })
                                    .then(response => response.json())
                                    .then(data => {
                                        if (data.success) {
                                            const qrImg = document.createElement('img');
                                            qrImg.width = 150;
                                            qrImg.height = 150;
                                            qrImg.style.border = '1px solid #ddd';
                                            qrImg.src = 'data:image/png;base64,' + data.qr_code;
                                            qrContainer.appendChild(qrImg);
                                        } else {
                                            qrContainer.innerHTML = '<div style="color: red;">ไม่สามารถสร้าง QR Code ได้</div>';
                                        }
                                    })
                                    .catch(error => {
                                        console.error('Error generating QR code:', error);
                                        qrContainer.innerHTML = '<div style="color: red;">เกิดข้อผิดพลาดในการสร้าง QR Code</div>';
                                    });
                                </script>
                            </div>
                            `;
                        } else if (receiptData.promptpay_qr) {
                            return `
                            <div class="qr-code">
                                <div>สแกนเพื่อชำระเงิน</div>
                                <img src="data:image/png;base64,${receiptData.promptpay_qr}" width="150" height="150">
                            </div>
                            `;
                        }
                        return '';
                    })()}
                    
                    <div class="receipt-footer">
                        <div>${localStorage.getItem('receipt_footer_text') || 'ขอบคุณที่ใช้บริการ'}</div>
                        <div style="margin-top: 10px; font-size: 12px;">
                            <div>หมายเลขพร้อมเพย์: ${localStorage.getItem('promptpay_number') || '0906016218'}</div>
                            <div>หมายเลขบัญชี: ${localStorage.getItem('bank_account_number') || '4067305940'}</div>
                            <div>ชื่อบัญชี: ${localStorage.getItem('bank_account_name') || 'อภิชาติ สุขเสนา'}</div>
                            <div>ธนาคาร: ${localStorage.getItem('bank_name') || 'ไทยพานิชย์'}</div>
                        </div>
                    </div>
                </div>
                
                <div class="no-print" style="text-align: center; margin-top: 20px;">
                    <button id="printButton" style="padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">
                        <i class="fas fa-print"></i> พิมพ์ใบเสร็จ
                    </button>
                    <button id="closeButton" style="padding: 10px 20px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        <i class="fas fa-times"></i> ปิดหน้าต่าง
                    </button>
                    
                    <script>
                        document.getElementById('printButton').addEventListener('click', function() {
                            window.print();
                        });
                        
                        document.getElementById('closeButton').addEventListener('click', function() {
                            window.close();
                        });
                    </script>
                </div>
            </body>
            </html>
        `;
        
        printWindow.document.write(receiptHtml);
        printWindow.document.close();
        
        // ให้ JavaScript ทำงานใน printWindow
        printWindow.onload = function() {
            // เพิ่มการตรวจสอบว่าหน้าต่างถูกปิดหรือไม่
            const checkWindowInterval = setInterval(() => {
                if (printWindow.closed) {
                    clearInterval(checkWindowInterval);
                    console.log('Print window was closed');
                }
            }, 1000);
            
            // ถ้าต้องการให้พิมพ์อัตโนมัติ ให้เปิดบรรทัดนี้
            // printWindow.print();
            showAlert('เตรียมข้อมูลใบเสร็จสำเร็จ กรุณากดปุ่มพิมพ์ใบเสร็จในหน้าต่างใหม่', 'success');
        };
        
    } catch (error) {
        console.error('Error printing receipt:', error);
        showAlert(`ไม่สามารถพิมพ์ใบเสร็จได้: ${error.message}`, 'danger');
        
        // ล้างข้อมูลใบเสร็จเพื่อให้ลองใหม่ในครั้งถัดไป
        window.receiptData = null;
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันสำหรับเคลียร์โต๊ะ
async function clearTable(tableId) {
    // ค้นหาข้อมูลโต๊ะเพื่อดึงสถานะปัจจุบัน
    const table = tables.find(t => t.table_id === tableId);
    const status = table ? table.status : null;
    
    // ถ้าสถานะเป็น needs_clearing ไม่ต้องแสดงกล่องยืนยัน
    if (status !== 'needs_clearing' && !confirm('คุณต้องการเคลียร์โต๊ะนี้หรือไม่?')) {
        return;
    }
    
    try {
        showLoading(true);
        
        // ค้นหาข้อมูลโต๊ะเพื่อดึง session_id ก่อนเคลียร์
        const oldSessionId = table ? table.session_id : null;
        console.log(`[DEBUG] clearTable: Clearing table ${tableId} with session_id: ${oldSessionId}`);
        
        const response = await fetch(`http://localhost:5000/api/tables/${tableId}/clear`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log(`[DEBUG] clearTable: Table ${tableId} cleared successfully. Old session_id from server: ${data.old_session_id}`);
            showAlert('เคลียร์โต๊ะสำเร็จ', 'success');
            
            // ล้างข้อมูลใบเสร็จเมื่อมีการกดเคลียร์โต๊ะ
            window.receiptData = null;
            console.log('[DEBUG] clearTable: Receipt data cleared');
            
            // ตรวจสอบและอัปเดตปุ่มพิมพ์ใบเสร็จให้เป็นปุ่มที่ถูก disable
            const actionButtons = document.getElementById('table-action-buttons');
            if (actionButtons) {
                const activePrintButton = Array.from(actionButtons.children).find(btn => 
                    btn.classList.contains('btn-info') && btn.innerHTML.includes('พิมพ์ใบเสร็จ'));
                    
                if (activePrintButton) {
                    const disabledPrintButton = document.createElement('button');
                    disabledPrintButton.type = 'button';
                    disabledPrintButton.className = 'btn btn-secondary me-2';
                    disabledPrintButton.disabled = true;
                    disabledPrintButton.title = 'ต้องกดเช็คบิลก่อน';
                    disabledPrintButton.innerHTML = '<i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ';
                    actionButtons.replaceChild(disabledPrintButton, activePrintButton);
                    console.log('Replaced active print button with disabled one');
                }
            }
            
            // รีเฟรชข้อมูลโต๊ะและตรวจสอบว่า session_id ถูกล้างแล้วจริงๆ
            await loadTables();
            
            // ปิด modal และรีเฟรชข้อมูล
            const modal = bootstrap.Modal.getInstance(document.getElementById('tableDetailsModal'));
            if (modal) {
                modal.hide();
                // เปิด modal ใหม่เพื่อแสดงข้อมูลล่าสุด
                setTimeout(() => showTableDetail(tableId), 100);
            }
            
            // ตรวจสอบว่าโต๊ะถูกเคลียร์ session_id แล้วจริงๆ
            const updatedTable = tables.find(t => t.table_id === tableId);
            console.log(`[DEBUG] clearTable: Table ${tableId} after clearing - session_id: ${updatedTable ? updatedTable.session_id : 'table not found'}`);
        } else {
            throw new Error(data.error || 'ไม่สามารถเคลียร์โต๊ะได้');
        }
    } catch (error) {
        console.error('Error clearing table:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันสำหรับกำหนดสี badge ตามสถานะ
function getStatusBadgeColor(status) {
    switch(status) {
        case 'available': return 'success';
        case 'occupied': return 'primary';
        case 'needs_checkout': return 'warning';
        case 'waiting_payment': return 'info';
        case 'needs_clearing': return 'warning';
        case 'checkout': return 'secondary';
        case 'calling': return 'danger';
        default: return 'secondary';
    }
}

async function clearTable() {
    if (!selectedTableId) return;
    
    if (!confirm('คุณต้องการเคลียร์โต๊ะนี้หรือไม่?')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`http://localhost:5000/api/tables/${selectedTableId}/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('เคลียร์โต๊ะสำเร็จ', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('tableDetailsModal'));
            if (modal) modal.hide();
            
            // รอสักครู่แล้วค่อย refresh เพื่อให้ backend อัปเดตข้อมูลเสร็จ
            setTimeout(async () => {
                await refreshTables();
            }, 200);
        } else {
            throw new Error(data.error || 'ไม่สามารถเคลียร์โต๊ะได้');
        }
        
    } catch (error) {
        console.error('Error clearing table:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

async function refreshTables() {
    try {
        // แสดงสถานะการโหลด
        const refreshBtn = document.querySelector('button[onclick="refreshTables()"]');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>กำลังรีเฟรช...';
        }
        
        // เพิ่ม delay เล็กน้อยเพื่อให้ backend มีเวลาอัปเดตข้อมูล
        await new Promise(resolve => setTimeout(resolve, 100));
        await loadTables();
        
        // คืนสถานะปุ่ม
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i>รีเฟรช';
        }
    } catch (error) {
        console.error('Error refreshing tables:', error);
        // คืนสถานะปุ่มในกรณีเกิดข้อผิดพลาด
        const refreshBtn = document.querySelector('button[onclick="refreshTables()"]');
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i>รีเฟรช';
        }
    }
}

// Menu Management
async function loadMenuCategories() {
    try {
        const response = await fetch('http://localhost:5000/api/menu/categories');
        const data = await response.json();
        
        // API ส่งข้อมูลเป็น array โดยตรง
        menuCategories = data;
        renderCategories();
        updateCategorySelect();
    } catch (error) {
        console.error('Error loading categories:', error);
        showAlert('ไม่สามารถโหลดหมวดหมู่เมนูได้: ' + error.message, 'danger');
    }
}

async function loadMenuItems() {
    try {
        const url = currentCategory ? `/api/menu/items/all?category_id=${currentCategory}` : '/api/menu/items/all';
        const response = await fetch(url);
        const data = await response.json();
        
        // ตรวจสอบว่า API ส่งข้อมูลในรูปแบบใด
        if (data.success) {
            menuItems = data.data;
        } else if (Array.isArray(data)) {
            menuItems = data;
        } else {
            throw new Error('รูปแบบข้อมูลไม่ถูกต้อง');
        }
        renderMenuItems();
    } catch (error) {
        console.error('Error loading menu items:', error);
        showAlert('ไม่สามารถโหลดรายการเมนูได้: ' + error.message, 'danger');
    }
}

function renderCategories() {
    const container = document.getElementById('categories-list');
    if (!container) {
        console.warn('categories-list element not found, skipping renderCategories');
        return;
    }
    container.innerHTML = '';
    
    // เพิ่มปุ่มแสดงสินค้าทั้งหมด
    const allItemsDiv = document.createElement('div');
    allItemsDiv.className = 'category-item';
    allItemsDiv.onclick = () => {
        currentCategory = null;
        loadMenuItems();
        // เพิ่มคลาส active ให้กับปุ่มแสดงสินค้าทั้งหมด
        document.querySelectorAll('.category-item').forEach(item => item.classList.remove('active'));
        allItemsDiv.classList.add('active');
    };
    allItemsDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <div class="category-name">สินค้าทั้งหมด</div>
                <div class="category-count">${menuItems.length} รายการ</div>
            </div>
        </div>
    `;
    container.appendChild(allItemsDiv);
    
    menuCategories.forEach((category, index) => {
        const itemCount = menuItems.filter(item => item.category_id === category.category_id).length;
        
        const div = document.createElement('div');
        div.className = 'category-item';
        div.onclick = () => {
            currentCategory = category.category_id;
            loadMenuItems();
            // เพิ่มคลาส active ให้กับหมวดหมู่ที่เลือก
            document.querySelectorAll('.category-item').forEach(item => item.classList.remove('active'));
            div.classList.add('active');
        };
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="category-name">${category.name}</div>
                    <div class="category-count">${itemCount} รายการ</div>
                </div>
                <div class="d-flex align-items-center">
                    <div class="btn-group me-2" role="group">
                        <button class="btn btn-sm btn-outline-secondary" onclick="event.stopPropagation(); moveCategoryUp(${category.category_id})" 
                                ${index === 0 ? 'disabled' : ''} title="เลื่อนขึ้น">
                            <i class="fas fa-chevron-up"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="event.stopPropagation(); moveCategoryDown(${category.category_id})" 
                                ${index === menuCategories.length - 1 ? 'disabled' : ''} title="เลื่อนลง">
                            <i class="fas fa-chevron-down"></i>
                        </button>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="event.stopPropagation(); editCategory(${category.category_id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); deleteCategory(${category.category_id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(div);
    });
}

function renderMenuItems() {
    const container = document.getElementById('menu-items-list');
    if (!container) {
        console.warn('menu-items-list element not found, skipping renderMenuItems');
        return;
    }
    container.innerHTML = '';
    
    // สร้าง row container สำหรับ Bootstrap grid
    const row = document.createElement('div');
    row.className = 'row';
    
    menuItems.forEach(item => {
        const category = menuCategories.find(cat => cat.category_id === item.category_id);
        
        // สร้าง column wrapper
        const col = document.createElement('div');
        col.className = 'col-lg-6 col-md-6 col-sm-12 mb-3';
        
        const div = document.createElement('div');
        div.className = 'menu-item h-100';
        div.innerHTML = `
            <div class="menu-item-header">
                <div>
                    <div class="menu-item-name">${item.name}</div>
                    <small class="text-muted">${category ? category.name : 'ไม่ระบุหมวดหมู่'}</small>
                </div>
                <div class="menu-item-price">${formatCurrency(item.price)}</div>
            </div>
            ${item.description ? `<div class="menu-item-description">${item.description}</div>` : ''}
            <div class="d-flex justify-content-between align-items-center">
                <div class="availability-toggle">
                    <label class="toggle-switch">
                        <input type="checkbox" ${item.is_available ? 'checked' : ''} 
                               onchange="toggleMenuAvailability(${item.item_id}, this.checked)">
                        <span class="toggle-slider"></span>
                    </label>
                    <span class="toggle-label ${item.is_available ? 'available' : 'unavailable'}">${item.is_available ? 'พร้อมให้บริการ' : 'ไม่พร้อมให้บริการ'}</span>
                </div>
                <div class="menu-item-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="editMenuItem(${item.item_id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteMenuItem(${item.item_id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        col.appendChild(div);
        row.appendChild(col);
    });
    
    container.appendChild(row);
    
    // อัปเดตจำนวนเมนูที่พร้อมและไม่พร้อมให้บริการ
    updateMenuCounts();
}

function updateMenuCounts() {
    const availableCount = menuItems.filter(item => item.is_available).length;
    const unavailableCount = menuItems.filter(item => !item.is_available).length;
    
    const availableElement = document.getElementById('available-count');
    const unavailableElement = document.getElementById('unavailable-count');
    
    if (availableElement) {
        availableElement.textContent = availableCount;
    }
    
    if (unavailableElement) {
        unavailableElement.textContent = unavailableCount;
    }
}

function updateCategorySelect() {
    const select = document.getElementById('menu-category');
    if (!select) {
        console.warn('menu-category element not found, skipping updateCategorySelect');
        return;
    }
    select.innerHTML = '<option value="">เลือกหมวดหมู่</option>';
    
    menuCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.category_id;
        option.textContent = category.name;
        select.appendChild(option);
    });
}

function showAddCategoryModal() {
    const modal = new bootstrap.Modal(document.getElementById('addCategoryModal'));
    modal.show();
}

async function showAddMenuModal() {
    try {
        // ดึงข้อมูลเมนูทั้งหมด
        const menuResponse = await fetch('/api/menu/items');
        const menuData = await menuResponse.json();
        
        if (!menuData.success) {
            throw new Error('ไม่สามารถดึงข้อมูลเมนูได้');
        }
        
        // ดึงข้อมูลหมวดหมู่
        const categoryResponse = await fetch('/api/menu/categories');
        const categoryData = await categoryResponse.json();
        
        const menuItems = menuData.data || [];
        const categories = Array.isArray(categoryData) ? categoryData : (categoryData.success ? categoryData.data || [] : []);
        
        // สร้าง modal สำหรับเลือกเมนู
        let modalHtml = `
            <div class="modal fade" id="addMenuModal" tabindex="-1" style="z-index: 1060;">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">เพิ่มรายการอาหาร</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <!-- ช่องค้นหา -->
                            <div class="mb-3">
                                <div class="input-group">
                                    <span class="input-group-text"><i class="fas fa-search"></i></span>
                                    <input type="text" class="form-control" id="menuSearchInput" placeholder="ค้นหาเมนู..." onkeyup="filterMenuItems()">
                                </div>
                            </div>
                            
                            <!-- ปุ่มหมวดหมู่ -->
                            <div class="mb-3">
                                <div class="btn-group flex-wrap" role="group">
                                    <button type="button" class="btn btn-outline-primary active" onclick="filterByCategory('all')" id="category-all">ทั้งหมด</button>
        `;
        
        // เพิ่มปุ่มหมวดหมู่
        categories.forEach(category => {
            modalHtml += `
                                    <button type="button" class="btn btn-outline-primary" onclick="filterByCategory(${category.category_id})" id="category-${category.category_id}">${category.name}</button>
            `;
        });
        
        modalHtml += `
                                </div>
                            </div>
                            
                            <!-- รายการเมนู -->
                            <div class="row" id="menuItemsContainer">
        `;
        
        menuItems.forEach(item => {
            modalHtml += `
                <div class="col-md-6 col-lg-4 mb-3 menu-item" data-category="${item.category_id || 0}" data-name="${item.name.toLowerCase()}">
                    <div class="card h-100">
                        <div class="card-body">
                            <h6 class="card-title">${item.name}</h6>
                            <p class="card-text text-muted small">${item.description || ''}</p>
                            <p class="card-text"><strong>฿${(item.price || 0).toFixed(2)}</strong></p>
                            <button type="button" class="btn btn-primary btn-sm w-100" 
                                    onclick="addMenuItemToOrder(${item.item_id}, '${item.name}', ${item.price})">
                                <i class="fas fa-plus me-1"></i>เพิ่ม
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        modalHtml += `
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ปิด</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // ลบ modal เก่าถ้ามี
        const existingModal = document.getElementById('addMenuModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // เพิ่ม modal ใหม่
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // แสดง modal
        const modal = new bootstrap.Modal(document.getElementById('addMenuModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading menu items:', error);
        showAlert('ไม่สามารถโหลดรายการเมนูได้', 'danger');
    }
}

// ฟังก์ชันกรองเมนูตามหมวดหมู่
function filterByCategory(categoryId) {
    const menuItems = document.querySelectorAll('.menu-item');
    const categoryButtons = document.querySelectorAll('[id^="category-"]');
    
    // อัปเดตสถานะปุ่ม
    categoryButtons.forEach(btn => btn.classList.remove('active'));
    document.getElementById(`category-${categoryId}`).classList.add('active');
    
    // กรองรายการเมนู
    menuItems.forEach(item => {
        if (categoryId === 'all' || item.dataset.category == categoryId) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// ฟังก์ชันค้นหาเมนู
function filterMenuItems() {
    const searchInput = document.getElementById('menuSearchInput');
    const searchTerm = searchInput.value.toLowerCase();
    const menuItems = document.querySelectorAll('.menu-item');
    
    menuItems.forEach(item => {
        const itemName = item.dataset.name;
        if (itemName.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
    
    // รีเซ็ตการเลือกหมวดหมู่เมื่อค้นหา
    if (searchTerm) {
        const categoryButtons = document.querySelectorAll('[id^="category-"]');
        categoryButtons.forEach(btn => btn.classList.remove('active'));
    }
}

// ฟังก์ชันสำหรับแสดง modal เพิ่มเมนูใหม่
function showCreateMenuModal() {
    console.log('showCreateMenuModal called');
    
    // แสดง modal ที่มีอยู่แล้วใน HTML สำหรับสร้างเมนูใหม่
    const modal = new bootstrap.Modal(document.getElementById('addMenuModal'));
    modal.show();
    
    // โหลดหมวดหมู่เมนูลงใน dropdown หลังจากแสดง modal แล้ว
    setTimeout(() => {
        loadMenuCategoriesForForm();
    }, 100);
}

// ฟังก์ชันโหลดหมวดหมู่เมนูสำหรับฟอร์ม
async function loadMenuCategoriesForForm() {
    console.log('loadMenuCategoriesForForm called');
    try {
        console.log('Fetching categories from API...');
        const response = await fetch('http://localhost:5000/api/menu/categories');
        console.log('API response:', response);
        const data = await response.json();
        console.log('API data:', data);
        
        const categorySelect = document.getElementById('menu-category');
        console.log('Category select element:', categorySelect);
        categorySelect.innerHTML = '<option value="">เลือกหมวดหมู่</option>';
        
        if (Array.isArray(data) && data.length > 0) {
            console.log('Categories found:', data.length);
            data.forEach(category => {
                console.log('Adding category:', category);
                const option = document.createElement('option');
                option.value = category.category_id;
                option.textContent = category.name;
                categorySelect.appendChild(option);
            });
        } else if (data.success && data.data) {
            console.log('Categories found (wrapped):', data.data.length);
            data.data.forEach(category => {
                console.log('Adding category:', category);
                const option = document.createElement('option');
                option.value = category.category_id;
                option.textContent = category.name;
                categorySelect.appendChild(option);
            });
        } else {
            console.log('No categories data found');
        }
    } catch (error) {
        console.error('Error loading categories for form:', error);
    }
}

async function addCategory() {
    const name = document.getElementById('category-name').value.trim();
    const description = document.getElementById('category-description').value.trim();
    
    if (!name) {
        showAlert('กรุณาระบุชื่อหมวดหมู่', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('http://localhost:5000/api/menu/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                description: description
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('เพิ่มหมวดหมู่สำเร็จ', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('add-category-form').reset();
            
            // Refresh data
            loadMenuCategories();
        } else {
            throw new Error(data.error || 'ไม่สามารถเพิ่มหมวดหมู่ได้');
        }
        
    } catch (error) {
        console.error('Error adding category:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

async function addMenuItem() {
    const name = document.getElementById('menu-name').value.trim();
    const categoryId = document.getElementById('menu-category').value;
    const price = parseFloat(document.getElementById('menu-price').value);
    const description = document.getElementById('menu-description').value.trim();
    const imageUrl = document.getElementById('menu-image').value.trim();
    const isAvailable = document.getElementById('menu-available').checked;
    
    // รวบรวมประเภทตัวเลือกอาหาร
    const checkedOptions = document.querySelectorAll('input[name="option-type"]:checked');
    let foodOptionType = 'none'; // ค่า default
    
    // ตรวจสอบ checkbox ที่ถูกเลือก
    for (const option of checkedOptions) {
        if (option.value === 'spice') {
            foodOptionType = 'spice';
            break; // ให้ความสำคัญกับ spice
        } else if (option.value === 'sweet') {
            foodOptionType = 'sweet';
        } else if (option.value === 'special') {
            foodOptionType = 'special';
        }
        // ถ้าเลือก none อย่างเดียว จะใช้ค่า default ที่ตั้งไว้
    }
    
    if (!name || !categoryId || !price) {
        showAlert('กรุณากรอกข้อมูลที่จำเป็น', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('http://localhost:5000/api/menu/items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                category_id: parseInt(categoryId),
                price: price,
                description: description,
                image_url: imageUrl,
                is_available: isAvailable,
                food_option_type: foodOptionType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('เพิ่มเมนูสำเร็จ', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addMenuModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('add-menu-form').reset();
            
            // Refresh data
            loadMenuItems();
        } else {
            throw new Error(data.error || 'ไม่สามารถเพิ่มเมนูได้');
        }
        
    } catch (error) {
        console.error('Error adding menu item:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

function refreshMenu() {
    loadMenuCategories();
    loadMenuItems();
}

// Orders Management
async function loadOrders() {
    try {
        console.log('Loading orders...');
        const response = await fetch('http://localhost:5000/api/orders');
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API response data:', data);
        
        if (data.success) {
            orders = data.data;
            console.log('Orders loaded:', orders.length);

            renderOrders();
        } else {
            throw new Error(data.error || 'ไม่สามารถโหลดรายการสั่งอาหารได้');
        }
    } catch (error) {
        console.error('Error loading orders:', error);
        showAlert(error.message, 'danger');
    }
}

function renderOrders() {
    const container = document.getElementById('orders-list');
    if (!container) {
        console.error('Element with id "orders-list" not found');
        return;
    }
    container.innerHTML = '';
    
    if (orders.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-receipt fa-3x mb-3"></i>
                <p>ไม่มีรายการสั่งอาหาร</p>
            </div>
        `;
        return;
    }
    
    // จัดกลุ่มออเดอร์ตามโต๊ะ
    const ordersByTable = {};
    orders.forEach(order => {
        const tableKey = order.table_id || order.table_name;
        if (!ordersByTable[tableKey]) {
            ordersByTable[tableKey] = {
                table_id: order.table_id,
                table_name: order.table_name || 'โต๊ะ ' + order.table_id,
                session_id: order.session_id, // เพิ่ม session_id
                order_number: order.order_id, // เพิ่มหมายเลขคำสั่งซื้อ
                orders: [],
                total_amount: 0,
                latest_order_time: order.created_at
            };
        }
        ordersByTable[tableKey].orders.push(order);
        
        // หาหมายเลขคำสั่งซื้อที่เล็กที่สุดของโต๊ะนี้ (คำสั่งซื้อแรก)
        if (order.order_id < ordersByTable[tableKey].order_number) {
            ordersByTable[tableKey].order_number = order.order_id;
        }
        
        // คำนวณยอดรวมของโต๊ะ (ใช้ราคารวมที่ frontend คำนวณแล้วรวม special options)
        let orderTotal = 0;
        order.items.forEach(item => {
            // ไม่รวมรายการที่ถูกปฏิเสธในการคำนวณยอดรวม
            if (item.status !== 'rejected') {
                // ใช้ราคารวมจาก frontend ที่รวม special options แล้ว
                orderTotal += item.total_price || (item.quantity * item.price);
            }
        });
        ordersByTable[tableKey].total_amount += orderTotal;
        
        // อัพเดทเวลาล่าสุด
        if (new Date(order.created_at) > new Date(ordersByTable[tableKey].latest_order_time)) {
            ordersByTable[tableKey].latest_order_time = order.created_at;
        }
    });
    
    // สร้างการ์ดโต๊ะขนาดใหญ่ (แสดงเฉพาะโต๊ะที่มี session_id)
    Object.values(ordersByTable).forEach(tableData => {
        // ซ่อนการ์ดของโต๊ะที่ไม่มี session_id (ถูกปิดเซสชั่นแล้ว)
        if (!tableData.session_id) {
            return;
        }
        
        const tableCard = document.createElement('div');
        tableCard.className = 'col-md-4 col-sm-6 col-12 mb-3';
        
        const cardContent = document.createElement('div');
        cardContent.className = 'table-order-card';
        
        // สร้างรายการอาหารทั้งหมดของโต๊ะ
        let allItemsHTML = '';
        let pendingCount = 0;
        let acceptedCount = 0;
        let completedCount = 0;
        let rejectedCount = 0;
        
        // รวบรวมรายการอาหารทั้งหมดพร้อมข้อมูลออเดอร์
        let allItems = [];
        tableData.orders.forEach(order => {
            order.items.forEach(item => {
                allItems.push({
                    ...item,
                    order_created_at: order.created_at
                });
            });
        });
        
        // เรียงลำดับรายการตาม order_item_id (ใหม่ไปเก่า - ID ใหญ่ไปเล็ก)
        allItems.sort((a, b) => {
            return b.order_item_id - a.order_item_id;
        });
        
        allItems.forEach(item => {
                // นับสถานะตามสถานะของแต่ละรายการ
                const itemStatus = item.status || 'pending';
                switch(itemStatus) {
                    case 'pending': pendingCount++; break;
                    case 'accepted': acceptedCount++; break;
                    case 'completed': completedCount++; break;
                    case 'rejected': rejectedCount++; break;
                }
                // ใช้ราคารวมที่ frontend คำนวณแล้วรวม special options
                const itemTotal = item.total_price || (item.quantity * item.price);
                const canAcceptItem = itemStatus === 'pending';
                
                // แยกแสดงตัวเลือกพิเศษและหมายเหตุ
                let specialOptionsDisplay = '';
                let itemNameWithSpice = item.name; // ประกาศตัวแปรข้างนอก if block
                
                if (item.customer_request) {
                    // แยกตัวเลือกพิเศษออกจากหมายเหตุ (ถ้ามี | คั่น)
                    const parts = item.customer_request.split(' | ');
                    // แยกตัวเลือก spice และ addon
                    const spiceOptions = parts.filter(part => 
                        part.includes('เผ็ด') || part.includes('หวาน') || part.includes('ปกติ')
                    );
                    const addonOptions = parts.filter(part => 
                        part.includes('ไข่') || part.includes('เพิ่ม')
                    ).filter(part => !part.includes('ไม่เพิ่ม')); // กรอง "ไม่เพิ่ม" ออก
                    
                    const notes = parts.filter(part => 
                        !part.includes('เผ็ด') && !part.includes('หวาน') && 
                        !part.includes('ไข่') && !part.includes('เพิ่ม') &&
                        !part.includes('ไม่เพิ่ม') && !part.includes('ปกติ')
                    );
                    
                    // รวม spice options เข้ากับชื่อเมนูในวงเล็บ
                    if (spiceOptions.length > 0) {
                        itemNameWithSpice += ` <span class="${getCustomerRequestClass(spiceOptions[0])}">(${spiceOptions[0]})</span>`;
                    }
                    
                    // แสดง addon options เป็นรายการด้านล่าง
                    if (addonOptions.length > 0) {
                        const addonList = addonOptions.map(option => `<div class="text-muted small">- ${option}</div>`).join('');
                        specialOptionsDisplay += `<div class="mt-1">${addonList}</div>`;
                    }
                    
                    if (notes.length > 0) {
                        specialOptionsDisplay += `<div class="special-notes"><i class="fas fa-sticky-note me-1"></i>${notes.join(', ')}</div>`;
                    }
                }
                
                allItemsHTML += `
                    <div class="table-order-item">
                        <div class="item-info">
                            <div class="item-name">
                                ${itemNameWithSpice}
                            </div>
                            ${specialOptionsDisplay}
                            <div class="item-details">
                                <span class="item-qty">จำนวน: ${item.quantity}</span>
                                <span class="item-price">${itemStatus === 'rejected' ? 
                                    `<span style="text-decoration: line-through; color: #6c757d;">${formatCurrency(itemTotal)}</span><br><span style="color: #dc3545; font-weight: bold;">${formatCurrency(0)}</span>` : 
                                    formatCurrency(itemTotal)
                                }</span>
                            </div>
                        </div>
                        <div class="item-actions">
                            <div class="order-status-badge">
                                ${getItemStatusBadge(itemStatus)}
                            </div>
                            ${canAcceptItem ? `
                                <div class="d-flex gap-2">
                                    <button class="btn btn-danger btn-sm" onclick="rejectOrderItem(${item.order_item_id})" title="ปฏิเสธรายการนี้">
                                        <i class="fas fa-times me-1"></i>ปฏิเสธ
                                    </button>
                                    <button class="btn btn-success btn-sm" onclick="acceptOrderItem(${item.order_item_id})" title="รับรายการนี้">
                                        <i class="fas fa-check me-1"></i>รับรายการ
                                    </button>
                                </div>
                            ` : ''}
                            ${itemStatus === 'accepted' ? `
                                <button class="btn btn-warning btn-sm mt-1" onclick="completeOrderItem(${item.order_item_id})" title="ทำเครื่องหมายเสร็จสิ้น">
                                    <i class="fas fa-check-double me-1"></i>เสร็จสิ้น
                                </button>
                            ` : ''}
                        </div>
                    </div>
                `;        });
        
        // สร้างสถิติสถานะ
        let statusSummary = '';
        if (pendingCount > 0) statusSummary += `<span class="status-count pending">${pendingCount} รอดำเนินการ</span>`;
        if (acceptedCount > 0) statusSummary += `<span class="status-count accepted">${acceptedCount} รับแล้ว</span>`;
        if (completedCount > 0) statusSummary += `<span class="status-count completed">${completedCount} เสร็จสิ้น</span>`;
        if (rejectedCount > 0) statusSummary += `<span class="status-count rejected">${rejectedCount} ปฏิเสธ</span>`;
        
        // สร้างปุ่มจัดการ
        let actionButtons = '';
        const hasActiveOrders = pendingCount > 0 || acceptedCount > 0;
        
        // แสดงปุ่มเสมอ แต่ปุ่มบางตัวจะแสดงเฉพาะเมื่อมี active orders
        actionButtons = `
            <div class="table-actions">
                ${hasActiveOrders && pendingCount > 0 ? `
                    <button class="btn btn-success btn-sm" onclick="acceptAllTableOrders('${tableData.table_id}')">
                        <i class="fas fa-check-double me-1"></i>รับทั้งหมด
                    </button>
                ` : ''}
                <button class="btn btn-outline-primary btn-sm" onclick="showTableOrderDetails('${tableData.table_id}')">
                    <i class="fas fa-eye me-1"></i>รายละเอียดทั้งหมด
                </button>
                ${hasActiveOrders && acceptedCount > 0 ? `
                    <button class="btn btn-warning btn-sm" onclick="completeAllTableOrders('${tableData.table_id}')">
                        <i class="fas fa-check me-1"></i>เสร็จสิ้นทั้งหมด
                    </button>
                ` : ''}
            </div>
        `;
        
        // สร้าง session indicator
        const sessionIndicator = tableData.session_id ? 
            `<span class="session-indicator" title="Session ID: ${tableData.session_id}">
                <i class="fas fa-circle text-success"></i>
                <small class="text-muted ms-1">#${tableData.session_id.substring(0, 8)}</small>
            </span>` : '';
        
        // ลบปุ่มปิดเซสชั่นออก
        const closeSessionButton = '';

        cardContent.innerHTML = `
            <div class="table-card-header">
                <div class="table-info">
                    <h4 class="table-name">
                        <i class="fas fa-utensils me-2"></i>${tableData.table_name}
                        ${sessionIndicator}
                        ${closeSessionButton}
                    </h4>
                    <div class="table-meta">
                        <span class="order-number">
                            <i class="fas fa-hashtag me-1"></i>No.${String(tableData.order_number).padStart(4, '0')}
                        </span>
                        <span class="order-time">
                            <i class="fas fa-clock me-1"></i>${formatDateTime(tableData.latest_order_time)}
                        </span>
                        <span class="order-count">
                            <i class="fas fa-list me-1"></i>${tableData.orders.reduce((total, order) => total + order.items.length, 0)} รายการ
                        </span>
                    </div>
                </div>
                <div class="table-total">
                    <div class="total-amount">${formatCurrency(tableData.total_amount)}</div>
                    <div class="total-label">ยอดรวม</div>
                </div>
            </div>
            
            <div class="status-summary">
                ${statusSummary}
            </div>
            
            <div class="table-order-items">
                ${allItemsHTML}
            </div>
            
            ${actionButtons}
        `;
        
        tableCard.appendChild(cardContent);
        container.appendChild(tableCard);
    });
}

// ฟังก์ชันช่วยเหลือสำหรับสถานะออเดอร์
function getOrderStatusBadge(status) {
    switch(status) {
        case 'pending':
            return '<span class="badge bg-warning">รอดำเนินการ</span>';
        case 'accepted':
            return '<span class="badge bg-primary">รับแล้ว</span>';
        case 'completed':
            return '<span class="badge bg-success">เสร็จสิ้น</span>';
        case 'rejected':
            return '<span class="badge bg-danger">ปฏิเสธ</span>';
        default:
            return '<span class="badge bg-warning">รอดำเนินการ</span>';
    }
}

// ฟังก์ชันช่วยเหลือสำหรับสถานะรายการอาหาร
function getItemStatusBadge(status) {
    switch(status) {
        case 'pending':
            return '<span class="badge bg-warning">รอดำเนินการ</span>';
        case 'accepted':
            return '<span class="badge bg-primary">รับแล้ว</span>';
        case 'completed':
            return '<span class="badge bg-success">เสร็จสิ้น</span>';
        case 'rejected':
            return '<span class="badge bg-danger">ปฏิเสธ</span>';
        case undefined:
        case null:
        case '':
            return '<span class="badge bg-primary">ไม่ระบุ</span>';
        default:
            return '<span class="badge bg-warning">รอดำเนินการ</span>';
    }
}

// ฟังก์ชันรับออเดอร์แต่ละรายการ
async function acceptSingleOrder(orderId) {
    if (!confirm('คุณต้องการรับออเดอร์นี้หรือไม่?')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/orders/${orderId}/accept`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            showAlert('รับออเดอร์เรียบร้อยแล้ว', 'success');
            loadOrders();
        } else {
            throw new Error('Failed to accept order');
        }
    } catch (error) {
        console.error('Error accepting order:', error);
        showAlert('เกิดข้อผิดพลาดในการรับออเดอร์', 'danger');
    }
}

// ฟังก์ชันทำเครื่องหมายออเดอร์แต่ละรายการว่าเสร็จสิ้น
async function completeSingleOrder(orderId) {
    if (!confirm('คุณต้องการทำเครื่องหมายออเดอร์นี้ว่าเสร็จสิ้นหรือไม่?')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/orders/${orderId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            showAlert('ทำเครื่องหมายเสร็จสิ้นเรียบร้อยแล้ว', 'success');
            loadOrders();
        } else {
            throw new Error('Failed to complete order');
        }
    } catch (error) {
        console.error('Error completing order:', error);
        showAlert('เกิดข้อผิดพลาดในการทำเครื่องหมายเสร็จสิ้น', 'danger');
    }
}

// ฟังก์ชันพิมพ์ใบเสร็จสำหรับโต๊ะ
async function reprintTableReceipt(tableId) {
    try {
        showLoading(true);
        
        // หาออเดอร์ล่าสุดของโต๊ะนี้
        const tableOrders = orders.filter(order => order.table_id == tableId);
        if (tableOrders.length === 0) {
            showAlert('ไม่พบออเดอร์สำหรับโต๊ะนี้', 'warning');
            return;
        }
        
        // ใช้ออเดอร์ล่าสุด
        const latestOrder = tableOrders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];
        
        const response = await fetch(`http://localhost:5000/api/orders/${latestOrder.order_id}`);
        const data = await response.json();
        
        if (data.success) {
            // สร้างหน้าต่างใหม่สำหรับพิมพ์
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>ใบเสร็จ #${latestOrder.order_id}</title>
                    <style>
                        body { font-family: 'Sarabun', sans-serif; margin: 20px; }
                        .receipt { max-width: 300px; margin: 0 auto; }
                        .header { text-align: center; margin-bottom: 20px; }
                        .order-info { margin-bottom: 15px; }
                        .items { margin-bottom: 15px; }
                        .item { display: flex; justify-content: space-between; margin-bottom: 5px; }
                        .total { border-top: 1px solid #000; padding-top: 10px; font-weight: bold; }
                        .footer { text-align: center; margin-top: 20px; font-size: 12px; }
                        @media print {
                            body { margin: 0; }
                            .no-print { display: none; }
                        }
                    </style>
                </head>
                <body>
                    <div class="receipt">
                        <div class="header">
                            <h2>ร้านอาหารดีลิเชียส</h2>
                            <p>ใบเสร็จ #${latestOrder.order_id}</p>
                        </div>
                        <div class="order-info">
                            <p>โต๊ะ: ${data.data.table_name || `โต๊ะ ${data.data.table_id}`}</p>
                            <p>วันที่: ${new Date(data.data.created_at).toLocaleString('th-TH', {
                            timeZone: 'Asia/Bangkok',
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        }).replace(/-/g, '/')}</p>
                        </div>
                        <div class="items">
            `);
            
            if (data.data.items && data.data.items.length > 0) {
                data.data.items.forEach(item => {
                    printWindow.document.write(`
                        <div class="item">
                            <span>${item.name} x ${item.quantity}</span>
                            <span>${item.total_price ? item.total_price.toLocaleString() : (item.unit_price * item.quantity).toLocaleString()} บาท</span>
                        </div>
                    `);
                    if (item.customer_request) {
                        printWindow.document.write(`<div style="font-size: 12px; color: #666; margin-left: 10px;">หมายเหตุ: ${item.customer_request}</div>`);
                    }
                });
            }
            
            printWindow.document.write(`
                        </div>
                        <div class="total">
                            <div style="display: flex; justify-content: space-between;">
                                <span>ยอดรวม:</span>
                                <span>${data.data.total_amount ? data.data.total_amount.toLocaleString() : '0'} บาท</span>
                            </div>
                        </div>
                        <div class="footer">
                            <p>ขอบคุณที่ใช้บริการ</p>
                            <p>พิมพ์เมื่อ: ${new Date().toLocaleString('th-TH', {
                            timeZone: 'Asia/Bangkok',
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        }).replace(/-/g, '/')}</p>
                        </div>
                    </div>
                    <div class="no-print" style="text-align: center; margin-top: 20px;">
                        <button onclick="window.print()">พิมพ์</button>
                        <button onclick="window.close()">ปิด</button>
                    </div>
                </body>
                </html>
            `);
            
            printWindow.document.close();
            
            // พิมพ์อัตโนมัติ
            setTimeout(() => {
                printWindow.print();
            }, 500);
            
            showAlert('เปิดหน้าต่างพิมพ์ใบเสร็จแล้ว', 'success');
            
        } else {
            throw new Error(data.error || 'ไม่สามารถสร้างใบเสร็จได้');
        }
    } catch (error) {
        console.error('Error reprinting receipt:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันปฏิเสธออเดอร์แต่ละรายการ
async function rejectSingleOrder(orderId) {
    if (!confirm('คุณต้องการปฏิเสธออเดอร์นี้หรือไม่? ราคาจะถูกเปลี่ยนเป็น 0')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/orders/${orderId}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            showAlert('ปฏิเสธออเดอร์เรียบร้อยแล้ว', 'success');
            loadOrders();
        } else {
            throw new Error('Failed to reject order');
        }
    } catch (error) {
        console.error('Error rejecting order:', error);
        showAlert('เกิดข้อผิดพลาดในการปฏิเสธออเดอร์', 'danger');
    }
}

// ฟังก์ชันจัดการออเดอร์ทั้งโต๊ะ
async function acceptAllTableOrders(tableId) {
    // หารายการที่รอดำเนินการในโต๊ะนี้
    const tableOrders = orders.filter(order => order.table_id == tableId);
    
    // รวบรวม order items ที่มีสถานะ pending
    let pendingItems = [];
    tableOrders.forEach(order => {
        if (order.items) {
            order.items.forEach(item => {
                if (item.status === 'pending') {
                    pendingItems.push(item);
                }
            });
        }
    });
    
    if (pendingItems.length === 0) {
        showAlert('ไม่มีรายการที่รอดำเนินการในโต๊ะนี้', 'warning');
        return;
    }
    
    if (!confirm(`คุณต้องการรับรายการทั้งหมด ${pendingItems.length} รายการของโต๊ะนี้หรือไม่?`)) {
        return;
    }
    
    try {
        // ใช้ order_item_id แทน order_id
        for (const item of pendingItems) {
            await fetch(`/api/order-items/${item.order_item_id}/accept`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
        }
        
        showAlert('รับรายการทั้งหมดเรียบร้อยแล้ว', 'success');
        loadOrders();
    } catch (error) {
        console.error('Error accepting all table orders:', error);
        showAlert('เกิดข้อผิดพลาดในการรับรายการ', 'danger');
    }
}

async function completeAllTableOrders(tableId) {
    // หารายการ order items ที่ยังไม่เสร็จสิ้นในโต๊ะนี้
    const acceptedItems = [];
    orders.filter(order => order.table_id == tableId).forEach(order => {
        order.items.forEach(item => {
            if (item.status === 'accepted') {
                acceptedItems.push(item);
            }
        });
    });
    
    if (acceptedItems.length === 0) {
        showAlert('ไม่มีรายการที่รับแล้วในโต๊ะนี้', 'warning');
        return;
    }
    
    if (!confirm(`คุณต้องการทำเครื่องหมายรายการทั้งหมด ${acceptedItems.length} รายการของโต๊ะนี้ว่าเสร็จสิ้นหรือไม่?`)) {
        return;
    }
    
    try {
        for (const item of acceptedItems) {
            await fetch(`http://localhost:5000/api/order-items/${item.order_item_id}/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
        }
        
        showAlert('ทำเครื่องหมายรายการทั้งหมดเป็นเสร็จสิ้นแล้ว', 'success');
        loadOrders();
    } catch (error) {
        console.error('Error completing all table orders:', error);
        showAlert('เกิดข้อผิดพลาดในการทำเครื่องหมายรายการ', 'danger');
    }
}

// ฟังก์ชันปิดเซสชั่นโต๊ะ
async function closeTableSession(tableId, sessionId) {
    if (!confirm(`คุณต้องการปิดเซสชั่น ${sessionId.substring(0, 8)} ของโต๊ะนี้หรือไม่?\n\nข้อมูลจะถูกบันทึกและโต๊ะจะถูกเคลียร์`)) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/tables/${tableId}/close-session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        if (response.ok) {
            showAlert('ปิดเซสชั่นและบันทึกข้อมูลเรียบร้อยแล้ว', 'success');
            loadOrders(); // รีโหลดข้อมูลออเดอร์
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to close session');
        }
    } catch (error) {
        console.error('Error closing table session:', error);
        showAlert('เกิดข้อผิดพลาดในการปิดเซสชั่น: ' + error.message, 'danger');
    }
}

function showTableOrderDetails(tableId) {
    const tableOrders = orders.filter(order => order.table_id == tableId);
    
    if (tableOrders.length === 0) {
        showAlert('ไม่พบออเดอร์สำหรับโต๊ะนี้', 'warning');
        return;
    }
    
    // แสดงรายละเอียดออเดอร์ทั้งหมดของโต๊ะในโมดัล
    let detailsHTML = '';
    tableOrders.forEach(order => {
        detailsHTML += `
            <div class="order-detail-section">
                <h6>ออเดอร์ #${order.order_id} - ${getOrderStatusBadge(order.status)}</h6>
                <small class="text-muted">${formatDateTime(order.created_at)}</small>
                <div class="order-items-detail">
        `;
        
        order.items.forEach(item => {
            // กำหนดสถานะ badge สำหรับแต่ละรายการ
            let itemStatusBadge = getItemStatusBadge(item.status).replace('badge', 'badge ms-2');
            
            let menuDisplay = item.name;
            

            // Parse customer_request to display spice level
            if (item.customer_request) {
                if (item.customer_request.includes(' | ')) {
                    const parts = item.customer_request.split(' | ');
                    if (parts[0] && parts[0].trim()) {
                        menuDisplay += ` <span class="text-muted small">(${parts[0].trim()})</span>`;
                    }
                } else {
                    menuDisplay += ` <span class="text-muted small">(${item.customer_request.trim()})</span>`;
                }
            }
            
            detailsHTML += `
                 <div class="item-detail-row">
                     <span>${menuDisplay}${itemStatusBadge}</span>
                     <span>x${item.quantity}</span>
                     <span>${formatCurrency(item.quantity * item.price)}</span>
                 </div>
             `;
         });
        
        detailsHTML += `
                </div>
            </div>
            <hr>
        `;
    });
    
    // แสดงในโมดัล
    showOrderDetailsModal(tableId, detailsHTML);
}

// ฟังก์ชันแสดงรายละเอียดออเดอร์ในโมดัล
function showOrderDetailsModal(tableId, detailsHTML) {
    // สร้างโมดัลแบบไดนามิก
    const modalHTML = `
        <div class="modal fade" id="tableOrderModal" tabindex="-1" aria-labelledby="tableOrderModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="tableOrderModalLabel">
                            <i class="fas fa-utensils me-2"></i>รายละเอียดออเดอร์ - โต๊ะ ${tableId}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="table-order-details">
                            ${detailsHTML}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ปิด</button>
                        <button type="button" class="btn btn-primary" onclick="printTableReceipt('${tableId}')">
                            <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบโมดัลเก่าถ้ามี
    const existingModal = document.getElementById('tableOrderModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่มโมดัลใหม่
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // แสดงโมดัล
    const modal = new bootstrap.Modal(document.getElementById('tableOrderModal'));
    modal.show();
    
    // ลบโมดัลเมื่อปิด
    document.getElementById('tableOrderModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

// ฟังก์ชันพิมพ์ใบเสร็จสำหรับโต๊ะ
function printTableReceipt(tableId) {
    const tableOrders = orders.filter(order => order.table_id == tableId);
    
    if (tableOrders.length === 0) {
        showAlert('ไม่พบออเดอร์สำหรับโต๊ะนี้', 'warning');
        return;
    }
    
    // รวมรายการอาหารทั้งหมด
    const allItems = {};
    let totalAmount = 0;
    
    tableOrders.forEach(order => {
        order.items.forEach(item => {
            // ไม่รวมรายการที่ถูกปฏิเสธในการพิมพ์ใบเสร็จ
            if (item.status !== 'rejected') {
                // ดึง addon options จาก customer_request (ส่วนที่ 2)
                let specialOptions = '';
                if (item.customer_request) {
                    if (item.customer_request.includes(' | ')) {
                        const parts = item.customer_request.split(' | ');
                        if (parts.length >= 2 && parts[1] !== 'ไม่เพิ่ม') {
                            specialOptions = parts[1] || ''; // addon options อยู่ในส่วนที่ 2
                        }
                    }
                }
                
                const key = `${item.name}_${specialOptions}`;
                if (allItems[key]) {
                    allItems[key].quantity += item.quantity;
                    allItems[key].total += item.quantity * item.price;
                } else {
                    allItems[key] = {
                        name: item.name,
                        price: item.price,
                        quantity: item.quantity,
                        total: item.quantity * item.price,
                        specialOptions: specialOptions
                    };
                }
                totalAmount += item.quantity * item.price;
            }
        });
    });
    
    // สร้างหน้าต่างพิมพ์
    const printWindow = window.open('', '_blank');
    const printContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>ใบเสร็จ - โต๊ะ ${tableId}</title>
            <style>
                body { font-family: 'Sarabun', sans-serif; margin: 20px; }
                .receipt-header { text-align: center; margin-bottom: 20px; }
                .receipt-title { font-size: 18px; font-weight: bold; }
                .receipt-info { margin: 10px 0; }
                .items-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .items-table th, .items-table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                .items-table th { background-color: #f5f5f5; }
                .total-row { font-weight: bold; font-size: 16px; }
                .print-date { text-align: right; margin-top: 20px; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="receipt-header">
                <div class="receipt-title">ใบเสร็จรวม</div>
                <div class="receipt-info">โต๊ะ: ${tableId}</div>
                <div class="receipt-info">จำนวนออเดอร์: ${tableOrders.length} รายการ</div>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>รายการ</th>
                        <th>จำนวน</th>
                        <th>ราคา/หน่วย</th>
                        <th>รวม</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.values(allItems).map(item => `
                        <tr>
                            <td>
                                ${item.name}
                                ${item.specialOptions && item.specialOptions.trim() !== '' ? `<br><small style="color: #666;">(${item.specialOptions})</small>` : ''}
                            </td>
                            <td>${item.quantity}</td>
                            <td>${formatCurrency(item.price)}</td>
                            <td>${formatCurrency(item.total)}</td>
                        </tr>
                    `).join('')}
                </tbody>
                <tfoot>
                    <tr class="total-row">
                        <td colspan="3">รวมทั้งสิ้น</td>
                        <td>${formatCurrency(totalAmount)}</td>
                    </tr>
                </tfoot>
            </table>
            
            <div class="print-date">
                พิมพ์เมื่อ: ${new Date().toLocaleString('th-TH', {
                        timeZone: 'Asia/Bangkok',
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                    }).replace(/-/g, '/')}
            </div>
            
            <script>
                window.onload = function() {
                    window.print();
                    window.onafterprint = function() {
                        window.close();
                    };
                };
            </script>
        </body>
        </html>
    `;
    
    printWindow.document.write(printContent);
    printWindow.document.close();
}

function filterOrders(status) {
    // Implementation for filtering orders
    console.log('Filter orders by status:', status);
}

function getCustomerRequestClass(customerRequest) {
    if (!customerRequest) return '';
    
    const request = customerRequest.toLowerCase();
    
    // เผ็ดมาก ให้ใช้สีแดง
    if (request.includes('เผ็ดมาก')) {
        return 'text-danger';
    }
    
    // เผ็ดน้อย ให้ใช้สีฟ้า
    if (request.includes('เผ็ดน้อย')) {
        return 'text-info';
    }
    
    // หวานมาก ให้ใช้สีชมพู
    if (request.includes('หวานมาก')) {
        return 'text-pink';
    }
    
    // หวานน้อย ให้ใช้สีฟ้า
    if (request.includes('หวานน้อย')) {
        return 'text-info';
    }
    
    // ปกติ (ทั้งเผ็ดปกติและหวานปกติ) ให้ใช้สีเทากลาง
    return 'text-secondary';
}

function refreshOrders() {
    loadOrders();
}




// Order Management Functions
async function acceptOrder(orderId) {
    try {
        const response = await fetch(`http://localhost:5000/api/orders/${orderId}/accept`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            loadOrders(); // รีเฟรชรายการออเดอร์
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error accepting order:', error);
        showAlert('เกิดข้อผิดพลาดในการรับออเดอร์', 'danger');
    }
}

async function rejectOrder(orderId) {
    if (!confirm('คุณแน่ใจหรือไม่ที่จะปฏิเสธออเดอร์นี้?')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/orders/${orderId}/reject`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            loadOrders(); // รีเฟรชรายการออเดอร์
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error rejecting order:', error);
        showAlert('เกิดข้อผิดพลาดในการปฏิเสธออเดอร์', 'danger');
    }
}

async function completeOrder(orderId) {
    try {
        const response = await fetch(`http://localhost:5000/api/orders/${orderId}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('ออเดอร์เสร็จสิ้นแล้ว', 'success');
            loadOrders(); // รีเฟรชรายการออเดอร์
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error completing order:', error);
        showAlert('เกิดข้อผิดพลาดในการทำเครื่องหมายออเดอร์เสร็จสิ้น', 'danger');
    }
}

async function showOrderDetails(orderId) {
    try {
        const response = await fetch(`http://localhost:5000/api/orders/${orderId}/items`);
        const data = await response.json();
        
        if (data.success) {
            displayOrderDetailsModal(orderId, data.data);
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error loading order details:', error);
        showAlert('เกิดข้อผิดพลาดในการโหลดรายละเอียดออเดอร์', 'danger');
    }
}

function displayOrderDetailsModal(orderId, items) {
    let itemsHTML = '';
    
    items.forEach(item => {
        let statusBadge = '';
        let actionButtons = '';
        
        // Use getItemStatusBadge function for consistent status display
        statusBadge = getItemStatusBadge(item.status);
        
        // Set action buttons based on status
        if (item.status === 'pending') {
            actionButtons = `
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-success" onclick="acceptOrderItem(${item.order_item_id})">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="rejectOrderItem(${item.order_item_id})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
        }
        
        itemsHTML += `
            <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                <div class="flex-grow-1">
                    <div class="fw-bold">${item.name}${item.customer_request ? ` <span class="${getCustomerRequestClass(item.customer_request)} small">(${item.customer_request})</span>` : ''}</div>
                    <div class="text-muted small">จำนวน: ${item.quantity} | ราคา: ${formatCurrency(item.unit_price * item.quantity)}</div>
                </div>
                <div class="d-flex align-items-center gap-2">
                    ${statusBadge}
                    ${actionButtons}
                </div>
            </div>
        `;
    });
    
    const modalHTML = `
        <div class="modal fade" id="orderDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">รายละเอียดออเดอร์ #${orderId}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${itemsHTML}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ปิด</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่าถ้ามี
    const existingModal = document.getElementById('orderDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal ใหม่
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('orderDetailsModal'));
    modal.show();
}

async function acceptOrderItem(orderItemId) {
    try {
        const response = await fetch(`http://localhost:5000/api/order-items/${orderItemId}/accept`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            // รีเฟรชข้อมูลออเดอร์
            loadOrders();
            // Refresh table details if currently viewing a table detail modal
            const tableDetailModal = document.getElementById('tableDetailModal');
            if (tableDetailModal && tableDetailModal.classList.contains('show') && selectedTableId) {
                // Re-fetch and update table details without closing the modal
                await showTableDetail(selectedTableId);
            }
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error accepting order item:', error);
        showAlert('เกิดข้อผิดพลาดในการรับรายการ', 'danger');
    }
}

async function rejectOrderItem(orderItemId) {
    if (!confirm('คุณแน่ใจหรือไม่ที่จะปฏิเสธรายการนี้?')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/order-items/${orderItemId}/reject`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            // รีเฟรชข้อมูลออเดอร์
            loadOrders();
            // Refresh table details if currently viewing a table detail modal
            const tableDetailModal = document.getElementById('tableDetailModal');
            if (tableDetailModal && tableDetailModal.classList.contains('show') && selectedTableId) {
                // Re-fetch and update table details without closing the modal
                await showTableDetail(selectedTableId);
            }
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error rejecting order item:', error);
        showAlert('เกิดข้อผิดพลาดในการปฏิเสธรายการ', 'danger');
    }
}

// Setup notification sound
function setupNotificationSound() {
    // Create audio context for notification sound
    try {
        notificationSound = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT');
        notificationSound.volume = 0.5;
    } catch (e) {
        console.log('Audio notification not supported');
    }
}

// Check for new orders
async function checkForNewOrders() {
    try {
        // ตรวจสอบออเดอร์ใหม่
        const response = await fetch('/api/orders');
        const data = await response.json();
        
        if (data.success) {
            const currentOrderCount = data.data.length;
            
            // Check if there are new orders
            if (lastOrderCount > 0 && currentOrderCount > lastOrderCount) {
                const newOrdersCount = currentOrderCount - lastOrderCount;
                
                // ดึงออเดอร์ใหม่ที่เพิ่งเข้ามา
                const newOrders = data.data.slice(0, newOrdersCount);
                
                // Show notification with table information
                showOrderNotification(newOrdersCount, newOrders);
                
                // Play sound if available
                if (notificationSound) {
                    notificationSound.play().catch(e => console.log('Could not play sound'));
                }
                
                // Update orders display if on orders section
                if (currentSection === 'orders') {
                    orders = data.data;
                    // ใช้ setTimeout เพื่อป้องกัน infinite loop
                    setTimeout(() => {
                        renderOrders();
                    }, 100);
                }
            }
            
            lastOrderCount = currentOrderCount;
        }
        
        // ลบการเรียก checkForNewNotifications ออกเพื่อป้องกันการ polling ซ้ำซ้อน
        // การแจ้งเตือนจะถูกจัดการโดย startNotificationPolling() แยกต่างหาก
        
    } catch (error) {
        console.error('Error checking for new orders:', error);
    }
}

// Show order notification
function showOrderNotification(count, newOrders = []) {
    let message;
    let tableId = null;
    
    if (count === 1 && newOrders.length > 0) {
        // แสดงข้อมูลโต๊ะสำหรับออเดอร์เดียว
        const order = newOrders[0];
        tableId = order.table_id;
        message = `โต๊ะ ${order.table_id}: มีออเดอร์ใหม่ 1 รายการ!`;
    } else if (count > 1) {
        // แสดงจำนวนออเดอร์ใหม่ทั้งหมด
        if (newOrders.length > 0) {
            const tableNumbers = newOrders.map(order => order.table_id).join(', ');
            tableId = newOrders[0].table_id; // ใช้โต๊ะแรกเป็นตัวแทน
            message = `โต๊ะ ${tableNumbers}: มีออเดอร์ใหม่ ${count} รายการ!`;
        } else {
            message = `มีออเดอร์ใหม่ ${count} รายการ!`;
        }
    } else {
        message = 'มีออเดอร์ใหม่ 1 รายการ!';
    }
    
    // ไม่บันทึกการแจ้งเตือนลงฐานข้อมูลเพื่อป้องกันการแจ้งเตือนซ้ำซ้อน
    // การแจ้งเตือนออเดอร์ใหม่จะถูกจัดการโดยระบบอื่นแล้ว
    
    // Update page title with notification
    document.title = `(${count}) ระบบจัดการร้านอาหาร - Admin Panel`;
    
    // Reset title after 5 seconds
    setTimeout(() => {
        document.title = 'ระบบจัดการร้านอาหาร - Admin Panel';
    }, 5000);
    
    // Show browser notification if permission granted
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('ออเดอร์ใหม่!', {
            body: message,
            icon: '/icon.ico'
        });
    } else if ('Notification' in window && Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                new Notification('ออเดอร์ใหม่!', {
                    body: message,
                    icon: '/icon.ico'
                });
            }
        });
    }
    


}

// Settings Management
async function loadSettings() {
    // Load current settings from server or localStorage
    const promptpayType = localStorage.getItem('promptpay_type') || 'phone';
    const promptpayValue = localStorage.getItem('promptpay_value') || '';
    const domainUrl = localStorage.getItem('domain_url') || '';
    const sheetId = localStorage.getItem('sheet_id') || '';
    const sheetName = localStorage.getItem('sheet_name') || 'ยอดขาย';
    
    // Load restaurant settings from API first, then fallback to localStorage
    let restaurantName = 'ร้านอาหาร A-FOOD';
    let restaurantAddress = 'สงขลา หาดใหญ่';
    let restaurantPhone = '02-xxx-xxxx';
    
    try {
        const response = await fetch('/api/restaurant-info');
        if (response.ok) {
            const result = await response.json();
            if (result.success && result.data) {
                restaurantName = result.data.name;
                restaurantAddress = result.data.address;
                restaurantPhone = result.data.phone;
            }
        }
    } catch (error) {
        console.log('Failed to load restaurant info from API, using localStorage:', error);
        // Fallback to localStorage
        restaurantName = localStorage.getItem('restaurant_name') || restaurantName;
        restaurantAddress = localStorage.getItem('restaurant_address') || restaurantAddress;
        restaurantPhone = localStorage.getItem('restaurant_phone') || restaurantPhone;
    }
    
    // Load receipt settings
    const receiptFooterText = localStorage.getItem('receipt_footer_text') || 'ขอบคุณที่ใช้บริการ';
    const promptpayNumber = localStorage.getItem('promptpay_number') || '0906016218';
    const bankAccountNumber = localStorage.getItem('bank_account_number') || '4067305940';
    const bankAccountName = localStorage.getItem('bank_account_name') || 'อภิชาติ สุขเสนา';
    const bankName = localStorage.getItem('bank_name') || 'ไทยพานิชย์';
    
    // ตรวจสอบว่า element มีอยู่ก่อนกำหนดค่า
    const promptpayTypeEl = document.getElementById('promptpay-type');
    const promptpayValueEl = document.getElementById('promptpay-value');
    const domainUrlEl = document.getElementById('domain-url');
    const sheetIdEl = document.getElementById('sheet-id');
    const sheetNameEl = document.getElementById('sheet-name');
    
    // Restaurant and receipt elements
    const restaurantNameEl = document.getElementById('restaurant-name');
    const restaurantAddressEl = document.getElementById('restaurant-address');
    const restaurantPhoneEl = document.getElementById('restaurant-phone');
    const receiptFooterTextEl = document.getElementById('receipt-footer-text');
    const promptpayNumberEl = document.getElementById('promptpay-number');
    const bankAccountNumberEl = document.getElementById('bank-account-number');
    const bankAccountNameEl = document.getElementById('bank-account-name');
    const bankNameEl = document.getElementById('bank-name');
    
    if (promptpayTypeEl) promptpayTypeEl.value = promptpayType;
    if (promptpayValueEl) promptpayValueEl.value = promptpayValue;
    if (domainUrlEl) domainUrlEl.value = domainUrl;
    if (sheetIdEl) sheetIdEl.value = sheetId;
    if (sheetNameEl) sheetNameEl.value = sheetName;
    
    // Set restaurant and receipt values
    if (restaurantNameEl) restaurantNameEl.value = restaurantName;
    if (restaurantAddressEl) restaurantAddressEl.value = restaurantAddress;
    if (restaurantPhoneEl) restaurantPhoneEl.value = restaurantPhone;
    if (receiptFooterTextEl) receiptFooterTextEl.value = receiptFooterText;
    if (promptpayNumberEl) promptpayNumberEl.value = promptpayNumber;
    if (bankAccountNumberEl) bankAccountNumberEl.value = bankAccountNumber;
    if (bankAccountNameEl) bankAccountNameEl.value = bankAccountName;
    if (bankNameEl) bankNameEl.value = bankName;
}

// Function to show success modal
function showSuccessModal(message) {
    // สร้าง modal element
    const modalHtml = `
        <div class="modal fade" id="successModal" tabindex="-1" aria-labelledby="successModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title" id="successModalLabel">
                            <i class="fas fa-check-circle me-2"></i>สำเร็จ!
                        </h5>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-3">
                            <i class="fas fa-check-circle text-success" style="font-size: 3rem;"></i>
                        </div>
                        <h4>${message}</h4>
                        <p class="text-muted">หน้าต่างนี้จะปิดอัตโนมัติใน <span id="countdown">3</span> วินาที</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // เพิ่ม modal เข้าไปใน body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('successModal'));
    modal.show();
    
    // นับถอยหลัง 3 วินาที
    let countdown = 3;
    const countdownElement = document.getElementById('countdown');
    
    const countdownInterval = setInterval(() => {
        countdown--;
        if (countdownElement) {
            countdownElement.textContent = countdown;
        }
        
        if (countdown <= 0) {
            clearInterval(countdownInterval);
            modal.hide();
            
            // ลบ modal element ออกจาก DOM หลังจากปิด
            setTimeout(() => {
                const modalElement = document.getElementById('successModal');
                if (modalElement) {
                    modalElement.remove();
                }
            }, 300);
        }
    }, 1000);
}

function setupFormHandlers() {
    // Restaurant form
    const restaurantForm = document.getElementById('restaurant-form');
    if (restaurantForm) {
        restaurantForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const nameEl = document.getElementById('restaurant-name');
            const addressEl = document.getElementById('restaurant-address');
            const phoneEl = document.getElementById('restaurant-phone');
            
            if (!nameEl || !addressEl || !phoneEl) {
                showAlert('ไม่พบฟอร์มการตั้งค่าข้อมูลร้าน', 'danger');
                return;
            }
            
            const name = nameEl.value.trim();
            const address = addressEl.value.trim();
            const phone = phoneEl.value.trim();
            
            if (!name || !address || !phone) {
                showAlert('กรุณากรอกข้อมูลให้ครบถ้วน', 'warning');
                return;
            }
            
            try {
                // บันทึกลงฐานข้อมูลผ่าน API
                const response = await fetch('/api/restaurant-info', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        restaurant_name: name,
                        restaurant_address: address,
                        restaurant_phone: phone
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // บันทึกลง localStorage เพื่อให้ใช้งานได้ทันที
                    localStorage.setItem('restaurant_name', name);
                    localStorage.setItem('restaurant_address', address);
                    localStorage.setItem('restaurant_phone', phone);
                    
                    // ส่ง custom event เพื่อแจ้งให้หน้าลูกค้าอัปเดตชื่อร้าน
                    window.dispatchEvent(new CustomEvent('restaurantNameUpdated', {
                        detail: { name: name, address: address, phone: phone }
                    }));
                    
                    showSuccessModal();
                } else {
                    showAlert(result.error || 'ไม่สามารถบันทึกข้อมูลร้านได้', 'danger');
                }
            } catch (error) {
                console.error('Error saving restaurant settings:', error);
                showAlert('ไม่สามารถบันทึกข้อมูลร้านได้', 'danger');
            }
        });
    }
    
    // Receipt form
    const receiptForm = document.getElementById('receipt-form');
    if (receiptForm) {
        receiptForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const footerTextEl = document.getElementById('receipt-footer-text');
            const promptpayNumberEl = document.getElementById('promptpay-number');
            const bankAccountNumberEl = document.getElementById('bank-account-number');
            const bankAccountNameEl = document.getElementById('bank-account-name');
            const bankNameEl = document.getElementById('bank-name');
            
            if (!footerTextEl || !promptpayNumberEl || !bankAccountNumberEl || !bankAccountNameEl || !bankNameEl) {
                showAlert('ไม่พบฟอร์มการตั้งค่าข้อมูลใบเสร็จ', 'danger');
                return;
            }
            
            const footerText = footerTextEl.value.trim();
            const promptpayNumber = promptpayNumberEl.value.trim();
            const bankAccountNumber = bankAccountNumberEl.value.trim();
            const bankAccountName = bankAccountNameEl.value.trim();
            const bankName = bankNameEl.value.trim();
            
            if (!footerText || !promptpayNumber || !bankAccountNumber || !bankAccountName || !bankName) {
                showAlert('กรุณากรอกข้อมูลให้ครบถ้วน', 'warning');
                return;
            }
            
            try {
                // บันทึกลง localStorage
                localStorage.setItem('receipt_footer_text', footerText);
                localStorage.setItem('promptpay_number', promptpayNumber);
                localStorage.setItem('bank_account_number', bankAccountNumber);
                localStorage.setItem('bank_account_name', bankAccountName);
                localStorage.setItem('bank_name', bankName);
                
                showSuccessModal();
            } catch (error) {
                console.error('Error saving receipt settings:', error);
                showAlert('ไม่สามารถบันทึกข้อมูลใบเสร็จได้', 'danger');
            }
        });
    }

    // PromptPay form
    const promptpayForm = document.getElementById('promptpay-form');
    if (promptpayForm) {
        promptpayForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const typeEl = document.getElementById('promptpay-type');
        const valueEl = document.getElementById('promptpay-value');
        
        if (!typeEl || !valueEl) {
            showAlert('ไม่พบฟอร์มการตั้งค่า PromptPay', 'danger');
            return;
        }
        
        const type = typeEl.value;
        const value = valueEl.value.trim();
        
        if (!value) {
            showAlert('กรุณาระบุหมายเลข', 'warning');
            return;
        }
        
        try {
            const response = await fetch('http://localhost:5000/api/settings/promptpay', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: type,
                    value: value
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                localStorage.setItem('promptpay_type', type);
                localStorage.setItem('promptpay_value', value);
                showSuccessModal('บันทึกการตั้งค่า PromptPay สำเร็จ!');
            } else {
                throw new Error(data.error || 'ไม่สามารถบันทึกการตั้งค่าได้');
            }
        } catch (error) {
            console.error('Error saving PromptPay settings:', error);
            showAlert(error.message, 'danger');
        }
        });
    }
    
    // Domain form
    const domainForm = document.getElementById('domain-form');
    if (domainForm) {
        domainForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const urlEl = document.getElementById('domain-url');
        
        if (!urlEl) {
            showAlert('ไม่พบฟอร์มการตั้งค่า Domain', 'danger');
            return;
        }
        
        const url = urlEl.value.trim();
        
        if (!url) {
            showAlert('กรุณาระบุ Domain URL', 'warning');
            return;
        }
        
        try {
            const response = await fetch('http://localhost:5000/api/settings/domain', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                localStorage.setItem('domain_url', url);
                showSuccessModal('บันทึกการตั้งค่า Domain สำเร็จ!');
            } else {
                throw new Error(data.error || 'ไม่สามารถบันทึกการตั้งค่าได้');
            }
        } catch (error) {
            console.error('Error saving domain settings:', error);
            showAlert(error.message, 'danger');
        }
        });
    }
    
    // Google Sheets form
    const sheetsForm = document.getElementById('sheets-form');
    if (sheetsForm) {
        sheetsForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const sheetIdEl = document.getElementById('sheet-id');
        const sheetNameEl = document.getElementById('sheet-name');
        const credentialsFileEl = document.getElementById('credentials-file');
        
        if (!sheetIdEl || !sheetNameEl || !credentialsFileEl) {
            showAlert('ไม่พบฟอร์มการตั้งค่า Google Sheets', 'danger');
            return;
        }
        
        const sheetId = sheetIdEl.value.trim();
        const sheetName = sheetNameEl.value.trim();
        const credentialsFile = credentialsFileEl.files[0];
        
        if (!sheetId || !sheetName) {
            showAlert('กรุณากรอกข้อมูลที่จำเป็น', 'warning');
            return;
        }
        
        try {
            const formData = new FormData();
            formData.append('sheet_id', sheetId);
            formData.append('sheet_name', sheetName);
            if (credentialsFile) {
                formData.append('credentials', credentialsFile);
            }
            
            const response = await fetch('http://localhost:5000/api/settings/sheets', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                localStorage.setItem('sheet_id', sheetId);
                localStorage.setItem('sheet_name', sheetName);
                showSuccessModal('บันทึกการตั้งค่า Google Sheets สำเร็จ!');
            } else {
                throw new Error(data.error || 'ไม่สามารถบันทึกการตั้งค่าได้');
            }
        } catch (error) {
            console.error('Error saving Google Sheets settings:', error);
            showAlert(error.message, 'danger');
        }
        });
    }
}

async function testGoogleSheets() {
    try {
        showLoading(true);
        
        const response = await fetch('http://localhost:5000/api/settings/sheets/test', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('ทดสอบการเชื่อมต่อ Google Sheets สำเร็จ', 'success');
        } else {
            throw new Error(data.error || 'การทดสอบล้มเหลว');
        }
    } catch (error) {
        console.error('Error testing Google Sheets:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// Tools
async function generateAllQR() {
    if (!confirm('คุณต้องการสร้าง QR Code ใหม่สำหรับทุกโต๊ะหรือไม่?')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('http://localhost:5000/api/tools/generate-qr', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('สร้าง QR Code สำเร็จ', 'success');
        } else {
            throw new Error(data.error || 'ไม่สามารถสร้าง QR Code ได้');
        }
    } catch (error) {
        console.error('Error generating QR codes:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันสำหรับพิมพ์ QR Code ทั้งหมด
async function printAllQR() {
    if (!confirm('คุณต้องการพิมพ์ QR Code สำหรับทุกโต๊ะหรือไม่?')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/tools/generate-qr', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            const qrCodes = data.data;
            const tableIds = Object.keys(qrCodes).sort((a, b) => parseInt(a) - parseInt(b));
            
            // สร้างหน้าต่างใหม่สำหรับพิมพ์
            const printWindow = window.open('', '_blank');
            
            let printContent = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>QR Codes - ทุกโต๊ะ</title>
                    <style>
                        body {
                            font-family: 'Sarabun', Arial, sans-serif;
                            margin: 0;
                            padding: 20px;
                            background: white;
                        }
                        .page-title {
                            text-align: center;
                            font-size: 24px;
                            font-weight: bold;
                            margin-bottom: 30px;
                            color: #333;
                        }
                        .qr-grid {
                            display: grid;
                            grid-template-columns: repeat(2, 1fr);
                            gap: 20px;
                            max-width: 800px;
                            margin: 0 auto;
                        }
                        .qr-item {
                            border: 2px solid #333;
                            padding: 15px;
                            text-align: center;
                            border-radius: 10px;
                            page-break-inside: avoid;
                        }
                        .table-title {
                            font-size: 18px;
                            font-weight: bold;
                            margin-bottom: 10px;
                            color: #333;
                        }
                        .qr-image {
                            margin: 10px 0;
                        }
                        .instructions {
                            font-size: 12px;
                            color: #666;
                            margin-top: 10px;
                            line-height: 1.4;
                        }
                        @media print {
                            body { margin: 0; padding: 10px; }
                            .qr-item { border: 2px solid #000; margin-bottom: 20px; }
                            .page-title { margin-bottom: 20px; }
                        }
                        @page {
                            margin: 1cm;
                        }
                    </style>
                </head>
                <body>
                    <div class="page-title">QR Codes สำหรับทุกโต๊ะ</div>
                    <div class="qr-grid">
            `;
            
            // เพิ่ม QR Code แต่ละโต๊ะ
            tableIds.forEach(tableId => {
                const qrData = qrCodes[tableId];
                printContent += `
                    <div class="qr-item">
                        <div class="table-title">โต๊ะ ${tableId}</div>
                        <div class="qr-image">
                            <img src="data:image/png;base64,${qrData.qr_code}" alt="QR Code โต๊ะ ${tableId}" style="max-width: 180px; height: auto;">
                        </div>
                        <div class="instructions">
                            สแกน QR Code เพื่อสั่งอาหาร
                        </div>
                        <div style="font-size: 10px; color: #fff; margin-top: 5px; word-break: break-all;">
                            ${qrData.url}
                        </div>
                    </div>
                `;
            });
            
            printContent += `
                    </div>
                </body>
                </html>
            `;
            
            printWindow.document.write(printContent);
            printWindow.document.close();
            
            // รอให้โหลดเสร็จแล้วพิมพ์
            printWindow.onload = function() {
                setTimeout(() => {
                    printWindow.print();
                    printWindow.close();
                }, 1000);
            };
            
            showAlert(`เตรียมพิมพ์ QR Code ทั้งหมด ${tableIds.length} โต๊ะสำเร็จ`, 'success');
        } else {
            throw new Error(data.error || 'ไม่สามารถสร้าง QR Code ได้');
        }
    } catch (error) {
        console.error('Error printing all QR codes:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

async function clearAllTables() {
    if (!confirm('คุณต้องการเคลียร์ทุกโต๊ะหรือไม่? การดำเนินการนี้ไม่สามารถยกเลิกได้')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('http://localhost:5000/api/tools/clear-all-tables', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('เคลียร์ทุกโต๊ะสำเร็จ', 'success');
            // รอสักครู่แล้วค่อย refresh เพื่อให้ backend อัปเดตข้อมูลเสร็จ
            setTimeout(async () => {
                await refreshTables();
            }, 200);
        } else {
            throw new Error(data.error || 'ไม่สามารถเคลียร์โต๊ะได้');
        }
    } catch (error) {
        console.error('Error clearing all tables:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

async function exportData() {
    try {
        showLoading(true);
        
        const response = await fetch('http://localhost:5000/api/tools/export-data');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `pos_data_${new Date().toLocaleString('sv-SE', { timeZone: 'Asia/Bangkok' }).split(' ')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('ส่งออกข้อมูลสำเร็จ', 'success');
        } else {
            throw new Error('ไม่สามารถส่งออกข้อมูลได้');
        }
    } catch (error) {
        console.error('Error exporting data:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// Auto-refresh data
function refreshData() {
    if (currentSection === 'tables') {
        refreshTables();
    } else if (currentSection === 'orders') {
        refreshOrders();
    } else if (currentSection === 'dashboard') {
        // ใช้ฟังก์ชันรีเฟรชที่ไม่รีเซ็ตสถานะของกราฟ
        if (typeof window.refreshDashboardData === 'function') {
            window.refreshDashboardData();
        } else {
            // fallback ถ้าฟังก์ชันไม่พร้อมใช้งาน
            loadSalesSummary();
        }
    }
    
    checkServerStatus();
}

// Edit/Delete functions for categories and menu items
function editCategory(categoryId) {
    const category = menuCategories.find(c => c.category_id === categoryId);
    if (!category) {
        showAlert('ไม่พบหมวดหมู่ที่ต้องการแก้ไข', 'error');
        return;
    }
    
    const newName = prompt('ชื่อหมวดหมู่ใหม่:', category.name);
    if (newName && newName.trim() !== '') {
        const newDescription = prompt('คำอธิบาย:', category.description || '');
        
        fetch(`http://localhost:5000/api/menu/categories/${categoryId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: newName.trim(),
                description: newDescription || ''
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('แก้ไขหมวดหมู่สำเร็จ', 'success');
                loadMenuCategories();
            } else {
                showAlert('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
        });
    }
}

function deleteCategory(categoryId) {
    const category = menuCategories.find(c => c.category_id === categoryId);
    if (!category) {
        showAlert('ไม่พบหมวดหมู่ที่ต้องการลบ', 'error');
        return;
    }
    
    if (confirm(`คุณต้องการลบหมวดหมู่ "${category.name}" หรือไม่?\n\nหมายเหตุ: หากมีเมนูในหมวดหมู่นี้ จะไม่สามารถลบได้`)) {
        fetch(`http://localhost:5000/api/menu/categories/${categoryId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('ลบหมวดหมู่สำเร็จ', 'success');
                loadMenuCategories();
                loadMenuItems(); // Refresh menu items
            } else {
                showAlert('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
        });
    }
}

async function moveCategoryUp(categoryId) {
    try {
        showLoading(true);
        
        const response = await fetch(`http://localhost:5000/api/menu/categories/${categoryId}/move-up`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('เลื่อนหมวดหมู่ขึ้นสำเร็จ', 'success');
            loadMenuCategories();
            loadMenuItems(); // Refresh menu items to reflect new order
        } else {
            showAlert('เกิดข้อผิดพลาด: ' + data.error, 'error');
        }
        
    } catch (error) {
        console.error('Error moving category up:', error);
        showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
    } finally {
        showLoading(false);
    }
}

async function moveCategoryDown(categoryId) {
    try {
        showLoading(true);
        
        const response = await fetch(`http://localhost:5000/api/menu/categories/${categoryId}/move-down`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('เลื่อนหมวดหมู่ลงสำเร็จ', 'success');
            loadMenuCategories();
            loadMenuItems(); // Refresh menu items to reflect new order
        } else {
            showAlert('เกิดข้อผิดพลาด: ' + data.error, 'error');
        }
        
    } catch (error) {
        console.error('Error moving category down:', error);
        showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
    } finally {
        showLoading(false);
    }
}

function editMenuItem(itemId) {
    const item = menuItems.find(i => i.item_id === itemId);
    if (!item) {
        showAlert('ไม่พบเมนูที่ต้องการแก้ไข', 'error');
        return;
    }
    
    // ตรวจสอบประเภทตัวเลือกอาหาร
    const currentOptionType = item.food_option_type || 'none';
    
    // Create edit form modal
    const modalHtml = `
        <div class="modal fade" id="editMenuModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">แก้ไขเมนู</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editMenuForm" data-menu-id="${item.item_id}">
                            <div class="mb-3">
                                <label class="form-label">ชื่อเมนู</label>
                                <input type="text" class="form-control" id="editMenuName" value="${item.name}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">ราคา</label>
                                <input type="number" class="form-control" id="editMenuPrice" value="${item.price}" step="0.01" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">หมวดหมู่</label>
                                <select class="form-control" id="editMenuCategory" required>
                                    ${menuCategories.map(cat => 
                                        `<option value="${cat.category_id}" ${cat.category_id === item.category_id ? 'selected' : ''}>${cat.name}</option>`
                                    ).join('')}
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">รูปภาพ</label>
                                <div class="input-group mb-3">
                                    <input type="text" class="form-control" id="editMenuImageUrl" value="${item.image_url || ''}" placeholder="URL รูปภาพ">
                                    <button class="btn btn-outline-secondary" type="button" id="editMenuImageUploadBtn">อัปโหลด</button>
                                </div>
                                <input type="file" class="form-control d-none" id="editMenuImageFile" accept=".png,.jpg,.jpeg,.gif,.svg">
                                ${item.image_url ? `<div class="mt-2"><img src="${item.image_url}" class="img-thumbnail" style="max-height: 100px;"></div>` : ''}
                                <div id="editMenuImagePreview" class="mt-2 ${!item.image_url ? 'd-none' : ''}"></div>
                            </div>

                            <div class="mb-3 form-check">
                                <input type="checkbox" class="form-check-input" id="editMenuAvailable" ${item.is_available ? 'checked' : ''}>
                                <label class="form-check-label">พร้อมขาย</label>
                            </div>
                            
                            <!-- Food Options Section -->
                            <div class="mb-3">
                                <div class="d-flex justify-content-between align-items-center" data-bs-toggle="collapse" data-bs-target="#editFoodOptionsCollapse" aria-expanded="false" style="cursor: pointer;">
                                    <label class="form-label mb-0">ตัวเลือกอาหาร</label>
                                    <i class="fas fa-chevron-down"></i>
                                </div>
                                <div class="collapse" id="editFoodOptionsCollapse">
                                    <div class="card card-body mt-2">
                                        <!-- Option Type Selection -->
                                        <div class="mb-3">
                                            <label class="form-label">ประเภทตัวเลือก (เลือกได้หลายตัวเลือก)</label>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="edit-option-type" id="editOptionNone" value="none" ${currentOptionType && currentOptionType.includes('none') ? 'checked' : ''}>
                                                <label class="form-check-label" for="editOptionNone">ไม่ระบุ</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="edit-option-type" id="editOptionSpice" value="spice" ${currentOptionType && currentOptionType.includes('spice') ? 'checked' : ''}>
                                                <label class="form-check-label" for="editOptionSpice">ระดับความเผ็ด</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="edit-option-type" id="editOptionSweet" value="sweet" ${currentOptionType && currentOptionType.includes('sweet') ? 'checked' : ''}>
                                                <label class="form-check-label" for="editOptionSweet">ระดับความหวาน</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="edit-option-type" id="editOptionSpecial" value="special" ${currentOptionType && currentOptionType.includes('special') ? 'checked' : ''}>
                                                <label class="form-check-label" for="editOptionSpecial">เพิ่มพิเศษ</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="button" class="btn btn-primary" onclick="saveMenuEdit(${itemId})">บันทึก</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('editMenuModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('editMenuModal'));
    modal.show();
    
    // เพิ่ม event listener สำหรับจัดการเงื่อนไขการเลือก checkbox
    setTimeout(() => {
        const noneCheckbox = document.getElementById('editOptionNone');
        const otherCheckboxes = document.querySelectorAll('input[name="edit-option-type"]:not(#editOptionNone)');
        
        // เมื่อคลิก "ไม่ระบุ"
        if (noneCheckbox) {
            noneCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    // ยกเลิกการเลือกตัวเลือกอื่นทั้งหมด
                    otherCheckboxes.forEach(checkbox => {
                        checkbox.checked = false;
                    });
                }
            });
        }
        
        // เมื่อคลิกตัวเลือกอื่น
        otherCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                if (this.checked && noneCheckbox) {
                    // ยกเลิกการเลือก "ไม่ระบุ"
                    noneCheckbox.checked = false;
                }
            });
        });
    }, 100);
}

// เพิ่ม Event Listener สำหรับปุ่มอัปโหลดรูปภาพ
document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'editMenuImageUploadBtn') {
        document.getElementById('editMenuImageFile').click();
    }
});

// เพิ่ม Event Listener สำหรับการเลือกไฟล์
document.addEventListener('change', function(event) {
    if (event.target && event.target.id === 'editMenuImageFile') {
        const file = event.target.files[0];
        if (file) {
            uploadMenuImage(file);
        }
    }
});

// ฟังก์ชันสำหรับอัปโหลดรูปภาพ
function uploadMenuImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // ดึงข้อมูล menu_id และ menu_name จากฟอร์มแก้ไขเมนู
    const menuId = document.querySelector('#editMenuForm')?.dataset?.menuId || '';
    const menuName = document.getElementById('editMenuName')?.value || '';
    
    // เพิ่มข้อมูลเมนูลงใน FormData
    if (menuId) formData.append('menu_id', menuId);
    if (menuName) formData.append('menu_name', menuName);
    
    showLoading(true);
    
    fetch('http://localhost:5000/api/upload/menu-image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // อัปเดต URL ในฟอร์ม
            document.getElementById('editMenuImageUrl').value = data.image_url;
            
            // แสดงตัวอย่างรูปภาพ
            const previewDiv = document.getElementById('editMenuImagePreview');
            previewDiv.innerHTML = `<img src="${data.image_url}" class="img-thumbnail" style="max-height: 100px;">`;
            previewDiv.classList.remove('d-none');
            
            showAlert('อัปโหลดรูปภาพสำเร็จและบันทึกลงฐานข้อมูลแล้ว', 'success');
        } else {
            showAlert('เกิดข้อผิดพลาดในการอัปโหลด: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('เกิดข้อผิดพลาดในการอัปโหลด', 'error');
    })
    .finally(() => {
        showLoading(false);
    });
}

function saveMenuEdit(itemId) {
    // รวบรวมประเภทตัวเลือกอาหาร (รองรับหลายตัวเลือก)
    const selectedOptions = document.querySelectorAll('input[name="edit-option-type"]:checked');
    let foodOptionTypes = [];
    
    selectedOptions.forEach(option => {
        foodOptionTypes.push(option.value);
    });
    
    // ถ้าไม่มีการเลือก ให้ใช้ค่า default เป็น 'none'
    const foodOptionType = foodOptionTypes.length > 0 ? foodOptionTypes.join(',') : 'none';
    
    console.log('DEBUG: Selected food option types:', foodOptionTypes);
    console.log('DEBUG: Combined food option type:', foodOptionType);
    
    const formData = {
        name: document.getElementById('editMenuName').value,
        price: parseFloat(document.getElementById('editMenuPrice').value),
        category_id: parseInt(document.getElementById('editMenuCategory').value),
        image_url: document.getElementById('editMenuImageUrl').value,
        is_available: document.getElementById('editMenuAvailable').checked,
        food_option_type: foodOptionType
    };
    
    console.log('DEBUG: Form data being sent:', formData);
    
    fetch(`http://localhost:5000/api/menu/items/${itemId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('แก้ไขเมนูสำเร็จ', 'success');
            loadMenuItems();
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editMenuModal'));
            modal.hide();
        } else {
            showAlert('เกิดข้อผิดพลาด: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
    });
}

function deleteMenuItem(itemId) {
    const item = menuItems.find(i => i.item_id === itemId);
    if (!item) {
        showAlert('ไม่พบเมนูที่ต้องการลบ', 'error');
        return;
    }
    
    if (confirm(`คุณต้องการลบเมนู "${item.name}" หรือไม่?`)) {
        fetch(`http://localhost:5000/api/menu/items/${itemId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('ลบเมนูสำเร็จ', 'success');
                loadMenuItems();
            } else {
                showAlert('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
        });
    }
}

// ฟังก์ชันสำหรับพิมพ์ QR Code
async function printTableQR(tableId) {
    try {
        showLoading(true);
        
        const response = await fetch(`http://localhost:5000/api/tables/${tableId}/qr/print`);
        const data = await response.json();
        
        if (data.success) {
            // ตรวจสอบว่ามีข้อมูล QR code หรือไม่
            if (!data.data.qr_code) {
                throw new Error('ไม่พบข้อมูล QR Code จากเซิร์ฟเวอร์');
            }
            
            console.log('QR Code data received:', data.data.qr_code.substring(0, 50) + '...');
            // สร้างหน้าต่างใหม่สำหรับพิมพ์
            const printWindow = window.open('', '_blank');
            const qrData = data.data;
            
            // ตรวจสอบว่าหน้าต่างถูกสร้างขึ้นสำเร็จหรือไม่ (อาจถูกบล็อกโดย popup blocker)
            if (!printWindow) {
                throw new Error('ไม่สามารถเปิดหน้าต่างพิมพ์ได้ โปรดอนุญาตให้เว็บไซต์เปิดหน้าต่างใหม่');
            }
            
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>QR Code - โต๊ะ ${qrData.table_id}</title>
                    <style>
                        body {
                            font-family: 'Sarabun', Arial, sans-serif;
                            text-align: center;
                            margin: 20px;
                            background: white;
                        }
                        .qr-container {
                            border: 2px solid #333;
                            padding: 10px;
                            margin: 0 auto;
                            max-width: 400px;
                            border-radius: 5px;
                        }
                        .table-title {
                            font-size: 18px;
                            font-weight: bold;
                            margin-bottom: 5px;
                            color: #333;
                        }
                        .qr-image {
                            margin: 10px 0;
                        }
                        .instructions {
                            font-size: 12px;
                            color: #666;
                            margin-top: 5px;
                            line-height: 1.3;
                        }
                        /* CSS สำหรับ URL ถูกลบออกเนื่องจากไม่ได้ใช้งานแล้ว */
                        @media print {
                            body { margin: 0; }
                            .qr-container { 
                                border: 2px solid #000;
                                width: 6cm;
                                height: 12cm;
                                box-sizing: border-box;
                                page-break-inside: avoid;
                            }
                            @page {
                                size: 6cm 12cm;
                                margin: 0;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="qr-container">
                        <div class="table-title">โต๊ะ ${qrData.table_id}</div>
                        <div class="qr-image">
                            <img 
                                src="${qrData.qr_code.startsWith('data:image') ? qrData.qr_code : `data:image/png;base64,${qrData.qr_code}`}" 
                                alt="QR Code โต๊ะ ${qrData.table_id}" 
                                style="max-width: 150px; height: auto;" 
                                onerror="console.error('QR code image failed to load'); this.style.display='none'; this.parentNode.innerHTML += '<p style=\'color:red; font-weight:bold\'>ไม่สามารถแสดงรูปภาพ QR code ได้</p><p>กรุณาลองพิมพ์ใหม่อีกครั้ง</p>';"
                                onload="console.log('QR code image loaded successfully');"
                            >
                        </div>
                        <div class="instructions">
                            <strong>วิธีใช้งาน:</strong><br>
                            1. สแกน QR Code ด้วยมือถือ<br>
                            2. เลือกเมนูที่ต้องการ<br>
                            3. ส่งออเดอร์ไปยังครัว
                        </div>
                        <!-- URL ถูกซ่อนตามคำขอ -->
                    </div>
                </body>
                </html>
            `);
            
            printWindow.document.close();
            
            // เรียกใช้ window.print() ทันทีที่หน้าต่างโหลดเสร็จ
            printWindow.onload = function() {
                // เรียกใช้ print dialog ทันที
                printWindow.print();
                
                // ปิดหน้าต่างหลังจากที่ผู้ใช้กดปิดหน้าต่างพิมพ์
                // ใช้ setTimeout เพื่อให้แน่ใจว่าหน้าต่างพิมพ์ได้แสดงแล้ว
                setTimeout(() => {
                    printWindow.close();
                }, 1000);
                
                // ตรวจสอบว่ารูปภาพ QR code โหลดสำเร็จหรือไม่ (สำหรับการบันทึกล็อก)
                const qrImage = printWindow.document.querySelector('.qr-image img');
                
                if (qrImage) {
                    qrImage.onload = function() {
                        console.log('QR code image loaded successfully');
                    };
                    
                    qrImage.onerror = function() {
                        console.error('Failed to load QR code image');
                        alert('ไม่สามารถโหลดรูปภาพ QR code ได้ กรุณาลองใหม่อีกครั้ง');
                        printWindow.close();
                    };
                } else {
                    console.error('QR code image element not found');
                }
            };
            
            showAlert(`เตรียมพิมพ์ QR Code โต๊ะ ${tableId} สำเร็จ`, 'success');
        } else {
            throw new Error(data.error || 'ไม่สามารถสร้าง QR Code ได้');
        }
    } catch (error) {
        console.error('Error printing QR code:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันสำหรับแสดง QR Code
async function startTableSession(tableId) {
    try {
        showLoading(true);
        
        const response = await fetch(`http://localhost:5000/api/tables/${tableId}/qr`);
        const data = await response.json();
        
        if (data.success) {
            // API /api/tables/${tableId}/qr จะอัปเดตสถานะโต๊ะเป็น occupied และกำหนด session_id ให้แล้ว
            // ไม่จำเป็นต้องเรียก API /api/tables/${tableId}/status อีก
            
            // รอให้ backend อัพเดทข้อมูลเสร็จก่อน
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // รีเฟรชข้อมูลโต๊ะ
            await loadTables();
            
            showAlert('สร้าง QR Code และเปิดเซสชั่นเรียบร้อย โต๊ะพร้อมรับลูกค้า', 'success');
            
            // แสดง QR Code
            showTableQR(tableId);
        } else {
            throw new Error(data.error || 'ไม่สามารถสร้าง QR Code ได้');
        }
    } catch (error) {
        console.error('Error starting table session:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันแสดง modal ยืนยันการปิดเซสชั่น
function showCloseSessionConfirmModal(tableId) {
    const modalHtml = `
        <div class="modal fade" id="closeSessionConfirmModal" tabindex="-1" aria-labelledby="closeSessionConfirmModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title" id="closeSessionConfirmModalLabel">
                            <i class="fas fa-exclamation-triangle me-2"></i>ยืนยันการปิดเซสชั่น
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-3">
                            <i class="fas fa-times-circle text-warning" style="font-size: 3rem;"></i>
                        </div>
                        <h4>ต้องการปิดเซสชั่นโต๊ะ ${tableId} หรือไม่?</h4>
                        <p class="text-muted">การปิดเซสชั่นจะทำให้โต๊ะกลับสู่สถานะว่าง และลูกค้าจะไม่สามารถสั่งอาหารผ่าน QR Code เดิมได้</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>ยกเลิก
                        </button>
                        <button type="button" class="btn btn-danger" onclick="confirmCloseTableSession(${tableId})">
                            <i class="fas fa-check me-2"></i>ยืนยันปิดเซสชั่น
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่า (ถ้ามี)
    const existingModal = document.getElementById('closeSessionConfirmModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal เข้าไปใน body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('closeSessionConfirmModal'));
    modal.show();
}

// ฟังก์ชันยืนยันการปิดเซสชั่น
async function confirmCloseTableSession(tableId) {
    // ปิด modal ยืนยัน
    const modal = bootstrap.Modal.getInstance(document.getElementById('closeSessionConfirmModal'));
    if (modal) {
        modal.hide();
    }
    
    try {
        showLoading(true);
        
        // เคลียร์โต๊ะ
        const response = await fetch(`http://localhost:5000/api/tables/${tableId}/clear`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('ปิดเซสชั่นเรียบร้อย โต๊ะกลับสู่สถานะว่าง', 'success');
            // รอสักครู่แล้วค่อย refresh เพื่อให้ backend อัปเดตข้อมูลเสร็จ
            setTimeout(async () => {
                await refreshTables();
                // หลังจากปิดเซสชันโต๊ะ ให้ล้างข้อมูลใบเสร็จเพื่อไม่ให้แสดงปุ่มพิมพ์ใบเสร็จในครั้งถัดไป
                window.receiptData = null;
                // แสดงรายละเอียดโต๊ะใหม่หลังจากปิดเซสชัน
                showTableDetail(tableId);
            }, 200);
        } else {
            throw new Error(data.error || 'ไม่สามารถปิดเซสชั่นได้');
        }
    } catch (error) {
        console.error('Error closing table session:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันเรียกใช้ modal ยืนยัน (เปลี่ยนจากเดิมที่ใช้ confirm)
async function closeTableSession(tableId) {
    showCloseSessionConfirmModal(tableId);
}

async function showTableQR(tableId) {
    try {
        showLoading(true);
        
        const response = await fetch(`http://localhost:5000/api/tables/${tableId}/qr`);
        const data = await response.json();
        
        if (data.success) {
            const qrData = data.data;
            
            // สร้าง Modal สำหรับแสดง QR Code
            const modalHtml = `
                <div class="modal fade" id="qrModal" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">QR Code - โต๊ะ ${tableId}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body text-center">
                                <img src="${qrData.qr_code}" alt="QR Code โต๊ะ ${tableId}" class="img-fluid mb-3" style="max-width: 300px;">
                                <p class="small mb-2" style="color: white !important;">${qrData.url}</p>
                                <div class="card border-info small mb-3">
                                    <div class="card-body p-2">
                                        <small class="text-info">
                                            <strong>Session ID:</strong> ${qrData.session_id}<br>
                                            <small class="text-muted">QR Code นี้จะใช้งานได้จนกว่าจะปิดเซสชั่น</small>
                                        </small>
                                    </div>
                                </div>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-primary" onclick="printTableQR(${tableId}); bootstrap.Modal.getInstance(document.getElementById('qrModal')).hide();">
                                        <i class="fas fa-print me-2"></i>พิมพ์ QR Code
                                    </button>
                                    <button class="btn btn-danger" onclick="closeTableSession(${tableId}); bootstrap.Modal.getInstance(document.getElementById('qrModal')).hide();">
                                        <i class="fas fa-times me-2"></i>ปิดเซสชั่น
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // ลบ Modal เก่า (ถ้ามี)
            const existingModal = document.getElementById('qrModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // เพิ่ม Modal ใหม่
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // แสดง Modal
            const modal = new bootstrap.Modal(document.getElementById('qrModal'));
            modal.show();
            
            // ลบ Modal เมื่อปิด
            document.getElementById('qrModal').addEventListener('hidden.bs.modal', function() {
                this.remove();
            });
            
        } else {
            throw new Error(data.error || 'ไม่สามารถแสดง QR Code ได้');
        }
    } catch (error) {
        console.error('Error showing QR code:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ฟังก์ชันสำหรับเพิ่มโต๊ะอัตโนมัติ
function showAddTableModal() {
    // หาหมายเลขโต๊ะถัดไปที่ยังไม่มี
    const existingTableIds = tables.map(table => table.table_id);
    let nextTableId = 1;
    
    // หาหมายเลขโต๊ะถัดไปที่ยังไม่มี
    while (existingTableIds.includes(nextTableId)) {
        nextTableId++;
    }
    
    const tableName = `โต๊ะ ${nextTableId}`;
    
    // เพิ่มโต๊ะทันทีโดยไม่ต้องเปิด modal
    fetch('http://localhost:5000/api/tables', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            table_id: nextTableId,
            table_name: tableName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(`เพิ่ม${tableName}เรียบร้อยแล้ว`, 'success');
            loadTables();
        } else {
            showAlert('เกิดข้อผิดพลาด: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
    });
}

// ฟังก์ชันสำหรับเพิ่มโต๊ะใหม่
function addNewTable() {
    const tableId = document.getElementById('newTableId').value.trim();
    const tableName = document.getElementById('newTableName').value.trim();
    
    if (!tableId || !tableName) {
        showAlert('กรุณากรอกข้อมูลให้ครบถ้วน', 'error');
        return;
    }
    
    if (isNaN(tableId) || parseInt(tableId) <= 0) {
        showAlert('หมายเลขโต๊ะต้องเป็นตัวเลขที่มากกว่า 0', 'error');
        return;
    }
    
    fetch('http://localhost:5000/api/tables', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            table_id: parseInt(tableId),
            table_name: tableName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('เพิ่มโต๊ะเรียบร้อยแล้ว', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('addTableModal'));
            modal.hide();
            loadTables();
        } else {
            showAlert('เกิดข้อผิดพลาด: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
    });
}

// ฟังก์ชันสำหรับยืนยันการลบโต๊ะ
function deleteTableConfirm(tableId, tableName) {
    if (confirm(`คุณต้องการลบ ${tableName} หรือไม่?\n\nหมายเหตุ: จะไม่สามารถลบได้หากมีออเดอร์ที่ยังไม่เสร็จสิ้น`)) {
        deleteTable(tableId);
    }
}

// ฟังก์ชันสำหรับลบโต๊ะ
function deleteTable(tableId) {
    fetch(`http://localhost:5000/api/tables/${tableId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('ลบโต๊ะเรียบร้อยแล้ว', 'success');
            loadTables();
        } else {
            showAlert('เกิดข้อผิดพลาด: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('เกิดข้อผิดพลาดในการเชื่อมต่อ', 'error');
    });
}

// Function to show delete table modal
function showDeleteTableModal() {
    // Load available tables for deletion
    fetch('http://localhost:5000/api/tables')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('deleteTableSelect');
            select.innerHTML = '<option value="">-- เลือกโต๊ะ --</option>';
            
            // Only show available tables
            const availableTables = data.filter(table => table.status === 'available');
            
            if (availableTables.length === 0) {
                select.innerHTML = '<option value="">ไม่มีโต๊ะว่างให้ลบ</option>';
            } else {
                availableTables.forEach(table => {
                    const option = document.createElement('option');
                    option.value = table.table_id;
                    option.textContent = `${table.table_name} (โต๊ะ ${table.table_id})`;
                    select.appendChild(option);
                });
            }
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('deleteTableModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error loading tables:', error);
            showAlert('เกิดข้อผิดพลาดในการโหลดข้อมูลโต๊ะ', 'error');
        });
}

// Function to confirm table deletion
function confirmDeleteTable() {
    const tableId = document.getElementById('deleteTableSelect').value;
    if (!tableId) return;
    
    deleteTable(tableId);
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteTableModal'));
    if (modal) modal.hide();
}

// Handle table selection for deletion
document.addEventListener('DOMContentLoaded', function() {
    const deleteTableSelect = document.getElementById('deleteTableSelect');
    const confirmButton = document.getElementById('confirmDeleteTable');
    const warningDiv = document.getElementById('deleteTableWarning');
    
    if (deleteTableSelect) {
        deleteTableSelect.addEventListener('change', function() {
            if (this.value) {
                confirmButton.disabled = false;
                warningDiv.classList.remove('d-none');
            } else {
                confirmButton.disabled = true;
                warningDiv.classList.add('d-none');
            }
        });
    }
});

// ฟังก์ชันสำหรับจัดการการแจ้งเตือนคำขอเรียกพนักงาน
function addStaffNotification(notification) {
    const notificationsList = document.getElementById('notifications-list');
    const noNotifications = document.getElementById('no-notifications');
    
    // ซ่อนข้อความ "ไม่มีการแจ้งเตือน"
    if (noNotifications) {
        noNotifications.style.display = 'none';
    }
    
    // สร้าง HTML สำหรับการแจ้งเตือน
    // สร้างเวลาไทยที่ถูกต้องสำหรับ notification ID
    const now = new Date();
const thaiTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Bangkok' }));
    const notificationId = `notification-${thaiTime.getTime()}`;
    const notificationHtml = `
        <div class="staff-notification" id="${notificationId}">
            <div class="notification-header">
                <h6 class="notification-title">
                    <i class="fas fa-bell me-2"></i>
                    คำขอเรียกพนักงาน
                </h6>
                <small class="notification-time">${formatTime(notification.timestamp)}</small>
            </div>
            <div class="notification-message">
                ${notification.message}
            </div>
            <button class="btn btn-accept btn-sm" onclick="acceptStaffRequest('${notificationId}')">
                <i class="fas fa-check me-1"></i>
                ยอมรับ
            </button>
        </div>
    `;
    
    // เพิ่มการแจ้งเตือนใหม่ที่ด้านบน
    notificationsList.insertAdjacentHTML('afterbegin', notificationHtml);
}

// ฟังก์ชันสำหรับยอมรับคำขอเรียกพนักงาน
function acceptStaffRequest(notificationId) {
    const notification = document.getElementById(notificationId);
    if (notification) {
        // เพิ่ม class สำหรับ animation fade out
        notification.classList.add('fade-out');
        
        // ลบการแจ้งเตือนหลังจาก animation เสร็จ
        setTimeout(() => {
            notification.remove();
            
            // ตรวจสอบว่ายังมีการแจ้งเตือนอื่นหรือไม่
            const notificationsList = document.getElementById('notifications-list');
            const remainingNotifications = notificationsList.querySelectorAll('.staff-notification');
            
            if (remainingNotifications.length === 0) {
                const noNotifications = document.getElementById('no-notifications');
                if (noNotifications) {
                    noNotifications.style.display = 'block';
                }
            }
        }, 300);
    }
}

// ฟังก์ชันสำหรับจัดรูปแบบเวลา
function formatTime(timestamp) {
    if (!timestamp) return '';
    let date;

    // Standardize the timestamp string from the database (YYYY-MM-DD HH:MM:SS) to an ISO 8601 format that JavaScript's Date constructor interprets as UTC.
    if (typeof timestamp === 'string' && timestamp.includes(' ')) {
        const isoTimestamp = timestamp.replace(' ', 'T') + 'Z';
        date = new Date(isoTimestamp);
    } else {
        // Fallback for other timestamp formats or Date objects
        date = new Date(timestamp);
    }

    // Check for invalid date
    if (isNaN(date.getTime())) {
        console.error('Invalid timestamp provided to formatTime:', timestamp);
        return 'Invalid Time';
    }

    // Now, format this correct Date object into the desired timezone and format.
    return date.toLocaleString('en-GB', {
        timeZone: 'Asia/Bangkok',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

// formatDateTime function is now imported from date-config.js

// ฟังก์ชันสำหรับจำลองการรับการแจ้งเตือน (สำหรับทดสอบ)
function simulateStaffRequest() {
    // สร้างเวลาไทยที่ถูกต้อง
    const now = new Date();
const thaiTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Bangkok' }));
    
    const notification = {
        table_id: 1,
        message: 'โต๊ะ 1 ขอ: ช้อน-ส้อม 2 ชิ้น, แก้ว 1 ชิ้น',
        timestamp: thaiTime.toISOString(),
        type: 'staff_request'
    };
    
    addStaffNotification(notification);
}

// ฟังก์ชันสำหรับตรวจสอบการแจ้งเตือนใหม่จากฐานข้อมูล
async function checkForNewNotifications() {
    try {
        const response = await fetch('/api/notifications');
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            const notificationsList = document.getElementById('notifications-list');
            const noNotifications = document.getElementById('no-notifications');
            
            // ซ่อนข้อความ "ไม่มีการแจ้งเตือน"
            if (noNotifications) {
                noNotifications.style.display = 'none';
            }
            
            // แสดงการแจ้งเตือนใหม่
            data.data.forEach(notification => {
                // ตรวจสอบว่าการแจ้งเตือนนี้ยังไม่ได้แสดงอยู่และยังไม่ได้ประมวลผล
                const existingNotification = document.getElementById(`notification-${notification.notification_id}`);
                if (!existingNotification && !processedNotifications.has(notification.notification_id)) {
                    processedNotifications.add(notification.notification_id);
                    addNotificationToList(notification);
                    
                    // เล่นเสียงแจ้งเตือน
                    if (notificationSound) {
                        notificationSound.play().catch(e => console.log('Could not play notification sound'));
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error checking for new notifications:', error);
    }
}

// ฟังก์ชันสำหรับเพิ่มการแจ้งเตือนลงในรายการ
function addNotificationToList(notification) {
    const notificationsList = document.getElementById('notifications-list');
    
    // กำหนดไอคอนและสีตามประเภทการแจ้งเตือน
    let icon, typeText, colorClass;
    switch (notification.type) {
        case 'order':
            icon = 'fas fa-utensils';
            typeText = 'ออเดอร์ใหม่';
            colorClass = 'notification-order';
            break;
        case 'order_request':
            icon = 'fas fa-shopping-cart';
            typeText = 'ออเดอร์ใหม่';
            colorClass = 'notification-item notification-order';
            break;
        case 'staff_request':
            icon = 'fas fa-bell';
            typeText = 'เรียกพนักงาน';
            colorClass = 'notification-item notification-staff';
            break;
        case 'item_request':
            icon = 'fas fa-utensils';
            typeText = 'ลูกค้าต้องการภาชนะเพิ่ม';
            colorClass = 'notification-item-request';
            break;
        case 'checkout':
            icon = 'fas fa-receipt';
            typeText = 'ขอเช็คบิล';
            colorClass = 'notification-checkout';
            break;
        case 'check_bill_request':
            icon = 'fas fa-receipt';
            typeText = 'เรียกเช็คบิล';
            colorClass = 'notification-item notification-staff';
            break;
        default:
            icon = 'fas fa-info-circle';
            typeText = 'แจ้งเตือน';
            colorClass = 'notification-default';
    }
    
    // แยกข้อมูลโต๊ะและข้อความจาก notification.message
    let tableNumber = '';
    let displayMessage = '';
    
    if (notification.type === 'item_request') {
        // สำหรับ item_request ข้อความมีรูปแบบ: "ลูกค้าต้องการภาชนะเพิ่ม|โต๊ะ X|รายการสิ่งของ"
        const parts = notification.message.split('|');
        if (parts.length >= 3) {
            const tableMatch = parts[1].match(/โต๊ะ\s*(\d+)/);
            if (tableMatch) {
                tableNumber = tableMatch[1];
            }
            displayMessage = `<span class="table-number">โต๊ะ ${tableNumber}</span> : ${parts[2]}`;
        }
    } else {
        // สำหรับ staff_request, order_request และอื่นๆ
        const tableMatch = notification.message.match(/โต๊ะ\s*(\d+)/);
        if (tableMatch) {
            tableNumber = tableMatch[1];
            // สำหรับ order_request ให้แสดงหมายเลขโต๊ะใน span
            if (notification.type === 'order_request') {
                displayMessage = notification.message.replace(/โต๊ะ\s*(\d+)/, `<span class="table-number">โต๊ะ ${tableNumber}</span>`);
            } else {
                displayMessage = `<span class="table-number">โต๊ะ ${tableNumber}</span> : ${typeText}`;
            }
        } else {
            displayMessage = notification.message;
        }
    }
    
    const notificationHtml = `
        <div class="notification-item ${colorClass}" id="notification-${notification.notification_id}">
            <div class="notification-header">
                <h6 class="notification-title">
                    <i class="${icon} me-2"></i>
                    ${typeText}
                </h6>
                <small class="notification-time">${formatTime(notification.created_at || notification.timestamp)}</small>
            </div>
            <div class="notification-message">
                ${displayMessage}
            </div>
            <div class="notification-actions mt-2">
                <button class="btn btn-success btn-sm" onclick="markNotificationRead(${notification.notification_id})">
                    <i class="fas fa-check me-1"></i>
                    ยอมรับ
                </button>
            </div>
        </div>
    `;
    
    // เพิ่มการแจ้งเตือนใหม่ที่ด้านบน
    notificationsList.insertAdjacentHTML('afterbegin', notificationHtml);
}

// ฟังก์ชันสำหรับทำเครื่องหมายการแจ้งเตือนว่าอ่านแล้ว
async function markNotificationRead(notificationId) {
    try {
        const response = await fetch(`/api/notifications/${notificationId}/read`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // ไม่ลบ notification_id ออกจาก processedNotifications เพื่อป้องกันการแสดงซ้ำ
            // processedNotifications.delete(notificationId); // ลบบรรทัดนี้
            
            const notification = document.getElementById(`notification-${notificationId}`);
            if (notification) {
                // เพิ่ม class สำหรับ animation fade out
                notification.classList.add('fade-out');
                
                // ลบการแจ้งเตือนหลังจาก animation เสร็จ
                setTimeout(() => {
                    notification.remove();
                    
                    // ตรวจสอบว่ายังมีการแจ้งเตือนอื่นหรือไม่
                    const notificationsList = document.getElementById('notifications-list');
                    const remainingNotifications = notificationsList.querySelectorAll('.notification-item');
                    
                    if (remainingNotifications.length === 0) {
                        const noNotifications = document.getElementById('no-notifications');
                        if (noNotifications) {
                            noNotifications.style.display = 'block';
                        }
                    }
                }, 300);
            }
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
        showAlert('ไม่สามารถทำเครื่องหมายการแจ้งเตือนได้', 'danger');
    }
}

// เพิ่มฟังก์ชันสำหรับตรวจสอบการแจ้งเตือนใหม่ (polling)
let notificationPollingInterval;

function startNotificationPolling() {
    // ตรวจสอบการแจ้งเตือนใหม่ทุก 5 วินาที (ลดความถี่ลง)
    notificationPollingInterval = setInterval(() => {
        checkForNewNotifications();
    }, 5000);
}

function stopNotificationPolling() {
    if (notificationPollingInterval) {
        clearInterval(notificationPollingInterval);
        notificationPollingInterval = null;
    }
}

// เก็บ ID ของการแจ้งเตือนที่ประมวลผลแล้ว
let processedNotifications = new Set();

// ปิด event listener สำหรับการแจ้งเตือนจาก localStorage เพื่อป้องกันการแจ้งเตือนซ้ำซ้อน
// การแจ้งเตือนจะถูกจัดการผ่าน startNotificationPolling() เท่านั้น

/*
window.addEventListener('newStaffNotification', function(event) {
    // Event listener นี้ถูกปิดการใช้งานเพื่อป้องกันการแจ้งเตือนซ้ำซ้อน
});
*/

// ปิดการตรวจสอบ localStorage เพื่อป้องกันการแจ้งเตือนซ้ำซ้อน
// การแจ้งเตือนจะถูกจัดการผ่าน startNotificationPolling() เท่านั้น

/*
function checkLocalStorageNotifications() {
    // ฟังก์ชันนี้ถูกปิดการใช้งานเพื่อป้องกันการแจ้งเตือนซ้ำซ้อน
}
*/

// ลบการ polling localStorage ออกเพื่อป้องกันการแสดงซ้ำ
// การแจ้งเตือนจะถูกจัดการผ่าน startNotificationPolling() และ window.addEventListener เท่านั้น

// หยุด polling เมื่อออกจากหน้า
window.addEventListener('beforeunload', function() {
    stopNotificationPolling();
});

// ฟังก์ชันแสดงประวัติคำสั่งซื้อ
function showOrderHistory() {
    // โหลดรายการโต๊ะใน dropdown
    loadTablesForHistory();
    
    // โหลดตัวเลือกเดือน
    loadMonthlyOptions();
    
    // ตั้งค่าวันที่เริ่มต้น (วันนี้)
    const today = new Date();
    
    document.getElementById('historyStartDate').value = today.toISOString().split('T')[0];
    document.getElementById('historyEndDate').value = today.toISOString().split('T')[0];
    
    // ตั้งค่าปุ่ม "วันนี้" เป็น active
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('button[onclick="setQuickFilter(\'today\')"]').classList.add('active');
    
    // แสดงส่วนสรุปตั้งแต่เริ่มต้น
    const summaryContainer = document.getElementById('summarySectionContainer');
    if (summaryContainer) {
        summaryContainer.style.display = 'block';
    }
    
    // แสดง Modal
    const modal = new bootstrap.Modal(document.getElementById('orderHistoryModal'));
    modal.show();
    
    // โหลดประวัติเริ่มต้น
    loadOrderHistory();
}

// ตั้งค่าตัวกรองด่วน
function setQuickFilter(type) {
    const today = new Date();
    let startDate, endDate;
    
    // ลบ active class จากปุ่มทั้งหมด
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // เพิ่ม active class ให้ปุ่มที่เลือก
    event.target.classList.add('active');
    
    // ล้างการเลือกเดือนและเช็คบ็อกซ์ช่วงวันที่
    document.getElementById('monthlyFilter').value = '';
    document.getElementById('enableCustomDateRange').checked = false;
    document.getElementById('customDateRangeContainer').style.display = 'none';
    document.getElementById('historyStartDate').disabled = true;
    document.getElementById('historyEndDate').disabled = true;
    
    switch(type) {
        case 'today':
            startDate = new Date(today);
            endDate = new Date(today);
            break;
        case '7days':
            startDate = new Date(today.getTime() - 6 * 24 * 60 * 60 * 1000);
            endDate = new Date(today);
            break;
        case '30days':
            startDate = new Date(today.getTime() - 29 * 24 * 60 * 60 * 1000);
            endDate = new Date(today);
            break;
        case 'all':
            startDate = null;
            endDate = null;
            break;
    }
    
    // ตั้งค่าวันที่ใน input
    document.getElementById('historyStartDate').value = startDate ? startDate.toISOString().split('T')[0] : '';
    document.getElementById('historyEndDate').value = endDate ? endDate.toISOString().split('T')[0] : '';
    
    // โหลดข้อมูลใหม่
    loadOrderHistory();
    
    // หมายเหตุ: ไม่เรียก loadSummaryData เพื่อป้องกันการเขียนทับข้อมูลใน dashboard
    // ให้ dashboard-enhanced.js จัดการข้อมูลสรุปยอดขายเอง
    // let filterType = type;
    // if (type === '7days') filterType = 'week7';
    // if (type === '30days') filterType = 'month30';
    // if (type === 'all') filterType = 'allTime';
    // loadSummaryData(filterType);
}

// โหลดตัวเลือกเดือน
function loadMonthlyOptions() {
    const select = document.getElementById('monthlyFilter');
    select.innerHTML = '<option value="">-- เลือกเดือน --</option>';
    
    const months = [
        'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
        'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
    ];
    
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth();
    
    // เพิ่มเดือนปีปัจจุบันและปีที่แล้ว
    for (let year = currentYear; year >= currentYear - 1; year--) {
        for (let month = 11; month >= 0; month--) {
            // ถ้าเป็นปีปัจจุบัน ให้แสดงเฉพาะเดือนที่ผ่านมาแล้ว
            if (year === currentYear && month > currentMonth) continue;
            
            const monthValue = `${year}-${String(month + 1).padStart(2, '0')}`;
            const monthText = `${months[month]} ${year}`;
            select.innerHTML += `<option value="${monthValue}">${monthText}</option>`;
        }
    }
}

// ตั้งค่าตัวกรองรายเดือน
function setMonthlyFilter() {
    const monthValue = document.getElementById('monthlyFilter').value;
    
    // ลบ active class จากปุ่มตัวกรองด่วนและล้างเช็คบ็อกซ์ช่วงวันที่
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById('enableCustomDateRange').checked = false;
    document.getElementById('customDateRangeContainer').style.display = 'none';
    document.getElementById('historyStartDate').disabled = true;
    document.getElementById('historyEndDate').disabled = true;
    
    if (monthValue) {
        const [year, month] = monthValue.split('-');
        const startDate = new Date(year, month - 1, 1);
        const endDate = new Date(year, month, 0); // วันสุดท้ายของเดือน
        
        document.getElementById('historyStartDate').value = startDate.toISOString().split('T')[0];
        document.getElementById('historyEndDate').value = endDate.toISOString().split('T')[0];
        
        // โหลดข้อมูลสรุปยอดขายสำหรับเดือนที่เลือก
        // if (typeof selectSummaryDateRange === 'function') {
        //     selectSummaryDateRange('month');
        // }
        // Note: Commented out to prevent interference with dashboard-enhanced.js
    } else {
        // ถ้าไม่เลือกเดือน ให้ล้างวันที่
        document.getElementById('historyStartDate').value = '';
        document.getElementById('historyEndDate').value = '';
        
        // โหลดข้อมูลสรุปยอดขายวันนี้
        // if (typeof selectSummaryDateRange === 'function') {
        //     selectSummaryDateRange('today');
        // }
        // Note: Commented out to prevent interference with dashboard-enhanced.js
    }
    
    // โหลดข้อมูลใหม่
    loadOrderHistory();
}

// ฟังก์ชันเปิด/ปิดการใช้ช่วงวันที่กำหนดเอง
function toggleCustomDateRange() {
    const checkbox = document.getElementById('enableCustomDateRange');
    const container = document.getElementById('customDateRangeContainer');
    const startDateInput = document.getElementById('historyStartDate');
    const endDateInput = document.getElementById('historyEndDate');
    
    if (checkbox.checked) {
        // เปิดใช้งานช่วงวันที่
        container.style.display = 'block';
        startDateInput.disabled = false;
        endDateInput.disabled = false;
        
        // ล้างตัวกรองอื่นๆ
        document.getElementById('monthlyFilter').value = '';
        document.querySelectorAll('.btn-group .btn').forEach(btn => {
            btn.classList.remove('active');
        });
    } else {
        // ปิดใช้งานช่วงวันที่
        container.style.display = 'none';
        startDateInput.disabled = true;
        endDateInput.disabled = true;
        startDateInput.value = '';
        endDateInput.value = '';
        
        // โหลดข้อมูลสรุปยอดขายวันนี้
        // if (typeof selectSummaryDateRange === 'function') {
        //     selectSummaryDateRange('today');
        // }
        // Note: Commented out to prevent interference with dashboard-enhanced.js
        loadOrderHistory();
    }
}

// ฟังก์ชันสำหรับควบคุม checkbox ในแดชบอร์ด
function toggleCustomDateRangeDashboard() {
    const checkbox = document.getElementById('enableCustomDateRangeDashboard');
    const container = document.getElementById('customDateInputsContainer');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    
    if (checkbox.checked) {
        // เปิดใช้งานช่วงวันที่กำหนดเอง
        container.style.display = 'block';
        startDateInput.disabled = false;
        endDateInput.disabled = false;
        
        // ล้าง active class จากปุ่มช่วงวันที่
        document.querySelectorAll('#btn-today, #btn-week, #btn-month').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // ตั้งค่าวันที่เริ่มต้นเป็นวันนี้
        const today = new Date().toISOString().split('T')[0];
        startDateInput.value = today;
        endDateInput.value = today;
        
        // โหลดข้อมูลแดชบอร์ดด้วยวันที่ที่เลือก
        if (typeof loadCustomDateData === 'function') {
            loadCustomDateData();
        }
    } else {
        // ปิดใช้งานช่วงวันที่กำหนดเอง
        container.style.display = 'none';
        startDateInput.disabled = true;
        endDateInput.disabled = true;
        startDateInput.value = '';
        endDateInput.value = '';
        
        // กลับไปใช้ช่วงวันที่เริ่มต้น (วันนี้)
        if (typeof selectDateRange === 'function') {
            selectDateRange('today');
        }
    }
}

// ฟังก์ชันโหลดข้อมูลตามช่วงวันที่ที่เลือก
function loadCustomDateRange() {
    const startDate = document.getElementById('historyStartDate').value;
    const endDate = document.getElementById('historyEndDate').value;
    
    if (startDate && endDate) {
        // ตรวจสอบว่าวันที่เริ่มต้นไม่เกินวันที่สิ้นสุด
        if (new Date(startDate) > new Date(endDate)) {
            alert('วันที่เริ่มต้นต้องไม่เกินวันที่สิ้นสุด');
            return;
        }
        
        // โหลดข้อมูลสรุปยอดขายสำหรับช่วงวันที่ที่เลือก
        // ใช้ dashboard-enhanced.js จัดการแทน
        // loadSummaryData('custom', null, startDate, endDate);
    } else if (startDate || endDate) {
        // ถ้ามีการเลือกวันที่เพียงด้านเดียว
        // ใช้ dashboard-enhanced.js จัดการแทน
        // loadSummaryData('custom', null, startDate, endDate);
    }
    
    // โหลดข้อมูลประวัติออเดอร์
    loadOrderHistory();
}

// ฟังก์ชันโหลดรายการโต๊ะสำหรับ dropdown ประวัติ
async function loadTablesForHistory() {
    try {
        const response = await fetch('/api/tables');
        const data = await response.json();
        
        const select = document.getElementById('historyTableSelect');
        select.innerHTML = '<option value="">-- ทุกโต๊ะ --</option>';
        
        if (data.success && data.tables) {
            data.tables.forEach(table => {
                const option = document.createElement('option');
                option.value = table.table_id;
                option.textContent = table.table_name || `โต๊ะ ${table.table_id}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading tables for history:', error);
    }
}

// ฟังก์ชันโหลดประวัติคำสั่งซื้อ
async function loadOrderHistory() {
    const tableId = document.getElementById('historyTableSelect').value;
    const startDate = document.getElementById('historyStartDate').value;
    const endDate = document.getElementById('historyEndDate').value;
    
    const container = document.getElementById('order-history-content');
    container.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
    
    try {
        let url = '/api/current-orders?';
        const params = new URLSearchParams();
        
        if (tableId) params.append('table_id', tableId);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        url += params.toString();
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success && data.data) {
            // แสดงข้อมูลสรุปและประวัติ
            displayOrderSummary(data.data);
            renderOrderHistory(data.data);
        } else {
            // ซ่อนข้อมูลสรุปและแสดงข้อความไม่พบข้อมูล
            hideSummarySection();
            container.innerHTML = '<div class="text-center text-muted py-4"><i class="fas fa-history fa-3x mb-3"></i><p>ไม่พบประวัติคำสั่งซื้อ</p></div>';
        }
        

    } catch (error) {
        console.error('Error loading order history:', error);
        hideSummarySection();
        container.innerHTML = '<div class="text-center text-danger py-4"><i class="fas fa-exclamation-triangle fa-3x mb-3"></i><p>เกิดข้อผิดพลาดในการโหลดประวัติ</p></div>';
    }
}

// ฟังก์ชันแสดงข้อมูลสรุปยอดขาย
function displayOrderSummary(history) {
    console.log('displayOrderSummary called with:', history);
    const summaryContainer = document.getElementById('summarySectionContainer');
    console.log('summaryContainer found:', summaryContainer);
    
    if (!history || history.length === 0) {
        console.log('No history data, hiding summary section');
        hideSummarySection();
        return;
    }
    
    // คำนวณข้อมูลสรุป
    let totalSales = 0;
    let totalOrders = 0;
    const uniqueSessions = new Set();
    
    // จัดกลุ่มตาม session_id เพื่อนับจำนวนบิล
    const sessionGroups = {};
    
    history.forEach(order => {
        const sessionKey = order.session_id || 'no-session';
        
        if (!sessionGroups[sessionKey]) {
            sessionGroups[sessionKey] = {
                session_id: order.session_id,
                total_amount: 0,
                order_count: 0
            };
            uniqueSessions.add(sessionKey);
        }
        
        // คำนวณยอดรวมของแต่ละออเดอร์
        let orderTotal = 0;
        order.items.forEach(item => {
            // ไม่รวมรายการที่ถูกปฏิเสธในการคำนวณยอดรวม
            if (item.status !== 'rejected') {
                orderTotal += item.quantity * (item.unit_price || item.price);
            }
        });
        
        sessionGroups[sessionKey].total_amount += orderTotal;
        sessionGroups[sessionKey].order_count += 1;
        totalOrders += 1;
    });
    
    // คำนวณยอดขายรวม
    Object.values(sessionGroups).forEach(session => {
        totalSales += session.total_amount;
    });
    
    const totalSessions = uniqueSessions.size;
    
    // อัปเดตข้อมูลในการ์ดสรุป
    document.getElementById('totalSummary').textContent = formatCurrency(totalSales);
    document.getElementById('totalSessions').textContent = totalSessions.toLocaleString();
    document.getElementById('totalOrders').textContent = totalOrders.toLocaleString();
    
    // แสดงส่วนสรุป
    summaryContainer.style.display = 'block';
}

// ฟังก์ชันซ่อนส่วนสรุป
function hideSummarySection() {
    const summaryContainer = document.getElementById('summarySectionContainer');
    if (summaryContainer) {
        summaryContainer.style.display = 'none';
    }
}

// ฟังก์ชันแสดงประวัติคำสั่งซื้อ
function renderOrderHistory(history) {
    const container = document.getElementById('order-history-content');
    
    if (history.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-4"><i class="fas fa-history fa-3x mb-3"></i><p>ไม่พบประวัติคำสั่งซื้อ</p></div>';
        return;
    }
    
    // จัดกลุ่มตาม session_id
    const sessionGroups = {};
    history.forEach(order => {
        const sessionKey = order.session_id || 'no-session';
        if (!sessionGroups[sessionKey]) {
            sessionGroups[sessionKey] = {
                session_id: order.session_id,
                table_id: order.table_id,
                table_name: order.table_name,
                orders: [],
                total_amount: 0,
                session_date: order.created_at,
                bill_status: order.bill_status || 'unchecked'
            };
        }
        sessionGroups[sessionKey].orders.push(order);
        
        // คำนวณยอดรวม
        let orderTotal = 0;
        order.items.forEach(item => {
            // ไม่รวมรายการที่ถูกปฏิเสธในการคำนวณยอดรวม
            if (item.status !== 'rejected') {
                orderTotal += item.quantity * (item.unit_price || item.price);
            }
        });
        sessionGroups[sessionKey].total_amount += orderTotal;
    });
    
    let historyHTML = '';
    Object.values(sessionGroups).forEach(session => {
        let itemsHTML = '';
        session.orders.forEach(order => {
            order.items.forEach(item => {
                const itemTotal = item.quantity * (item.unit_price || item.price);
                
                // Handle price display for rejected items
                let priceDisplay, totalDisplay;
                if (item.status === 'rejected') {
                    // Show strikethrough original price and 0.00 for rejected items
                    priceDisplay = `<span style="text-decoration: line-through; color: #6c757d;">${formatCurrency(item.unit_price || item.price)}</span><br><span style="color: #dc3545; font-weight: bold;">${formatCurrency(0)}</span>`;
                    totalDisplay = `<span style="text-decoration: line-through; color: #6c757d;">${formatCurrency(itemTotal)}</span><br><span style="color: #dc3545; font-weight: bold;">${formatCurrency(0)}</span>`;
                } else {
                    // Normal price display for other statuses
                    priceDisplay = formatCurrency(item.unit_price || item.price);
                    totalDisplay = formatCurrency(itemTotal);
                }
                
                // สร้างชื่อรายการพร้อมระดับความเผ็ดและเพิ่มพิเศษ
                let itemNameWithDetails = item.name;
                let specialOptionsDisplay = '';
                
                if (item.customer_request) {
                    // แยกตัวเลือกพิเศษออกจากหมายเหตุ (ถ้ามี | คั่น)
                    const parts = item.customer_request.split(' | ');
                    // แยกตัวเลือก spice และ addon
                    const spiceOptions = parts.filter(part => 
                        part.includes('เผ็ด') || part.includes('หวาน') || part.includes('ปกติ')
                    );
                    const addonOptions = parts.filter(part => 
                        part.includes('ไข่') || part.includes('เพิ่ม')
                    ).filter(part => !part.includes('ไม่เพิ่ม')); // กรอง "ไม่เพิ่ม" ออก
                    
                    const notes = parts.filter(part => 
                        !part.includes('เผ็ด') && !part.includes('หวาน') && 
                        !part.includes('ไข่') && !part.includes('เพิ่ม') &&
                        !part.includes('ไม่เพิ่ม') && !part.includes('ปกติ')
                    );
                    
                    // รวม spice options เข้ากับชื่อเมนูในวงเล็บ
                    if (spiceOptions.length > 0) {
                        itemNameWithDetails += ` <span class="${getCustomerRequestClass(spiceOptions[0])}">(${spiceOptions[0]})</span>`;
                    }
                    
                    // แสดง addon options เป็นรายการด้านล่าง
                    if (addonOptions.length > 0) {
                        const addonList = addonOptions.map(option => `<div class="text-muted small">- ${option}</div>`).join('');
                        specialOptionsDisplay += `<div class="mt-1">${addonList}</div>`;
                    }
                    
                    if (notes.length > 0) {
                        specialOptionsDisplay += `<div class="special-notes"><i class="fas fa-sticky-note me-1"></i>${notes.join(', ')}</div>`;
                    }
                }
                
                itemsHTML += `
                    <tr>
                        <td>
                            <div>${itemNameWithDetails}</div>
                            ${specialOptionsDisplay}
                        </td>
                        <td class="text-center">${item.quantity}</td>
                        <td class="text-end">${priceDisplay}</td>
                        <td class="text-end">${totalDisplay}</td>
                        <td class="text-center">
                            <span class="badge ${getStatusBadgeClass(item.status)}">
                                ${getStatusText(item.status)}
                            </span>
                        </td>
                    </tr>
                `;
            });
        });
        
        historyHTML += `
            <div class="card mb-3">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-utensils me-2"></i>
                            ${session.table_name || `โต๊ะ ${session.table_id}`}
                            ${session.session_id ? `<small class="text-muted ms-2">#${session.session_id.substring(0, 8)}</small>` : ''}
                        </h6>
                        <div class="mt-1">
                            <span class="badge bg-${getBillStatusColor(session.bill_status)}">${getBillStatusText(session.bill_status)}</span>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <div class="text-end">
                                <div class="fw-bold text-primary">${formatCurrency(session.total_amount)}</div>
                                <small class="text-muted">${formatDateTime(session.session_date)}</small>
                            </div>
                            <div class="btn-group">
                                <button class="btn btn-outline-success btn-sm" onclick="console.log('Print button clicked for session:', '${session.session_id}'); reprintReceipt(${session.orders[0].order_id});" title="พิมพ์ใบเสร็จ" style="font-weight: bold;">
                                    <i class="fas fa-print"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="confirmDeleteSession('${session.session_id}')" title="ลบประวัติ">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>รายการ</th>
                                    <th class="text-center">จำนวน</th>
                                    <th class="text-end">ราคา</th>
                                    <th class="text-end">รวม</th>
                                    <th class="text-center">สถานะ</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${itemsHTML}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = historyHTML;
}

// ฟังก์ชันช่วยเหลือสำหรับสถานะ
function getStatusBadgeClass(status) {
    switch(status) {
        case 'pending': return 'bg-warning';
        case 'accepted': return 'bg-info';
        case 'active': return 'bg-primary';
        case 'completed': return 'bg-success';
        case 'cancelled': return 'bg-danger';
        case 'rejected': return 'bg-danger';
        default: return 'bg-primary';
    }
}

function getStatusText(status) {
    switch(status) {
        case 'pending': return 'รอดำเนินการ';
        case 'accepted': return 'รับแล้ว';
        case 'active': return 'กำลังดำเนินการ';
        case 'completed': return 'เสร็จสิ้น';
        case 'cancelled': return 'ยกเลิก';
        case 'rejected': return 'ปฏิเสธ';
        default: return status;
    }
}

// ฟังก์ชันส่งออกประวัติคำสั่งซื้อ
function exportOrderHistory() {
    const tableId = document.getElementById('historyTableSelect').value;
    const startDate = document.getElementById('historyStartDate').value;
    const endDate = document.getElementById('historyEndDate').value;
    
    let url = '/api/order-history/export?';
    const params = new URLSearchParams();
    
    if (tableId) params.append('table_id', tableId);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    url += params.toString();
    
    // เปิดลิงก์ในหน้าต่างใหม่เพื่อดาวน์โหลด
    window.open(url, '_blank');
}

// ยืนยันการลบประวัติ session
function confirmDeleteSession(sessionId) {
    if (!sessionId || sessionId === 'no-session') {
        showAlert('ไม่สามารถลบประวัติที่ไม่มี session ID ได้', 'warning');
        return;
    }
    
    const modalHtml = `
        <div class="modal fade" id="deleteSessionModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-trash me-2"></i>
                            ลบประวัติออเดอร์
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="card border-warning">
                            <div class="card-body p-2">
                                <small class="text-warning">
                                    <i class="fas fa-exclamation-triangle me-2"></i>
                                    คุณแน่ใจหรือไม่ที่จะลบประวัติออเดอร์ทั้งหมดในเซสชันนี้?
                                </small>
                            </div>
                        </div>
                        <p class="text-danger">
                            <strong>คำเตือน:</strong> การลบประวัติออเดอร์จะไม่สามารถกู้คืนได้ และจะส่งผลต่อรายงานและสถิติของระบบ
                        </p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="button" class="btn btn-danger" onclick="deleteSession('${sessionId}'); bootstrap.Modal.getInstance(document.getElementById('deleteSessionModal')).hide();">
                            <i class="fas fa-trash me-1"></i>ลบประวัติ
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ Modal เก่า (ถ้ามี)
    const existingModal = document.getElementById('deleteSessionModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม Modal ใหม่
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง Modal
    const modal = new bootstrap.Modal(document.getElementById('deleteSessionModal'));
    modal.show();
    
    // ลบ Modal เมื่อปิด
    document.getElementById('deleteSessionModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// ลบประวัติ session
async function deleteSession(sessionId) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/delete-session/${sessionId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('ลบประวัติออเดอร์สำเร็จ', 'success');
            // โหลดประวัติใหม่
            loadOrderHistory();
        } else {
            throw new Error(data.error || 'ไม่สามารถลบประวัติออเดอร์ได้');
        }
    } catch (error) {
        console.error('Error deleting session:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// Additional Options Management Functions
let optionTypes = [];

async function loadOptionTypes() {
    try {
        const response = await fetch('/api/option-types');
        const result = await response.json();
        
        if (result.success) {
            optionTypes = result.data.map(type => ({
                id: type.key,
                name: type.name,
                type: type.key,
                option_type_id: type.option_type_id,
                description: type.description
            }));
        } else {
            console.error('Error loading option types:', result.error);
            // Fallback to default data
            optionTypes = [
                { id: 'spice', name: 'ระดับความเผ็ด', type: 'spice' },
                { id: 'sweet', name: 'ระดับความหวาน', type: 'sweet' }
            ];
        }
        
        renderOptionTypes();
    } catch (error) {
        console.error('Error loading option types:', error);
        // Fallback to default data
        optionTypes = [
            { id: 'spice', name: 'ระดับความเผ็ด', type: 'spice' },
            { id: 'sweet', name: 'ระดับความหวาน', type: 'sweet' }
        ];
        renderOptionTypes();
    }
}

function renderOptionTypes() {
    const container = document.getElementById('option-types-list');
    if (!container) return;
    
    container.innerHTML = optionTypes.map(option => `
        <div class=\"option-type-item mb-2 p-3 border rounded\">
            <div class=\"d-flex justify-content-between align-items-center\">
                <div>
                    <strong>${option.name}</strong>
                    <small class=\"text-muted d-block\">รหัส: ${option.type}</small>
                    ${option.description ? `<small class=\"text-info d-block\">${option.description}</small>` : ''}
                </div>
                <div>
                    <button class=\"btn btn-sm btn-outline-success me-2\" onclick=\"manageOptionValues('${option.id}')\" title=\"จัดการตัวเลือกย่อย\" style=\"background-color: #198754 !important; color: white !important; border: 1px solid #198754 !important; display: inline-block !important; visibility: visible !important; opacity: 1 !important; z-index: 9999 !important;\">
                        <i class=\"fas fa-list\"></i>
                    </button>
                    <button class=\"btn btn-sm btn-outline-primary me-2\" onclick=\"editOptionType('${option.id}')\">
                        <i class=\"fas fa-edit\"></i>
                    </button>
                    <button class=\"btn btn-sm btn-outline-danger\" onclick=\"deleteOptionType('${option.id}')\">
                        <i class=\"fas fa-trash\"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function showAddOptionTypeModal() {
    const modalHTML = `
        <div class="modal fade" id="addOptionTypeModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">เพิ่มประเภทตัวเลือกใหม่</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addOptionTypeForm">
                            <div class="mb-3">
                                <label for="optionTypeName" class="form-label">ชื่อประเภทตัวเลือก</label>
                                <input type="text" class="form-control" id="optionTypeName" required>
                                <div class="form-text">เช่น ระดับความเผ็ด, ระดับความหวาน</div>
                            </div>
                            <div class="mb-3">
                                <label for="optionTypeKey" class="form-label">รหัสประเภท (Key)</label>
                                <input type="text" class="form-control" id="optionTypeKey" required>
                                <div class="form-text">เช่น spice, sweet (ใช้ภาษาอังกฤษ ไม่มีช่องว่าง)</div>
                            </div>
                            <div class="mb-3">
                                <label for="optionTypeDescription" class="form-label">คำอธิบาย (ไม่บังคับ)</label>
                                <textarea class="form-control" id="optionTypeDescription" rows="2"></textarea>
                                <div class="form-text">คำอธิบายเพิ่มเติมเกี่ยวกับประเภทตัวเลือกนี้</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="button" class="btn btn-primary" onclick="addOptionType()">เพิ่ม</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('addOptionTypeModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('addOptionTypeModal'));
    modal.show();
}

async function addOptionType() {
    const name = document.getElementById('optionTypeName').value.trim();
    const key = document.getElementById('optionTypeKey').value.trim();
    const description = document.getElementById('optionTypeDescription').value.trim();
    
    if (!name || !key) {
        showAlert('กรุณากรอกข้อมูลให้ครบถ้วน', 'warning');
        return;
    }
    
    // Validate key format (only lowercase letters and underscores)
    if (!/^[a-z_]+$/.test(key)) {
        showAlert('รหัสประเภทต้องเป็นภาษาอังกฤษตัวเล็กและขีดล่างเท่านั้น', 'warning');
        return;
    }
    
    // Check if key already exists
    if (optionTypes.find(option => option.id === key)) {
        showAlert('รหัสประเภทนี้มีอยู่แล้ว', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/option-types', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                key: key,
                name: name,
                description: description || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('เพิ่มประเภทตัวเลือกสำเร็จ', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addOptionTypeModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('optionTypeName').value = '';
            document.getElementById('optionTypeKey').value = '';
            document.getElementById('optionTypeDescription').value = '';
            
            // Refresh option types list
            loadOptionTypes();
        } else {
            throw new Error(data.error || 'ไม่สามารถเพิ่มประเภทตัวเลือกได้');
        }
        
    } catch (error) {
        console.error('Error adding option type:', error);
        showAlert('เกิดข้อผิดพลาด: ' + error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

function editOptionType(optionId) {
    const option = optionTypes.find(opt => opt.id === optionId);
    if (!option) return;
    
    const modalHTML = `
        <div class="modal fade" id="editOptionTypeModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">แก้ไขประเภทตัวเลือก</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editOptionTypeForm">
                            <div class="mb-3">
                                <label for="editOptionTypeName" class="form-label">ชื่อประเภทตัวเลือก</label>
                                <input type="text" class="form-control" id="editOptionTypeName" value="${option.name}" required>
                            </div>
                            <div class="mb-3">
                                <label for="editOptionTypeKey" class="form-label">รหัสประเภท (Key)</label>
                                <input type="text" class="form-control" id="editOptionTypeKey" value="${option.type}" required>
                                <div class="form-text">การเปลี่ยนรหัสอาจส่งผลต่อเมนูที่มีอยู่</div>
                            </div>
                            <div class="mb-3">
                                <label for="editOptionTypeDescription" class="form-label">คำอธิบาย (ไม่บังคับ)</label>
                                <textarea class="form-control" id="editOptionTypeDescription" rows="2">${option.description || ''}</textarea>
                                <div class="form-text">คำอธิบายเพิ่มเติมเกี่ยวกับประเภทตัวเลือกนี้</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="button" class="btn btn-primary" onclick="saveOptionTypeEdit('${optionId}')">บันทึก</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('editOptionTypeModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('editOptionTypeModal'));
    modal.show();
}

async function saveOptionTypeEdit(optionId) {
    const name = document.getElementById('editOptionTypeName').value.trim();
    const key = document.getElementById('editOptionTypeKey').value.trim();
    const description = document.getElementById('editOptionTypeDescription').value.trim();
    
    if (!name || !key) {
        showAlert('กรุณากรอกข้อมูลให้ครบถ้วน', 'warning');
        return;
    }
    
    // Validate key format (only lowercase letters and underscores)
    if (!/^[a-z_]+$/.test(key)) {
        showAlert('รหัสประเภทต้องเป็นภาษาอังกฤษตัวเล็กและขีดล่างเท่านั้น', 'warning');
        return;
    }
    
    // Check if key already exists (excluding current option)
    if (optionTypes.find(option => option.type === key && option.id !== optionId)) {
        showAlert('รหัสประเภทนี้มีอยู่แล้ว', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`/api/option-types/${optionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: key,
                name: name,
                description: description || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('แก้ไขประเภทตัวเลือกสำเร็จ', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editOptionTypeModal'));
            modal.hide();
            
            // Refresh option types list
            loadOptionTypes();
        } else {
            throw new Error(data.error || 'ไม่สามารถแก้ไขประเภทตัวเลือกได้');
        }
        
    } catch (error) {
        console.error('Error updating option type:', error);
        showAlert('เกิดข้อผิดพลาด: ' + error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

async function deleteOptionType(optionId) {
    const option = optionTypes.find(opt => opt.id === optionId);
    if (!option) return;
    
    if (confirm(`คุณต้องการลบประเภทตัวเลือก "${option.name}" หรือไม่?\n\nการลบอาจส่งผลต่อเมนูที่ใช้ประเภทตัวเลือกนี้`)) {
        try {
            showLoading(true);
            
            const response = await fetch(`/api/option-types/${optionId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('ลบประเภทตัวเลือกสำเร็จ', 'success');
                
                // Refresh option types list
                loadOptionTypes();
            } else {
                throw new Error(data.error || 'ไม่สามารถลบประเภทตัวเลือกได้');
            }
            
        } catch (error) {
            console.error('Error deleting option type:', error);
            showAlert('เกิดข้อผิดพลาด: ' + error.message, 'danger');
        } finally {
            showLoading(false);
        }
    }
}

// ฟังก์ชันจัดการตัวเลือกย่อย
function manageOptionValues(optionType) {
    console.log('Managing option values for:', optionType);
    
    let modalTitle = '';
    
    // กำหนดชื่อ modal ตามประเภท
    if (optionType === 'spice') {
        modalTitle = 'จัดการระดับความเผ็ด';
    } else if (optionType === 'sweet') {
        modalTitle = 'จัดการระดับความหวาน';
    }
    
    // ดึงข้อมูลค่าตัวเลือกจาก API
    fetch(`/api/option-values?option_type=${optionType}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const optionValues = data.data;
                showOptionValuesModal(optionType, modalTitle, optionValues);
            } else {
                showAlert('ไม่สามารถดึงข้อมูลค่าตัวเลือกได้', 'error');
            }
        })
        .catch(error => {
            console.error('Error fetching option values:', error);
            showAlert('เกิดข้อผิดพลาดในการดึงข้อมูล', 'error');
        });
}

// ฟังก์ชันแสดง modal สำหรับจัดการค่าตัวเลือก
function showOptionValuesModal(optionType, modalTitle, optionValues) {
    
    // สร้าง HTML สำหรับ modal
    const modalHTML = `
        <div class="modal fade" id="optionValuesModal" tabindex="-1" data-option-type="${optionType}">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-list me-2"></i>${modalTitle}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="mb-0">รายการตัวเลือก</h6>
                            <button class="btn btn-primary btn-sm" onclick="addNewOptionValue('${optionType}')">
                                <i class="fas fa-plus me-1"></i>เพิ่มตัวเลือก
                            </button>
                        </div>
                        <div id="optionValuesList">
                            ${optionValues.map(option => `
                                <div class="option-value-item mb-2 p-3 border rounded" data-option-id="${option.option_value_id}">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div class="d-flex align-items-center">
                                            <div class="form-check me-3">
                                                <input class="form-check-input" type="radio" name="defaultOption" 
                                                       id="default_${option.option_value_id}" value="${option.option_value_id}" ${option.is_default ? 'checked' : ''}
                                                       onchange="setDefaultOption(${option.option_value_id})">
                                                <label class="form-check-label" for="default_${option.option_value_id}">
                                                    <small class="text-muted">ค่าเริ่มต้น</small>
                                                </label>
                                            </div>
                                            <div>
                                                <strong>${option.name}</strong>
                                                ${option.additional_price > 0 ? `<span class="badge bg-info ms-2">+${option.additional_price} บาท</span>` : ''}
                                                ${option.is_default ? '<span class="badge bg-success ms-2">ค่าเริ่มต้น</span>' : ''}
                                            </div>
                                        </div>
                                        <div>
                                            <button class="btn btn-sm btn-outline-primary me-1" 
                                                    onclick="editOptionValue(${option.option_value_id}, '${option.name}', ${option.additional_price || 0})">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" 
                                                    onclick="deleteOptionValue(${option.option_value_id})">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ปิด</button>
                        <button type="button" class="btn btn-primary" onclick="saveOptionValues('${optionType}')">
                            <i class="fas fa-save me-1"></i>บันทึก
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่าถ้ามี
    const existingModal = document.getElementById('optionValuesModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal ใหม่
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('optionValuesModal'));
    modal.show();
}

// ฟังก์ชันเพิ่มตัวเลือกใหม่
function addNewOptionValue(optionType) {
    // สร้าง modal สำหรับเพิ่มตัวเลือกใหม่
    const addOptionModal = `
        <div class="modal fade" id="addOptionValueModal" tabindex="-1" aria-labelledby="addOptionValueModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="addOptionValueModalLabel">
                            <i class="fas fa-plus me-2"></i>เพิ่มตัวเลือกใหม่
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="newOptionName" class="form-label">ชื่อตัวเลือก</label>
                            <input type="text" class="form-control" id="newOptionName" placeholder="ระบุชื่อตัวเลือกใหม่">
                        </div>
                        <div class="mb-3">
                            <label for="newOptionPrice" class="form-label">ราคาเพิ่มเติม (บาท)</label>
                            <input type="number" class="form-control" id="newOptionPrice" placeholder="0" min="0" step="0.01" value="0">
                            <div class="form-text">ระบุราคาเพิ่มเติมสำหรับตัวเลือกนี้ (ถ้าไม่มีให้ใส่ 0)</div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="button" class="btn btn-primary" onclick="saveNewOptionValue('${optionType}')">
                            <i class="fas fa-save me-1"></i>บันทึก
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่าถ้ามี
    const existingModal = document.getElementById('addOptionValueModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal ใหม่
    document.body.insertAdjacentHTML('beforeend', addOptionModal);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('addOptionValueModal'));
    modal.show();
    
    // Focus ที่ input field
    setTimeout(() => {
        document.getElementById('newOptionName').focus();
    }, 500);
}

// ฟังก์ชันบันทึกตัวเลือกใหม่
function saveNewOptionValue(optionType) {
    const nameInput = document.getElementById('newOptionName');
    const priceInput = document.getElementById('newOptionPrice');
    const name = nameInput.value.trim();
    const additionalPrice = parseFloat(priceInput.value) || 0;
    
    if (!name) {
        showAlert('กรุณาระบุชื่อตัวเลือก', 'warning');
        nameInput.focus();
        return;
    }
    
    if (additionalPrice < 0) {
        showAlert('ราคาเพิ่มเติมต้องไม่ติดลบ', 'warning');
        priceInput.focus();
        return;
    }
    
    // เรียก API เพื่อเพิ่มค่าตัวเลือกใหม่
    fetch('/api/option-values', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            option_type: optionType,
            name: name,
            is_default: false,
            sort_order: 0,
            additional_price: additionalPrice
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // ปิด modal เพิ่มตัวเลือก
                const addModal = bootstrap.Modal.getInstance(document.getElementById('addOptionValueModal'));
                if (addModal) {
                    addModal.hide();
                }
                
                showAlert(data.message, 'success');
                // รีเฟรชเฉพาะรายการตัวเลือกใน modal ที่เปิดอยู่
                refreshOptionValuesList(optionType);
            } else {
                showAlert(data.error || 'ไม่สามารถเพิ่มตัวเลือกได้', 'error');
            }
        })
        .catch(error => {
            console.error('Error adding option value:', error);
            showAlert('เกิดข้อผิดพลาดในการเพิ่มตัวเลือก', 'error');
        });
}

// ฟังก์ชันรีเฟรชรายการตัวเลือกใน modal ที่เปิดอยู่
function refreshOptionValuesList(optionType) {
    console.log('refreshOptionValuesList called with optionType:', optionType);
    // ดึงข้อมูลตัวเลือกใหม่จาก API
    fetch(`/api/option-values?option_type=${optionType}`)
        .then(response => response.json())
        .then(data => {
            console.log('API response for option values:', data);
            if (data.success) {
                const optionValues = data.data;
                console.log('Option values data:', optionValues);
                // อัปเดตเฉพาะส่วน optionValuesList ใน modal
                const optionValuesList = document.getElementById('optionValuesList');
                console.log('optionValuesList element:', optionValuesList);
                if (optionValuesList) {
                    const newHTML = optionValues.map(option => {
                        console.log('Creating button for option:', option.option_value_id, 'with price:', option.additional_price);
                        return `
                        <div class="option-value-item mb-2 p-3 border rounded" data-option-id="${option.option_value_id}">
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="d-flex align-items-center">
                                    <div class="form-check me-3">
                                        <input class="form-check-input" type="radio" name="defaultOption" 
                                               id="default_${option.option_value_id}" value="${option.option_value_id}" ${option.is_default ? 'checked' : ''}
                                               onchange="setDefaultOption(${option.option_value_id})">
                                        <label class="form-check-label" for="default_${option.option_value_id}">
                                            <small class="text-muted">ค่าเริ่มต้น</small>
                                        </label>
                                    </div>
                                    <div>
                                        <strong>${option.name}</strong>
                                        ${option.additional_price > 0 ? `<span class="badge bg-info ms-2">+${option.additional_price} บาท</span>` : ''}
                                        ${option.is_default ? '<span class="badge bg-success ms-2">ค่าเริ่มต้น</span>' : ''}
                                    </div>
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-outline-primary me-1" 
                                            onclick="editOptionValue(${option.option_value_id}, '${option.name}', ${option.additional_price || 0})">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" 
                                            onclick="deleteOptionValue(${option.option_value_id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        `;
                    }).join('');
                    console.log('Setting new HTML for optionValuesList');
                    optionValuesList.innerHTML = newHTML;
                }
            }
        })
        .catch(error => {
            console.error('Error refreshing option values:', error);
        });
}

// ฟังก์ชันแก้ไขตัวเลือก
function editOptionValue(optionId, currentName, currentPrice = 0) {
    console.log('editOptionValue called with:', { optionId, currentName, currentPrice });
    // สร้าง modal สำหรับแก้ไขชื่อตัวเลือกและราคาเพิ่มเติม
    const modalHtml = `
        <div class="modal fade" id="editOptionValueModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">แก้ไขตัวเลือก</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">ชื่อตัวเลือก:</label>
                            <input type="text" class="form-control" id="editOptionValueInput" value="${currentName}">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">ราคาเพิ่มเติม (บาท):</label>
                            <input type="number" class="form-control" id="editOptionPriceInput" value="${currentPrice}" min="0" step="0.01">
                            <div class="form-text">ระบุราคาเพิ่มเติมสำหรับตัวเลือกนี้ (ถ้าไม่มีให้ใส่ 0)</div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="button" class="btn btn-primary" onclick="saveOptionValueEdit(${optionId})">บันทึก</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่าถ้ามี
    const existingModal = document.getElementById('editOptionValueModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal ใหม่
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('editOptionValueModal'));
    modal.show();
    
    // Focus ที่ input field
    setTimeout(() => {
        const input = document.getElementById('editOptionValueInput');
        if (input) {
            input.focus();
            input.select();
        }
    }, 300);
}

// ฟังก์ชันบันทึกการแก้ไขตัวเลือก
function saveOptionValueEdit(optionId) {
    console.log('saveOptionValueEdit called with optionId:', optionId);
    
    const nameInput = document.getElementById('editOptionValueInput');
    const priceInput = document.getElementById('editOptionPriceInput');
    
    if (!nameInput || !priceInput) {
        showAlert('ไม่พบช่องกรอกข้อมูล', 'error');
        return;
    }
    
    const newName = nameInput.value.trim();
    const newPrice = parseFloat(priceInput.value) || 0;
    
    console.log('Input values:', { newName, newPrice });
    
    if (!newName) {
        showAlert('กรุณากรอกชื่อตัวเลือก', 'warning');
        nameInput.focus();
        return;
    }
    
    if (newPrice < 0) {
        showAlert('ราคาเพิ่มเติมต้องไม่ติดลบ', 'warning');
        priceInput.focus();
        return;
    }
    
    // ลบการเปรียบเทียบค่าเดิมออกเนื่องจากไม่จำเป็น
    
    // เรียก API เพื่ออัปเดตค่าในฐานข้อมูล
    const requestData = {
        name: newName,
        additional_price: newPrice
    };
    
    console.log('Sending API request:', requestData);
    
    fetch(`/api/option-values/${optionId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('API response:', data);
        
        if (data.success) {
            showAlert(data.message, 'success');
            // ปิด modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editOptionValueModal'));
            if (modal) {
                modal.hide();
            }
            // รีเฟรช modal โดยดึง optionType จาก element
            const modalElement = document.querySelector('#optionValuesModal');
            console.log('Modal element found:', modalElement);
            if (modalElement) {
                const optionType = modalElement.dataset.optionType;
                console.log('Option type from modal:', optionType);
                if (optionType) {
                    console.log('Calling refreshOptionValuesList with:', optionType);
                    refreshOptionValuesList(optionType);
                } else {
                    console.log('No option type found in modal dataset');
                }
            } else {
                console.log('Modal element not found');
            }
        } else {
            console.log('API error:', data.error);
            showAlert(data.error || 'ไม่สามารถแก้ไขได้', 'error');
        }
    })
    .catch(error => {
        console.error('Network error:', error);
        showAlert('เกิดข้อผิดพลาดในการแก้ไข', 'error');
    });
}

// ฟังก์ชันลบตัวเลือก
function deleteOptionValue(optionId) {
    if (confirm('คุณต้องการลบตัวเลือกนี้หรือไม่?')) {
        // เรียก API เพื่อลบค่าในฐานข้อมูล
        fetch(`/api/option-values/${optionId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message, 'success');
                // รีเฟรช modal โดยดึง optionType จาก element
                const modalElement = document.querySelector('#optionValuesModal');
                if (modalElement) {
                    const optionType = modalElement.dataset.optionType;
                    if (optionType) {
                        refreshOptionValuesList(optionType);
                    }
                }
            } else {
                showAlert(data.error || 'ไม่สามารถลบได้', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting option value:', error);
            showAlert('เกิดข้อผิดพลาดในการลบ', 'error');
        });
    }
}

// ฟังก์ชันกำหนดค่าเริ่มต้น
function setDefaultOption(optionId) {
    // อัปเดต UI ให้แสดงค่าเริ่มต้นใหม่
    const badges = document.querySelectorAll('.badge.bg-success');
    badges.forEach(badge => badge.remove());
    
    const selectedItem = document.querySelector(`[data-option-id="${optionId}"]`);
    if (selectedItem) {
        const nameDiv = selectedItem.querySelector('strong').parentElement;
        nameDiv.insertAdjacentHTML('beforeend', '<span class="badge bg-success ms-2">ค่าเริ่มต้น</span>');
    }
}

// ฟังก์ชันบันทึกการตั้งค่า
function saveOptionValues(optionType) {
    // เก็บข้อมูลค่าเริ่มต้นที่เลือก
    const selectedDefault = document.querySelector(`input[name="defaultOption"]:checked`);
    
    if (!selectedDefault) {
        showAlert('กรุณาเลือกค่าเริ่มต้น', 'warning');
        return;
    }
    
    const defaultOptionId = selectedDefault.value;
    
    // ส่งข้อมูลไปยัง API เพื่อบันทึกค่าเริ่มต้น
    fetch(`/api/option-values/set-default`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            option_type: optionType,
            default_option_id: defaultOptionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // แสดง modal แจ้งเตือนการบันทึกสำเร็จ
            const successModal = `
                <div class="modal fade" id="saveSuccessModal" tabindex="-1" aria-labelledby="saveSuccessModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header bg-success text-white">
                                <h5 class="modal-title" id="saveSuccessModalLabel">
                                    <i class="fas fa-check-circle me-2"></i>บันทึกสำเร็จ
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body text-center">
                                <div class="mb-3">
                                    <i class="fas fa-check-circle text-success" style="font-size: 3rem;"></i>
                                </div>
                                <h6 class="mb-2">บันทึกการตั้งค่าเรียบร้อยแล้ว</h6>
                                <p class="text-muted mb-0">การตั้งค่าค่าเริ่มต้นได้รับการบันทึกเรียบร้อยแล้ว</p>
                            </div>
                            <div class="modal-footer justify-content-center">
                                <button type="button" class="btn btn-success" data-bs-dismiss="modal">
                                    <i class="fas fa-check me-1"></i>ตกลง
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // เพิ่ม modal ลงใน DOM
            document.body.insertAdjacentHTML('beforeend', successModal);
            
            // แสดง modal
            const modal = new bootstrap.Modal(document.getElementById('saveSuccessModal'));
            modal.show();
            
            // ลบ modal หลังจากปิด
            document.getElementById('saveSuccessModal').addEventListener('hidden.bs.modal', function () {
                this.remove();
            });
            
            // ปิด modal หลัก
            const mainModal = bootstrap.Modal.getInstance(document.getElementById('optionValuesModal'));
            if (mainModal) {
                mainModal.hide();
            }
        } else {
            showAlert(data.error || 'ไม่สามารถบันทึกได้', 'error');
        }
    })
    .catch(error => {
        console.error('Error saving default option:', error);
        showAlert('เกิดข้อผิดพลาดในการบันทึก', 'error');
    });
}

async function completeOrderItem(orderItemId) {
    try {
        const response = await fetch(`http://localhost:5000/api/order-items/${orderItemId}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            loadOrders();
            // Refresh table details if currently viewing a table detail modal
            const tableDetailModal = document.getElementById('tableDetailModal');
            if (tableDetailModal && tableDetailModal.classList.contains('show') && selectedTableId) {
                // Re-fetch and update table details without closing the modal
                await showTableDetail(selectedTableId);
            }
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        console.error('Error completing order item:', error);
        showAlert('เกิดข้อผิดพลาดในการทำเครื่องหมายรายการเสร็จสิ้น', 'danger');
    }
}

// ฟังก์ชันสำหรับแปลงสถานะบิลเป็นสี
function getBillStatusColor(status) {
    switch(status) {
        case 'checked': return 'success';
        case 'unchecked': return 'primary';
        default: return 'primary';
    }
}

// ฟังก์ชันสำหรับแปลงสถานะบิลเป็นข้อความ
function getBillStatusText(status) {
    switch(status) {
        case 'checked': return 'เช็คบิลแล้ว';
        case 'unchecked': return 'ยังไม่เช็คบิล';
        default: return 'ยังไม่เช็คบิล';
    }
}

// ฟังก์ชันสำหรับพิมพ์ใบเสร็จซ้ำ - ใช้ฟังก์ชัน printReceipt เดียวกัน
// ฟังก์ชัน reprintReceipt เดิม - ตอนนี้เรียกใช้ printReceipt แบบใหม่
async function reprintReceipt(orderId) {
    return await printReceipt(orderId, true);
}

// ฟังก์ชันสำหรับเปลี่ยนสถานะบิล
async function toggleBillStatus(orderId, currentStatus) {
    try {
        const newStatus = currentStatus === 'checked' ? 'unchecked' : 'checked';
        const statusText = newStatus === 'checked' ? 'เช็คบิลแล้ว' : 'ยังไม่เช็คบิล';
        
        if (!confirm(`คุณต้องการเปลี่ยนสถานะบิลเป็น "${statusText}" หรือไม่?`)) {
            return;
        }
        
        showLoading(true);
        
        const response = await fetch(`/api/orders/${orderId}/bill-status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                bill_status: newStatus
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(`เปลี่ยนสถานะบิลเป็น "${statusText}" เรียบร้อยแล้ว`, 'success');
            loadOrderHistory(); // โหลดข้อมูลใหม่
        } else {
            throw new Error(data.error || 'ไม่สามารถเปลี่ยนสถานะบิลได้');
        }
    } catch (error) {
        console.error('Error toggling bill status:', error);
        showAlert('เกิดข้อผิดพลาดในการเปลี่ยนสถานะบิล', 'danger');
    } finally {
        showLoading(false);
    }
}
