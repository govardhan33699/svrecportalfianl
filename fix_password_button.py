import os

filepath = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\student_template\student_change_password.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace button text
content = content.replace('>Change Password</button>', '>Save Changes</button>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Submit button updated successfully!")
