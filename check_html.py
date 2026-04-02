from bs4 import BeautifulSoup
import sys

file_path = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\hod_template\view_student_detail.html"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    soup = BeautifulSoup(content, 'html.parser')
    
    # Prettify may help reveal missing tags
    print("Prettify check:")
    # beautifulsoup doesn't throw on unclosed tags easily, but we can inspect structure.
    # We can use html5lib for stricter parsing as well.
    print("Parsed successfully. No major BeautifulSoup crash.")
except Exception as e:
    print(f"Error: {e}")
