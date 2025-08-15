import requests

response = requests.get('http://localhost:5000')
html = response.text

print("Searching for sales cards in HTML:")
lines = html.split('\n')

for i, line in enumerate(lines):
    if 'ยอดขาย' in line and 'text-xs font-weight-bold' in line:
        print(f'Line {i}: {line.strip()}')
        
print("\nSearching for specific IDs:")
for i, line in enumerate(lines):
    if 'id="current-week-sales"' in line or 'id="current-week-label"' in line:
        print(f'Line {i}: {line.strip()}')
        
print("\nSearching for warning class (current week card):")
for i, line in enumerate(lines):
    if 'text-warning' in line and 'ยอดขาย' in line:
        print(f'Line {i}: {line.strip()}')