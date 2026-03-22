import os

start_dir = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN"
output_file = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\all_subjects.txt"

paths = []
for root, dirs, files in os.walk(start_dir):
    for f in files:
        if "password_reset_subject" in f:
            paths.append(os.path.join(root, f))

with open(output_file, 'w') as f_out:
    if paths:
        for p in paths:
            f_out.write(p + '\n')
    else:
        f_out.write("No matching files found anywhere.")

print(f"Count: {len(paths)}")
