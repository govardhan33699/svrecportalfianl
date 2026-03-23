import re

with open(r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\hod_template\home_content.html", "r", encoding="utf-8") as f:
    content = f.read()

tags = re.findall(r"{%\s*(\w+)", content)
print("All Django block tags found (first word):")
counts = {}
for t in tags:
    counts[t] = counts.get(t, 0) + 1

for t, c in counts.items():
    print(f"{t}: {c}")

print("\nVerifying pairs:")
pairs = [('if', 'endif'), ('for', 'endfor'), ('block', 'endblock'), ('comment', 'endcomment')]
for open_tag, close_tag in pairs:
    o = counts.get(open_tag, 0)
    c = counts.get(close_tag, 0)
    print(f"{open_tag.upper()}: {o} opens vs {c} closes")
    if o != c:
        print(f"  --> MISMATCH! {open_tag.upper()} needs attention!")

print("\nStreaming conditional and loop tags for structure check:")
full_tags = re.findall(r"{%\s*(if|endif|for|endfor|else|elif|block|endblock)\b[^%]*%}", content)
stack = []
for tag in full_tags:
    # Remove arguments to just get the tag name
    name = tag.split()[0]
    print(f"Tag: {name}")

print("\nDone.")
