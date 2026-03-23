import re

file_path = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\hod_views.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Match def words
matches = re.finditer(r"def\s+(\w+)\s*\(", content)

with open(r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\views_out_exact.txt", "w") as f:
    f.write("View functions found:\n")
    for m in matches:
        func_name = m.group(1)
        if 'manage' in func_name:
            line_num = content[:m.start()].count('\n') + 1
            f.write(f"Line {line_num}: {func_name}\n")
            # Print next 10 lines to find query
            block = content[m.start():m.start()+400]
            f.write(f"  BLOCK:\n{block}\n---\n")

print("DUMP COMPLETED")
