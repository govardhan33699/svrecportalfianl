import re

file_path = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\hod_template\home_content.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

def fix_multiline_tags(match):
    tag = match.group(0)
    # Replace all newlines and multiple spaces with a single space inside the tag
    fixed_tag = re.sub(r'\s+', ' ', tag)
    return fixed_tag

# Match anything between {{ and }}
new_content = re.sub(r'{{[^}]+}}', fix_multiline_tags, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("ALL MULTILINE TAGS REJOINED SUCCESSFULLY.")
