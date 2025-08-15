@echo off
chcp 65001 >nul
echo Starting menu update...

REM Get current menu items and delete them
echo Deleting current menu items...
for /L %%i in (1,1,100) do (
    curl -s -X DELETE "http://localhost:5000/api/menu/items/%%i" >nul 2>&1
)

REM Get current categories and delete them
echo Deleting current categories...
for /L %%i in (1,1,20) do (
    curl -s -X DELETE "http://localhost:5000/api/menu/categories/%%i" >nul 2>&1
)

REM Add new categories
echo Adding new categories...

REM Category 1: อาหารจานเดียว
curl -s -X POST "http://localhost:5000/api/menu/categories" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"อาหารจานเดียว\", \"description\": \"อาหารจานเดียวหลากหลายรสชาติ\"}"

REM Category 2: อาหารทานเล่น
curl -s -X POST "http://localhost:5000/api/menu/categories" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"อาหารทานเล่น\", \"description\": \"อาหารทานเล่นและของว่าง\"}"

REM Category 3: ยำ / สลัด
curl -s -X POST "http://localhost:5000/api/menu/categories" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ยำ / สลัด\", \"description\": \"ยำและสลัดสดใส\"}"

REM Category 4: เครื่องดื่มเย็น / ร้อน
curl -s -X POST "http://localhost:5000/api/menu/categories" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"เครื่องดื่มเย็น / ร้อน\", \"description\": \"เครื่องดื่มหลากหลาย\"}"

REM Category 5: ของหวาน
curl -s -X POST "http://localhost:5000/api/menu/categories" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ของหวาน\", \"description\": \"ของหวานและขนมหวาน\"}"

echo Categories added successfully!

REM Wait a moment for categories to be created
timeout /t 2 /nobreak >nul

echo Adding menu items...

REM อาหารจานเดียว (category_id will be auto-assigned, assuming 1)
curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวผัดหมู / ไก่ / กุ้ง\", \"price\": 60, \"category_id\": 1, \"description\": \"ข้าวผัดหอมๆ เลือกได้ทั้งหมู ไก่ หรือกุ้ง\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวกระเพราหมูสับไข่ดาว\", \"price\": 65, \"category_id\": 1, \"description\": \"ข้าวกระเพราหมูสับรสจัดจ้าน เสิร์ฟพร้อมไข่ดาว\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวหมูกระเทียม\", \"price\": 60, \"category_id\": 1, \"description\": \"ข้าวหมูกระเทียมหอมกรุ่น\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวไข่เจียวหมูสับ\", \"price\": 55, \"category_id\": 1, \"description\": \"ข้าวไข่เจียวฟูๆ ใส่หมูสับ\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวผัดกะเพราเต้าหู้ (มังสวิรัติ)\", \"price\": 60, \"category_id\": 1, \"description\": \"ข้าวผัดกะเพราเต้าหู้สำหรับคนรักสุขภาพ\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวราดแกงเขียวหวานไก่\", \"price\": 70, \"category_id\": 1, \"description\": \"ข้าวราดแกงเขียวหวานไก่เข้มข้น\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวคลุกกะปิ\", \"price\": 65, \"category_id\": 1, \"description\": \"ข้าวคลุกกะปิรสชาติดั้งเดิม\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวผัดน้ำพริกลงเรือ\", \"price\": 70, \"category_id\": 1, \"description\": \"ข้าวผัดน้ำพริกลงเรือรสเผ็ดหวาน\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวคั่วกลิ้งหมู\", \"price\": 70, \"category_id\": 1, \"description\": \"ข้าวคั่วกลิ้งหมูสูตรใต้\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวหน้าไก่เทอริยากิ\", \"price\": 75, \"category_id\": 1, \"description\": \"ข้าวหน้าไก่เทอริยากิสไตล์ญี่ปุ่น\"}"

REM อาหารทานเล่น (category_id: 2)
curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"เฟรนช์ฟรายส์\", \"price\": 45, \"category_id\": 2, \"description\": \"มันฝรั่งทอดกรอบนอกนุ่มใน\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"นักเก็ตไก่\", \"price\": 50, \"category_id\": 2, \"description\": \"นักเก็ตไก่ทอดกรอบ\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ไก่ป๊อป\", \"price\": 55, \"category_id\": 2, \"description\": \"ไก่ป๊อปชิ้นเล็กทอดกรอบ\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"หมูทอดจิ้มแจ่ว\", \"price\": 60, \"category_id\": 2, \"description\": \"หมูทอดกรอบเสิร์ฟพร้อมแจ่ว\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ไก่ทอดเกลือ\", \"price\": 55, \"category_id\": 2, \"description\": \"ไก่ทอดเกลือรสชาติกำลังดี\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ปีกไก่ทอดน้ำปลา\", \"price\": 60, \"category_id\": 2, \"description\": \"ปีกไก่ทอดน้ำปลาหอมหวาน\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ลูกชิ้นลวกจิ้ม\", \"price\": 45, \"category_id\": 2, \"description\": \"ลูกชิ้นลวกสดใหม่\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"เกี๊ยวซ่าทอด\", \"price\": 50, \"category_id\": 2, \"description\": \"เกี๊ยวซ่าทอดกรอบ\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"แหนมคลุก\", \"price\": 55, \"category_id\": 2, \"description\": \"แหนมคลุกรสเปรี้ยวหวาน\"}"

curl -s -X POST "http://localhost:5000/api/menu/items" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"name\": \"ข้าวโพดชีส\", \"price\": 50, \"category_id\": 2, \"description\": \"ข้าวโพดหวานโรยชีส\"}"

echo Menu update completed!
echo Please refresh the web page to see the new menu.
pause