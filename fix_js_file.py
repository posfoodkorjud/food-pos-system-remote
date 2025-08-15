# Read the original file and clean it
with open('C:\\Users\\KORJUD\\Desktop\\A_FOOD_POS4\\A_FOOD_POS\\FOOD_POS\\frontend\\js\\order.js', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Find the last meaningful line of code
last_code_line_index = -1
for i in range(len(lines) - 1, -1, -1):
    line = lines[i].strip()
    if line and not line.startswith('//') and not line.startswith('/*') and line != '//':
        last_code_line_index = i
        break

print(f"Last meaningful code line found at index: {last_code_line_index}")
print(f"Line content: {lines[last_code_line_index]}")

# Keep only lines up to the last meaningful code line
clean_lines = lines[:last_code_line_index + 1]

# Write the cleaned content back
with open('C:\\Users\\KORJUD\\Desktop\\A_FOOD_POS4\\A_FOOD_POS\\FOOD_POS\\frontend\\js\\order.js', 'w', encoding='utf-8') as f:
    f.write('\n'.join(clean_lines))

print(f"File cleaned. Reduced from {len(lines)} lines to {len(clean_lines)} lines.")

# Verify bracket count
cleaned_content = '\n'.join(clean_lines)
open_brackets = cleaned_content.count('{')
close_brackets = cleaned_content.count('}')
print(f"Open brackets: {open_brackets}")
print(f"Close brackets: {close_brackets}")
print(f"Difference: {open_brackets - close_brackets}")