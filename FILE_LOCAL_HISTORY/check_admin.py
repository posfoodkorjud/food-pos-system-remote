import requests

response = requests.get('http://localhost:5000/admin')
print('Status:', response.status_code)

lines = response.text.split('\n')
for i, line in enumerate(lines):
    if 'ยอดขาย 7 วันล่าสุด' in line:
        print(f'Line {i+1}: {line.strip()}')
        # Print next few lines to see context
        for j in range(1, 10):
            if i+j < len(lines):
                print(f'Line {i+j+1}: {lines[i+j].strip()}')
        break

# Also check for current week card
for i, line in enumerate(lines):
    if 'สัปดาห์นี้' in line:
        print(f'Found สัปดาห์นี้ at line {i+1}: {line.strip()}')
        break
else:
    print('สัปดาห์นี้ not found in HTML')