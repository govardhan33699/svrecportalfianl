import os

folder = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\registration"

with open(r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\reg_files.txt", 'w') as f_out:
    for f in os.listdir(folder):
        f_out.write(f"'{f}'\n")

print("Files listed.")
