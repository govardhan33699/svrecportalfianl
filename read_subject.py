import glob
import os

path = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\registration\password_reset_subject*"
files = glob.glob(path)

with open(r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\subject_content.txt", 'w') as f_out:
    if files:
        filepath = files[0]
        f_out.write(f"File found: '{filepath}'\n")
        with open(filepath, 'r') as f:
            f_out.write("Content:\n")
            f_out.write(f.read())
    else:
        f_out.write("No files matched the pattern.")

print("Search completed.")
