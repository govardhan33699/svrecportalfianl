import os
import re

search_dir = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates"
pattern = re.compile(r"<nav class=\"erpnext-navbar", re.IGNORECASE)

matches = []
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(".html"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern.search(content):
                        matches.append(filepath)
            except Exception as e:
                pass

print("--- NAVBAR MATCHES ---")
for m in matches:
    print(m)
print("--- END ---")
