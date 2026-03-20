import os

filepath = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\student_template\student_attendance_report.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove background: #f8f9fa from the table cell
content = content.replace('background: #f8f9fa;', '')

# 2. Append Dark Mode styles right before the closing style tag </style>
dark_mode_style = """
    /* Dark Mode Overrides for Attendance Report */
    .dark-mode .attendance-table {
        border-color: rgba(255, 255, 255, 0.08) !important;
    }
    .dark-mode .attendance-table th {
        background-color: #090d16 !important; /* Dark blue/black headers */
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
    }
    .dark-mode .attendance-table td {
        background-color: transparent !important;
        border-color: rgba(255, 255, 255, 0.04) !important;
        color: #ffffff !important;
    }
    .dark-mode .total-row {
        background-color: rgba(255, 255, 255, 0.04) !important;
    }
    .dark-mode .attendance-stats-header {
        background: #090c14 !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
"""

content = content.replace('</style>', dark_mode_style + '\n</style>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Attendance Report styles updated successfully!")
