import re

file_path = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\hod_views.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Match def words
matches = re.finditer(r"def\s+(\w+)\s*\(", content)

print("Found view functions containing 'manage':")
for m in matches:
    func_name = m.group(1)
    if 'manage' in func_name:
        # Find line number
        line_num = content[:m.start()].count('\n') + 1
        print(f"Line {line_num}: {func_name}")

print("\nDone.")
