import os

filepath = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\registration\erpnext_base.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add newlines after tags to expand them nicely
formatted = content.replace('</head>', '\n</head>').replace('<body>', '\n<body>').replace('</div>', '</div>\n')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(formatted)

print("Split completed.")
