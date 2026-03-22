import os

start_dir = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN"
output_file = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\settings_path.txt"

paths = []
for root, dirs, files in os.walk(start_dir):
    if "settings.py" in files:
        paths.append(os.path.join(root, "settings.py"))

with open(output_file, 'w') as f:
    for p in paths:
        f.write(p + '\n')

print(f"File found count: {len(paths)}")
