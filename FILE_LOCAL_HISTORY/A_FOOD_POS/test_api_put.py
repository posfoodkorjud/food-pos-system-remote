import requests
import json

# Test the PUT API endpoint directly
url = "http://localhost:5000/api/menu/items/344"
data = {
    "name": "Test Menu",
    "price": 100.0,
    "category_id": 1,
    "description": "Test description",
    "image_url": "test.jpg",
    "preparation_time": 15,
    "is_available": True,
    "food_option_type": "spice"
}

headers = {
    "Content-Type": "application/json"
}

print("Testing PUT request to:", url)
print("Data being sent:", json.dumps(data, indent=2))

try:
    response = requests.put(url, json=data, headers=headers)
    print("\nResponse status:", response.status_code)
    print("Response headers:", dict(response.headers))
    print("Response content:", response.text)
    
    if response.status_code == 200:
        print("\n✅ API call successful!")
    else:
        print("\n❌ API call failed!")
        
except Exception as e:
    print("\n❌ Error occurred:", str(e))