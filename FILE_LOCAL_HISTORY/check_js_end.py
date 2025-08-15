with open('C:\\Users\\KORJUD\\Desktop\\A_FOOD_POS4\\A_FOOD_POS\\FOOD_POS\\frontend\\js\\order.js', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    
    # Find the last non-comment, non-empty line
    last_code_lines = []
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line and not line.startswith('//') and not line.startswith('/*') and line != '//':
            last_code_lines.append((i+1, lines[i]))
            if len(last_code_lines) >= 10:
                break
    
    print("Last 10 code lines:")
    for line_num, line_content in reversed(last_code_lines):
        print(f"Line {line_num}: {line_content}")
    
    # Check for syntax issues
    print("\nChecking for unclosed brackets...")
    open_brackets = content.count('{')
    close_brackets = content.count('}')
    print(f"Open brackets: {open_brackets}")
    print(f"Close brackets: {close_brackets}")
    print(f"Difference: {open_brackets - close_brackets}")