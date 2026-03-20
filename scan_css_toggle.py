import os
import re

search_dir = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\static"
pattern = re.compile(r"\.theme-toggle", re.IGNORECASE)

matches = []
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(".css"):
            filepath = os.path.join(root, file)
            # Skip the known one to see others
            if "erpnext-style.css" in filepath:
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern.search(content):
                        matches.append(filepath)
            except Exception as e:
                pass

print("--- CSS MATCHES ---")
for m in matches:
    print(m)
print("--- END ---")
