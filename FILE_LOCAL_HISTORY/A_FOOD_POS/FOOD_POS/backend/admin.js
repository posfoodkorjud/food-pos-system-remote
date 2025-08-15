// Admin Panel JavaScript

// Global variables
let currentSection = 'tables';
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
    
    // Setup notification sound
    setupNotificationSound();
    
    // Setup auto-refresh with order checking
    setInterval(checkForNewOrders, 5000); // Check every 5 seconds
    setInterval(refreshData, 30000); // Refresh all data every 30 seconds
    
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

function showAlert(message, type = 'info') {
    // เปลี่ยนจาก alert เป็น modal
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
        <div class="modal fade" id="notificationModal" tabindex="-1" aria-labelledby="notificationModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header ${headerClass}">
                        <h5 class="modal-title" id="notificationModalLabel">
                            <i class="${iconClass.split(' ')[0]} ${iconClass.split(' ')[1]} me-2"></i>${title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-3">
                            <i class="${iconClass}" style="font-size: 3rem;"></i>
                        </div>
                        <h4>${message}</h4>
                        <p class="text-muted">หน้าต่างนี้จะปิดอัตโนมัติใน <span id="notificationCountdown">3</span> วินาที</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่า (ถ้ามี)
    const existingModal = document.getElementById('notificationModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal เข้าไปใน body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('notificationModal'));
    modal.show();
    
    // นับถอยหลัง 3 วินาที
    let countdown = 3;
    const countdownElement = document.getElementById('notificationCountdown');
    
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
                const modalElement = document.getElementById('notificationModal');
                if (modalElement) {
                    modalElement.remove();
                }
            }, 300);
        }
    }, 1000);
}

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
            
            // ลบ modal ออกจาก DOM หลังจากปิด
            setTimeout(() => {
                const modalElement = document.getElementById('successModal');
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

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('th-TH', {
        timeZone: 'Asia/Bangkok',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    }).replace(/-/g, '/');
}

// Navigation
function showSection(sectionName) {
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
    
    event.target.classList.add('active');
    currentSection = sectionName;
    
    // Load section-specific data
    switch(sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'tables':
            refreshTables();
            break;
        case 'menu':
            refreshMenu();
            break;
        case 'orders':
            refreshOrders();
            break;
        case 'settings':
            loadSettings();
            break;
    }
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
    container.innerHTML = '';
    
    tables.forEach(table => {
        const col = document.createElement('div');
        col.className = 'col-md-3 col-sm-4 col-6';
        
        const statusClass = getTableStatusClass(table.status);
        const statusText = getTableStatusText(table.status);
        
        col.innerHTML = `
            <div class="table-card ${statusClass}">
                <div onclick="showTableDetail(${table.table_id})" style="cursor: pointer;">
                    <div class="table-number">โต๊ะ ${table.table_id}</div>
                    <div class="table-status">${statusText}</div>
                    ${table.session_id ? `<div class="table-info">Session: ${table.session_id.substring(0, 8)}...</div>` : ''}
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
                        ${table.session_id ? 
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
                                <th class="text-center">จำนวน</th>
                                <th class="text-end">ราคา</th>
                                <th class="text-end">รวม</th>
                                <th>หมายเหตุ</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            tableData.orders.forEach(order => {
                const statusClass = order.status === 'completed' ? 'completed-order' : '';
                const statusBadge = order.status === 'completed' ? 
                    '<span class="completed-badge">เสร็จสิ้น</span>' : 
                    '<span class="active-badge">กำลังทำ</span>';
                
                // Parse customer_request to move special options from notes to under menu name
                let menuDisplay = order.menu_name;
                let notesDisplay = '-';
                
                if (order.customer_request) {
                    if (order.customer_request.includes(' | ')) {
                        const parts = order.customer_request.split(' | ');
                        // Don't show special options under menu name anymore
                        // Keep notes (second part) in notes column - but move it to under menu name
                        if (parts[1] && parts[1].trim()) {
                            menuDisplay = `${order.menu_name}<br><small class="text-warning">- ${parts[1].trim()}</small>`;
                        }
                        // Keep notes column empty for admin to edit later
                        notesDisplay = '-';
                    } else {
                        // If no separator, don't show anything below menu name
                        menuDisplay = order.menu_name;
                        notesDisplay = '-';
                    }
                }
                
                contentHtml += `
                    <tr class="${statusClass}">
                        <td>${menuDisplay} ${statusBadge}</td>
                        <td class="text-center">${order.quantity}</td>
                        <td class="text-end">฿${(order.price !== undefined && order.price !== null) ? order.price.toFixed(2) : '0.00'}</td>
                        <td class="text-end">฿${(order.total !== undefined && order.total !== null) ? order.total.toFixed(2) : '0.00'}</td>
                        <td class="text-muted small">${notesDisplay}</td>
                    </tr>
                `;
            });
            
            contentHtml += `
                        </tbody>
                        <tfoot>
                            <tr class="table-active">
                                <th colspan="3" class="text-end">ยอดรวมทั้งหมด:</th>
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
        document.getElementById('table-details-content').innerHTML = contentHtml;
        
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
        
        // ปุ่มเช็คบิล - แสดงเมื่อโต๊ะมีสถานะ occupied และมีรายการสั่งอาหาร
        if (tableData.status === 'occupied' && tableData.orders && tableData.orders.length > 0) {
            actionButtons += `
                <button type="button" class="btn btn-warning me-2" onclick="checkoutTable(${tableId})">
                    <i class="fas fa-receipt me-1"></i>เช็คบิล
                </button>
            `;
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
        
        document.getElementById('table-action-buttons').innerHTML = actionButtons;
        
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

// ==================== ORDER HISTORY MANAGEMENT ====================

// แสดง Modal ประวัติการสั่งอาหาร
function showOrderHistory() {
    // โหลดรายการโต๊ะใน dropdown
    loadTablesForHistory();
    
    // โหลดตัวเลือกเดือน
    loadMonthlyOptions();
    
    // ตั้งค่าวันที่เริ่มต้น (7 วันที่แล้ว)
    const today = new Date();
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    document.getElementById('historyStartDate').value = lastWeek.toISOString().split('T')[0];
    document.getElementById('historyEndDate').value = today.toISOString().split('T')[0];
    
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
    
    // ล้างการเลือกเดือน
    document.getElementById('monthlyFilter').value = '';
    
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
    
    // ลบ active class จากปุ่มตัวกรองด่วน
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    if (monthValue) {
        const [year, month] = monthValue.split('-');
        const startDate = new Date(year, month - 1, 1);
        const endDate = new Date(year, month, 0); // วันสุดท้ายของเดือน
        
        document.getElementById('historyStartDate').value = startDate.toISOString().split('T')[0];
        document.getElementById('historyEndDate').value = endDate.toISOString().split('T')[0];
        
        // โหลดข้อมูลสรุปยอดขายสำหรับเดือนที่เลือก
        if (typeof selectSummaryDateRange === 'function') {
            selectSummaryDateRange('month');
        }
    } else {
        // ถ้าไม่เลือกเดือน ให้ล้างวันที่
        document.getElementById('historyStartDate').value = '';
        document.getElementById('historyEndDate').value = '';
        
        // โหลดข้อมูลสรุปยอดขายทั้งหมด
        if (typeof selectSummaryDateRange === 'function') {
            selectSummaryDateRange('today');
        }
    }
    
    // โหลดข้อมูลใหม่
    loadOrderHistory();
}

// โหลดรายการโต๊ะสำหรับ dropdown
async function loadTablesForHistory() {
    try {
        const response = await fetch('/api/tables');
        const data = await response.json();
        
        const select = document.getElementById('historyTableSelect');
        select.innerHTML = '<option value="">-- ทุกโต๊ะ --</option>';
        
        if (data.success && data.data) {
            data.data.forEach(table => {
                select.innerHTML += `<option value="${table.table_id}">โต๊ะ ${table.table_id} - ${table.name}</option>`;
            });
        }
    } catch (error) {
        console.error('Error loading tables for history:', error);
    }
}

// โหลดประวัติการสั่งอาหาร
async function loadOrderHistory() {
    try {
        showLoading(true);
        
        const tableId = document.getElementById('historyTableSelect').value;
        const startDate = document.getElementById('historyStartDate').value;
        const endDate = document.getElementById('historyEndDate').value;
        
        let url = '/api/order-history?';
        const params = [];
        
        if (tableId) params.push(`table_id=${tableId}`);
        if (startDate) params.push(`start_date=${startDate}`);
        if (endDate) params.push(`end_date=${endDate}`);
        
        url += params.join('&');
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            console.log('Order history data:', data.data);
            renderOrderHistoryList(data.data || []);
        } else {
            throw new Error(data.error || 'ไม่สามารถโหลดประวัติได้');
        }
    } catch (error) {
        console.error('Error loading order history:', error);
        document.getElementById('order-history-content').innerHTML = `
            <div class="card border-danger">
                <div class="card-body p-2">
                    <small class="text-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        เกิดข้อผิดพลาด: ${error.message}
                    </small>
                </div>
            </div>
        `;
    } finally {
        showLoading(false);
    }
}

// แสดงรายการประวัติการสั่งอาหาร
function renderOrderHistoryList(orders) {
    const container = document.getElementById('order-history-content');
    
    if (!orders || orders.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-history fa-3x mb-3"></i>
                <p>ไม่พบประวัติการสั่งอาหารในช่วงเวลาที่เลือก</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    orders.forEach(order => {
        const orderDate = new Date(order.created_at).toLocaleString('th-TH', {
                    timeZone: 'Asia/Bangkok',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }).replace(/-/g, '/');
                const completedDate = order.completed_at ? new Date(order.completed_at).toLocaleString('th-TH', {
                    timeZone: 'Asia/Bangkok',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }).replace(/-/g, '/') : '-';
        
        html += `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-0">
                            <i class="fas fa-receipt me-2"></i>
                            ออเดอร์ #${order.order_id} - ${order.table_name || `โต๊ะ ${order.table_id}`}
                        </h6>
                        <small class="text-muted">
                            สั่งเมื่อ: ${orderDate} | 
                            เสร็จเมื่อ: ${completedDate} | 
                            สถานะ: <span class="badge bg-${getStatusColor(order.status)}">${getStatusText(order.status)}</span> |
                            บิล: <span class="badge bg-${getBillStatusColor(order.bill_status || 'unchecked')}">${getBillStatusText(order.bill_status || 'unchecked')}</span>
                        </small>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-outline-primary btn-sm" onclick="showOrderHistoryDetails(${order.order_id})">
                            <i class="fas fa-eye me-1"></i>รายละเอียด
                        </button>
                        <button class="btn btn-outline-success btn-sm" onclick="console.log('Print button clicked for order:', ${order.order_id}); reprintReceipt(${order.order_id});" style="font-weight: bold;">
                            <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                        </button>
                        <button class="btn btn-outline-${(order.bill_status === 'checked') ? 'warning' : 'info'} btn-sm" onclick="toggleBillStatus(${order.order_id}, '${order.bill_status || 'unchecked'}')">
                            <i class="fas fa-${(order.bill_status === 'checked') ? 'times' : 'check'} me-1"></i>${(order.bill_status === 'checked') ? 'ยกเลิกเช็ค' : 'เช็คบิล'}
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="confirmDeleteOrderHistory(${order.order_id})">
                            <i class="fas fa-trash me-1"></i>ลบ
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>เมนู</th>
                                    <th class="text-center">จำนวน</th>
                                    <th class="text-end">ราคา</th>
                                    <th class="text-end">รวม</th>
                                    <th>หมายเหตุ</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        if (order.items && order.items.length > 0) {
            order.items.forEach(item => {
                const statusClass = order.status === 'completed' ? 'completed-order' : '';
                const statusBadge = order.status === 'completed' ? 
                    '<span class="completed-badge">เสร็จสิ้น</span>' : 
                    '<span class="active-badge">กำลังทำ</span>';
                
                let menuDisplay = item.name;
                let notesDisplay = '-';
                
                if (item.customer_request) {
                    if (item.customer_request.includes(' | ')) {
                        const parts = item.customer_request.split(' | ');
                        if (parts[1] && parts[1].trim()) {
                            menuDisplay = `${item.name}<br><small class="text-warning">- ${parts[1].trim()}</small>`;
                        }
                        notesDisplay = '-';
                    } else {
                        menuDisplay = item.name;
                        notesDisplay = '-';
                    }
                }
                
                html += `
                    <tr class="${statusClass}">
                        <td>${menuDisplay} ${statusBadge}</td>
                        <td class="text-center">${item.quantity}</td>
                        <td class="text-end">฿${(item.price !== undefined && item.price !== null) ? item.price.toFixed(2) : '0.00'}</td>
                        <td class="text-end">฿${(item.total_price ? item.total_price : (item.price * item.quantity)).toFixed(2)}</td>
                        <td class="text-muted small">${notesDisplay}</td>
                    </tr>
                `;
            });
        }
        
        html += `
                            </tbody>
                            <tfoot>
                                <tr class="table-active">
                                    <th colspan="3" class="text-end">ยอดรวมทั้งหมด:</th>
                                    <th class="text-end">฿${order.total_amount ? order.total_amount.toFixed(2) : '0.00'}</th>
                                    <th></th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>

                    
                    <!-- Custom Div Section for each bill -->
                    <div class="custom-bill-section mt-3" style="background-color: #e8f4fd; border: 3px solid #007bff; border-radius: 10px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        <div class="card border-info mb-3" style="border-left: 5px solid #007bff;">
                            <div class="card-body p-2">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <i class="fas fa-info-circle me-2 text-primary"></i>
                                        <strong class="text-primary">ข้อมูลเพิ่มเติมสำหรับบิล #${order.order_id}</strong>
                                        <p class="mb-0 mt-2 text-muted">ส่วนนี้สามารถใช้สำหรับแสดงข้อมูลเพิ่มเติมหรือฟีเจอร์พิเศษสำหรับแต่ละบิล</p>
                                    </div>
                                <div>
                                    <button class="btn btn-success btn-lg" onclick="console.log('Print button clicked for order:', ${order.order_id}); reprintReceipt(${order.order_id});" style="font-weight: bold; box-shadow: 0 4px 8px rgba(0,0,0,0.3); background: linear-gradient(45deg, #28a745, #20c997); border: none; padding: 12px 24px;">
                                        <i class="fas fa-print me-2"></i>พิมพ์ใบเสร็จ
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="text-center">
                            <small class="text-muted">🖨️ คลิกปุ่มด้านบนเพื่อพิมพ์ใบเสร็จสำหรับออเดอร์นี้</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// แสดงรายละเอียดออเดอร์
async function showOrderHistoryDetails(orderId) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/orders/${orderId}`);
        const data = await response.json();
        
        if (data.success && data.data) {
            const order = data.data;
            
            const modalHtml = `
                <div class="modal fade" id="orderDetailsModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-receipt me-2"></i>
                                    รายละเอียดออเดอร์ #${order.order_id}
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <strong>โต๊ะ:</strong> ${order.table_name || `โต๊ะ ${order.table_id}`}<br>
                                        <strong>วันที่สั่ง:</strong> ${new Date(order.created_at).toLocaleString('th-TH', {
                            timeZone: 'Asia/Bangkok',
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        }).replace(/-/g, '/')}<br>
                                        <strong>สถานะ:</strong> <span class="badge bg-${getStatusColor(order.status)}">${getStatusText(order.status)}</span>
                                    </div>
                                    <div class="col-md-6">
                                        <strong>Session ID:</strong> ${order.session_id || '-'}<br>
                                        <strong>เสร็จเมื่อ:</strong> ${order.completed_at ? new Date(order.completed_at).toLocaleString('th-TH', {
                            timeZone: 'Asia/Bangkok',
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        }).replace(/-/g, '/') : '-'}<br>
                                        <strong>ยอดรวม:</strong> <span class="text-primary fw-bold">${order.total_amount ? order.total_amount.toLocaleString() : '0'} บาท</span>
                                    </div>
                                </div>
                                <hr>
                                <h6>รายการอาหาร:</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>รายการ</th>
                                                <th>จำนวน</th>
                                                <th>ราคา/หน่วย</th>
                                                <th>รวม</th>
                                                <th>สถานะ</th>
                                                <th>หมายเหตุ</th>
                                            </tr>
                                        </thead>
                                        <tbody>
            `;
            
            if (order.items && order.items.length > 0) {
                order.items.forEach(item => {
                    modalHtml += `
                        <tr>
                            <td>${item.name}</td>
                            <td>${item.quantity}</td>
                            <td>${item.price ? item.price.toLocaleString() : '0'} บาท</td>
                            <td>${item.total_price ? item.total_price.toLocaleString() : (item.price * item.quantity).toLocaleString()} บาท</td>
                            <td>${getItemStatusBadge(item.status)}</td>
                            <td>${item.customer_request || '-'}</td>
                        </tr>
                    `;
                });
            }
            
            modalHtml += `
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ปิด</button>
                                <button type="button" class="btn btn-success" onclick="reprintReceipt(${order.order_id}); bootstrap.Modal.getInstance(document.getElementById('orderDetailsModal')).hide();">
                                    <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // ลบ Modal เก่า (ถ้ามี)
            const existingModal = document.getElementById('orderDetailsModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // เพิ่ม Modal ใหม่
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // แสดง Modal
            const modal = new bootstrap.Modal(document.getElementById('orderDetailsModal'));
            modal.show();
            
            // ลบ Modal เมื่อปิด
            document.getElementById('orderDetailsModal').addEventListener('hidden.bs.modal', function() {
                this.remove();
            });
            
        } else {
            throw new Error(data.error || 'ไม่พบข้อมูลออเดอร์');
        }
    } catch (error) {
        console.error('Error showing order details:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// พิมพ์ใบเสร็จย้อนหลัง - ตอนนี้เรียกใช้ printReceipt แบบใหม่
async function reprintReceipt(orderId) {
    return await printReceipt(orderId, true);
}



// ยืนยันการลบประวัติออเดอร์
function confirmDeleteOrderHistory(orderId) {
    const modalHtml = `
        <div class="modal fade" id="deleteOrderModal" tabindex="-1">
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
                                    คุณแน่ใจหรือไม่ที่จะลบประวัติออเดอร์ #${orderId}?
                                </small>
                            </div>
                        </div>
                        <p class="text-danger">
                            <strong>คำเตือน:</strong> การลบประวัติออเดอร์จะไม่สามารถกู้คืนได้ และจะส่งผลต่อรายงานและสถิติของระบบ
                        </p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="button" class="btn btn-danger" onclick="deleteOrderHistory(${orderId}); bootstrap.Modal.getInstance(document.getElementById('deleteOrderModal')).hide();">
                            <i class="fas fa-trash me-1"></i>ลบออเดอร์
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ Modal เก่า (ถ้ามี)
    const existingModal = document.getElementById('deleteOrderModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม Modal ใหม่
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง Modal
    const modal = new bootstrap.Modal(document.getElementById('deleteOrderModal'));
    modal.show();
    
    // ลบ Modal เมื่อปิด
    document.getElementById('deleteOrderModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// ลบประวัติออเดอร์
async function deleteOrderHistory(orderId) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/orders/${orderId}`, {
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
        console.error('Error deleting order history:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// ส่งออกข้อมูลประวัติ
async function exportOrderHistory() {
    try {
        showLoading(true);
        
        const tableId = document.getElementById('historyTableSelect').value;
        const startDate = document.getElementById('historyStartDate').value;
        const endDate = document.getElementById('historyEndDate').value;
        
        let url = '/api/order-history/export?';
        const params = [];
        
        if (tableId) params.push(`table_id=${tableId}`);
        if (startDate) params.push(`start_date=${startDate}`);
        if (endDate) params.push(`end_date=${endDate}`);
        
        url += params.join('&');
        
        // สร้างลิงก์ดาวน์โหลด
        const link = document.createElement('a');
        link.href = url;
        link.download = `order_history_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showAlert('เริ่มดาวน์โหลดไฟล์ประวัติการสั่งอาหาร', 'success');
        
    } catch (error) {
        console.error('Error exporting order history:', error);
        showAlert('เกิดข้อผิดพลาดในการส่งออกข้อมูล', 'danger');
    } finally {
        showLoading(false);
    }
}

// Helper functions
function getStatusColor(status) {
    switch (status) {
        case 'pending': return 'warning';
        case 'accepted': return 'info';
        case 'active': return 'primary';
        case 'completed': return 'success';
        case 'cancelled': return 'danger';
        case 'rejected': return 'danger';
        default: return 'secondary';
    }
}

function getStatusText(status) {
    switch (status) {
        case 'pending': return 'รอดำเนินการ';
        case 'accepted': return 'รับแล้ว';
        case 'active': return 'กำลังดำเนินการ';
        case 'completed': return 'เสร็จสิ้น';
        case 'cancelled': return 'ยกเลิก';
        case 'rejected': return 'ปฏิเสธ';
        default: return status;
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
                        const price = parseFloat(order.total || order.total_price || order.price || 0);
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
async function printReceipt(identifier, isReprint = false) {
    // รองรับทั้งการพิมพ์ใบเสร็จครั้งแรก (identifier = tableId) และการพิมพ์ซ้ำ (identifier = orderId)
    let tableId = identifier;
    
    if (isReprint) {
        // กรณีพิมพ์ซ้ำ: identifier คือ orderId
        try {
            showLoading(true);
            
            // ดึงข้อมูลใบเสร็จจาก API
            const response = await fetch(`/api/orders/${identifier}`);
            const data = await response.json();
            
            if (data.success && data.data.table_id) {
                // ตั้งค่า receiptData ให้เหมือนกับที่ checkoutTable ทำ
                window.receiptData = {
                    tableId: data.data.table_id,
                    table_id: data.data.table_id,
                    orders: data.data.items || [],
                    totalAmount: data.data.total_amount || 0,
                    total_amount: data.data.total_amount || 0,
                    // ไม่ตั้งค่า arrivalTime และ checkoutTime ให้ระบบจัดรูปแบบเองในส่วนการสร้างใบเสร็จ
                    session_created_at: data.data.created_at,
                    checkout_at: data.data.completed_at || new Date().toISOString()
                };
                
                tableId = data.data.table_id;
                
                // เรียกใช้ฟังก์ชัน printReceipt อีกครั้งแบบไม่ใช่การพิมพ์ซ้ำ
                return await printReceipt(tableId, false);
                
            } else {
                throw new Error(data.error || 'ไม่สามารถดึงข้อมูลใบเสร็จได้');
            }
        } catch (error) {
            console.error('Error reprinting receipt:', error);
            showAlert(error.message, 'danger');
            return;
        } finally {
            showLoading(false);
        }
    }
    try {
        console.log('Printing receipt for table:', tableId);
        console.log('Current receipt data:', window.receiptData);
        showLoading(true);
        
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
                const checkoutResponse = await fetch(`/api/tables/${tableId}/checkout`, {
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
                    window.receiptData = checkoutData.data;
                    console.log('Created receipt data from checkout API:', window.receiptData);
                    return await printReceipt(tableId); // เรียกฟังก์ชันตัวเองอีกครั้งหลังจากได้ข้อมูลแล้ว
                }
            } catch (checkoutError) {
                console.error('Error fetching from checkout API:', checkoutError);
                // ถ้าไม่สำเร็จ ให้ลองดึงข้อมูลจาก orders API แทน
            }
            
            // ดึงข้อมูลโต๊ะและออเดอร์
            const response = await fetch(`/api/tables/${tableId}/orders?session_id=${session_id}`);
            const data = await response.json();
            console.log('Orders API response:', data);
            
            if (!data.success) {
                throw new Error('ไม่สามารถดึงข้อมูลใบเสร็จได้');
            }
            
            if (!data.data.orders || data.data.orders.length === 0) {
                throw new Error('ไม่พบรายการอาหารสำหรับโต๊ะนี้');
            }
            
            window.receiptData = {
                table_id: tableId,
                session_id: session_id,
                orders: data.data.orders,
                total_amount: data.data.total_amount,
                created_at: data.data.created_at,
                session_created_at: data.data.session_created_at,
                checkout_at: data.data.checkout_at
            };
            console.log('Created receipt data from orders API:', window.receiptData);
            console.log('API data.data:', data.data);
            console.log('session_created_at from API:', data.data.session_created_at);
            console.log('checkout_at from API:', data.data.checkout_at);
        }
        
        // สร้างหน้าต่างใหม่สำหรับพิมพ์ใบเสร็จ
        const printWindow = window.open('', '_blank');
        
        if (!printWindow) {
            throw new Error('ไม่สามารถเปิดหน้าต่างพิมพ์ได้ โปรดอนุญาตให้เว็บไซต์เปิดหน้าต่างใหม่');
        }
        
        // ตรวจสอบและปรับรูปแบบข้อมูลใบเสร็จให้ถูกต้อง
        const receiptData = window.receiptData;
        console.log('🔥🔥🔥 NEW VERSION LOADED - Using receipt data for printing:', receiptData);
        console.log('About to start TIME DEBUG INFO...');
        
        // Debug: ตรวจสอบข้อมูลเวลาก่อนสร้าง HTML
        console.log('=== TIME DEBUG INFO ===');
        console.log('Starting time debug checks...');
        console.log('receiptData.arrivalTime:', receiptData.arrivalTime);
        console.log('receiptData.checkoutTime:', receiptData.checkoutTime);
        console.log('receiptData.session_created_at:', receiptData.session_created_at);
        console.log('receiptData.checkout_at:', receiptData.checkout_at);
        console.log('hasArrivalTime:', !!receiptData.arrivalTime);
        console.log('hasCheckoutTime:', !!receiptData.checkoutTime);
        console.log('========================');
        
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
        
        // สร้างข้อมูลเวลาที่จัดรูปแบบแล้วสำหรับแสดงในใบเสร็จ
        if (!receiptData.arrivalTime && receiptData.session_created_at) {
            try {
                const arrivalDate = new Date(receiptData.session_created_at);
                receiptData.arrivalTime = arrivalDate.toLocaleString('th-TH', {
                    timeZone: 'Asia/Bangkok',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }).replace(/-/g, '/');
            } catch (error) {
                console.warn('Error formatting arrival time:', error);
            }
        }
        
        if (!receiptData.checkoutTime && receiptData.checkout_at) {
            try {
                const checkoutDate = new Date(receiptData.checkout_at);
                receiptData.checkoutTime = checkoutDate.toLocaleString('th-TH', {
                    timeZone: 'Asia/Bangkok',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }).replace(/-/g, '/');
            } catch (error) {
                console.warn('Error formatting checkout time:', error);
            }
        }
        
        console.log('Receipt data after time formatting:', {
            arrivalTime: receiptData.arrivalTime,
            checkoutTime: receiptData.checkoutTime,
            session_created_at: receiptData.session_created_at,
            checkout_at: receiptData.checkout_at
        });
        
        // Debug: ตรวจสอบข้อมูลก่อนส่งไปยัง template
        console.log('Final receiptData before template:', {
            arrivalTime: receiptData.arrivalTime,
            checkoutTime: receiptData.checkoutTime,
            hasArrivalTime: !!receiptData.arrivalTime,
            hasCheckoutTime: !!receiptData.checkoutTime
        });
        
        // Debug: ตรวจสอบข้อมูลดิบที่ได้รับจาก API
        console.log('Raw receiptData from API:', receiptData);
        console.log('receiptData.session_created_at type:', typeof receiptData.session_created_at);
        console.log('receiptData.checkout_at type:', typeof receiptData.checkout_at);
        
        // ดึงข้อมูลร้านจาก localStorage
        const restaurantName = localStorage.getItem('restaurant_name') || 'ร้านอาหาร A-FOOD';
        const restaurantAddress = localStorage.getItem('restaurant_address') || 'สงขลา หาดใหญ่';
        const restaurantPhone = localStorage.getItem('restaurant_phone') || '02-xxx-xxxx';
        const restaurantTel = `โทร. ${restaurantPhone}`;
        
        // ตรวจสอบและกำหนดวันที่ใบเสร็จ (ใช้เวลาสร้างโต๊ะแทนเวลาพิมพ์)
        let receiptDate;
        try {
            // ใช้ arrivalTime ที่ได้จากการจัดรูปแบบแล้ว หรือ fallback ไปยังข้อมูลดิบ
            if (receiptData.arrivalTime) {
                receiptDate = receiptData.arrivalTime.split(' ')[0]; // เอาเฉพาะส่วนวันที่
            } else {
                receiptDate = new Date(receiptData.session_created_at || receiptData.created_at || new Date()).toLocaleDateString('th-TH', { timeZone: 'Asia/Bangkok' });
            }
        } catch (error) {
            console.warn('Error formatting receipt date:', error);
            receiptDate = new Date().toLocaleDateString('th-TH', { timeZone: 'Asia/Bangkok' }); // ใช้วันที่ปัจจุบันถ้าแปลงวันที่ไม่สำเร็จ
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
                    }
                    .receipt-info > div {
                        font-size: 24px !important;
                    }
                    .receipt-info .tiny-text {
                        font-size: 20px !important;
                    }
                    .receipt-info > div:first-child {
                        font-size: 14px;
                        font-weight: bold;
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
                            -webkit-print-color-adjust: exact;
                            print-color-adjust: exact;
                        }
                        .receipt {
                            width: 100%;
                            border: none;
                            transform: scale(1.5);
                            transform-origin: top center;
                        }
                        .receipt-info > div {
                            font-size: 24px !important;
                        }
                        .receipt-info .tiny-text {
                            font-size: 20px !important;
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
    <div>ใบเสร็จรับเงิน</div>
    <div class="tiny-text">โต๊ะ: ${receiptData.tableId || receiptData.table_id}</div>
    <div class="tiny-text">วันที่: ${receiptDate}</div>
    ${(() => {
        console.log('🔥 TIME DISPLAY DEBUG - arrivalTime:', receiptData.arrivalTime);
        console.log('🔥 TIME DISPLAY DEBUG - checkoutTime:', receiptData.checkoutTime);
        let timeInfo = [];
        if (receiptData.arrivalTime) {
            timeInfo.push(`เวลาที่มาถึง: ${receiptData.arrivalTime}`);
            console.log('🔥 Added arrival time to receipt');
        }
        if (receiptData.checkoutTime) {
            timeInfo.push(`เวลาเช็คบิล: ${receiptData.checkoutTime}`);
            console.log('🔥 Added checkout time to receipt');
        }
        console.log('🔥 Final timeInfo array:', timeInfo);
        const result = timeInfo.length > 0 ? timeInfo.map(t => `<div class="tiny-text">${t}</div>`).join('') : '';
        console.log('🔥 Final time HTML result:', result);
        return result;
    })()}
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
                
                // ดึงตัวเลือกพิเศษจาก customer_request
                let specialOptions = '';
                if (order.customer_request) {
                    if (order.customer_request.includes(' | ')) {
                        const parts = order.customer_request.split(' | ');
                        if (parts.length >= 3) {
                            specialOptions = parts[2] || ''; // ตัวเลือกพิเศษอยู่ในส่วนที่ 3
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
                
                // เพิ่มจำนวนและยอดรวม
                groupedOrders[orderKey].quantity += quantity;
                groupedOrders[orderKey].total += parseFloat(total);
            });
            
            // แสดงรายการที่รวมแล้ว
            Object.values(groupedOrders).forEach(item => {
                const unitPrice = item.status === 'rejected' ? 0 : (item.price || (item.total / item.quantity));
                const statusText = item.status === 'rejected' ? '(ยกเลิก)' : '';
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
                        
                        if (totalAmount > 0) {
                            return `
                            <div class="qr-code">
                                <div>สแกนเพื่อชำระเงิน</div>
                                <div id="promptpay-qr-container"></div>
                                <script>
                                    // สร้าง PromptPay QR Code ที่ถูกต้อง
                                    const qrContainer = document.getElementById('promptpay-qr-container');
                                    
                                    // เรียก API เพื่อสร้าง PromptPay QR Code (ใช้การตั้งค่าจาก database)
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
                                            qrImg.src = data.qr_code;
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
        
        const response = await fetch(`/api/tables/${tableId}/clear`, {
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
        
        const response = await fetch(`/api/tables/${selectedTableId}/clear`, {
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
        const response = await fetch('/api/menu/categories');
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
        // ใช้ API endpoint ใหม่ที่แสดงเมนูทั้งหมด รวมถึงรายการที่ไม่พร้อมจำหน่าย
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
    container.innerHTML = '';
    
    menuItems.forEach(item => {
        const category = menuCategories.find(cat => cat.category_id === item.category_id);
        
        const div = document.createElement('div');
        div.className = 'menu-item';
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
                    <span class="toggle-label">${item.is_available ? 'พร้อมให้บริการ' : 'ไม่พร้อมให้บริการ'}</span>
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
        
        container.appendChild(div);
    });
}

function updateCategorySelect() {
    const select = document.getElementById('menu-category');
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

function showAddMenuModal() {
    const modal = new bootstrap.Modal(document.getElementById('addMenuModal'));
    modal.show();
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
        
        const response = await fetch('/api/menu/categories', {
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
    const optionType = document.querySelector('input[name="option-type"]:checked').value;
    let foodOptionType = 'none'; // ค่า default
    
    if (optionType === 'spice') {
        foodOptionType = 'spice';
    } else if (optionType === 'sweet') {
        foodOptionType = 'sweet';
    } else if (optionType === 'none') {
        foodOptionType = 'none';
    }
    
    if (!name || !categoryId || !price) {
        showAlert('กรุณากรอกข้อมูลที่จำเป็น', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/menu/items', {
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
        const response = await fetch('/api/orders');
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
    
    orders.forEach(order => {
        const div = document.createElement('div');
        div.className = 'order-item';
        
        let itemsHTML = '';
        let total = 0;
        
        order.items.forEach(item => {
            const itemTotal = item.quantity * item.price;
            total += itemTotal;
            itemsHTML += `
                <div class="order-item-row">
                    <div class="order-item-name">
                        ${item.name}
                        ${item.customer_request ? `<span class="${getCustomerRequestClass(item.customer_request)} small"> (${item.customer_request})</span>` : ''}
                    </div>
                    <div class="order-item-qty">x${item.quantity}</div>
                    <div class="order-item-price">${formatCurrency(itemTotal)}</div>
                </div>
            `;
        });
        
        let statusBadge = '';
        let actionButtons = '';
        
        // กำหนด badge และปุ่มตามสถานะ
        statusBadge = getOrderStatusBadge(order.status);
        
        switch(order.status) {
            case 'pending':
                actionButtons = `
                    <div class="d-flex gap-2 mt-2">
                        <button class="btn btn-danger btn-sm" onclick="rejectOrder(${order.order_id})">
                            <i class="fas fa-times me-1"></i>ปฏิเสธ
                        </button>
                        <button class="btn btn-success btn-sm" onclick="acceptOrder(${order.order_id})">
                            <i class="fas fa-check me-1"></i>รับออเดอร์
                        </button>
                        <button class="btn btn-outline-primary btn-sm" onclick="showOrderDetails(${order.order_id})">
                            <i class="fas fa-eye me-1"></i>รายละเอียด
                        </button>
                        <button class="btn btn-info btn-sm" onclick="reprintReceipt(${order.order_id})">
                            <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                        </button>
                    </div>
                `;
                break;
            case 'accepted':
                statusBadge = '<span class="badge bg-primary">รับออเดอร์แล้ว</span>';
                actionButtons = `
                    <div class="d-flex gap-2 mt-2">
                        <button class="btn btn-outline-primary btn-sm" onclick="showOrderDetails(${order.order_id})">
                            <i class="fas fa-eye me-1"></i>จัดการรายการ
                        </button>
                        <button class="btn btn-success btn-sm" onclick="completeOrder(${order.order_id})">
                            <i class="fas fa-check-double me-1"></i>เสร็จสิ้น
                        </button>
                        <button class="btn btn-info btn-sm" onclick="reprintReceipt(${order.order_id})">
                            <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                        </button>
                    </div>
                `;
                break;
            case 'completed':
                statusBadge = '<span class="badge bg-success">เสร็จสิ้น</span>';
                actionButtons = `
                    <div class="d-flex gap-2 mt-2">
                        <button class="btn btn-outline-primary btn-sm" onclick="showOrderDetails(${order.order_id})">
                            <i class="fas fa-eye me-1"></i>รายละเอียด
                        </button>
                        <button class="btn btn-info btn-sm" onclick="reprintReceipt(${order.order_id})">
                            <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                        </button>
                    </div>
                `;
                break;
            case 'rejected':
                statusBadge = '<span class="badge bg-danger">ปฏิเสธแล้ว</span>';
                actionButtons = `
                    <div class="d-flex gap-2 mt-2">
                        <button class="btn btn-outline-primary btn-sm" onclick="showOrderDetails(${order.order_id})">
                            <i class="fas fa-eye me-1"></i>รายละเอียด
                        </button>
                        <button class="btn btn-info btn-sm" onclick="reprintReceipt(${order.order_id})">
                            <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                        </button>
                    </div>
                `;
                break;
            default:
                statusBadge = '<span class="badge bg-secondary">ไม่ทราบสถานะ</span>';
                actionButtons = `
                    <div class="d-flex gap-2 mt-2">
                        <button class="btn btn-danger btn-sm" onclick="rejectOrder(${order.order_id})">
                            <i class="fas fa-times me-1"></i>ปฏิเสธ
                        </button>
                        <button class="btn btn-success btn-sm" onclick="acceptOrder(${order.order_id})">
                            <i class="fas fa-check me-1"></i>รับออเดอร์
                        </button>
                        <button class="btn btn-outline-primary btn-sm" onclick="showOrderDetails(${order.order_id})">
                            <i class="fas fa-eye me-1"></i>รายละเอียด
                        </button>
                        <button class="btn btn-info btn-sm" onclick="reprintReceipt(${order.order_id})">
                            <i class="fas fa-print me-1"></i>พิมพ์ใบเสร็จ
                        </button>
                    </div>
                `;
        }
        
        div.innerHTML = `
            <div class="order-header">
                <div class="order-info">
                    <div class="order-table">${order.table_name || 'โต๊ะ ' + order.table_id}</div>
                    <div class="order-time">${formatDateTime(order.created_at)}</div>
                </div>
                <div class="order-total">${formatCurrency(total)}</div>
            </div>
            <div class="order-items">
                ${itemsHTML}
            </div>
            <div class="d-flex justify-content-between align-items-center">
                ${statusBadge}
            </div>
            ${actionButtons}
        `;
        
        container.appendChild(div);
    });
}

function filterOrders(status) {
    // Implementation for filtering orders
    console.log('Filter orders by status:', status);
}

function getCustomerRequestClass(customerRequest) {
    if (!customerRequest) return '';
    
    const request = customerRequest.toLowerCase();
    
    // หวานมาก เผ็ดมาก ให้ใช้สีแดง
    if (request.includes('หวานมาก') || request.includes('เผ็ดมาก')) {
        return 'text-danger';
    }
    
    // หวานน้อย เผ็ดน้อย ให้ใช้สีฟ้า
    if (request.includes('หวานน้อย') || request.includes('เผ็ดน้อย')) {
        return 'text-info';
    }
    
    // หวานปกติ เผ็ดปกติ ให้ใช้สีขาว
    return 'text-white';
}

function refreshOrders() {
    loadOrders();
}




// Order Management Functions
async function acceptOrder(orderId) {
    try {
        const response = await fetch(`/api/orders/${orderId}/accept`, {
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
        const response = await fetch(`/api/orders/${orderId}/reject`, {
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
        const response = await fetch(`/api/orders/${orderId}/complete`, {
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
        const response = await fetch(`/api/orders/${orderId}/items`);
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

function getOrderStatusBadge(status) {
    switch(status) {
        case 'pending':
            return '<span class="badge bg-warning">รอดำเนินการ</span>';
        case 'accepted':
            return '<span class="badge bg-success">รับแล้ว</span>';
        case 'completed':
            return '<span class="badge bg-primary">เสร็จสิ้น</span>';
        case 'rejected':
            return '<span class="badge bg-danger">ปฏิเสธ</span>';
        default:
            return '<span class="badge bg-warning">รอดำเนินการ</span>';
    }
}

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
        default:
            return '<span class="badge bg-warning">รอดำเนินการ</span>';
    }
}

function displayOrderDetailsModal(orderId, items) {
    let itemsHTML = '';
    
    items.forEach(item => {
        let statusBadge = getItemStatusBadge(item.status);
        let actionButtons = '';
        
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
                    <div class="fw-bold">${item.name}</div>
                    <div class="text-muted small">จำนวน: ${item.quantity} | ราคา: ${formatCurrency(item.unit_price * item.quantity)}</div>
                    ${item.customer_request ? `<div class="${getCustomerRequestClass(item.customer_request)} small">หมายเหตุ: ${item.customer_request}</div>` : ''}
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
        const response = await fetch(`/api/order-items/${orderItemId}/accept`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            // ปิด modal และรีเฟรช
            const modal = bootstrap.Modal.getInstance(document.getElementById('orderDetailsModal'));
            modal.hide();
            loadOrders();
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
        const response = await fetch(`/api/order-items/${orderItemId}/reject`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            // ปิด modal และรีเฟรช
            const modal = bootstrap.Modal.getInstance(document.getElementById('orderDetailsModal'));
            modal.hide();
            loadOrders();
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
        const response = await fetch('/api/orders');
        const data = await response.json();
        
        if (data.success) {
            const currentOrderCount = data.data.length;
            
            // Check if there are new orders
            if (lastOrderCount > 0 && currentOrderCount > lastOrderCount) {
                const newOrdersCount = currentOrderCount - lastOrderCount;
                
                // Show notification
                showOrderNotification(newOrdersCount);
                
                // Play sound if available
                if (notificationSound) {
                    notificationSound.play().catch(e => console.log('Could not play sound'));
                }
                
                // Update orders display if on orders section
                if (currentSection === 'orders') {
                    orders = data.data;
                    renderOrders();
                }
            }
            
            lastOrderCount = currentOrderCount;
        }
    } catch (error) {
        console.error('Error checking for new orders:', error);
    }
}

// Show order notification
function showOrderNotification(count) {
    const message = count === 1 ? 'มีออเดอร์ใหม่ 1 รายการ!' : `มีออเดอร์ใหม่ ${count} รายการ!`;
    
    // Show alert
    showAlert(message, 'success');
    
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
    try {
        // Load PromptPay settings from server
        const promptpayResponse = await fetch('/api/settings/promptpay');
        if (promptpayResponse.ok) {
            const promptpayData = await promptpayResponse.json();
            if (promptpayData.success) {
                document.getElementById('promptpay-type').value = promptpayData.type;
                document.getElementById('promptpay-value').value = promptpayData.value;
            }
        }
    } catch (error) {
        console.error('Error loading PromptPay settings:', error);
        // Fallback to localStorage
        const promptpayType = localStorage.getItem('promptpay_type') || 'phone';
        const promptpayValue = localStorage.getItem('promptpay_value') || '';
        document.getElementById('promptpay-type').value = promptpayType;
        document.getElementById('promptpay-value').value = promptpayValue;
    }
    
    // Load other settings from localStorage
    const domainUrl = localStorage.getItem('domain_url') || '';
    const sheetId = localStorage.getItem('sheet_id') || '';
    const sheetName = localStorage.getItem('sheet_name') || 'ยอดขาย';
    
    document.getElementById('domain-url').value = domainUrl;
    document.getElementById('sheet-id').value = sheetId;
    document.getElementById('sheet-name').value = sheetName;
}

function setupFormHandlers() {
    // PromptPay form
    document.getElementById('promptpay-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const type = document.getElementById('promptpay-type').value;
        const value = document.getElementById('promptpay-value').value.trim();
        
        if (!value) {
            showAlert('กรุณาระบุหมายเลข', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/settings/promptpay', {
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
                
                // แสดง modal บันทึกสำเร็จ
                showSuccessModal('บันทึกการตั้งค่า PromptPay สำเร็จ!');
            } else {
                throw new Error(data.error || 'ไม่สามารถบันทึกการตั้งค่าได้');
            }
        } catch (error) {
            console.error('Error saving PromptPay settings:', error);
            showAlert(error.message, 'danger');
        }
    });
    
    // Domain form
    document.getElementById('domain-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = document.getElementById('domain-url').value.trim();
        
        if (!url) {
            showAlert('กรุณาระบุ Domain URL', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/settings/domain', {
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
    
    // Google Sheets form
    document.getElementById('sheets-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const sheetId = document.getElementById('sheet-id').value.trim();
        const sheetName = document.getElementById('sheet-name').value.trim();
        const credentialsFile = document.getElementById('credentials-file').files[0];
        
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
            
            const response = await fetch('/api/settings/sheets', {
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

async function testGoogleSheets() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/settings/sheets/test', {
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
        
        const response = await fetch('/api/tools/generate-qr', {
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
        
        const response = await fetch('/api/tools/clear-all-tables', {
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
        
        const response = await fetch('/api/tools/export-data');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `pos_data_${new Date().toISOString().split('T')[0]}.json`;
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
        
        fetch(`/api/menu/categories/${categoryId}`, {
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
        fetch(`/api/menu/categories/${categoryId}`, {
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
        
        const response = await fetch(`/api/menu/categories/${categoryId}/move-up`, {
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
        
        const response = await fetch(`/api/menu/categories/${categoryId}/move-down`, {
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
                                                <input class="form-check-input" type="checkbox" name="edit-option-type" id="editOptionNone" value="none" ${currentOptionType === 'none' ? 'checked' : ''}>
                                                <label class="form-check-label" for="editOptionNone">ไม่ระบุ</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="edit-option-type" id="editOptionSpice" value="spice" ${currentOptionType === 'spice' ? 'checked' : ''}>
                                                <label class="form-check-label" for="editOptionSpice">ระดับความเผ็ด</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="edit-option-type" id="editOptionSweet" value="sweet" ${currentOptionType === 'sweet' ? 'checked' : ''}>
                                                <label class="form-check-label" for="editOptionSweet">ระดับความหวาน</label>
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
    
    fetch('/api/upload/menu-image', {
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

// ฟังก์ชันสำหรับเปลี่ยนสถานะ availability ของเมนู
async function toggleMenuAvailability(itemId, isAvailable) {
    try {
        const response = await fetch(`/api/menu/items/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                is_available: isAvailable
            })
        });
        
        const data = await response.json();
        
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
            }
            
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
    
    fetch(`/api/menu/items/${itemId}`, {
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
        fetch(`/api/menu/items/${itemId}`, {
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
        
        const response = await fetch(`/api/tables/${tableId}/qr/print`);
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
        
        const response = await fetch(`/api/tables/${tableId}/qr`);
        const data = await response.json();
        
        if (data.success) {
            // API /api/tables/${tableId}/qr จะอัปเดตสถานะโต๊ะเป็น occupied และกำหนด session_id ให้แล้ว
            // ไม่จำเป็นต้องเรียก API /api/tables/${tableId}/status อีก
            
            // รอให้ backend อัพเดทข้อมูลเสร็จก่อน
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // รีเฟรชข้อมูลโต๊ะ
            await loadTables();
            
            // แสดง Modal แจ้งเตือนความสำเร็จ
            showSuccessModal('สร้าง QR Code และเปิดเซสชั่นเรียบร้อย โต๊ะพร้อมรับลูกค้า');
            
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
        const response = await fetch(`/api/tables/${tableId}/clear`, {
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
        
        const response = await fetch(`/api/tables/${tableId}/qr`);
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

// ==================== BILL STATUS MANAGEMENT ====================

// ฟังก์ชันสำหรับกำหนดสีของสถานะบิล
function getBillStatusColor(status) {
    switch(status) {
        case 'checked': return 'success';
        case 'unchecked': return 'secondary';
        default: return 'secondary';
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
            showAlert(data.message, 'success');
            // รีเฟรชรายการประวัติออเดอร์
            loadOrderHistory();
        } else {
            throw new Error(data.error || 'ไม่สามารถอัปเดตสถานะบิลได้');
        }
        
    } catch (error) {
        console.error('Error updating bill status:', error);
        showAlert(error.message, 'danger');
    } finally {
        showLoading(false);
    }
}

// Dashboard Functions
let salesChart = null;
let categoryChart = null;

async function loadDashboard() {
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
    }
}

async function loadSalesSummary() {
    try {
        const response = await fetch('/api/sales-summary');
        const data = await response.json();
        
        if (data.success) {
            const summary = data.data;
            
            // Update summary cards (excluding today-sales and today-orders to prevent conflicts with dashboard-enhanced.js)
            // document.getElementById('today-sales').textContent = `฿${summary.today.total.toLocaleString()}`;
            document.getElementById('week-sales').textContent = `฿${summary.week.total.toLocaleString()}`;
            // document.getElementById('today-orders').textContent = summary.today.orders.toLocaleString();
            document.getElementById('total-sales').textContent = `฿${summary.total.total.toLocaleString()}`;
            
            // Update additional stats
            document.getElementById('total-sessions').textContent = summary.today.sessions.toLocaleString();
            document.getElementById('week-orders').textContent = summary.week.orders.toLocaleString();
            document.getElementById('month-orders').textContent = summary.month.orders.toLocaleString();
        }
    } catch (error) {
        console.error('Error loading sales summary:', error);
    }
}

async function loadSalesChart(days = 7) {
    try {
        const response = await fetch(`/api/sales-chart?days=${days}`);
        const data = await response.json();
        
        if (data.success) {
            updateSalesChart(data.data);
        }
    } catch (error) {
        console.error('Error loading sales chart:', error);
        // Create dummy data if API fails
        const dummyData = {
            labels: [],
            sales: []
        };
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dummyData.labels.push(date.toLocaleDateString('th-TH', { timeZone: 'Asia/Bangkok', month: 'short', day: 'numeric' }));
            dummyData.sales.push(Math.random() * 10000);
        }
        
        updateSalesChart(dummyData);
    }
}

function updateSalesChart(data = null) {
    const ctx = document.getElementById('salesChart').getContext('2d');
    
    if (salesChart) {
        salesChart.destroy();
    }
    
    // Default data if none provided
    if (!data) {
        const days = parseInt(document.getElementById('chart-period').value) || 7;
        data = {
            labels: [],
            sales: []
        };
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            data.labels.push(date.toLocaleDateString('th-TH', { timeZone: 'Asia/Bangkok', month: 'short', day: 'numeric' }));
            data.sales.push(Math.random() * 10000);
        }
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
            <div class="item-amount">฿${(item.sales || item.total || 0).toLocaleString()}</div>
        </div>
    `).join('');
}

async function loadCategoryChart() {
    try {
        const response = await fetch('/api/category-sales');
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
function updateSalesChart() {
    const days = parseInt(document.getElementById('chart-period').value);
    loadSalesChart(days);
}