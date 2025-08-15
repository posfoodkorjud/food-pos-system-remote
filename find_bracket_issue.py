import re

# Read the JavaScript file
with open('C:\\Users\\KORJUD\\Desktop\\A_FOOD_POS4\\A_FOOD_POS\\FOOD_POS\\frontend\\js\\order.js', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Track brackets line by line
open_count = 0
close_count = 0
bracket_balance = 0
problematic_lines = []

for i, line in enumerate(lines):
    line_num = i + 1
    
    # Count brackets in this line
    line_open = line.count('{')
    line_close = line.count('}')
    
    open_count += line_open
    close_count += line_close
    bracket_balance += line_open - line_close
    
    # If balance goes negative, we have too many closing brackets
    if bracket_balance < 0:
        problematic_lines.append((line_num, line.strip(), bracket_balance))
    
    # Show lines with brackets
    if line_open > 0 or line_close > 0:
        print(f"Line {line_num}: {line.strip()[:80]} | Open: {line_open}, Close: {line_close}, Balance: {bracket_balance}")

print(f"\nTotal: Open brackets: {open_count}, Close brackets: {close_count}")
print(f"Final balance: {bracket_balance}")

if problematic_lines:
    print("\nProblematic lines (negative balance):")
    for line_num, line_content, balance in problematic_lines:
        print(f"Line {line_num}: {line_content} (Balance: {balance})")