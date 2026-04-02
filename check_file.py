import sys

file_path = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\hod_template\view_student_detail.html"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start = max(160, 0)
    end = min(200, len(lines))
    
    print(f"--- Printing Lines {start+1} to {end} with raw representations ---")
    for i in range(start, end):
        print(f"{i+1}: {repr(lines[i])}")
        
except Exception as e:
    print(f"Error: {e}")
