// Global variables
let currentTable = null;
let cart = [];
let allMenuItems = [];
let currentCategory = null;
let orderStatus = null;

// Utility: Get query string parameter
function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Load restaurant information
async function loadRestaurantInfo() {
    try {
        // Try to load from API first
        const response = await fetch('/api/restaurant-info');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.data) {
                updateRestaurantName(data.data.name);
                return;
            }
        }
    } catch (error) {
        console.log('Failed to load restaurant info from API, using localStorage:', error);
    }
    
    // Fallback to localStorage
    const savedRestaurantName = localStorage.getItem('restaurant_name');
    if (savedRestaurantName) {
        updateRestaurantName(savedRestaurantName);
    }
    // If no data found anywhere, keep default name
}

// Update restaurant name in h1 element
function updateRestaurantName(name) {
    const restaurantNameElement = document.querySelector('h1.restaurant-name');
    if (restaurantNameElement && name) {
        restaurantNameElement.textContent = name;
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Initializing application');
    
    // Load restaurant information first
    loadRestaurantInfo();
    
    // Listen for localStorage changes (for restaurant name updates)
    window.addEventListener('storage', function(e) {
        if (e.key === 'restaurant_name' && e.newValue) {
            updateRestaurantName(e.newValue);
        }
    });
    
    // Also listen for custom events (for same-tab updates)
    window.addEventListener('restaurantNameUpdated', function(e) {
        if (e.detail && e.detail.name) {
            updateRestaurantName(e.detail.name);
        }
    });
    
    // Check for table_id in query string
    const tableId = getQueryParam('table');
    const sessionId = getQueryParam('session');
    if (tableId) {
        // Fetch table info from backend
        fetch(`http://localhost:5000/api/tables`)
            .then(response => response.json())
            .then(tables => {
                const table = tables.find(t => t.id == tableId || t.table_id == tableId);
                if (table) {
                    currentTable = { id: table.id || table.table_id, name: table.table_name, status: table.status };
                    // Update navbar
                    const tableInfo = document.getElementById('table-info');
                    if (tableInfo) tableInfo.textContent = table.table_name;
                    // Hide table selection and show menu
                    document.getElementById('table-selection-section').style.display = 'none';
                    document.querySelector('.menu-section').style.display = 'block';
                    
                    // Fetch order status to show edit menu button if needed
                    fetchOrderStatus(tableId);
                }
            });
    }
    loadTables();
    loadCategories();
    initializeSearch();
    updateCartDisplay();
    
    // เพิ่ม event listener สำหรับปุ่มเช็คบิล
    const checkBillBtn = document.getElementById('checkBillBtn');
    if (checkBillBtn) {
        checkBillBtn.addEventListener('click', requestCheckout);
    }
    
    // เริ่มการตรวจสอบเซสชั่น
    startSessionMonitoring();
});

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.getElementById('menu-search');
    const clearButton = document.getElementById('clear-search');
    
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            if (query.length > 0) {
                clearButton.classList.remove('d-none');
                searchMenuItems(query);
            } else {
                clearButton.classList.add('d-none');
                if (currentCategory) {
                    loadMenuByCategory(currentCategory);
                }
            }
        });
    }
    
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            clearButton.classList.add('d-none');
            if (currentCategory) {
                loadMenuByCategory(currentCategory);
            }
        });
    }
}

// Search menu items
function searchMenuItems(query) {
    const filteredItems = allMenuItems.filter(item => 
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        item.description.toLowerCase().includes(query.toLowerCase())
    );
    
    displayMenuItems(filteredItems);
    
    // Show/hide empty state
    const emptyState = document.getElementById('empty-state');
    if (filteredItems.length === 0) {
        emptyState.classList.remove('d-none');
    } else {
        emptyState.classList.add('d-none');
    }
}

// Load tables
function loadTables() {
    fetch('http://localhost:5000/api/tables')
        .then(response => response.json())
        .then(tables => {
            const tableContainer = document.getElementById('table-selection');
            if (!tableContainer) return; // ป้องกัน error ถ้าไม่มี element นี้
            tableContainer.innerHTML = '';
            
            tables.forEach(table => {
                const tableCard = document.createElement('div');
                tableCard.className = `col-md-3 col-sm-4 col-6 mb-3`;
                tableCard.innerHTML = `
                    <div class="table-card ${table.status === 'occupied' ? 'occupied' : 'available'}" 
                         onclick="selectTable(${table.table_id}, '${table.table_name}', '${table.status}')">
                        <div class="card-body text-center p-3">
                            <h5 class="card-title mb-2">${table.table_name}</h5>
                            <p class="card-text small text-muted mb-3">${table.seats} ที่นั่ง</p>
                            <div class="d-flex justify-content-center align-items-center">
                                <span class="badge ${table.status === 'occupied' ? 'bg-danger' : 'bg-success'} px-3 py-2">
                                    <i class="fas ${table.status === 'occupied' ? 'fa-user-friends' : 'fa-check'} me-1"></i>
                                    ${table.status === 'occupied' ? 'มีลูกค้า' : 'ว่าง'}
                                </span>
                            </div>
                        </div>
                    </div>
                `;
                tableContainer.appendChild(tableCard);
            });
        })
        .catch(error => {
            console.error('Error loading tables:', error);
            showAlert('เกิดข้อผิดพลาดในการโหลดโต๊ะ', 'error');
        });
}

// Select table
function selectTable(tableId, tableName, status) {
    currentTable = { id: tableId, name: tableName, status: status };
    
    // Update navbar to show selected table
    const tableInfo = document.getElementById('table-info');
    if (tableInfo) {
        tableInfo.textContent = tableName;
    }
    
    // Hide table selection and show menu
    document.getElementById('table-selection-section').style.display = 'none';
    document.querySelector('.menu-section').style.display = 'block';
    
    showAlert(`เลือกโต๊ะ ${tableName} แล้ว`, 'success');
}

// Helper function to get category name by ID
function getCategoryNameById(categoryId) {
    console.log('getCategoryNameById called with categoryId:', categoryId);
    // ดึงข้อมูลจาก API แทนการ hardcode
    return fetch(`http://localhost:5000/api/menu/category/${categoryId}`)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                return data[0].name;
            } else {
                return '';
            }
        })
        .catch(error => {
            console.error('Error getting category name:', error);
            return '';
        });
}

// Load categories
function loadCategories() {
    console.log('loadCategories called');
    fetch('http://localhost:5000/api/menu/categories')
        .then(response => response.json())
        .then(response => {
            console.log('Categories response:', response);
            const categories = response.data || response;
            console.log('Categories array:', categories);
            
            // ตรวจสอบว่ามีหมวดหมู่หรือไม่
            if (!categories || categories.length === 0) {
                console.log('No categories found');
                return;
            }
            
            // สร้างแท็บหมวดหมู่
            const categoryTabs = document.getElementById('category-tabs');
            if (categoryTabs) {
                categoryTabs.innerHTML = '';
                
                // เพิ่มแท็บ "ทั้งหมด" เป็นตัวแรก
                const allTab = document.createElement('li');
                allTab.className = 'category-tab active';
                allTab.setAttribute('data-category-id', 'all');
                allTab.innerHTML = 'ทั้งหมด';
                allTab.addEventListener('click', function() {
                    // ลบคลาส active จากทุกแท็บ
                    document.querySelectorAll('.category-tab').forEach(tab => tab.classList.remove('active'));
                    // เพิ่มคลาส active ให้แท็บที่คลิก
                    this.classList.add('active');
                    // โหลดเมนูทั้งหมด
                    loadMenuByCategory('all');
                });
                categoryTabs.appendChild(allTab);
                
                // เพิ่มแท็บสำหรับแต่ละหมวดหมู่
                categories.forEach((category, index) => {
                    const tab = document.createElement('li');
                    tab.className = 'category-tab';
                    tab.setAttribute('data-category-id', category.category_id);
                    tab.innerHTML = category.name;
                    tab.style.animationDelay = `${index * 0.05}s`;
                    tab.addEventListener('click', function() {
                        // ลบคลาส active จากทุกแท็บ
                        document.querySelectorAll('.category-tab').forEach(tab => tab.classList.remove('active'));
                        // เพิ่มคลาส active ให้แท็บที่คลิก
                        this.classList.add('active');
                        // โหลดเมนูตามหมวดหมู่
                        loadMenuByCategory(category.category_id);
                    });
                    categoryTabs.appendChild(tab);
                });
            }
            
            // โหลดเมนูทั้งหมดโดยไม่กรองตามหมวดหมู่เป็นค่าเริ่มต้น
            loadMenuByCategory('all');
            
            console.log('Auto-loading all menu items');
        })
        .catch(error => {
            console.error('Error loading categories:', error);
            showAlert('เกิดข้อผิดพลาดในการโหลดหมวดหมู่', 'error');
        });
}

// Load menu by category
async function loadMenuByCategory(categoryId) {
    console.log('=== loadMenuByCategory called with categoryId:', categoryId);
    
    // ถ้า categoryId เป็น null จะโหลดสินค้าทั้งหมด
    const url = 'http://localhost:5000/api/menu/items';
    
    currentCategory = categoryId;
    
    // Clear search
    const searchInput = document.getElementById('menu-search');
    const clearButton = document.getElementById('clear-search');
    if (searchInput) searchInput.value = '';
    if (clearButton) clearButton.classList.add('d-none');
    
    console.log('Fetching menu items with URL:', url);
    try {
        const response = await fetch(url);
        console.log('Menu items response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const responseData = await response.json();
        console.log('Menu items response:', responseData);
        // ตรวจสอบโครงสร้างของ response
        let menuItems = [];
        
        if (responseData.success === true && responseData.data) {
            // กรณีที่ response มีโครงสร้าง { success: true, data: [...] }
            menuItems = responseData.data;
        } else if (Array.isArray(responseData)) {
            // กรณีที่ response เป็น array โดยตรงง
            menuItems = responseData;
        } else if (responseData.success === false) {
            // กรณีที่ API ส่ง success: false กลับมา
            console.error('API response not successful:', responseData);
            showAlert('ไม่สามารถโหลดเมนูได้', 'error');
        }
        
        console.log('Menu items array:', menuItems);
        console.log('Menu items length:', menuItems.length);
        allMenuItems = menuItems;
        
        // กรองเมนูตามหมวดหมู่ที่เลือก ยกเว้นกรณีเลือก 'ทั้งหมด'
        if (categoryId && categoryId !== 'all') {
            menuItems = menuItems.filter(item => item.category_id == categoryId);
            console.log('Filtered menu items by category:', menuItems.length);
        }
        
        await displayMenuItems(menuItems);
        
        // Hide empty state
        const emptyState = document.getElementById('empty-state');
        if (emptyState) emptyState.classList.add('d-none');
    } catch (error) {
        console.error('Error loading menu:', error);
        showAlert('เกิดข้อผิดพลาดในการโหลดเมนู', 'error');
        await displayMenuItems([]);
    }
}

// Display menu items

async function displayMenuItems(menuItems) {
    console.log('displayMenuItems called with', menuItems.length, 'items');
    
    // ตรวจสอบและแสดง menu-section ก่อน
    const menuSection = document.querySelector('.menu-section');
    if (menuSection) {
        menuSection.style.display = 'block';
    }
    
    // รอให้ DOM พร้อมและลองหา element อีกครั้งถ้าไม่เจอ
    let menuContent = document.getElementById('menu-content');
    
    if (!menuContent) {
        console.warn('menu-content element not found, checking if this page needs it...');
        // ตรวจสอบว่าอยู่ในหน้าที่ต้องการ menu-content หรือไม่
        const currentPage = window.location.pathname;
        if (currentPage.includes('admin') || currentPage.includes('dashboard')) {
            console.log('This page does not require menu-content element, skipping...');
            return;
        }
        
        // รอ 100ms แล้วลองอีกครั้ง
        await new Promise(resolve => setTimeout(resolve, 100));
        menuContent = document.getElementById('menu-content');
        
        if (!menuContent) {
            console.error('menu-content element still not found after waiting');
            return;
        }
    }
    
    menuContent.innerHTML = '';
    
    if (!menuItems || menuItems.length === 0) {
        console.log('No menu items to display');
        menuContent.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-utensils fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">ไม่มีเมนูในหมวดหมู่นี้</h5>
            </div>
        `;
        return;
    }
    

    
    const row = document.createElement('div');
    row.className = 'row';
    
    menuItems.forEach(item => {
        const col = document.createElement('div');
        col.className = 'col-lg-3 col-md-4 col-sm-6 col-12 mb-4';
        const imgSrc = item.image_url || '/frontend/images/placeholder-1x1.svg';
        

        
        col.innerHTML = `
            <div class="menu-item-card h-100" onclick="addToCart(${item.item_id}, '${item.name}', ${item.price})">
                <div class="position-relative menu-img-container">
                    <img src="${imgSrc}" 
                         class="card-img-top menu-img-1x1" 
                         alt="${item.name}"
                         style="aspect-ratio: 1/1; width: 100%; object-fit: cover; background: #f8f8f8; border-radius: 12px;">
                    <div class="position-absolute top-0 end-0 m-2">
                        <span class="badge bg-primary px-2 py-1 rounded-pill">
                            ฿${item.price.toLocaleString()}
                        </span>
                    </div>
                </div>
                <div class="card-body p-3">
                    <h6 class="card-title mb-2 fw-bold">${item.name}</h6>
                    <p class="card-text text-muted small mb-3">${item.description || 'ไม่มีรายละเอียด'}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="text-primary fw-bold fs-5">฿${item.price.toLocaleString()}</span>
                        <button class="btn btn-primary btn-sm px-3 rounded-pill" onclick="event.stopPropagation(); (async () => { await addToCart(${item.item_id}, '${item.name}', ${item.price}); })();">
                            <i class="fas fa-plus me-1"></i>
                            เพิ่ม
                        </button>
                    </div>
                </div>
            </div>
        `;
        row.appendChild(col);
    });
    
    menuContent.appendChild(row);
}

// Add item to cart
// Global variable to store current item being added
let currentItemToAdd = null;

async function addToCart(itemId, itemName, itemPrice) {
    console.log('=== addToCart called ===');
    console.log('Parameters:', { itemId, itemName, itemPrice });
    console.log('currentTable:', currentTable);
    console.log('allMenuItems length:', allMenuItems.length);
    
    if (!currentTable) {
        console.log('currentTable is null, showing alert');
        showAlert('กรุณาเลือกโต๊ะก่อน', 'warning');
        return;
    }
    
    // Find the menu item to check food_option_type
    const menuItem = allMenuItems.find(item => item.item_id === itemId);
    console.log('Found menuItem:', menuItem);
    console.log('allMenuItems sample:', allMenuItems.slice(0, 3));
    
    if (menuItem && menuItem.food_option_type && menuItem.food_option_type !== 'none') {
        console.log('Showing options modal for:', menuItem.food_option_type);
        // Show options modal
        await showMenuItemOptionsModal(itemId, itemName, itemPrice, menuItem.food_option_type, menuItem.image_url);
    } else {
        console.log('Adding directly to cart without options');
        // Add directly to cart without options
        addItemToCartDirectly(itemId, itemName, itemPrice);
    }
}

// Add menu item directly to order (bypass cart)
function addMenuItemDirectlyToOrder(itemId, itemName, itemPrice) {
    console.log('addMenuItemDirectlyToOrder called:', { itemId, itemName, itemPrice, currentTable });
    if (!currentTable) {
        console.log('currentTable is null, showing alert');
        showAlert('กรุณาเลือกโต๊ะก่อน', 'warning');
        return;
    }
    
    // Find the menu item to check food_option_type
    const menuItem = allMenuItems.find(item => item.item_id === itemId);
    
    if (menuItem && menuItem.food_option_type && menuItem.food_option_type !== 'none') {
        // Show options modal for direct order
        showMenuItemOptionsModalForDirectOrder(itemId, itemName, itemPrice, menuItem.food_option_type, menuItem.image_url);
    } else {
        // Add directly to order without options
        addItemDirectlyToOrder(itemId, itemName, itemPrice);
    }
}

async function showMenuItemOptionsModal(itemId, itemName, itemPrice, foodOptionType, imageUrl) {
    currentItemToAdd = {
        item_id: itemId,
        name: itemName,
        price: itemPrice,
        food_option_type: foodOptionType
    };
    
    // Update modal content
    document.getElementById('menuItemOptionsTitle').textContent = itemName;
    document.getElementById('menuItemOptionsName').textContent = itemName;
    document.getElementById('menuItemOptionsPrice').textContent = `฿${itemPrice.toLocaleString()}`;
    
    // Set image
    const imageElement = document.getElementById('menuItemOptionsImage');
    if (imageUrl) {
        imageElement.src = imageUrl;
        imageElement.style.display = 'block';
    } else {
        imageElement.style.display = 'none';
    }
    
    // Clear special request field - check if element exists first
    const customerRequestElement = document.getElementById('specialRequest');
    if (customerRequestElement) {
        customerRequestElement.value = '';
    }
    
    // Clear all previously selected options to prevent price calculation issues
    const foodOptionsContainer = document.getElementById('foodOptionsContainer');
    if (foodOptionsContainer) {
        // Clear all checkboxes and radio buttons
        const checkboxes = foodOptionsContainer.querySelectorAll('input[type="checkbox"]');
        const radioButtons = foodOptionsContainer.querySelectorAll('input[type="radio"]');
        
        checkboxes.forEach(checkbox => checkbox.checked = false);
        radioButtons.forEach(radio => radio.checked = false);
        
        console.log('Cleared previous options: checkboxes =', checkboxes.length, 'radios =', radioButtons.length);
    }
    
    // Show modal first
    const modal = new bootstrap.Modal(document.getElementById('menuItemOptionsModal'));
    
    // Add event listener for when modal is fully shown
    const modalElement = document.getElementById('menuItemOptionsModal');
    modalElement.addEventListener('shown.bs.modal', async function modalShownHandler() {
        // Remove this event listener after it's called once
        modalElement.removeEventListener('shown.bs.modal', modalShownHandler);
        
        await setupModalElements(foodOptionType);
        // Initialize total price display
        initializeTotalPrice();
    });
    
    modal.show();
}

async function setupModalElements(foodOptionType) {
    const foodOptionsContainer = document.getElementById('foodOptionsContainer');
    const spiceOptions = document.getElementById('spiceOptions');
    const sweetnessOptions = document.getElementById('sweetnessOptions');
    const specialOptions = document.getElementById('specialOptions');
    
    console.log('setupModalElements called with foodOptionType:', foodOptionType);
    console.log('foodOptionsContainer:', foodOptionsContainer);
    console.log('spiceOptions:', spiceOptions);
    console.log('sweetnessOptions:', sweetnessOptions);
    console.log('specialOptions:', specialOptions);
    
    // Check if elements exist before using them
    if (!foodOptionsContainer || !spiceOptions || !sweetnessOptions) {
        console.error('Required modal elements not found:');
        console.error('foodOptionsContainer:', foodOptionsContainer);
        console.error('spiceOptions:', spiceOptions);
        console.error('sweetnessOptions:', sweetnessOptions);
        console.error('specialOptions:', specialOptions);
        
        // Try again after a short delay
        setTimeout(async () => {
            console.log('Retrying setupModalElements...');
            await setupModalElements(foodOptionType);
        }, 100);
        return;
    }
    
    // specialOptions might be null, but we can still proceed
    if (!specialOptions) {
        console.warn('specialOptions element not found, but continuing with other options');
    }
    
    // Continue with the rest of the function
    await setupModalOptions(foodOptionType, spiceOptions, sweetnessOptions, specialOptions);
}

// Function to load dynamic options from API
async function loadDynamicOptions(optionType, container, inputName, buttonClass) {
    try {
        const response = await fetch(`/api/option-values?option_type=${optionType}`);
        const result = await response.json();
        
        if (result.success && result.data) {
            // Clear existing content
            const existingContent = container.querySelector('.row');
            if (existingContent) {
                existingContent.innerHTML = '';
            } else {
                // Create the structure if it doesn't exist
            let title = '';
            let selectionText = '';
            if (optionType === 'spice') {
                title = 'ระดับความเผ็ด';
                selectionText = '(เลือกได้อย่างเดียว)';
            } else if (optionType === 'sweet') {
                title = 'ระดับความหวาน';
                selectionText = '(เลือกได้ 1 รายการ)';
            } else if (optionType === 'addon') {
                title = 'ตัวเลือกพิเศษ';
                selectionText = '(เลือกได้หลายตัวเลือก)';
            }
            
            container.innerHTML = `
                <h6 class="mb-3">${title} ${selectionText}</h6>
                <div class="row g-2"></div>
            `;
            }
            
            const rowContainer = container.querySelector('.row');
            let defaultSet = false;
            
            // Create options from API data
            result.data.forEach((option, index) => {
                const colDiv = document.createElement('div');
                // Use col-6 for addon options, col-4 for others
                colDiv.className = optionType === 'addon' ? 'col-6' : 'col-4';
                
                const inputId = `${optionType}${index}`;
                const priceText = option.additional_price > 0 ? ` (+${option.additional_price}฿)` : '';
                
                // Use radio for spice and sweet options, checkbox for others
                const inputType = (optionType === 'spice' || optionType === 'sweet') ? 'radio' : 'checkbox';
                
                colDiv.innerHTML = `
                    <input type="${inputType}" class="btn-check" name="${inputName}" id="${inputId}" value="${option.name}" data-price="${option.additional_price}">
                    <label class="btn ${buttonClass} w-100" for="${inputId}">${option.name}${priceText}</label>
                `;
                
                rowContainer.appendChild(colDiv);
                
                // Set default selection
                if (option.is_default && !defaultSet) {
                    document.getElementById(inputId).checked = true;
                    defaultSet = true;
                }
                
                // For addon options, set "ไม่เพิ่ม" as default if no default is set
            if (optionType === 'addon' && option.name === 'ไม่เพิ่ม' && !defaultSet) {
                document.getElementById(inputId).checked = true;
                defaultSet = true;
            }
        });
        
        // Add event listeners to update total price when options change
        const inputs = container.querySelectorAll('input[type="checkbox"], input[type="radio"]');
        inputs.forEach(input => {
            input.addEventListener('change', updateTotalPrice);
        });
            
            // Add event listeners for special options logic
            if (optionType === 'addon') {
                setupSpecialOptionsLogic(rowContainer);
            }
        }
    } catch (error) {
        console.error('Error loading dynamic options:', error);
        // Fallback to existing hardcoded options if API fails
    }
}

// Function to handle special options logic
function setupSpecialOptionsLogic(container) {
    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    const noAddCheckbox = Array.from(checkboxes).find(cb => cb.value === 'ไม่เพิ่ม');
    const otherCheckboxes = Array.from(checkboxes).filter(cb => cb.value !== 'ไม่เพิ่ม');
    
    if (noAddCheckbox) {
        // Set "ไม่เพิ่ม" as default if nothing is selected
        const ensureSelection = () => {
            const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
            if (!anyChecked) {
                noAddCheckbox.checked = true;
                updateTotalPrice();
            }
        };
        
        // When "ไม่เพิ่ม" is clicked
        noAddCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // Uncheck all other options
                otherCheckboxes.forEach(cb => {
                    cb.checked = false;
                });
                updateTotalPrice();
            } else {
                // Prevent unchecking "ไม่เพิ่ม" if no other options are selected
                setTimeout(ensureSelection, 10);
            }
        });
        
        // When any other option is clicked
        otherCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                if (this.checked && noAddCheckbox.checked) {
                    // Uncheck "ไม่เพิ่ม" when selecting other options
                    noAddCheckbox.checked = false;
                } else if (!this.checked) {
                    // Check if we need to re-select "ไม่เพิ่ม"
                    setTimeout(ensureSelection, 10);
                }
                updateTotalPrice();
            });
        });
        
        // Initialize with "ไม่เพิ่ม" selected if nothing else is selected
        ensureSelection();
    }
}

async function setupModalOptions(foodOptionType, spiceOptions, sweetnessOptions, specialOptions) {
    console.log('setupModalOptions called with foodOptionType:', foodOptionType);
    
    const foodOptionsContainer = document.getElementById('foodOptionsContainer');
    
    // Hide all options first
    spiceOptions.classList.add('d-none');
    sweetnessOptions.classList.add('d-none');
    if (specialOptions) {
        specialOptions.classList.add('d-none');
    }
    
    // Check if any options should be shown
    let hasOptions = false;
    
    if (foodOptionType && foodOptionType.includes('spice')) {
        console.log('Spice options detected, loading from API');
        await loadDynamicOptions('spice', spiceOptions, 'spiceLevel', 'btn-outline-warning');
        foodOptionsContainer.classList.remove('d-none');
        spiceOptions.classList.remove('d-none');
        hasOptions = true;
    }
    
    if (foodOptionType && foodOptionType.includes('sweet')) {
        console.log('Sweet options detected, loading from API');
        await loadDynamicOptions('sweet', sweetnessOptions, 'sweetnessLevel', 'btn-outline-info');
        foodOptionsContainer.classList.remove('d-none');
        sweetnessOptions.classList.remove('d-none');
        hasOptions = true;
    }
    
    if (foodOptionType && foodOptionType.includes('special')) {
        console.log('Special options detected, loading from API');
        
        // Get specialOptions element (try again if it was null)
        let currentSpecialOptions = specialOptions;
        if (!currentSpecialOptions) {
            console.log('specialOptions was null, trying to find it again...');
            currentSpecialOptions = document.getElementById('specialOptions');
            console.log('Found specialOptions on retry:', currentSpecialOptions);
        }
        
        if (currentSpecialOptions) {
            console.log('Loading special options from API');
            await loadDynamicOptions('addon', currentSpecialOptions, 'specialLevel', 'btn-outline-success');
            foodOptionsContainer.classList.remove('d-none');
            currentSpecialOptions.classList.remove('d-none');
            hasOptions = true;
        } else {
            console.error('specialOptions element still not found!');
        }
    } else {
        console.log('No special options detected for foodOptionType:', foodOptionType);
    }
    
    if (!hasOptions) {
        foodOptionsContainer.classList.add('d-none');
    }
    
    console.log('setupModalOptions completed. hasOptions:', hasOptions);
}

function confirmAddToCart() {
    if (!currentItemToAdd) return;
    
    let selectedOptions = [];
    
    // Calculate total price including additional charges
    let totalPrice = currentItemToAdd.price;
    const selectedInputs = document.querySelectorAll('#foodOptionsContainer input:checked');
    selectedInputs.forEach(input => {
        const additionalPrice = parseFloat(input.dataset.price) || 0;
        totalPrice += additionalPrice;
    });
    
    // Check for spice options
    if (currentItemToAdd.food_option_type && currentItemToAdd.food_option_type.includes('spice')) {
        const selectedSpices = document.querySelectorAll('input[name="spiceLevel"]:checked');
        if (selectedSpices.length > 0) {
            selectedOptions.push(Array.from(selectedSpices).map(input => input.value).join(', '));
        } else {
            selectedOptions.push('เผ็ดปกติ');
        }
    }
    
    // Check for sweetness options
    if (currentItemToAdd.food_option_type && currentItemToAdd.food_option_type.includes('sweet')) {
        const selectedSweets = document.querySelectorAll('input[name="sweetnessLevel"]:checked');
        if (selectedSweets.length > 0) {
            selectedOptions.push(Array.from(selectedSweets).map(input => input.value).join(', '));
        } else {
            selectedOptions.push('หวานปกติ');
        }
    }
    
    // Check for special options
    if (currentItemToAdd.food_option_type && currentItemToAdd.food_option_type.includes('special')) {
        const selectedSpecials = document.querySelectorAll('input[name="specialLevel"]:checked');
        if (selectedSpecials.length > 0) {
            selectedOptions.push(Array.from(selectedSpecials).map(input => input.value).join(', '));
        }
    }
    
    const selectedOption = selectedOptions.length > 0 ? selectedOptions.join(' | ') : null;
    
    // Get note from textarea
    const noteElement = document.getElementById('specialRequest');
    const note = noteElement ? noteElement.value.trim() : '';
    
    // Check if this is for direct order or cart
    if (currentItemToAdd.direct_order) {
        // Add directly to order
        addItemDirectlyToOrder(
            currentItemToAdd.item_id, 
            currentItemToAdd.name, 
            totalPrice, 
            selectedOption,
            note
        );
    } else {
        // Add to cart with selected option and note
        addItemToCartDirectly(
            currentItemToAdd.item_id, 
            currentItemToAdd.name, 
            totalPrice, 
            selectedOption,
            note
        );
    }
    
    // Hide modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('menuItemOptionsModal'));
    modal.hide();
    
    // Clear note field for next use
    if (noteElement) {
        noteElement.value = '';
    }
    
    // Reset confirm button text
    const confirmButton = document.querySelector('#menuItemOptionsModal .btn-primary');
    if (confirmButton) {
        confirmButton.textContent = 'เพิ่มลงตะกร้า';
    }
    
    currentItemToAdd = null;
}

// Function to calculate and update total price
function updateTotalPrice() {
    if (!currentItemToAdd) {
        console.log('currentItemToAdd is not set, cannot update total price');
        return;
    }
    
    let totalPrice = currentItemToAdd.price;
    
    // Add prices from selected options
    const selectedInputs = document.querySelectorAll('#foodOptionsContainer input:checked');
    selectedInputs.forEach(input => {
        const additionalPrice = parseFloat(input.dataset.price) || 0;
        totalPrice += additionalPrice;
    });
    
    // Update the display
    const totalPriceDisplay = document.getElementById('totalPriceDisplay');
    if (totalPriceDisplay) {
        totalPriceDisplay.textContent = `ยอดรวม: ฿${totalPrice.toLocaleString()}`;
        console.log('Updated total price display to:', totalPrice);
    } else {
        console.log('totalPriceDisplay element not found');
    }
}

// Function to initialize total price display when modal opens
function initializeTotalPrice() {
    // Wait a moment for the modal to be fully rendered
    setTimeout(() => {
        updateTotalPrice();
    }, 100);
}

function addItemToCartDirectly(itemId, itemName, itemPrice, selectedOption = null, note = '') {
    console.log('DEBUG: addItemToCartDirectly called with:', { itemId, itemName, itemPrice, selectedOption, note });
    console.log('DEBUG: cart before adding:', cart);
    
    // For items with the same ID, option, and note, we'll increase quantity
    // Otherwise, we'll add a new item to the cart
    const existingItem = cart.find(item => 
        item.item_id === itemId && 
        item.selected_option === selectedOption &&
        item.note === note
    );
    
    console.log('DEBUG: existingItem found:', existingItem);
    
    if (existingItem) {
        console.log('DEBUG: Increasing quantity for existing item');
        existingItem.quantity += 1;
    } else {
        console.log('DEBUG: Adding new item to cart');
        const cartItem = {
            item_id: itemId,
            name: itemName,
            price: itemPrice,
            quantity: 1,
            note: note
        };
        
        if (selectedOption) {
            cartItem.selected_option = selectedOption;
            cartItem.display_name = `${itemName} <span style="color: #d2691e;">(${selectedOption})</span>`;
        } else {
            cartItem.display_name = itemName;
        }
        
        console.log('DEBUG: cartItem to be added:', cartItem);
        cart.push(cartItem);
        console.log('DEBUG: cart after push:', cart);
    }
    
    console.log('DEBUG: About to call updateCartDisplay');
    updateCartDisplay();
    const displayName = selectedOption ? `${itemName} (${selectedOption})` : itemName;
    showAlert(`เพิ่ม ${displayName} ลงในตะกร้าแล้ว`, 'success');
    console.log('DEBUG: addItemToCartDirectly completed');
}

// Add item directly to order (bypass cart completely)
function addItemDirectlyToOrder(itemId, itemName, itemPrice, selectedOption = null, note = '') {
    const sessionId = getQueryParam('session');
    const orderData = {
        table_id: currentTable.id,
        items: [{
            item_id: itemId,
            quantity: 1,
            price: itemPrice // ใช้ราคารวมที่คำนวณแล้วจาก frontend
        }]
    };
    
    // Add selected option if exists
    if (selectedOption) {
        orderData.items[0].selected_option = selectedOption;
    }
    
    // Add note if exists
    if (note) {
        orderData.items[0].note = note;
    }
    
    if (sessionId) {
        orderData.session_id = sessionId;
    }
    
    fetch('http://localhost:5000/api/orders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            const displayName = selectedOption ? `${itemName} (${selectedOption})` : itemName;
            showAlert(`เพิ่ม ${displayName} เข้าสู่รายการสั่งอาหารแล้ว!`, 'success');
            fetchOrderStatus(currentTable.id); // โหลดสถานะโต๊ะล่าสุดหลังสั่งอาหาร
            loadTables(); // Reload tables to update status
        } else {
            showAlert(result.message || 'เกิดข้อผิดพลาดในการสั่งอาหาร', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding item to order:', error);
        showAlert('เกิดข้อผิดพลาดในการสั่งอาหาร', 'error');
    });
}

// Show options modal for direct order
function showMenuItemOptionsModalForDirectOrder(itemId, itemName, itemPrice, foodOptionType, imageUrl) {
    currentItemToAdd = {
        item_id: itemId,
        name: itemName,
        price: itemPrice,
        food_option_type: foodOptionType,
        direct_order: true // Flag to indicate this should go directly to order
    };
    
    // Update modal content
    document.getElementById('menuItemOptionsTitle').textContent = itemName;
    document.getElementById('menuItemOptionsName').textContent = itemName;
    document.getElementById('menuItemOptionsPrice').textContent = `฿${itemPrice.toLocaleString()}`;
    
    // Set image
    const imageElement = document.getElementById('menuItemOptionsImage');
    if (imageUrl) {
        imageElement.src = imageUrl;
        imageElement.style.display = 'block';
    } else {
        imageElement.style.display = 'none';
    }
    
    // Clear special request field - check if element exists first
    const customerRequestElement = document.getElementById('specialRequest');
    if (customerRequestElement) {
        customerRequestElement.value = '';
    }
    
    // Clear all previously selected options to prevent price calculation issues
    const foodOptionsContainer = document.getElementById('foodOptionsContainer');
    if (foodOptionsContainer) {
        // Clear all checkboxes and radio buttons
        const checkboxes = foodOptionsContainer.querySelectorAll('input[type="checkbox"]');
        const radioButtons = foodOptionsContainer.querySelectorAll('input[type="radio"]');
        
        checkboxes.forEach(checkbox => checkbox.checked = false);
        radioButtons.forEach(radio => radio.checked = false);
        
        console.log('Cleared previous options for direct order: checkboxes =', checkboxes.length, 'radios =', radioButtons.length);
    }
    
    // Show the modal first
    const modal = new bootstrap.Modal(document.getElementById('menuItemOptionsModal'));
    modal.show();
    
    // Wait a moment for modal to be ready, then get elements
    setTimeout(async () => {
        // Show/hide appropriate options
        const foodOptionsContainer = document.getElementById('foodOptionsContainer');
        const spiceOptions = document.getElementById('spiceOptions');
        const sweetnessOptions = document.getElementById('sweetnessOptions');
        const specialOptions = document.getElementById('specialOptions');
        
        // Check if elements exist before using them
        if (!foodOptionsContainer || !spiceOptions || !sweetnessOptions || !specialOptions) {
            console.error('Required modal elements not found in direct order function');
            return;
        }
        
        // Continue with the rest of the function
        await setupModalOptions(foodOptionType, spiceOptions, sweetnessOptions, specialOptions);
        // Initialize total price display
        initializeTotalPrice();
    }, 100);
}

// Update cart display
function updateCartDisplay() {
    const cartItems = document.getElementById('cart-items');
    const totalAmount = document.getElementById('total-amount');
    const confirmBtn = document.getElementById('confirm-order-btn');
    const cartBadge = document.querySelector('.cart-badge');
    const cartSummary = document.getElementById('cart-summary');
    const emptyCart = document.getElementById('empty-cart');
    
    // Calculate totals
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    // Update cart badge with animation
    if (cartBadge) {
        const previousCount = parseInt(cartBadge.textContent) || 0;
        
        if (totalItems > 0) {
            cartBadge.textContent = totalItems;
            cartBadge.style.display = 'flex';
            
            // Add bounce animation if count increased
            if (totalItems > previousCount) {
                cartBadge.classList.remove('animate-add');
                // Force reflow
                cartBadge.offsetHeight;
                cartBadge.classList.add('animate-add');
                
                // Remove animation class after animation completes
                setTimeout(() => {
                    cartBadge.classList.remove('animate-add');
                }, 600);
            }
        } else {
            cartBadge.style.display = 'none';
        }
    }
    
    // Update cart summary
    if (cartSummary) {
        if (totalItems > 0) {
            cartSummary.textContent = `${totalItems} รายการ • ฿${totalPrice.toLocaleString()}`;
        } else {
            cartSummary.textContent = 'ยังไม่มีรายการ';
        }
    }
    
    // Update total amount
    if (totalAmount) {
        totalAmount.textContent = `฿${totalPrice.toLocaleString()}`;
    }
    
    // Enable/disable confirm button
    if (confirmBtn) {
        console.log('DEBUG: updateCartDisplay - cart.length:', cart.length);
        console.log('DEBUG: updateCartDisplay - cart contents:', cart);
        console.log('DEBUG: updateCartDisplay - confirmBtn.disabled before:', confirmBtn.disabled);
        confirmBtn.disabled = cart.length === 0;
        console.log('DEBUG: updateCartDisplay - confirmBtn.disabled after:', confirmBtn.disabled);
    }
    
    // Show/hide empty cart state
    if (emptyCart && cartItems) {
        if (cart.length === 0) {
            emptyCart.classList.remove('d-none');
            cartItems.innerHTML = '';
        } else {
            emptyCart.classList.add('d-none');
            renderCartItems();
        }
    }
}

// Render cart items
function renderCartItems() {
    const cartItems = document.getElementById('cart-items');
    
    if (!cartItems) {
        console.error('cart-items element not found');
        return;
    }
    
    cartItems.innerHTML = '';
    
    cart.forEach((item, index) => {
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        const displayName = item.display_name || item.name;
        
        // Prepare special options and note display if exists
        let specialOptionsText = '';
        let noteDisplay = '';
        
        if (item.note) {
            // Check if note contains both special options and notes (separated by ' | ')
            if (item.note.includes(' | ')) {
                const parts = item.note.split(' | ');
                if (parts[0] && parts[0].trim()) {
                    // Show special options inline with menu name in dark orange text
                    specialOptionsText = ` <span class="small" style="color: #d2691e;">${parts[0].trim()}</span>`;
                }
                if (parts[1] && parts[1].trim()) {
                    noteDisplay = `<div class="text-danger small mb-1">
                        หมายเหตุ: ${parts[1].trim()}
                    </div>`;
                }
            } else {
                // If no separator, treat as note only
                noteDisplay = `<div class="text-danger small mb-1">
                    หมายเหตุ: ${item.note}
                </div>`;
            }
        }
        
        let cartItemHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div class="flex-grow-1">
                    <h6 class="mb-1 fw-bold">${displayName}${specialOptionsText}</h6>
                    <p class="text-muted small mb-0">฿${item.price.toLocaleString()} × ${item.quantity}</p>
                    ${noteDisplay}
                </div>
                <div class="text-end">
                    <div class="fw-bold text-primary">฿${(item.price * item.quantity).toLocaleString()}</div>
                </div>
            </div>
            <div class="d-flex justify-content-between align-items-center">
                <div class="quantity-controls">
                    <button class="quantity-btn" onclick="updateQuantityByIndex(${index}, -1)">
                        <i class="fas fa-minus"></i>
                    </button>
                    <span class="quantity-display">${item.quantity}</span>
                    <button class="quantity-btn" onclick="updateQuantityByIndex(${index}, 1)">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
                <button class="btn btn-outline-danger btn-sm" onclick="removeFromCartByIndex(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        cartItem.innerHTML = cartItemHTML;
        cartItems.appendChild(cartItem);
    });
}

// Update quantity by index
function updateQuantityByIndex(index, change) {
    if (index >= 0 && index < cart.length) {
        cart[index].quantity += change;
        if (cart[index].quantity <= 0) {
            removeFromCartByIndex(index);
        } else {
            updateCartDisplay();
        }
    }
}

// Remove from cart by index
function removeFromCartByIndex(index) {
    if (index >= 0 && index < cart.length) {
        cart.splice(index, 1);
        updateCartDisplay();
        showAlert('ลบรายการออกจากตะกร้าแล้ว', 'info');
    }
}

// Legacy functions for backward compatibility
function updateQuantity(itemId, change) {
    const item = cart.find(item => item.item_id === itemId);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(itemId);
        } else {
            updateCartDisplay();
        }
    }
}

function removeFromCart(itemId) {
    cart = cart.filter(item => item.item_id !== itemId);
    updateCartDisplay();
    showAlert('ลบรายการออกจากตะกร้าแล้ว', 'info');
}

// Confirm order
function confirmOrder() {
    if (!currentTable || cart.length === 0) {
        showAlert('กรุณาเลือกโต๊ะและเพิ่มรายการอาหาร', 'warning');
        return;
    }
    
    // แสดง loading spinner
    const confirmBtn = document.querySelector('[onclick="confirmOrder()"]');
    const originalText = confirmBtn ? confirmBtn.innerHTML : '';
    if (confirmBtn) {
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>กำลังส่งคำสั่ง...';
        confirmBtn.disabled = true;
    }
    
    const sessionId = getQueryParam('session');
    const orderData = {
        table_id: currentTable.id,
        items: cart.map(item => {
            const orderItem = {
                item_id: item.item_id,
                quantity: item.quantity,
                price: item.price // ใช้ราคารวมที่คำนวณแล้วจาก frontend
            };
            
            if (item.selected_option) {
                orderItem.selected_option = item.selected_option;
            }
            
            if (item.note) {
                orderItem.note = item.note;
            }
            
            return orderItem;
        })
    };
    if (sessionId) {
        orderData.session_id = sessionId;
    }
    
    console.log('[DEBUG] confirmOrder: Sending order data:', orderData);
    console.log('[DEBUG] confirmOrder: Cart contents:', cart);
    console.log('[DEBUG] confirmOrder: Current table:', currentTable);
    
    // สร้าง AbortController สำหรับ timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
        controller.abort();
    }, 10000); // 10 วินาที timeout
    
    fetch('http://localhost:5000/api/orders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData),
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId);
        console.log('[DEBUG] confirmOrder: Response status:', response.status);
        if (!response.ok) {
            return response.text().then(text => {
                console.error('[DEBUG] confirmOrder: Error response text:', text);
                throw new Error(`HTTP ${response.status}: ${text}`);
            });
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            showAlert('✅ สั่งอาหารสำเร็จ!', 'success');
            
            // ส่งการแจ้งเตือนออเดอร์ใหม่ไปยัง admin
            sendOrderRequest();
            
            cart = [];
            updateCartDisplay();
            fetchOrderStatus(currentTable.id); // โหลดสถานะโต๊ะล่าสุดหลังสั่งอาหาร
            // Close cart sidebar
            const cartSidebar = bootstrap.Offcanvas.getInstance(document.getElementById('cartSidebar'));
            if (cartSidebar) {
                cartSidebar.hide();
            }
            // Reload tables to update status
            loadTables();
        } else {
            console.error('[DEBUG] confirmOrder: Server returned error:', result);
            showAlert(`❌ ${result.message || 'เกิดข้อผิดพลาดในการสั่งอาหาร'}`, 'error');
        }
    })
    .catch(error => {
        clearTimeout(timeoutId);
        console.error('[DEBUG] confirmOrder: Fetch error:', error);
        
        if (error.name === 'AbortError') {
            showAlert('⚠️ การดำเนินการใช้เวลานานเกินไป กรุณาลองใหม่อีกครั้ง', 'warning');
        } else {
            showAlert(`❌ เกิดข้อผิดพลาดในการสั่งอาหาร: ${error.message}`, 'error');
        }
    })
    .finally(() => {
        // คืนค่าปุ่มเป็นปกติ
        if (confirmBtn) {
            confirmBtn.innerHTML = originalText;
            confirmBtn.disabled = false;
        }
    });
}

// Request bill
function updateBillButton() {
    const billBtn = document.getElementById('request-bill-btn');
    const editBtn = document.getElementById('edit-menu-btn');
    
    if (!billBtn) return;
    
    // แสดงปุ่มเช็คบิลเมื่อสถานะโต๊ะเป็น 'served' หรือ 'needs_checkout'
    if (orderStatus === 'served' || orderStatus === 'needs_checkout') {
        billBtn.classList.remove('d-none');
        // แสดงปุ่มแก้ไขเมนูเมื่อมีออเดอร์แล้ว
        if (editBtn) {
            editBtn.classList.remove('d-none');
        }
    } else {
        billBtn.classList.add('d-none');
        // ซ่อนปุ่มแก้ไขเมนูเมื่อยังไม่มีออเดอร์
        if (editBtn) {
            editBtn.classList.add('d-none');
        }
    }
}

// Fetch order status for table
function fetchOrderStatus(tableId) {
    if (!tableId) return;
    
    const sessionId = getQueryParam('session');
    
    // ตรวจสอบสถานะเซสชั่นก่อน
    if (sessionId) {
        checkSessionStatus(tableId, sessionId);
    }
    
    let url = `http://localhost:5000/api/tables/${tableId}/order-summary`;
    if (sessionId) {
        url += `?session_id=${sessionId}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // อัพเดทสถานะโต๊ะ
                if (currentTable && data.data) {
                    currentTable.status = data.data.status;
                }
                
                // อัพเดทสถานะออเดอร์
                if (data.data && data.data.orders && data.data.orders.length > 0) {
                    // ใช้สถานะของออเดอร์ล่าสุด
                    const latestOrder = data.data.orders[data.data.orders.length - 1];
                    orderStatus = latestOrder && latestOrder.status ? latestOrder.status : null;
                } else {
                    orderStatus = null;
                }
                
                // อัพเดทปุ่มเช็คบิล
                updateBillButton();
            }
        })
        .catch(error => {
            console.error('Error fetching order status:', error);
        });
}

// ฟังก์ชันตรวจสอบสถานะเซสชั่น
function checkSessionStatus(tableId, sessionId) {
    fetch(`http://localhost:5000/api/tables/${tableId}/session/check?session_id=${sessionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && !data.session_valid) {
                // เซสชั่นไม่ถูกต้อง เปลี่ยนเส้นทางไปยังหน้า error
                let errorMessage = 'เซสชั่นของคุณได้ถูกปิดแล้ว';
                let errorTitle = 'เซสชั่นหมดอายุ';
                
                if (data.table_status === 'checkout') {
                    errorMessage = 'QR Code นี้ไม่สามารถใช้งานได้แล้ว เนื่องจากโต๊ะได้ทำการเช็คบิลแล้ว กรุณาติดต่อพนักงานเพื่อขอ QR Code ใหม่';
                    errorTitle = 'QR Code หมดอายุ';
                } else {
                    errorMessage = 'เซสชั่นของคุณได้ถูกปิดโดยร้าน กรุณาติดต่อพนักงานเพื่อขอ QR Code ใหม่';
                }
                
                // เปลี่ยนเส้นทางไปยังหน้า error
                window.location.href = `/error?title=${encodeURIComponent(errorTitle)}&message=${encodeURIComponent(errorMessage)}`;
            } else if (data.success && data.table_status === 'waiting_payment') {
                // โต๊ะอยู่ในสถานะรอชำระเงิน แสดงหน้ารอเช็คบิล
                showWaitingForCheckoutState();
            }
        })
        .catch(error => {
            console.error('Error checking session status:', error);
        });
}
// Edit menu function
function editMenu() {
    if (!currentTable || !currentTable.id) {
        showAlert('กรุณาเลือกโต๊ะก่อน', 'error');
        return;
    }
    
    // แสดง modal ประวัติการสั่งอาหารเพื่อให้แก้ไข
    showOrderHistory();
    
    // เปลี่ยนข้อความในปุ่มเช็คบิลเป็น "บันทึกการแก้ไข"
    const checkBillBtn = document.getElementById('checkBillBtn');
    if (checkBillBtn) {
        checkBillBtn.innerHTML = '<i class="fas fa-save me-2"></i>บันทึกการแก้ไข';
        checkBillBtn.onclick = function() {
            saveMenuChanges();
        };
    }
    
    showAlert('คุณสามารถแก้ไขรายการอาหารได้ในหน้าต่างที่เปิดขึ้น', 'info');
}

// Save menu changes
function saveMenuChanges() {
    showAlert('บันทึกการแก้ไขเรียบร้อยแล้ว', 'success');
    
    // ปิด modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('orderHistoryModal'));
    if (modal) {
        modal.hide();
    }
    
    // เปลี่ยนข้อความในปุ่มกลับเป็นเดิม
    const checkBillBtn = document.getElementById('checkBillBtn');
    if (checkBillBtn) {
        checkBillBtn.innerHTML = '<i class="fas fa-receipt me-2"></i>เช็คบิล';
        checkBillBtn.onclick = function() {
            requestCheckout();
        };
    }
    
    // รีเฟรชข้อมูลออเดอร์
    if (currentTable && currentTable.id) {
        fetchOrderStatus(currentTable.id);
    }
}

function requestBill() {
    if (!currentTable) {
        showAlert('กรุณาเลือกโต๊ะก่อน', 'warning');
        return;
    }
    
    fetch(`http://localhost:5000/api/orders/bill/${currentTable.id}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('ขอเช็คบิลสำเร็จ!', 'success');
        } else {
            showAlert(result.message || 'เกิดข้อผิดพลาดในการขอเช็คบิล', 'error');
        }
    })
    .catch(error => {
        console.error('Error requesting bill:', error);
        showAlert('เกิดข้อผิดพลาดในการขอเช็คบิล', 'error');
    });
}

// Show alert - เปลี่ยนเป็น modal
function showAlert(message, type = 'info') {
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
        <div class="modal fade" id="orderNotificationModal" tabindex="-1" aria-labelledby="orderNotificationModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header ${headerClass}">
                        <h5 class="modal-title" id="orderNotificationModalLabel">
                            <i class="${iconClass.split(' ')[0]} ${iconClass.split(' ')[1]} me-2"></i>${title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-3">
                            <i class="${iconClass}" style="font-size: 3rem;"></i>
                        </div>
                        <h4>${message}</h4>
                        <p class="text-muted">หน้าต่างนี้จะปิดอัตโนมัติใน <span id="orderNotificationCountdown">3</span> วินาที</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // ลบ modal เก่า (ถ้ามี)
    const existingModal = document.getElementById('orderNotificationModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // เพิ่ม modal เข้าไปใน body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('orderNotificationModal'));
    modal.show();
    
    // นับถอยหลัง 3 วินาที
    let countdown = 3;
    const countdownElement = document.getElementById('orderNotificationCountdown');
    
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
                const modalElement = document.getElementById('orderNotificationModal');
                if (modalElement) {
                    modalElement.remove();
                }
            }, 300);
        }
    }, 1000);
}

// Reset to table selection
function resetToTableSelection() {
    currentTable = null;
    cart = [];
    updateCartDisplay();
    
    // Show table selection and hide menu
    document.getElementById('table-selection-section').style.display = 'block';
    document.querySelector('.category-section').style.display = 'none';
    document.querySelector('.menu-section').style.display = 'none';
    
    // Update navbar
    const tableInfo = document.getElementById('table-info');
    if (tableInfo) {
        tableInfo.innerHTML = '';
    }
    
    // Close cart sidebar if open
    const cartSidebar = bootstrap.Offcanvas.getInstance(document.getElementById('cartSidebar'));
    if (cartSidebar) {
        cartSidebar.hide();
    }
}
// ...
// แสดง modal ประวัติการสั่งอาหาร
function showOrderHistory() {
    if (!currentTable || !currentTable.id) {
        showAlert('กรุณาเลือกโต๊ะก่อน', 'error');
        return;
    }
    fetchOrderHistory(currentTable.id);
    const modal = new bootstrap.Modal(document.getElementById('orderHistoryModal'));
    modal.show();
}

// ดึงประวัติการสั่งอาหารของโต๊ะ
function fetchOrderHistory(tableId) {
    const sessionId = getQueryParam('session');
    let url = `http://localhost:5000/api/tables/${tableId}/orders`;
    if (sessionId) {
        url += `?session_id=${sessionId}`;
    }
    fetch(url)
        .then(response => response.json())
        .then(data => {
            renderOrderHistory(data);
        })
        .catch(error => {
            console.error('Error fetching order history:', error);
            document.getElementById('order-history-list').innerHTML = '<div class="text-danger">เกิดข้อผิดพลาดในการโหลดประวัติการสั่งอาหาร</div>';
        });
}

// แสดงผลประวัติการสั่งอาหาร
function renderOrderHistory(data) {
    const container = document.getElementById('order-history-list');
    
    if (!container) {
        console.error('order-history-list element not found');
        return;
    }
    
    // ตรวจสอบว่ามีข้อมูลหรือไม่
    if (!data || !data.success || !data.data || !data.data.orders || data.data.orders.length === 0) {
        // ถ้าเป็นรูปแบบเก่า
        if (data && data.menu_items && data.menu_items.length > 0) {
            // แสดงในรูปแบบเก่า
            let html = '<div class="order-history-item">';
            
            // แสดงรายการอาหาร
            data.menu_items.forEach(item => {
                html += `
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <strong>${item.name}</strong>
                            ${item.customer_request ? `<br><small class="text-muted">หมายเหตุ: ${item.customer_request}</small>` : ''}
                        </div>
                        <div class="text-end">
                            <div>จำนวน: ${item.quantity}</div>
                            <div class="text-primary">฿${item.total_price.toLocaleString()}</div>
                        </div>
                    </div>
                `;
            });
            
            // แสดงยอดรวม
            html += `
                <div class="d-flex justify-content-between align-items-center py-3 mt-2">
                    <strong class="fs-5">ยอดรวมทั้งสิ้น:</strong>
                    <strong class="fs-4 text-primary">฿${data.total_price.toLocaleString()}</strong>
                </div>
            </div>`;
            
            container.innerHTML = html;
            return;
        } else {
            container.innerHTML = '<div class="text-center text-muted">ไม่มีประวัติการสั่งอาหาร</div>';
            return;
        }
    }
    
    // ใช้ข้อมูลจาก API ในรูปแบบใหม่
    const tableData = data.data;
    
    // สร้างเนื้อหาสำหรับแสดงผล
    let html = `
        <div class="row mb-3">
            <div class="col-md-6">
                <h6><i class="fas fa-table me-2"></i>${tableData.table_name}</h6>
                ${tableData.session_id ? `<p class="mb-1"><small>Session ID: ${tableData.session_id}</small></p>` : ''}
            </div>
            <div class="col-md-6 text-end">
                <h5 class="text-primary"><strong>ยอดรวม: ฿${(tableData.total_amount !== undefined && tableData.total_amount !== null) ? tableData.total_amount.toFixed(2) : '0.00'}</strong></h5>
                <p class="mb-0 text-muted">รายการทั้งหมด: ${tableData.order_count || 0} รายการ</p>
            </div>
        </div>
    `;
    
    if (tableData.orders && tableData.orders.length > 0) {
        html += `
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
            console.log('Order item_status:', order.item_status); // Debug log
            const statusClass = order.item_status === 'completed' ? 'completed-order' : (order.item_status === 'pending' ? 'pending-order' : 'active-order');
            // Use getItemStatusBadge function for consistent status display
            let statusBadge;
            if (typeof getItemStatusBadge === 'function') {
                statusBadge = getItemStatusBadge(order.item_status);
            } else {
                // Fallback if function not available
                statusBadge = getItemStatusBadge(order.item_status);
            }
            console.log('Order item_status:', order.item_status, 'statusBadge:', statusBadge); // Debug log
            // Parse customer_request to show special options under menu name (same as admin)
            let menuDisplay = order.menu_name;
            let notesDisplay = '-';
            
            if (order.customer_request) {
                if (order.customer_request.includes(' | ')) {
                    const parts = order.customer_request.split(' | ');
                    // Show spice level (first part) after menu name and notes (second part) under menu name
                    let menuText = order.menu_name;
                    if (parts[0] && parts[0].trim()) {
                        menuText += ` <span class="text-muted small">${parts[0].trim()}</span>`;
                    }
                    if (parts[1] && parts[1].trim()) {
                        menuDisplay = `${menuText}<br><small class="text-warning">- ${parts[1].trim()}</small>`;
                    } else {
                        menuDisplay = menuText;
                    }
                    notesDisplay = '-';
                } else {
                    // If no separator, show entire request under menu name
                    menuDisplay = `${order.menu_name}<br><small class="text-warning">- ${order.customer_request.trim()}</small>`;
                    notesDisplay = '-';
                }
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
            
            html += `
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
        
        html += `
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
        html += `
            <div class="text-center py-4">
                <i class="fas fa-utensils fa-3x text-muted mb-3"></i>
                <p class="text-muted">ยังไม่มีรายการสั่งอาหาร</p>
            </div>
        `;
    }
    
    container.innerHTML = html;
}
// ...
// ฟังก์ชันเปิด cart sidebar
function showCart() {
    const cartSidebarEl = document.getElementById('cartSidebar');
    if (cartSidebarEl) {
        const cartSidebar = new bootstrap.Offcanvas(cartSidebarEl);
        cartSidebar.show();
    }
}

// ฟังก์ชันสำหรับส่งคำขอเช็คบิล
async function requestCheckout() {
    const tableId = getQueryParam('table');
    const sessionId = getQueryParam('session');
    
    if (!tableId) {
        showAlert('ไม่พบข้อมูลโต๊ะ', 'error');
        return;
    }
    
    try {
        // แสดง loading
        document.getElementById('checkBillBtn').disabled = true;
        document.getElementById('checkBillBtn').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> กำลังดำเนินการ...';
        
        // ส่งคำขอไปยัง API
        const response = await fetch(`http://localhost:5000/api/tables/${tableId}/checkout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // ส่งการแจ้งเตือนไปยัง admin
            try {
                await fetch('http://localhost:5000/api/check-bill-request', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ table_id: parseInt(tableId) })
                });
                
                // ส่งการแจ้งเตือนทันทีไปยัง admin panel ผ่าน localStorage
                // สร้างเวลาไทยที่ถูกต้อง
                const now = new Date();
                
                const notificationData = {
                    table_id: parseInt(tableId),
                    message: `ขอเช็คบิล!|โต๊ะ ${tableId}`,
                    timestamp: now.toISOString(),
                    type: 'check_bill_request',
                    notification_id: now.getTime()
                };
                
                // บันทึกลง localStorage เพื่อให้ admin panel อ่านได้
                localStorage.setItem('newNotification', JSON.stringify(notificationData));
                
                // ส่ง event เพื่อแจ้งให้ admin panel ทราบ
                window.dispatchEvent(new CustomEvent('newStaffNotification', {
                    detail: notificationData
                }));
            } catch (notificationError) {
                console.error('Error sending notification:', notificationError);
            }
            
            // ปิด modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('orderHistoryModal'));
            if (modal) modal.hide();
            
            // แสดงข้อความสำเร็จ
            showAlert('ส่งคำขอเช็คบิลเรียบร้อยแล้ว พนักงานจะมาที่โต๊ะของคุณในไม่ช้า', 'success');
            
            // แสดงหน้ารอเช็คบิลและซ่อนส่วนการสั่งอาหาร
            showWaitingForCheckoutState();
        } else {
            throw new Error(data.error || 'ไม่สามารถส่งคำขอเช็คบิลได้');
        }
    } catch (error) {
        console.error('Error requesting checkout:', error);
        showAlert(error.message || 'เกิดข้อผิดพลาดในการส่งคำขอเช็คบิล', 'error');
    } finally {
        // คืนค่าปุ่มเป็นปกติ
        document.getElementById('checkBillBtn').disabled = false;
        document.getElementById('checkBillBtn').innerHTML = '<i class="fas fa-receipt me-2"></i>เช็คบิล';
    }
}

// ฟังก์ชันช่วยเหลือสำหรับสถานะรายการ
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

// ตัวแปรสำหรับเก็บ interval ของการตรวจสอบเซสชั่น
let sessionCheckInterval = null;

// เริ่มการตรวจสอบสถานะเซสชั่นเป็นระยะ ๆ
function startSessionMonitoring() {
    const tableId = getQueryParam('table');
    const sessionId = getQueryParam('session');
    
    if (!tableId || !sessionId) return;
    
    // ตรวจสอบทุก 5 วินาที
    sessionCheckInterval = setInterval(() => {
        checkSessionStatus(tableId, sessionId);
    }, 5000);
}

// หยุดการตรวจสอบสถานะเซสชั่น
function stopSessionMonitoring() {
    if (sessionCheckInterval) {
        clearInterval(sessionCheckInterval);
        sessionCheckInterval = null;
    }
}

// ฟังก์ชันแสดงสถานะรอเช็คบิล
function showWaitingForCheckoutState() {
    // หยุดการตรวจสอบเซสชั่นเพื่อป้องกันการรีเฟรช
    stopSessionMonitoring();
    
    // เคลียร์หน้าจอทั้งหมด
    document.body.innerHTML = '';
    
    // เพิ่ม CSS ที่จำเป็นกลับมา
    const head = document.head;
    
    // เพิ่ม Bootstrap CSS
    const bootstrapLink = document.createElement('link');
    bootstrapLink.rel = 'stylesheet';
    bootstrapLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css';
    head.appendChild(bootstrapLink);
    
    // เพิ่ม Font Awesome
    const fontAwesomeLink = document.createElement('link');
    fontAwesomeLink.rel = 'stylesheet';
    fontAwesomeLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
    head.appendChild(fontAwesomeLink);
    
    // เพิ่ม Google Fonts
    const googleFontsLink = document.createElement('link');
    googleFontsLink.rel = 'stylesheet';
    googleFontsLink.href = 'https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap';
    head.appendChild(googleFontsLink);
    
    // ตั้งค่า CSS สำหรับ body
    document.body.style.margin = '0';
    document.body.style.padding = '20px';
    document.body.style.backgroundColor = '#f8f9fa';
    document.body.style.fontFamily = 'Sarabun, sans-serif';
    
    // สร้างและแสดงเฉพาะตารางรายการสินค้า
    const waitingSection = document.createElement('div');
    waitingSection.id = 'waiting-checkout-section';
    waitingSection.className = 'container-fluid py-4';
    waitingSection.innerHTML = `
        <!-- Header Section -->
        <div class="text-center mb-4">
            <div class="card border-0 shadow-sm" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <div class="card-body py-4">
                    <div class="d-flex align-items-center justify-content-center mb-2">
                        <div class="spinner-border spinner-border-sm me-3" role="status" style="color: #ffd700;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <h3 class="mb-0 fw-bold">
                            <i class="fas fa-receipt me-2" style="color: #ffd700;"></i>
                            กำลังรอพนักงานเช็คบิล
                        </h3>
                        <div class="spinner-border spinner-border-sm ms-3" role="status" style="color: #ffd700;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>
                    <p class="mb-0 fs-5 opacity-90">
                        <i class="fas fa-clock me-2"></i>
                        โปรดรอสักครู่ พนักงานจะมาเช็คบิลให้ท่านเร็วๆ นี้
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Order Summary Section -->
        <div class="card shadow-lg border-0">
            <div class="card-header bg-light border-0 py-3">
                <h5 class="mb-0 text-center">
                    <i class="fas fa-list-alt me-2 text-primary"></i>
                    สรุปรายการสั่งอาหาร
                </h5>
            </div>
            <div class="card-body p-4">
                <div id="waiting-order-list">
                    <!-- รายการอาหารจะแสดงที่นี่ -->
                </div>
            </div>
        </div>
    `;
    
    // เพิ่ม CSS สำหรับหน้าจอมือถือ
    const mobileStyles = document.createElement('style');
    mobileStyles.textContent = `
        @media (max-width: 768px) {
            .container-fluid {
                padding-left: 10px !important;
                padding-right: 10px !important;
            }
            
            .card {
                margin-bottom: 15px;
            }
            
            .table-responsive {
                font-size: 0.8rem;
            }
            
            .badge {
                font-size: 0.7rem;
            }
            
            h3 {
                font-size: 1.3rem !important;
            }
            
            h4 {
                font-size: 1.1rem !important;
            }
            
            h5 {
                font-size: 1rem !important;
            }
            
            .spinner-border-sm {
                width: 1rem;
                height: 1rem;
            }
        }
        
        @media (max-width: 576px) {
            .container-fluid {
                padding-left: 5px !important;
                padding-right: 5px !important;
            }
            
            .card-body {
                padding: 1rem !important;
            }
            
            .table td, .table th {
                padding: 0.5rem 0.25rem;
            }
        }
    `;
    document.head.appendChild(mobileStyles);
    
    // เพิ่มหน้ารอเช็คบิลลงใน DOM
    document.body.appendChild(waitingSection);
    
    // โหลดและแสดงรายการอาหารทั้งหมด
    loadOrderListForWaiting();
}

// ฟังก์ชันโหลดรายการอาหารสำหรับหน้ารอเช็คบิล
function loadOrderListForWaiting() {
    const tableId = getQueryParam('table');
    const sessionId = getQueryParam('session');
    
    if (!tableId) return;
    
    let url = `http://localhost:5000/api/tables/${tableId}/order-summary`;
    if (sessionId) {
        url += `?session_id=${sessionId}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data && data.data.orders) {
                renderWaitingOrderList(data.data);
            }
        })
        .catch(error => {
            console.error('Error loading order list for waiting:', error);
        });
}

// ฟังก์ชันแสดงรายการอาหารในหน้ารอเช็คบิล
function renderWaitingOrderList(tableData) {
    const container = document.getElementById('waiting-order-list');
    if (!container) return;
    

    
    let html = '';
    
    if (tableData.orders && tableData.orders.length > 0) {
        html += `
            <div class="table-responsive">
                <table class="table table-striped table-sm">
                    <thead class="table-light">
                        <tr>
                            <th style="width: 40%; font-size: 0.9rem;">เมนู</th>
                            <th class="text-center" style="width: 15%; font-size: 0.9rem;">สถานะ</th>
                            <th class="text-center" style="width: 10%; font-size: 0.9rem;">จำนวน</th>
                            <th class="text-end" style="width: 35%; font-size: 0.9rem;">รวม</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        tableData.orders.forEach(order => {
            const statusBadge = getItemStatusBadge(order.item_status);
            
            // Parse customer_request
            let menuDisplay = order.menu_name;
            let notesDisplay = '-';
            
            if (order.customer_request) {
                if (order.customer_request.includes(' | ')) {
                    const parts = order.customer_request.split(' | ');
                    if (parts[1] && parts[1].trim()) {
                        menuDisplay = `${order.menu_name}<br><small class="text-warning">- ${parts[1].trim()}</small>`;
                    }
                    notesDisplay = '-';
                } else {
                    menuDisplay = order.menu_name;
                    notesDisplay = '-';
                }
            }
            
            // Handle price display for rejected items
            let priceDisplay, totalDisplay;
            if (order.item_status === 'rejected') {
                const originalPrice = (order.unit_price !== undefined && order.unit_price !== null) ? order.unit_price.toFixed(2) : '0.00';
                const originalTotal = (order.total_price !== undefined && order.total_price !== null) ? order.total_price.toFixed(2) : '0.00';
                priceDisplay = `<span style="text-decoration: line-through; color: #6c757d;">฿${originalPrice}</span><br><span class="text-danger">฿0.00</span>`;
                totalDisplay = `<span style="text-decoration: line-through; color: #6c757d;">฿${originalTotal}</span><br><span class="text-danger">฿0.00</span>`;
            } else {
                const price = (order.unit_price !== undefined && order.unit_price !== null) ? order.unit_price.toFixed(2) : '0.00';
                const total = (order.total_price !== undefined && order.total_price !== null) ? order.total_price.toFixed(2) : '0.00';
                priceDisplay = `฿${price}`;
                totalDisplay = `฿${total}`;
            }
            
            html += `
                <tr>
                    <td style="font-size: 0.85rem; line-height: 1.3;">
                        <div class="fw-bold">${order.menu_name}</div>
                        ${order.customer_request && order.customer_request.includes(' | ') && order.customer_request.split(' | ')[1] && order.customer_request.split(' | ')[1].trim() ? 
                            `<small class="text-warning d-block">- ${order.customer_request.split(' | ')[1].trim()}</small>` : ''}
                        <small class="text-muted d-block">฿${(order.unit_price !== undefined && order.unit_price !== null) ? order.unit_price.toFixed(2) : '0.00'} × ${order.quantity || 1}</small>
                    </td>
                    <td class="text-center" style="font-size: 0.8rem;">${statusBadge}</td>
                    <td class="text-center" style="font-size: 0.85rem;">
                        <span class="badge bg-dark">${order.quantity || 1}</span>
                    </td>
                    <td class="text-end" style="font-size: 0.9rem; font-weight: 600;">${totalDisplay}</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
            
            <!-- Total Summary Card -->
            <div class="mt-4">
                <div class="card border-0" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white;">
                    <div class="card-body text-center py-3">
                        <div class="row align-items-center">
                            <div class="col-6">
                                <h6 class="mb-1 opacity-90">รายการทั้งหมด</h6>
                                <h5 class="mb-0 fw-bold">${tableData.order_count || 0} รายการ</h5>
                            </div>
                            <div class="col-6">
                                <h6 class="mb-1 opacity-90">ยอดรวมทั้งหมด</h6>
                                <h4 class="mb-0 fw-bold">฿${(tableData.total_amount || 0).toFixed(2)}</h4>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        html += `
            <div class="text-center py-4">
                <i class="fas fa-utensils fa-3x text-muted mb-3"></i>
                <p class="text-muted">ยังไม่มีรายการสั่งอาหาร</p>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// หมายเหตุ: การเริ่มต้น startSessionMonitoring ได้ย้ายไปรวมกับ DOMContentLoaded listener หลักแล้ว

// หยุดการตรวจสอบเซสชั่นเมื่อออกจากหน้า
window.addEventListener('beforeunload', function() {
    stopSessionMonitoring();
});

// Call Staff Modal Functions
let staffRequestQuantities = {
    spoon: 0,
    glass: 0,
    straw: 0,
    plate: 0
};

function callStaff() {
    console.log('callStaff function called');
    
    // Ensure DOM is ready
    if (document.readyState !== 'complete') {
        console.log('DOM not ready, waiting...');
        setTimeout(callStaff, 100);
        return;
    }
    
    // Reset quantities
    staffRequestQuantities = {
        spoon: 0,
        glass: 0,
        straw: 0,
        plate: 0
    };
    
    // Update display
    updateQuantityDisplays();
    
    // อัปเดตสถานะปุ่มส่งคำขอ
    updateSendRequestButtonState();
    
    // Wait a bit for DOM to be fully ready
    setTimeout(() => {
        // Show modal with proper options
        const modalElement = document.getElementById('callStaffModal');
        console.log('Modal element found:', modalElement);
        console.log('Document ready state:', document.readyState);
        console.log('All modals in document:', document.querySelectorAll('.modal'));
        
        if (modalElement) {
            console.log('Creating Bootstrap modal');
            try {
                const modal = new bootstrap.Modal(modalElement, {
                    backdrop: true,
                    keyboard: true,
                    focus: true
                });
                console.log('Showing modal');
                modal.show();
            } catch (error) {
                console.error('Error creating/showing modal:', error);
            }
        } else {
            console.error('Modal element not found');
            console.log('Available elements with id:', document.querySelectorAll('[id]'));
        }
    }, 50);
}

function increaseQuantity(item) {
    if (staffRequestQuantities[item] < 10) {
        staffRequestQuantities[item]++;
        updateQuantityDisplay(item);
    }
}

function decreaseQuantity(item) {
    if (staffRequestQuantities[item] > 0) {
        staffRequestQuantities[item]--;
        updateQuantityDisplay(item);
    }
}

function updateQuantityDisplay(item) {
    const element = document.getElementById(item + '-quantity');
    if (element) {
        element.textContent = staffRequestQuantities[item];
    }
    // อัปเดตสถานะปุ่มส่งคำขอ
    updateSendRequestButtonState();
}

function updateQuantityDisplays() {
    Object.keys(staffRequestQuantities).forEach(item => {
        updateQuantityDisplay(item);
    });
}

// ฟังก์ชันอัปเดตสถานะปุ่มส่งคำขอ
function updateSendRequestButtonState() {
    const sendRequestBtn = document.querySelector('button[onclick="sendItemRequest()"]');
    if (!sendRequestBtn) return;
    
    // ตรวจสอบว่ามีรายการที่ร้องขอหรือไม่
    const hasRequests = Object.values(staffRequestQuantities).some(qty => qty > 0);
    
    if (hasRequests) {
        // มีรายการที่ร้องขอ - เปิดใช้งานปุ่ม
        sendRequestBtn.disabled = false;
        sendRequestBtn.style.background = '';
        sendRequestBtn.style.borderColor = '';
        sendRequestBtn.style.color = '';
    } else {
        // ไม่มีรายการที่ร้องขอ - ปิดใช้งานปุ่มและเปลี่ยนเป็นสีเทา
        sendRequestBtn.disabled = true;
        sendRequestBtn.style.background = '#6c757d';
        sendRequestBtn.style.borderColor = '#6c757d';
        sendRequestBtn.style.color = '#ffffff';
    }
}

function sendStaffRequest() {
    // Get table ID from URL parameters
    const tableId = getQueryParam('table');
    if (!tableId) {
        showErrorModal('ไม่พบข้อมูลโต๊ะ');
        return;
    }
    
    // เปลี่ยนสีปุ่มเป็นสีเทาทันที
    const callStaffBtn = document.querySelector('.btn-call-staff');
    const modalCallStaffBtn = document.querySelector('button[onclick="sendStaffRequest()"]');
    
    if (callStaffBtn) {
        callStaffBtn.style.background = '#6c757d';
        callStaffBtn.style.borderColor = '#6c757d';
        callStaffBtn.disabled = true;
    }
    if (modalCallStaffBtn) {
        modalCallStaffBtn.style.background = '#6c757d';
        modalCallStaffBtn.style.borderColor = '#6c757d';
        modalCallStaffBtn.disabled = true;
    }
    
    // Prepare staff call request with required format
    const requestData = {
        table_id: parseInt(tableId),
        requests: [{
            item: 'เรียกพนักงาน',
            quantity: 1
        }]
    };
    
    // Send request to server
    fetch('/api/staff-request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // ปิด modal เรียกพนักงาน
            const callStaffModal = bootstrap.Modal.getInstance(document.getElementById('callStaffModal'));
            if (callStaffModal) {
                callStaffModal.hide();
            }
            
            // แสดง modal ใหม่ที่แสดงว่าเรียกพนักงานแล้ว
            showStaffCalledModal();
            
            // ส่งการแจ้งเตือนทันทีไปยัง admin panel ผ่าน localStorage
            // สร้างเวลาไทยที่ถูกต้อง
            const now = new Date();
            
            const notificationData = {
                table_id: parseInt(tableId),
                message: `โต๊ะ ${tableId} ขอ: เรียกพนักงาน 1 ชิ้น`,
                timestamp: now.toISOString(),
                type: 'staff_request',
                notification_id: now.getTime()
            };
            
            // บันทึกลง localStorage เพื่อให้ admin panel อ่านได้
            localStorage.setItem('newNotification', JSON.stringify(notificationData));
            
            // ส่ง event เพื่อแจ้งให้ admin panel ทราบ
            window.dispatchEvent(new CustomEvent('newStaffNotification', {
                detail: notificationData
            }));
        } else {
            showErrorModal('เกิดข้อผิดพลาดในการส่งคำขอ');
        }
    })
    .catch(error => {
        console.error('Error sending staff request:', error);
        showErrorModal('เกิดข้อผิดพลาดในการเชื่อมต่อ');
    });
}

// Modal functions for error and success messages
function showErrorModal(message) {
    showAlert(message, 'error');
}

function showSuccessModal(message) {
    showAlert(message, 'success');
}

function sendItemRequest() {
    // Check if any items are requested
    const hasRequests = Object.values(staffRequestQuantities).some(qty => qty > 0);
    
    if (!hasRequests) {
        showErrorModal('กรุณาเลือกรายการที่ต้องการขอเพิ่ม');
        return;
    }
    
    // Get table ID from URL parameters
    const tableId = getQueryParam('table');
    if (!tableId) {
        showErrorModal('ไม่พบข้อมูลโต๊ะ');
        return;
    }
    
    // เปลี่ยนสีปุ่มเป็นสีเทาและปิดใช้งานทันที
    const sendRequestBtn = document.querySelector('button[onclick="sendItemRequest()"]');
    if (sendRequestBtn) {
        sendRequestBtn.style.background = '#6c757d';
        sendRequestBtn.style.borderColor = '#6c757d';
        sendRequestBtn.disabled = true;
    }
    
    // Prepare request data
    const requestData = {
        table_id: parseInt(tableId),
        requests: []
    };
    
    // Add requested items
    Object.keys(staffRequestQuantities).forEach(item => {
        if (staffRequestQuantities[item] > 0) {
            let itemName = '';
            switch(item) {
                case 'spoon': itemName = 'ช้อน-ส้อม'; break;
                case 'glass': itemName = 'แก้ว'; break;
                case 'straw': itemName = 'หลอด'; break;
                case 'plate': itemName = 'จาน'; break;
            }
            requestData.requests.push({
                item: itemName,
                quantity: staffRequestQuantities[item]
            });
        }
    });
    
    // Send request to server
    fetch('/api/item-request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('callStaffModal'));
            modal.hide();
            
            // แสดง modal "ส่งคำขอเรียบร้อยแล้ว"
            showItemRequestSuccessModal();
            
            // สร้างรายการสิ่งของที่ขอ
            const requestedItems = [];
            Object.keys(staffRequestQuantities).forEach(item => {
                if (staffRequestQuantities[item] > 0) {
                    let itemName = '';
                    switch(item) {
                        case 'spoon': itemName = 'ช้อน-ส้อม'; break;
                        case 'glass': itemName = 'แก้ว'; break;
                        case 'straw': itemName = 'หลอด'; break;
                        case 'plate': itemName = 'จาน'; break;
                    }
                    requestedItems.push(`${itemName} ${staffRequestQuantities[item]} ชิ้น`);
                }
            });
            
            // ส่งการแจ้งเตือนทันทีไปยัง admin panel ผ่าน localStorage
            // สร้างเวลาไทยที่ถูกต้อง
            const now = new Date();
            
            const notificationData = {
                table_id: parseInt(tableId),
                message: `ลูกค้าต้องการภาชนะเพิ่ม|โต๊ะ ${tableId}|${requestedItems.join(', ')}`,
                timestamp: now.toISOString(),
                type: 'item_request',
                notification_id: now.getTime()
            };
            
            // บันทึกลง localStorage เพื่อให้ admin panel อ่านได้
            localStorage.setItem('newNotification', JSON.stringify(notificationData));
            
            // ส่ง event เพื่อแจ้งให้ admin panel ทราบ
            window.dispatchEvent(new CustomEvent('newStaffNotification', {
                detail: notificationData
            }));
        } else {
            showErrorModal('เกิดข้อผิดพลาดในการส่งคำขอ');
            // รีเซ็ตปุ่มกลับสู่สถานะปกติหากเกิดข้อผิดพลาด
            resetItemRequestButton();
        }
    })
    .catch(error => {
        console.error('Error sending item request:', error);
        showErrorModal('เกิดข้อผิดพลาดในการเชื่อมต่อ');
        // รีเซ็ตปุ่มกลับสู่สถานะปกติหากเกิดข้อผิดพลาด
        resetItemRequestButton();
    });
}

// ฟังก์ชันแสดง modal เรียกพนักงานแล้ว
function showStaffCalledModal() {
    // สร้าง modal element
    const modalHtml = `
        <div class="modal fade" id="staffCalledModal" tabindex="-1" aria-labelledby="staffCalledModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-body text-center py-5">
                        <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
                        <h4 class="mb-3">เรียกพนักงานแล้ว</h4>
                        <p class="text-muted">พนักงานจะมาให้บริการในไม่ช้า</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // เพิ่ม modal เข้าไปใน body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('staffCalledModal'));
    modal.show();
    
    // ปิด modal หลังจาก 3 วินาที
    setTimeout(() => {
        modal.hide();
        // ลบ modal element ออกจาก DOM หลังจากปิด
        setTimeout(() => {
            const modalElement = document.getElementById('staffCalledModal');
            if (modalElement) {
                modalElement.remove();
            }
        }, 300); // รอให้ animation เสร็จก่อน
        
        // รีเซ็ตปุ่มกลับสู่สถานะปกติ
        resetStaffButton();
    }, 3000);
}
 
 // ฟังก์ชันรีเซ็ตปุ่มเรียกพนักงานกลับสู่สถานะปกติ
 function resetStaffButton() {
    const callStaffBtn = document.querySelector('.btn-call-staff');
    const modalCallStaffBtn = document.querySelector('button[onclick="sendStaffRequest()"]');
    
    if (callStaffBtn) {
        callStaffBtn.style.background = '';
        callStaffBtn.style.borderColor = '';
        callStaffBtn.disabled = false;
    }
    if (modalCallStaffBtn) {
        modalCallStaffBtn.style.background = '';
        modalCallStaffBtn.style.borderColor = '';
        modalCallStaffBtn.disabled = false;
    }
}

// ฟังก์ชันแสดง modal "ส่งคำขอเรียบร้อยแล้ว"
function showItemRequestSuccessModal() {
    // สร้าง modal element
    const modalHtml = `
        <div class="modal fade" id="itemRequestSuccessModal" tabindex="-1" aria-labelledby="itemRequestSuccessModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-body text-center py-5">
                        <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
                        <h5 class="modal-title mb-3">ส่งคำขอเรียบร้อยแล้ว</h5>
                        <p class="text-muted">พนักงานจะนำสิ่งของที่ขอมาให้ในไม่ช้า</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // เพิ่ม modal เข้าไปใน body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // แสดง modal
    const modal = new bootstrap.Modal(document.getElementById('itemRequestSuccessModal'));
    modal.show();
    
    // ปิด modal หลังจาก 3 วินาที และลบออกจาก DOM
    setTimeout(() => {
        modal.hide();
        setTimeout(() => {
            const modalElement = document.getElementById('itemRequestSuccessModal');
            if (modalElement) {
                modalElement.remove();
            }
            // รีเซ็ตปุ่มหลังจาก modal ปิด
            resetItemRequestButton();
        }, 300);
    }, 3000);
}

// ฟังก์ชันรีเซ็ตปุ่มส่งคำขอ
function resetItemRequestButton() {
    const sendRequestBtn = document.querySelector('button[onclick="sendItemRequest()"]');
    if (sendRequestBtn) {
        sendRequestBtn.style.background = '';
        sendRequestBtn.style.borderColor = '';
        sendRequestBtn.disabled = false;
    }
}
 
 // ฟังก์ชันส่งการแจ้งเตือนออเดอร์ใหม่
 function sendOrderRequest() {
    // Get table ID from URL parameters
    const tableId = getQueryParam('table');
    if (!tableId) {
        console.error('ไม่พบข้อมูลโต๊ะ');
        return;
    }
    
    // Prepare order notification request
    const requestData = {
        table_id: parseInt(tableId)
    };
    
    // Send request to server
    fetch('/api/order-request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('ส่งการแจ้งเตือนออเดอร์ใหม่เรียบร้อยแล้ว');
            
            // ส่งการแจ้งเตือนทันทีไปยัง admin panel ผ่าน localStorage
            // สร้างเวลาไทยที่ถูกต้อง
            const now = new Date();
            
            const notificationData = {
                table_id: parseInt(tableId),
                message: `ได้รับออเดอร์ใหม่!|โต๊ะ ${tableId}`,
                timestamp: now.toISOString(),
                type: 'order_request',
                notification_id: now.getTime()
            };
            
            // บันทึกลง localStorage เพื่อให้ admin panel อ่านได้
            localStorage.setItem('newNotification', JSON.stringify(notificationData));
            
            // ส่ง event เพื่อแจ้งให้ admin panel ทราบ
            window.dispatchEvent(new CustomEvent('newStaffNotification', {
                detail: notificationData
            }));
        } else {
            console.error('เกิดข้อผิดพลาดในการส่งการแจ้งเตือนออเดอร์');
        }
    })
    .catch(error => {
        console.error('Error sending order notification:', error);
    });
}

// Function to setup hardcoded special options logic
function setupHardcodedSpecialOptionsLogic() {
    const specialInputs = document.querySelectorAll('input[name="specialLevel"]');
    const noAddInput = document.getElementById('specialNone');
    const otherInputs = Array.from(specialInputs).filter(input => input.id !== 'specialNone');
    
    if (specialInputs.length > 0) {
        // Function to ensure "ไม่เพิ่ม" is selected if nothing else is selected
        const ensureSelection = () => {
            const anyChecked = Array.from(specialInputs).some(input => input.checked);
            if (!anyChecked && noAddInput) {
                noAddInput.checked = true;
                updateTotalPrice();
            }
        };
        
        specialInputs.forEach(input => {
            input.addEventListener('change', function() {
                if (this.id === 'specialNone' && this.checked) {
                    // If "ไม่เพิ่ม" is selected, uncheck all others
                    otherInputs.forEach(otherInput => {
                        otherInput.checked = false;
                    });
                } else if (this.checked && this.id !== 'specialNone') {
                    // If any other option is selected, uncheck "ไม่เพิ่ม"
                    if (noAddInput) {
                        noAddInput.checked = false;
                    }
                } else if (!this.checked) {
                    // If unchecking an option, ensure something is still selected
                    setTimeout(ensureSelection, 10);
                }
                
                updateTotalPrice();
            });
            
            // Prevent unchecking if it would leave nothing selected
            input.addEventListener('click', function(e) {
                if (this.checked && this.id === 'specialNone') {
                    // Don't allow unchecking "ไม่เพิ่ม" if no other options are selected
                    const otherChecked = otherInputs.some(input => input.checked);
                    if (!otherChecked) {
                        e.preventDefault();
                        return false;
                    }
                }
            });
        });
        
        // Initialize with "ไม่เพิ่ม" selected if nothing else is selected
        ensureSelection();
    }
}

// Initialize hardcoded special options when modal is shown
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('menuItemOptionsModal');
    if (modal) {
        modal.addEventListener('shown.bs.modal', function() {
            // Setup hardcoded special options logic
            setTimeout(() => {
                setupHardcodedSpecialOptionsLogic();
            }, 100);
        });
    }
});