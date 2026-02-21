import os
from datetime import datetime

paths = [
    r"c:\Users\shiva\Downloads\College-ERP-main\db.sqlite3",
    r"c:\Users\shiva\Downloads\College-ERP-main\College-ERP-main\db.sqlite3"
]

for p in paths:
    if os.path.exists(p):
        stat = os.stat(p)
        mtime = datetime.fromtimestamp(stat.st_mtime)
        print(f"File: {p}")
        print(f"  Size: {stat.st_size} bytes")
        print(f"  Modified: {mtime}")
    else:
        print(f"File: {p} - NOT FOUND")
