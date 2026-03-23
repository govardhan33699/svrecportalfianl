import re

with open(r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\hod_template\home_content.html", "r", encoding="utf-8") as f:
    content = f.read()

# Match standard block tags including {% empty %} wait, list them
tags = re.findall(r"{%\s*(if|else|elif|endif|for|empty|endfor|block|endblock)\b", content)

with open(r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\tags_out.txt", "w") as f:
    f.write("ORDERED TAGS LIST:\n")
    for t in tags:
        f.write(f"{t}\n")
    
    # Also Count them
    f.write("\nSTATS:\n")
    counts = {}
    for t in tags:
        counts[t] = counts.get(t, 0) + 1
    
    for t, c in counts.items():
        f.write(f"{t}: {c}\n")

print("DUMP COMPLETED TO tags_out.txt")
