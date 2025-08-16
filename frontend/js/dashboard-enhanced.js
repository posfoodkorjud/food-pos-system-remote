// Enhanced Dashboard JavaScript
let currentDate = new Date();
let selectedDateRange = 'today'; // Default to today
let dashboardSalesChart = null;
let dashboardCategoryChart = null;
let dashboardMonthlyTrendChart = null;
let salesData = {};
let isLoadingData = false; // ป้องกันการเรียก API ซ้ำซ้อน
let currentChartPeriod = 7; // เก็บสถานะของ chart period ที่เลือกไว้

// Initialize enhanced dashboard
function initializeEnhancedDashboard() {
    console.log('[DEBUG] initializeEnhancedDashboard: Starting...');
    setDefaultDates();
    
    // Setup Thai date format for existing date inputs
    setTimeout(() => {
        const startDate = document.getElementById('start-date');
        const endDate = document.getElementById('end-date');
        if (startDate && !startDate.parentNode.querySelector('.thai-date-display')) {
            setupThaiDateFormat(startDate);
        }
        if (endDate && !endDate.parentNode.querySelector('.thai-date-display')) {
            setupThaiDateFormat(endDate);
        }
    }, 100);
    
    generateCalendar();
    initializeCharts();
    
    // Set up event listener for chart period selector
    setTimeout(() => {
        const periodSelect = document.getElementById('chart-period');
        if (periodSelect) {
            console.log('[DEBUG] initializeEnhancedDashboard: Setting up period selector event listener');
            periodSelect.addEventListener('change', changeSalesChartPeriod);
            
            // Trigger initial load with saved period or default
            console.log('[DEBUG] initializeEnhancedDashboard: Triggering initial changeSalesChartPeriod');
            // ตั้งค่า chart period ให้ตรงกับค่าที่เก็บไว้
            periodSelect.value = currentChartPeriod;
            changeSalesChartPeriod();
        } else {
            console.log('[DEBUG] initializeEnhancedDashboard: Period selector not found, using fallback loadChartData');
            // โหลดข้อมูลกราฟหลังจากเริ่มต้นกราฟแล้ว
            console.log('[DEBUG] initializeEnhancedDashboard: Loading chart data...');
            loadChartData();
        }
    }, 500);
    
    // โหลดข้อมูลสรุปยอดขายเริ่มต้น
    console.log('[DEBUG] initializeEnhancedDashboard: Loading initial summary data...');
    setTimeout(() => {
        console.log('[DEBUG] initializeEnhancedDashboard: Calling selectSummaryDateRange("today")');
        selectSummaryDateRange('today');
    }, 1000);
    
    console.log('[DEBUG] initializeEnhancedDashboard: Completed with chart data loading scheduled');
}

// Set default dates
function setDefaultDates() {
    const today = new Date();
    const startDate = document.getElementById('start-date');
    const endDate = document.getElementById('end-date');
    
    if (startDate && endDate) {
        startDate.value = formatDateForInput(today);
        endDate.value = formatDateForInput(today);
    }
}

// Setup Thai date format for input fields
function setupThaiDateFormat(inputElement) {
    if (!inputElement) return;
    
    // Check if already setup
    if (inputElement.parentNode.querySelector('.thai-date-display')) {
        return;
    }
    
    // Create a display element to show Thai format
    const displayElement = document.createElement('div');
    displayElement.className = 'thai-date-display';
    displayElement.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: #ffffff;
        border: 1px solid #ddd;
        border-radius: 0.25rem;
        padding: 0.25rem 1.75rem 0.25rem 0.5rem;
        font-size: 0.8rem;
        line-height: 1.3;
        color: #495057;
        cursor: pointer;
        display: flex;
        align-items: center;
        z-index: 3;
        pointer-events: auto;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease;
        font-weight: 400;
        min-height: 32px;
        max-height: 32px;
        overflow: hidden;
    `;
    
    // Wrap the input in a container
    const container = document.createElement('div');
    container.style.cssText = `
        position: relative;
        display: inline-block;
        width: 100%;
        margin: 0;
        height: 32px;
    `;
    inputElement.parentNode.insertBefore(container, inputElement);
    container.appendChild(inputElement);
    container.appendChild(displayElement);
    
    // Add a subtle icon to the right side
    const iconElement = document.createElement('div');
    iconElement.innerHTML = '📅';
    iconElement.style.cssText = `
        position: absolute;
        right: 0.375rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 0.75rem;
        color: #6c757d;
        pointer-events: none;
        z-index: 4;
        opacity: 0.6;
    `;
    container.appendChild(iconElement);
    
    // Style the original input
    inputElement.style.opacity = '0';
    inputElement.style.position = 'absolute';
    inputElement.style.top = '0';
    inputElement.style.left = '0';
    inputElement.style.width = '100%';
    inputElement.style.height = '100%';
    inputElement.style.zIndex = '1';
    inputElement.style.cursor = 'pointer';
    inputElement.style.pointerEvents = 'auto';
    
    // Update display when value changes
    function updateDisplay() {
        if (inputElement.value) {
            displayElement.textContent = formatDateForDisplay(inputElement.value);
            displayElement.style.color = '#495057';
            displayElement.style.fontWeight = '400';
        } else {
            displayElement.textContent = 'เลือกวันที่';
            displayElement.style.color = '#6c757d';
            displayElement.style.fontWeight = '400';
        }
    }
    
    // Initial display update
    updateDisplay();
    
    // Listen for changes
    inputElement.addEventListener('change', () => {
        updateDisplay();
        displayElement.style.color = '#495057';
    });
    inputElement.addEventListener('input', updateDisplay);
    
    // Function to open date picker
    function openDatePicker() {
        inputElement.focus();
        try {
            if (inputElement.showPicker) {
                inputElement.showPicker();
            } else {
                // Fallback for browsers that don't support showPicker
                inputElement.click();
            }
        } catch (error) {
            // Fallback if showPicker fails
            inputElement.click();
        }
    }
    
    // Add hover effects
    displayElement.addEventListener('mouseenter', () => {
        displayElement.style.borderColor = '#007bff';
        displayElement.style.boxShadow = '0 1px 4px rgba(0, 123, 255, 0.12)';
    });
    
    displayElement.addEventListener('mouseleave', () => {
        displayElement.style.borderColor = '#ddd';
        displayElement.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.08)';
    });
    
    // Click handler for display element
    displayElement.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        displayElement.style.borderColor = '#0056b3';
        displayElement.style.boxShadow = '0 1px 6px rgba(0, 86, 179, 0.15)';
        openDatePicker();
    });
    
    // Also handle clicks on the container
    container.addEventListener('click', (e) => {
        if (e.target === container || e.target === displayElement) {
            e.preventDefault();
            e.stopPropagation();
            openDatePicker();
        }
    });
}

// Format date for input field
function formatDateForInput(date) {
    // HTML input type="date" requires YYYY-MM-DD format
    // Use local time instead of UTC to avoid timezone issues
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Format date for Thai display (DD/MM/YYYY)
function formatDateForDisplay(dateStr) {
    if (!dateStr) return '';
    const [year, month, day] = dateStr.split('-');
    return `${day}/${month}/${year}`;
}

// Parse Thai date format (DD/MM/YYYY) to ISO format (YYYY-MM-DD)
function parseDateFromDisplay(displayDate) {
    if (!displayDate) return '';
    const [day, month, year] = displayDate.split('/');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
}

// Select date range
// Function for summary cards only (used by div buttons)
function selectSummaryDateRange(range) {
    console.log('[DEBUG] selectSummaryDateRange: Called with range:', range, 'at:', new Date().toISOString());
    console.log('[DEBUG] selectSummaryDateRange: Previous selectedDateRange:', selectedDateRange);
    selectedDateRange = range;
    console.log('[DEBUG] selectSummaryDateRange: New selectedDateRange:', selectedDateRange);
    const today = new Date();
    let startDate, endDate;
    
    // Remove active class from all buttons
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to selected button
    document.getElementById(`btn-${range}`).classList.add('active');
    
    switch(range) {
        case 'today':
            startDate = new Date(today);
            endDate = new Date(today);
            break;
        case 'week':
            startDate = new Date(today);
            startDate.setDate(today.getDate() - 6); // Start date is 6 days ago (total 7 days including today)
            endDate = new Date(today); // End date is today
            break;
        case 'month':
            startDate = new Date(today);
            startDate.setDate(today.getDate() - 29); // Start date is 29 days ago (total 30 days including today)
            endDate = new Date(today); // End date is today
            break;
    }
    
    // Update sales label text based on selected range with date information
    const salesLabelEl = document.querySelector('.text-xs.font-weight-bold.text-primary.text-uppercase.mb-1');
    if (salesLabelEl) {
        switch(range) {
            case 'today':
                salesLabelEl.textContent = `ยอดขายวันนี้ (${formatDateForDisplay(formatDateForInput(startDate))})`;
                break;
            case 'week':
                salesLabelEl.textContent = `ยอดขาย 7 วันล่าสุด (${formatDateForDisplay(formatDateForInput(startDate))} - ${formatDateForDisplay(formatDateForInput(endDate))})`;
                break;
            case 'month':
                salesLabelEl.textContent = `ยอดขาย 30 วันล่าสุด (${formatDateForDisplay(formatDateForInput(startDate))} - ${formatDateForDisplay(formatDateForInput(endDate))})`;
                break;
        }
    }
    
    // Update date inputs
    document.getElementById('start-date').value = formatDateForInput(startDate);
    document.getElementById('end-date').value = formatDateForInput(endDate);
    
    // Update Thai date displays
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    if (startDateInput && startDateInput.parentNode.querySelector('.thai-date-display')) {
        startDateInput.parentNode.querySelector('.thai-date-display').textContent = formatDateForDisplay(startDateInput.value);
    }
    if (endDateInput && endDateInput.parentNode.querySelector('.thai-date-display')) {
        endDateInput.parentNode.querySelector('.thai-date-display').textContent = formatDateForDisplay(endDateInput.value);
    }
    
    // Load dashboard data for summary cards only
    loadSummaryData();
    
    // *** ไม่เรียก loadTopItemsData() เพื่อไม่ให้ปุ่มวันที่ส่งผลต่อเมนูขายดี ***
    // เมนูขายดีจะถูกควบคุมโดย chart period dropdown เท่านั้น
}

// Legacy function for backward compatibility
function selectDateRange(range) {
    selectSummaryDateRange(range);
}

// Function to load data for summary cards only
async function loadSummaryData() {
    // ป้องกันการเรียก API ซ้ำซ้อน
    if (isLoadingData) {
        console.log('[DEBUG] loadSummaryData: Already loading, skipping...');
        return;
    }
    
    isLoadingData = true;
    console.log('[DEBUG] loadSummaryData: Starting data load...');
    console.log('[DEBUG] loadSummaryData: selectedDateRange =', selectedDateRange);
    
    try {
        // ใช้ช่วงวันที่ตาม selectedDateRange เป็นหลัก
        // เพื่อให้ข้อมูลสรุปตรงกับปุ่มที่เลือก
        let startDate, endDate;
        const today = new Date();
        
        // ใช้ selectedDateRange เป็นหลัก
        switch(selectedDateRange) {
            case 'today':
                startDate = new Date(today);
                endDate = new Date(today);
                break;
            case 'week':
                startDate = new Date(today);
                startDate.setDate(today.getDate() - 6); // Start date is 6 days ago (total 7 days including today)
                endDate = new Date(today); // End date is today
                break;
            case 'month':
                startDate = new Date(today);
                startDate.setDate(today.getDate() - 29); // Start date is 29 days ago (total 30 days including today)
                endDate = new Date(today); // End date is today
                break;
            case 'custom':
                // สำหรับ custom date range ให้ใช้ค่าจาก input fields
                startDate = document.getElementById('start-date').value;
                endDate = document.getElementById('end-date').value;
                break;
            default:
                // Default to today
                startDate = new Date(today);
                endDate = new Date(today);
        }
        console.log('[DEBUG] loadSummaryData: Using selectedDateRange', selectedDateRange, 'from', startDate?.toDateString?.() || startDate, 'to', endDate?.toDateString?.() || endDate);
        
        // Format dates for API call (ถ้าเป็น Date object)
        const startDateStr = typeof startDate === 'string' ? startDate : formatDateForInput(startDate);
        const endDateStr = typeof endDate === 'string' ? endDate : formatDateForInput(endDate);
        
        console.log('[DEBUG] loadSummaryData: Date range for selectedDateRange', selectedDateRange, ':', startDateStr, 'to', endDateStr);
        
        showLoadingState();
        
        // Fetch data from API with date range
        const apiUrl = `/api/dashboard-data?start=${startDateStr}&end=${endDateStr}`;
        console.log('[DEBUG] loadSummaryData: Calling API:', apiUrl);
        const response = await fetch(apiUrl);
        const responseData = await response.json();
        
        console.log('[DEBUG] loadSummaryData: API response:', responseData);
        console.log('[DEBUG] loadSummaryData: periodSales from API:', responseData.data?.periodSales);
        console.log('[DEBUG] loadSummaryData: totalCustomers from API:', responseData.data?.totalCustomers);
        
        // Extract data from response
        const apiData = responseData.data || responseData;
        
        // Map API data to the format expected by updateSummaryCards
        const data = {
            periodSales: apiData.periodSales || 0,
            todaySales: apiData.todaySales || 0,
            weekSales: apiData.weekSales || 0,
            monthSales: apiData.monthSales || 0,
            totalCustomers: apiData.totalCustomers || 0,


        };
        
        console.log('[DEBUG] loadSummaryData: Mapped data:', data);
        
        // Update only summary cards, not charts
        updateSummaryCards(data);
        updateChangeIndicators();
        
        hideLoadingState();
        
        console.log('[DEBUG] loadSummaryData: Data load completed successfully');
        
    } catch (error) {
        console.error('Error loading summary data:', error);
        
        // Show error but do not overwrite with mock data if API failed
        console.error('[DEBUG] loadSummaryData: API failed, not updating summary cards with mock data to prevent flicker.');
        hideLoadingState();
    } finally {
        isLoadingData = false;
        console.log('[DEBUG] loadSummaryData: Loading flag reset');
    }
}



// Load custom date data
function loadCustomDateData() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    if (startDate && endDate) {
        // Remove active class from preset buttons
        document.querySelectorAll('.btn-group .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Set selected date range to custom to prevent auto-reset
        selectedDateRange = 'custom';
        
        // Update sales label for custom date range
        const salesLabelEl = document.querySelector('.text-xs.font-weight-bold.text-primary.text-uppercase.mb-1');
        if (salesLabelEl) {
            if (startDate === endDate) {
                salesLabelEl.textContent = `ยอดขายวันที่ ${formatDateThai(startDate)}`;
            } else {
                salesLabelEl.textContent = `ยอดขาย ${formatDateThai(startDate)} - ${formatDateThai(endDate)}`;
            }
        }
        
        // Load summary data only
        loadSummaryData();
        
        // *** ไม่เรียก loadTopItemsData() เพื่อไม่ให้ custom date inputs ส่งผลต่อเมนูขายดี ***
        // เมนูขายดีจะถูกควบคุมโดย chart period dropdown เท่านั้น
    }
}

// Format date for Thai display
function formatDateThai(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('th-TH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Load dashboard data
async function loadDashboardData() {
    try {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        // Show loading state
        showLoadingState();
        
        // Fetch data from API
        const response = await fetch(`/api/dashboard-data?start=${startDate}&end=${endDate}`);
        const responseData = await response.json();
        
        // Extract data from response
        const data = responseData.data || responseData;
        
        // Update summary cards
        updateSummaryCards(data);
        
        // Update charts
        updateCharts(data);
        
        // Update top items
        const daysDiff = Math.ceil((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24)) + 1;
        console.log('[DEBUG] topItems data received for period:', daysDiff, 'days');
        console.log('[DEBUG] topItems data:', data.topItems);
        console.log('[DEBUG] Date range used:', startDate, 'to', endDate);
        updateTopItems(data.topItems || []);
        
        // Update calendar with sales data
        updateCalendarWithSales(data.dailySales || {});
        
        // Hide loading state
        hideLoadingState();
        
    } catch (error) {
        // Load mock data for demonstration
        loadMockData();
    }
}

// Load mock data for demonstration
function loadMockData() {
    const mockData = {
        todaySales: 15420.50,
        weekSales: 89750.25,
        monthSales: 342180.75,
        totalCustomers: 1247,


        dailySales: generateMockDailySales(),
        categorySales: {
            'อาหารจานหลัก': 45.2,
            'เครื่องดื่ม': 28.7,
            'ของหวาน': 16.8,
            'อื่นๆ': 9.3
        },
        topItems: [
            { name: 'ผัดไทย', sales: 156, amount: 7800 },
            { name: 'ต้มยำกุ้ง', sales: 134, amount: 6700 },
            { name: 'ข้าวผัดกุ้ง', sales: 128, amount: 5120 },
            { name: 'ส้มตำ', sales: 98, amount: 3920 },
            { name: 'แกงเขียวหวาน', sales: 87, amount: 4350 }
        ],
        monthlyTrend: generateMockMonthlyTrend()
    };
    
    updateSummaryCards(mockData);
    updateCharts(mockData);
    updateTopItems(mockData.topItems);
    updateCalendarWithSales(mockData.dailySales);
}

// Generate mock daily sales data
function generateMockDailySales() {
    const sales = {};
    const today = new Date();
    
    for (let i = 0; i < 30; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const dateStr = formatDateForInput(date);
        
        sales[dateStr] = {
            sales: Math.floor(Math.random() * 20000) + 5000,
            orders: Math.floor(Math.random() * 50) + 10,
            customers: Math.floor(Math.random() * 80) + 20
        };
    }
    
    return sales;
}

// Generate mock monthly trend data
function generateMockMonthlyTrend() {
    const months = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.'];
    return months.map(month => ({
        month,
        sales: Math.floor(Math.random() * 300000) + 200000
    }));
}

// Update summary cards
function updateSummaryCards(data) {
    console.log('[DEBUG] updateSummaryCards: Called at:', new Date().toISOString());
    console.log('[DEBUG] updateSummaryCards: Updating with data:', data);
    console.log('[DEBUG] updateSummaryCards: Selected date range:', selectedDateRange);
    console.log('[DEBUG] updateSummaryCards: todaySales:', data.todaySales, 'periodSales:', data.periodSales);
    
    // Update today-sales card based on selected date range
    const todaySalesElement = document.getElementById('today-sales');
    const todaySalesLabelElement = todaySalesElement?.parentNode.querySelector('.text-xs.font-weight-bold.text-primary.text-uppercase.mb-1');
    if (todaySalesElement && todaySalesLabelElement) {
        let salesValue, labelText;
        const today = new Date();
        
        switch(selectedDateRange) {
            case 'today':
                salesValue = data.todaySales || 0;
                labelText = `ยอดขายวันนี้ (${formatDateForDisplay(formatDateForInput(today))})`;
                break;
            case 'week':
                salesValue = data.periodSales || 0;
                const weekStart = new Date(today);
                weekStart.setDate(today.getDate() - 6);
                labelText = `ยอดขาย 7 วันล่าสุด (${formatDateForDisplay(formatDateForInput(weekStart))} - ${formatDateForDisplay(formatDateForInput(today))})`;
                break;
            case 'month':
                salesValue = data.periodSales || 0;
                console.log('[DEBUG] Month case - data.periodSales:', data.periodSales, 'data object:', data);
                const monthStart = new Date(today);
                monthStart.setDate(today.getDate() - 29);
                labelText = `ยอดขาย 30 วันล่าสุด (${formatDateForDisplay(formatDateForInput(monthStart))} - ${formatDateForDisplay(formatDateForInput(today))})`;
                break;
            default:
                salesValue = data.todaySales || 0;
                labelText = `ยอดขายวันนี้ (${formatDateForDisplay(formatDateForInput(today))})`;
        }
        
        todaySalesElement.textContent = `฿${salesValue.toLocaleString()}`;
        todaySalesLabelElement.textContent = labelText;
        console.log('[DEBUG] updateSummaryCards: Updated today-sales card:', labelText, salesValue);
    } else {
        console.warn('[DEBUG] updateSummaryCards: today-sales element not found');
    }
    
    // Update week sales card - show current week sales (Monday to Sunday) - FIXED DISPLAY
    const weekSalesElement = document.getElementById('week-sales');
    const weekSalesLabelElement = weekSalesElement?.parentNode.querySelector('.text-xs.font-weight-bold.text-success.text-uppercase.mb-1');
    if (weekSalesElement && weekSalesLabelElement) {
        // Calculate current week (Monday to Sunday)
        const today = new Date();
        const currentDay = today.getDay(); // 0 = Sunday, 1 = Monday, ..., 6 = Saturday
        const mondayOffset = currentDay === 0 ? -6 : 1 - currentDay; // If Sunday, go back 6 days to Monday
        
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() + mondayOffset);
        
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6); // Sunday
        
        // Use weekSales from data if available, otherwise use a default value
        const weekSalesValue = data.weekSales || data.periodSales || 0;
        const weekLabelText = `ยอดขายสัปดาห์นี้ (${formatDateForDisplay(formatDateForInput(weekStart))} - ${formatDateForDisplay(formatDateForInput(weekEnd))})`;
        
        weekSalesElement.textContent = `฿${weekSalesValue.toLocaleString()}`;
        weekSalesLabelElement.textContent = weekLabelText;
        console.log('[DEBUG] updateSummaryCards: Updated week-sales card (FIXED):', weekLabelText, weekSalesValue);
    }
    

    
    // Update month sales card - show current month sales (1st to last day of month) - FIXED DISPLAY
    const monthSalesElement = document.getElementById('month-sales');
    const monthSalesLabelElement = monthSalesElement?.parentNode.querySelector('.text-xs.font-weight-bold.text-info.text-uppercase.mb-1');
    if (monthSalesElement && monthSalesLabelElement) {
        // Calculate current month (1st to last day)
        const today = new Date();
        const monthStart = new Date(today.getFullYear(), today.getMonth(), 1); // First day of current month
        const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0); // Last day of current month
        
        // Use monthSales from data if available, otherwise use a default value
        const monthSalesValue = data.monthSales || data.periodSales || 0;
        const monthLabelText = `ยอดขายเดือนนี้ (${formatDateForDisplay(formatDateForInput(monthStart))} - ${formatDateForDisplay(formatDateForInput(monthEnd))})`;
        
        monthSalesElement.textContent = `฿${monthSalesValue.toLocaleString()}`;
        monthSalesLabelElement.textContent = monthLabelText;
        console.log('[DEBUG] updateSummaryCards: Updated month-sales card (FIXED):', monthLabelText, monthSalesValue);
    }
    
    // Update total customers card with date range based on selected period
    const totalCustomersElement = document.getElementById('total-customers');
    const totalCustomersLabelElement = totalCustomersElement?.parentNode.querySelector('.text-xs.font-weight-bold.text-warning.text-uppercase.mb-1');
    if (totalCustomersElement && totalCustomersLabelElement) {
        if (data.totalCustomers !== undefined) {
            totalCustomersElement.textContent = data.totalCustomers?.toLocaleString() || '0';
        }
        
        // Update label based on selected date range
        let labelText;
        const today = new Date();
        
        switch(selectedDateRange) {
            case 'today':
                labelText = `จำนวนลูกค้าวันนี้ (${formatDateForDisplay(formatDateForInput(today))})`;
                break;
            case 'week':
                const weekStart = new Date(today);
                weekStart.setDate(today.getDate() - 6);
                labelText = `จำนวนลูกค้า 7 วันล่าสุด (${formatDateForDisplay(formatDateForInput(weekStart))} - ${formatDateForDisplay(formatDateForInput(today))})`;
                break;
            case 'month':
                const monthStart = new Date(today);
                monthStart.setDate(today.getDate() - 29);
                labelText = `จำนวนลูกค้า 30 วันล่าสุด (${formatDateForDisplay(formatDateForInput(monthStart))} - ${formatDateForDisplay(formatDateForInput(today))})`;
                break;
            default:
                labelText = `จำนวนลูกค้าวันนี้ (${formatDateForDisplay(formatDateForInput(today))})`;
        }
        
        totalCustomersLabelElement.textContent = labelText;
        console.log('[DEBUG] updateSummaryCards: Updated total-customers card:', labelText);
    }
    

    

    
    // Update change indicators (mock data)
    updateChangeIndicators();
    
    console.log('[DEBUG] updateSummaryCards: All cards updated successfully');
}

// Update change indicators
function updateChangeIndicators() {
    // Hide change indicators since we don't have historical data to calculate real changes
    const changeIds = ['today-change', 'week-change', 'month-change'];
    
    changeIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = ''; // Clear mock data
            element.style.display = 'none'; // Hide the element
        }
    });
}

// Initialize charts
function initializeCharts() {
    initializeSalesChart();
    initializeCategoryChart();
    initializeMonthlyTrendChart();
}

// Initialize sales chart
function initializeSalesChart() {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;
    
    dashboardSalesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'รายได้ (฿)',
                data: [],
                backgroundColor: 'rgba(78, 115, 223, 0.8)',
                borderColor: 'rgba(78, 115, 223, 1)',
                borderWidth: 1,
                yAxisID: 'y'
            }, {
                label: 'จำนวนออเดอร์',
                data: [],
                type: 'line',
                backgroundColor: 'rgba(28, 200, 138, 0.1)',
                borderColor: 'rgba(28, 200, 138, 1)',
                borderWidth: 2,
                fill: false,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'รายได้ (฿)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'จำนวนออเดอร์'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.datasetIndex === 0) {
                                return `รายได้: ฿${context.parsed.y.toLocaleString()}`;
                            } else {
                                return `ออเดอร์: ${context.parsed.y} รายการ`;
                            }
                        }
                    }
                }
            }
        }
    });
}

// Initialize category chart
function initializeCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    dashboardCategoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    'rgba(78, 115, 223, 0.8)',
                    'rgba(28, 200, 138, 0.8)',
                    'rgba(54, 185, 204, 0.8)',
                    'rgba(246, 194, 62, 0.8)',
                    'rgba(231, 74, 59, 0.8)'
                ],
                borderColor: [
                    'rgba(78, 115, 223, 1)',
                    'rgba(28, 200, 138, 1)',
                    'rgba(54, 185, 204, 1)',
                    'rgba(246, 194, 62, 1)',
                    'rgba(231, 74, 59, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed}%`;
                        }
                    }
                }
            }
        }
    });
}

// Initialize monthly trend chart
function initializeMonthlyTrendChart() {
    const ctx = document.getElementById('monthlyTrendChart');
    if (!ctx) return;
    
    dashboardMonthlyTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'ยอดขายรายเดือน',
                data: [],
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                borderColor: 'rgba(78, 115, 223, 1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `ยอดขาย: ฿${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'ยอดขาย (฿)'
                    }
                }
            }
        }
    });
}

// Update charts
function updateCharts(data) {
    updateSalesChart(data.dailySales || {});
    updateCategoryChart(data.categorySales || {});
    updateMonthlyTrendChart(data.monthlyTrend || []);
}

// Update sales chart
function updateSalesChart(dailySales) {
    if (!dashboardSalesChart) return;
    
    const period = document.getElementById('chart-period').value;
    const days = parseInt(period);
    const labels = [];
    const salesData = [];
    const ordersData = [];
    
    // ตรวจสอบว่ามีข้อมูลจริงหรือไม่
    const hasRealData = dailySales && Object.keys(dailySales).length > 0;
    console.log('[DEBUG] updateSalesChart: Has real data:', hasRealData, 'dailySales:', dailySales);
    
    const today = new Date();
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const dateStr = formatDateForInput(date);
        
        let dayData;
        if (hasRealData && dailySales[dateStr]) {
            // ใช้ข้อมูลจริงจาก API
            dayData = dailySales[dateStr];
            console.log(`[DEBUG] Real data for ${dateStr}:`, dayData);
        } else {
            // ใส่ 0 สำหรับวันที่ไม่มีข้อมูล
            dayData = {
                sales: 0,
                orders: 0
            };
            console.log(`[DEBUG] No data for ${dateStr}, using zero values`);
        }
        
        labels.push(date.getDate() + '/' + (date.getMonth() + 1));
        salesData.push(dayData.sales);
        ordersData.push(dayData.orders);
    }
    
    console.log('[DEBUG] updateSalesChart: Final data - Sales:', salesData, 'Orders:', ordersData);
    
    dashboardSalesChart.data.labels = labels;
    dashboardSalesChart.data.datasets[0].data = salesData;
    dashboardSalesChart.data.datasets[1].data = ordersData;
    dashboardSalesChart.update();
}

// Update category chart
function updateCategoryChart(categorySales) {
    if (!dashboardCategoryChart) return;
    
    const labels = Object.keys(categorySales);
    const data = Object.values(categorySales);
    
    dashboardCategoryChart.data.labels = labels;
    dashboardCategoryChart.data.datasets[0].data = data;
    dashboardCategoryChart.update();
}

// Update monthly trend chart
function updateMonthlyTrendChart(monthlyData) {
    if (!dashboardMonthlyTrendChart) return;
    
    const labels = monthlyData.map(item => item.month);
    const data = monthlyData.map(item => item.sales);
    
    dashboardMonthlyTrendChart.data.labels = labels;
    dashboardMonthlyTrendChart.data.datasets[0].data = data;
    dashboardMonthlyTrendChart.update();
}

// Update top items
function updateTopItems(items) {
    const container = document.getElementById('top-items-list');
    if (!container) return;
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-3">
                <i class="fas fa-info-circle fa-2x mb-2"></i>
                <p>ไม่มีข้อมูลเมนูขายดี</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = items.map((item, index) => `
        <div class="top-item">
            <div class="item-rank">${index + 1}</div>
            <div class="item-info">
                <div class="item-name">${item.name}</div>
                <div class="item-sales">${item.quantity} รายการ</div>
            </div>
            <div class="item-amount">฿${(item.sales || 0).toLocaleString()}</div>
        </div>
    `).join('');
}

// Generate calendar
function generateCalendar() {
    const container = document.getElementById('sales-calendar');
    if (!container) return;
    
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const monthNames = [
        'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
        'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
    ];
    
    const dayNames = ['อา', 'จ', 'อ', 'พ', 'พฤ', 'ศ', 'ส'];
    
    let html = `
        <div class="calendar-container">
            <div class="calendar-header">
                <button class="calendar-nav" onclick="changeMonth(-1)">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <h5 class="calendar-title">${monthNames[month]} ${year}</h5>
                <button class="calendar-nav" onclick="changeMonth(1)">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            <div class="calendar-grid">
    `;
    
    // Add day headers
    dayNames.forEach(day => {
        html += `<div class="calendar-day-header">${day}</div>`;
    });
    
    // Add calendar days
    const today = new Date();
    const currentDateCopy = new Date(startDate);
    
    for (let i = 0; i < 42; i++) {
        const isCurrentMonth = currentDateCopy.getMonth() === month;
        const isToday = currentDateCopy.toDateString() === today.toDateString();
        const dateStr = formatDateForInput(currentDateCopy);
        
        let classes = 'calendar-day';
        if (!isCurrentMonth) classes += ' other-month';
        if (isToday) classes += ' today';
        
        html += `
            <div class="${classes}" onclick="selectCalendarDate('${dateStr}')" data-date="${dateStr}">
                <div>${currentDateCopy.getDate()}</div>
                <div class="calendar-day-sales" id="sales-${dateStr}"></div>
            </div>
        `;
        
        currentDateCopy.setDate(currentDateCopy.getDate() + 1);
    }
    
    html += `
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Change month
function changeMonth(direction) {
    currentDate.setMonth(currentDate.getMonth() + direction);
    generateCalendar();
    
    // Reload summary data only for new month
    loadSummaryData();
    
    // *** ไม่เรียก loadTopItemsData() เพื่อไม่ให้การเปลี่ยนเดือนส่งผลต่อเมนูขายดี ***
    // เมนูขายดีจะถูกควบคุมโดย chart period dropdown เท่านั้น
}

// Update calendar with sales data
function updateCalendarWithSales(dailySales) {
    Object.entries(dailySales).forEach(([date, data]) => {
        const salesElement = document.getElementById(`sales-${date}`);
        const dayElement = document.querySelector(`[data-date="${date}"]`);
        
        if (salesElement && dayElement) {
            salesElement.textContent = `฿${(data.sales / 1000).toFixed(0)}k`;
            
            if (data.sales > 0) {
                dayElement.classList.add('has-sales');
                if (data.sales > 15000) {
                    dayElement.classList.add('high-sales');
                }
            }
        }
    });
}

// Select calendar date
function selectCalendarDate(dateStr) {
    // Remove previous selection
    document.querySelectorAll('.calendar-day.selected').forEach(day => {
        day.classList.remove('selected');
    });
    
    // Add selection to clicked date
    const dayElement = document.querySelector(`[data-date="${dateStr}"]`);
    if (dayElement) {
        dayElement.classList.add('selected');
    }
    
    // Show date details
    showDateDetails(dateStr);
}

// Show date details
function showDateDetails(dateStr) {
    const container = document.getElementById('selected-date-details');
    if (!container) return;
    
    // Get sales data for the date (mock data for now)
    const salesData = salesData || {};
    const dayData = salesData[dateStr] || generateMockDayData();
    
    const date = new Date(dateStr);
    const formattedDate = date.toLocaleDateString('th-TH', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    container.innerHTML = `
        <h6 class="mb-3">${formattedDate}</h6>
        <div class="date-detail-item">
            <span class="date-detail-label">ยอดขาย</span>
            <span class="date-detail-value sales">฿${dayData.sales.toLocaleString()}</span>
        </div>
        <div class="date-detail-item">
            <span class="date-detail-label">จำนวนออเดอร์</span>
            <span class="date-detail-value orders">${dayData.orders} รายการ</span>
        </div>
        <div class="date-detail-item">
            <span class="date-detail-label">จำนวนลูกค้า</span>
            <span class="date-detail-value">${dayData.customers} คน</span>
        </div>
        <div class="date-detail-item">
            <span class="date-detail-label">ค่าเฉลี่ยต่อออเดอร์</span>
            <span class="date-detail-value">฿${(dayData.sales / dayData.orders || 0).toFixed(2)}</span>
        </div>
    `;
}

// Generate mock day data
function generateMockDayData() {
    return {
        sales: Math.floor(Math.random() * 20000) + 5000,
        orders: Math.floor(Math.random() * 50) + 10,
        customers: Math.floor(Math.random() * 80) + 20
    };
}

// Change sales chart period
// Function to load data for charts only (NOT top items)
async function loadChartData() {
    try {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        // Show loading state
        showLoadingState();
        
        // Fetch data from API
        const response = await fetch(`/api/dashboard-data?start=${startDate}&end=${endDate}`);
        const responseData = await response.json();
        
        // Extract data from response
        const data = responseData.data || responseData;
        
        // Update only charts, NOT summary cards or top items
        updateCharts(data);
        
        // Hide loading state
        hideLoadingState();
        
    } catch (error) {
        console.error('Error loading chart data:', error);
        hideLoadingState();
    }
}

// Function to load data for charts ONLY with specific date range (NOT top items)
async function loadChartDataWithDateRange(startDate, endDate) {
    try {
        console.log('[DEBUG] loadChartDataWithDateRange: Loading chart data for', startDate, 'to', endDate);
        
        // Show loading state
        showLoadingState();
        
        // Fetch data from API
        const response = await fetch(`/api/dashboard-data?start=${startDate}&end=${endDate}`);
        const responseData = await response.json();
        
        console.log('[DEBUG] loadChartDataWithDateRange: API response:', responseData);
        
        // Extract data from response
        const data = responseData.data || responseData;
        
        // Update ONLY charts, NOT top items (top items should follow summary date range)
        updateCharts(data);
        
        // Hide loading state
        hideLoadingState();
        
    } catch (error) {
        console.error('Error loading chart data with date range:', error);
        hideLoadingState();
    }
}

// Function to load top items data with current summary date range
async function loadTopItemsData() {
    try {
        console.log('[DEBUG] loadTopItemsData: Loading top items with summary date range');
        
        // Get current summary date range from input fields
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        console.log('[DEBUG] loadTopItemsData: Using date range', startDate, 'to', endDate);
        
        // Fetch data from API using summary date range
        const response = await fetch(`/api/dashboard-data?start=${startDate}&end=${endDate}`);
        const responseData = await response.json();
        
        // Extract data from response
        const data = responseData.data || responseData;
        
        // Update ONLY top items
        console.log('[DEBUG] loadTopItemsData: topItems data received:', data.topItems);
        updateTopItems(data.topItems || []);
        
    } catch (error) {
        console.error('Error loading top items data:', error);
    }
}

// Function to load top items data with specific date range (for chart period)
async function loadTopItemsDataWithDateRange(startDate, endDate) {
    try {
        console.log('[DEBUG] loadTopItemsDataWithDateRange: Loading top items for chart period', startDate, 'to', endDate);
        
        // Fetch data from API using chart date range
        const response = await fetch(`/api/dashboard-data?start=${startDate}&end=${endDate}`);
        const responseData = await response.json();
        
        // Extract data from response
        const data = responseData.data || responseData;
        
        // Update ONLY top items
        console.log('[DEBUG] loadTopItemsDataWithDateRange: topItems data received:', data.topItems);
        updateTopItems(data.topItems || []);
        
    } catch (error) {
        console.error('Error loading top items data with date range:', error);
    }
}

function changeSalesChartPeriod() {
    console.log('[DEBUG] changeSalesChartPeriod() called');
    const periodSelect = document.getElementById('chart-period');
    const days = parseInt(periodSelect.value);
    console.log('[DEBUG] Selected period:', days, 'days');
    
    // เก็บสถานะของ chart period ที่เลือกไว้
    currentChartPeriod = days;
    
    // Calculate date range for API call
    const today = new Date();
    let startDate, endDate;
    
    // สำหรับทุกช่วงเวลา ใช้การคำนวณแบบเดียวกัน (วันย้อนหลังจริงๆ)
    endDate = new Date(today);
    startDate = new Date(today);
    startDate.setDate(endDate.getDate() - (days - 1));
    
    console.log(`[DEBUG] Calculating ${days} days back from ${today.toDateString()}`);
    console.log(`[DEBUG] Start date: ${startDate.toDateString()}, End date: ${endDate.toDateString()}`);
    
    // Format dates for API call
    const startDateStr = formatDateForInput(startDate);
    const endDateStr = formatDateForInput(endDate);
    console.log('[DEBUG] Date range for API:', startDateStr, 'to', endDateStr);
    
    // *** ไม่อัปเดต date input fields เพื่อไม่ให้ส่งผลต่อข้อมูลสรุปยอดขาย ***
    // การเปลี่ยนแปลงช่วงวันที่ของกราฟไม่ควรส่งผลต่อข้อมูลสรุปยอดขายที่แสดงในการ์ด
    
    // Load data for charts and top items with the calculated date range
    loadChartDataWithDateRange(startDateStr, endDateStr);
    
    // Load top items data with chart period date range
    loadTopItemsDataWithDateRange(startDateStr, endDateStr);
}

// Show loading state (ลดการกระพริบโดยไม่เปลี่ยน opacity)
function showLoadingState() {
    // เพิ่ม loading indicator แทนการเปลี่ยน opacity
    const dashboardSection = document.querySelector('#dashboard-section');
    if (dashboardSection && !dashboardSection.querySelector('.loading-indicator')) {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading-indicator';
        loadingDiv.style.cssText = 'position: absolute; top: 10px; right: 10px; color: #007bff; font-size: 12px;';
        loadingDiv.textContent = 'กำลังโหลด...';
        dashboardSection.style.position = 'relative';
        dashboardSection.appendChild(loadingDiv);
    }
}

// Hide loading state
function hideLoadingState() {
    const loadingIndicator = document.querySelector('.loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// Note: initializeEnhancedDashboard is called from admin.html

// Add event listeners for date range buttons
// Initialize dashboard when DOM is loaded
let dashboardInitialized = false;

function initializeDashboard() {
    if (dashboardInitialized) {
        console.log('[DEBUG] initializeDashboard: Already initialized, skipping...');
        return;
    }
    
    console.log('[DEBUG] initializeDashboard: Starting initialization...');
    
    // Add event listeners for date range buttons
    const todayBtn = document.getElementById('btn-today');
    const weekBtn = document.getElementById('btn-week');
    const monthBtn = document.getElementById('btn-month');
    
    console.log('[DEBUG] initializeDashboard: Found buttons:', {
        today: !!todayBtn,
        week: !!weekBtn,
        month: !!monthBtn
    });
    
    // ป้องกันการผูก event listener ซ้ำโดยตรวจสอบ attribute
    if (todayBtn && !todayBtn.hasAttribute('data-listener-added')) {
        todayBtn.addEventListener('click', () => {
            console.log('[DEBUG] initializeDashboard: Today button clicked');
            selectSummaryDateRange('today');
        });
        todayBtn.setAttribute('data-listener-added', 'true');
    }
    if (weekBtn && !weekBtn.hasAttribute('data-listener-added')) {
        weekBtn.addEventListener('click', () => {
            console.log('[DEBUG] initializeDashboard: Week button clicked');
            selectSummaryDateRange('week');
        });
        weekBtn.setAttribute('data-listener-added', 'true');
    }
    if (monthBtn && !monthBtn.hasAttribute('data-listener-added')) {
        monthBtn.addEventListener('click', () => {
            console.log('[DEBUG] initializeDashboard: Month button clicked');
            selectSummaryDateRange('month');
        });
        monthBtn.setAttribute('data-listener-added', 'true');
    }
    
    dashboardInitialized = true;
    
    // Set "today" as default selection
    setTimeout(() => {
        console.log('[DEBUG] initializeDashboard: Setting default to today');
        selectSummaryDateRange('today');
    }, 100);
}

// Call initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] DOMContentLoaded: Initializing dashboard...');
    initializeDashboard();
    
    // Re-initialize when dashboard section is shown (for tab switching)
    const dashboardSection = document.getElementById('dashboard-section');
    if (dashboardSection) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const isVisible = dashboardSection.style.display !== 'none';
                    if (isVisible && !dashboardSection.dataset.initialized && !dashboardInitialized) {
                        console.log('[DEBUG] Dashboard section became visible, re-initializing...');
                        initializeDashboard();
                        dashboardSection.dataset.initialized = 'true';
                    }
                }
            });
        });
        
        observer.observe(dashboardSection, {
            attributes: true,
            attributeFilter: ['style']
        });
    }
});

// Also call when dashboard section is shown (but don't reset date selection)
if (typeof window.showSection === 'function') {
    const originalShowSection = window.showSection;
    window.showSection = function(sectionId) {
        originalShowSection(sectionId);
        if (sectionId === 'dashboard') {
            console.log('[DEBUG] showSection: Dashboard section shown');
            // ไม่ต้องผูก event listener ซ้ำ เพราะ initializeDashboard() จะจัดการแล้ว
            // เพียงแค่เรียก initializeDashboard() ซึ่งจะตรวจสอบว่าได้ผูกแล้วหรือยัง
            setTimeout(() => {
                initializeDashboard();
            }, 100);
        }
    };
}

// ฟังก์ชันสำหรับรีเฟรชข้อมูลโดยไม่รีเซ็ตสถานะของกราฟ
function refreshDashboardData() {
    console.log('[DEBUG] refreshDashboardData: Refreshing without resetting chart state');
    
    // รีเฟรชข้อมูลสรุปยอดขาย
    loadSummaryData();
    
    // *** ไม่เรียก loadTopItemsData() เพื่อไม่ให้ auto-refresh ส่งผลต่อเมนูขายดี ***
    // เมนูขายดีจะถูกควบคุมโดย chart period dropdown เท่านั้น
    
    // รีเฟรชกราฟและเมนูขายดีโดยรักษาสถานะที่เลือกไว้
    const periodSelect = document.getElementById('chart-period');
    if (periodSelect && currentChartPeriod) {
        // รักษาสถานะของ chart period ที่เลือกไว้
        periodSelect.value = currentChartPeriod;
        changeSalesChartPeriod(); // จะเรียก loadTopItemsDataWithDateRange() ด้วย
    } else {
        // ถ้าไม่มี chart period ที่เก็บไว้ ให้ใช้ค่าเริ่มต้น
        loadChartData();
    }
}

// Export functions for global access
window.selectDateRange = selectDateRange;
window.selectSummaryDateRange = selectSummaryDateRange;
window.loadCustomDateData = loadCustomDateData;
window.loadDashboardData = loadDashboardData;
window.loadSummaryData = loadSummaryData;
window.loadChartData = loadChartData;
window.changeSalesChartPeriod = changeSalesChartPeriod;
window.changeMonth = changeMonth;
window.selectCalendarDate = selectCalendarDate;
window.refreshDashboardData = refreshDashboardData;