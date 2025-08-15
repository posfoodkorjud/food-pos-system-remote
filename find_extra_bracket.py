# Read the JavaScript file
with open('C:\\Users\\KORJUD\\Desktop\\A_FOOD_POS4\\A_FOOD_POS\\FOOD_POS\\frontend\\js\\order.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track brackets
balance = 0
for i, line in enumerate(lines):
    line_num = i + 1
    open_brackets = line.count('{')
    close_brackets = line.count('}')
    
    balance += open_brackets - close_brackets
    
    # Print lines with brackets and show balance
    if open_brackets > 0 or close_brackets > 0:
        print(f"Line {line_num}: Balance={balance} | {line.strip()[:100]}")
        
        # If balance goes negative, we found the problem
        if balance < 0:
            print(f"*** PROBLEM FOUND AT LINE {line_num} ***")
            print(f"Line content: {line.strip()}")
            break

print(f"\nFinal balance: {balance}")
if balance == -1:
    print("There is exactly 1 extra closing bracket.")
elif balance < 0:
    print(f"There are {abs(balance)} extra closing brackets.")
elif balance > 0:
    print(f"There are {balance} missing closing brackets.")
else:
    print("Brackets are balanced.")