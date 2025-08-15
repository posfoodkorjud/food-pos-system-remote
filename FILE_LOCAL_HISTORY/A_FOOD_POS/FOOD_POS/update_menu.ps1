# PowerShell script to update menu via API
# Script to update menu through API endpoints

$baseUrl = "http://localhost:5000/api"

Write-Host "Starting menu update..." -ForegroundColor Green

# Function to make API calls
function Invoke-ApiCall {
    param(
        [string]$Method,
        [string]$Uri,
        [hashtable]$Body = $null
    )
    
    try {
        $headers = @{
            'Content-Type' = 'application/json; charset=utf-8'
        }
        
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers -Body $jsonBody
        } else {
            $response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers
        }
        
        return $response
    }
    catch {
        Write-Host "Error calling API: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Get current categories and items
Write-Host "Getting current menu data..." -ForegroundColor Yellow
$currentCategories = Invoke-ApiCall -Method "GET" -Uri "$baseUrl/menu/categories"
$currentItems = Invoke-ApiCall -Method "GET" -Uri "$baseUrl/menu/items"

if ($currentCategories -and $currentCategories.success) {
    Write-Host "Found categories: $($currentCategories.data.Count)" -ForegroundColor Cyan
    
    # Delete all current menu items first
    if ($currentItems -and $currentItems.success) {
        Write-Host "Found menu items: $($currentItems.data.Count)" -ForegroundColor Cyan
        Write-Host "Deleting current menu items..." -ForegroundColor Yellow
        
        foreach ($item in $currentItems.data) {
            if ($item.is_available -eq 1) {
                $deleteResult = Invoke-ApiCall -Method "DELETE" -Uri "$baseUrl/menu/items/$($item.item_id)"
                if ($deleteResult -and $deleteResult.success) {
                    Write-Host "Deleted item: $($item.name)" -ForegroundColor Gray
                }
            }
        }
    }
    
    # Delete current categories
    Write-Host "Deleting current categories..." -ForegroundColor Yellow
    foreach ($category in $currentCategories.data) {
        if ($category.is_active -eq 1) {
            $deleteResult = Invoke-ApiCall -Method "DELETE" -Uri "$baseUrl/menu/categories/$($category.category_id)"
            if ($deleteResult -and $deleteResult.success) {
                Write-Host "Deleted category: $($category.name)" -ForegroundColor Gray
            }
        }
    }
}

# Add new categories
Write-Host "Adding new categories..." -ForegroundColor Yellow
$categories = @(
    @{ name = "อาหารจานเดียว"; description = "อาหารจานเดียวหลากหลายรสชาติ" },
    @{ name = "อาหารทานเล่น"; description = "อาหารทานเล่นและของว่าง" },
    @{ name = "ยำ / สลัด"; description = "ยำและสลัดสดใส" },
    @{ name = "เครื่องดื่มเย็น / ร้อน"; description = "เครื่องดื่มหลากหลาย" },
    @{ name = "ของหวาน"; description = "ของหวานและขนมหวาน" }
)

$categoryIds = @{}
foreach ($category in $categories) {
    $result = Invoke-ApiCall -Method "POST" -Uri "$baseUrl/menu/categories" -Body $category
    if ($result -and $result.success) {
        $categoryIds[$category.name] = $result.data.category_id
        Write-Host "Added category: $($category.name)" -ForegroundColor Green
    } else {
        Write-Host "Failed to add category: $($category.name)" -ForegroundColor Red
    }
}

# Add new menu items
Write-Host "Adding new menu items..." -ForegroundColor Yellow
$menuItems = @(
    # Main dishes
    @{ name = "ข้าวผัดหมู / ไก่ / กุ้ง"; price = 60; category = "อาหารจานเดียว"; description = "ข้าวผัดหอมๆ เลือกได้ทั้งหมู ไก่ หรือกุ้ง" },
    @{ name = "ข้าวกระเพราหมูสับไข่ดาว"; price = 65; category = "อาหารจานเดียว"; description = "ข้าวกระเพราหมูสับรสจัดจ้าน เสิร์ฟพร้อมไข่ดาว" },
    @{ name = "ข้าวหมูกระเทียม"; price = 60; category = "อาหารจานเดียว"; description = "ข้าวหมูกระเทียมหอมกรุ่น" },
    @{ name = "ข้าวไข่เจียวหมูสับ"; price = 55; category = "อาหารจานเดียว"; description = "ข้าวไข่เจียวฟูๆ ใส่หมูสับ" },
    @{ name = "ข้าวผัดกะเพราเต้าหู้ (มังสวิรัติ)"; price = 60; category = "อาหารจานเดียว"; description = "ข้าวผัดกะเพราเต้าหู้สำหรับคนรักสุขภาพ" },
    @{ name = "ข้าวราดแกงเขียวหวานไก่"; price = 70; category = "อาหารจานเดียว"; description = "ข้าวราดแกงเขียวหวานไก่เข้มข้น" },
    @{ name = "ข้าวคลุกกะปิ"; price = 65; category = "อาหารจานเดียว"; description = "ข้าวคลุกกะปิรสชาติดั้งเดิม" },
    @{ name = "ข้าวผัดน้ำพริกลงเรือ"; price = 70; category = "อาหารจานเดียว"; description = "ข้าวผัดน้ำพริกลงเรือรสเผ็ดหวาน" },
    @{ name = "ข้าวคั่วกลิ้งหมู"; price = 70; category = "อาหารจานเดียว"; description = "ข้าวคั่วกลิ้งหมูสูตรใต้" },
    @{ name = "ข้าวหน้าไก่เทอริยากิ"; price = 75; category = "อาหารจานเดียว"; description = "ข้าวหน้าไก่เทอริยากิสไตล์ญี่ปุ่น" },
    
    # Snacks
    @{ name = "เฟรนช์ฟรายส์"; price = 45; category = "อาหารทานเล่น"; description = "มันฝรั่งทอดกรอบนอกนุ่มใน" },
    @{ name = "นักเก็ตไก่"; price = 50; category = "อาหารทานเล่น"; description = "นักเก็ตไก่ทอดกรอบ" },
    @{ name = "ไก่ป๊อป"; price = 55; category = "อาหารทานเล่น"; description = "ไก่ป๊อปชิ้นเล็กทอดกรอบ" },
    @{ name = "หมูทอดจิ้มแจ่ว"; price = 60; category = "อาหารทานเล่น"; description = "หมูทอดกรอบเสิร์ฟพร้อมแจ่ว" },
    @{ name = "ไก่ทอดเกลือ"; price = 55; category = "อาหารทานเล่น"; description = "ไก่ทอดเกลือรสชาติกำลังดี" },
    @{ name = "ปีกไก่ทอดน้ำปลา"; price = 60; category = "อาหารทานเล่น"; description = "ปีกไก่ทอดน้ำปลาหอมหวาน" },
    @{ name = "ลูกชิ้นลวกจิ้ม"; price = 45; category = "อาหารทานเล่น"; description = "ลูกชิ้นลวกสดใหม่" },
    @{ name = "เกี๊ยวซ่าทอด"; price = 50; category = "อาหารทานเล่น"; description = "เกี๊ยวซ่าทอดกรอบ" },
    @{ name = "แหนมคลุก"; price = 55; category = "อาหารทานเล่น"; description = "แหนมคลุกรสเปรี้ยวหวาน" },
    @{ name = "ข้าวโพดชีส"; price = 50; category = "อาหารทานเล่น"; description = "ข้าวโพดหวานโรยชีส" },
    
    # Salads
    @{ name = "ยำวุ้นเส้นหมูสับ"; price = 65; category = "ยำ / สลัด"; description = "ยำวุ้นเส้นหมูสับรสจัดจ้าน" },
    @{ name = "ยำรวมทะเล"; price = 85; category = "ยำ / สลัด"; description = "ยำรวมทะเลสดใหม่" },
    @{ name = "ยำไข่ดาว"; price = 60; category = "ยำ / สลัด"; description = "ยำไข่ดาวกรอบรสเปรี้ยวหวาน" },
    @{ name = "ยำแซลมอน"; price = 90; category = "ยำ / สลัด"; description = "ยำแซลมอนสดใหม่" },
    @{ name = "ยำขนมจีน"; price = 65; category = "ยำ / สลัด"; description = "ยำขนมจีนรสชาติดั้งเดิม" },
    @{ name = "ยำมาม่า"; price = 65; category = "ยำ / สลัด"; description = "ยำมาม่าสไตล์วัยรุ่น" },
    @{ name = "ยำไส้กรอก"; price = 60; category = "ยำ / สลัด"; description = "ยำไส้กรอกรสเผ็ดหวาน" },
    @{ name = "ยำหมูยอ"; price = 60; category = "ยำ / สลัด"; description = "ยำหมูยอรสชาติเข้มข้น" },
    @{ name = "ยำเห็ดรวม"; price = 65; category = "ยำ / สลัด"; description = "ยำเห็ดรวมหลากหลายชนิด" },
    @{ name = "ซีซาร์สลัด"; price = 75; category = "ยำ / สลัด"; description = "ซีซาร์สลัดสไตล์ตะวันตก" },
    
    # Beverages
    @{ name = "ชาไทยเย็น / ชาเขียวเย็น"; price = 35; category = "เครื่องดื่มเย็น / ร้อน"; description = "ชาไทยหรือชาเขียวเย็นหวานมัน" },
    @{ name = "กาแฟเย็น / อเมริกาโน่"; price = 40; category = "เครื่องดื่มเย็น / ร้อน"; description = "กาแฟเย็นหรืออเมริกาโน่หอมกรุ่น" },
    @{ name = "โกโก้เย็น"; price = 40; category = "เครื่องดื่มเย็น / ร้อน"; description = "โกโก้เย็นหวานหอม" },
    @{ name = "นมชมพู"; price = 35; category = "เครื่องดื่มเย็น / ร้อน"; description = "นมชมพูหวานเย็น" },
    @{ name = "น้ำผึ้งมะนาวโซดา"; price = 45; category = "เครื่องดื่มเย็น / ร้อน"; description = "น้ำผึ้งมะนาวโซดาสดชื่น" },
    @{ name = "ลาเต้เย็น"; price = 45; category = "เครื่องดื่มเย็น / ร้อน"; description = "ลาเต้เย็นหอมนุ่มลิ้น" },
    @{ name = "ชามะนาว"; price = 35; category = "เครื่องดื่มเย็น / ร้อน"; description = "ชามะนาวสดชื่น" },
    @{ name = "ชาดำเย็น"; price = 30; category = "เครื่องดื่มเย็น / ร้อน"; description = "ชาดำเย็นรสชาติดั้งเดิม" },
    @{ name = "ม็อกเทลลิ้นจี่โซดา"; price = 50; category = "เครื่องดื่มเย็น / ร้อน"; description = "ม็อกเทลลิ้นจี่โซดาหวานซ่า" },
    @{ name = "น้ำเก๊กฮวย"; price = 30; category = "เครื่องดื่มเย็น / ร้อน"; description = "น้ำเก๊กฮวยชื่นใจ" },
    
    # Desserts
    @{ name = "ขนมปังปิ้งเนยน้ำตาล"; price = 30; category = "ของหวาน"; description = "ขนมปังปิ้งเนยน้ำตาลหอมหวาน" },
    @{ name = "ปังเย็นช็อกโกแลต"; price = 45; category = "ของหวาน"; description = "ปังเย็นช็อกโกแลตเข้มข้น" },
    @{ name = "บิงซูผลไม้"; price = 65; category = "ของหวาน"; description = "บิงซูผลไม้สดใหม่" },
    @{ name = "กล้วยทอด"; price = 30; category = "ของหวาน"; description = "กล้วยทอดกรอบหวาน" },
    @{ name = "เฉาก๊วยนมสด"; price = 35; category = "ของหวาน"; description = "เฉาก๊วยนมสดเย็นชื่นใจ" },
    @{ name = "แพนเค้กกล้วยหอม"; price = 50; category = "ของหวาน"; description = "แพนเค้กกล้วยหอมนุ่มฟู" },
    @{ name = "ไอศกรีมกะทิสด"; price = 40; category = "ของหวาน"; description = "ไอศกรีมกะทิสดหอมมัน" },
    @{ name = "โรตีใส่กล้วย"; price = 40; category = "ของหวาน"; description = "โรตีใส่กล้วยหอมหวาน" },
    @{ name = "เครปเย็น"; price = 50; category = "ของหวาน"; description = "เครปเย็นหลากหลายรสชาติ" },
    @{ name = "ชีสเค้ก"; price = 55; category = "ของหวาน"; description = "ชีสเค้กนุ่มละมุน" }
)

$addedItems = 0
foreach ($item in $menuItems) {
    if ($categoryIds.ContainsKey($item.category)) {
        $menuData = @{
            name = $item.name
            price = $item.price
            category_id = $categoryIds[$item.category]
            description = $item.description
        }
        
        $result = Invoke-ApiCall -Method "POST" -Uri "$baseUrl/menu/items" -Body $menuData
        if ($result -and $result.success) {
            $addedItems++
            Write-Host "Added menu: $($item.name) - $($item.price) THB" -ForegroundColor Green
        } else {
            Write-Host "Failed to add menu: $($item.name)" -ForegroundColor Red
        }
    } else {
        Write-Host "Category not found: $($item.category)" -ForegroundColor Red
    }
}

Write-Host "`nMenu update completed!" -ForegroundColor Green
Write-Host "Added categories: $($categories.Count)" -ForegroundColor Cyan
Write-Host "Added menu items: $addedItems" -ForegroundColor Cyan
Write-Host "Please refresh the web page to see the new menu" -ForegroundColor Yellow