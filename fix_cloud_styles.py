import os

filepath = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN\main_app\templates\student_template\student_cloud_storage.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

dark_mode_style = """
    /* Dark Mode Overrides for Cloud Storage */
    .dark-mode .cloud-container {
        background: transparent !important; /* Inherit pure black backing */
    }
    .dark-mode .cloud-title h2 {
        color: #ffffff !important;
    }
    .dark-mode .category-btn {
        background: rgba(30, 30, 36, 0.45) !important;
        border-color: rgba(255, 255, 255, 0.05) !important;
        color: #cbd5e1 !important;
    }
    .dark-mode .category-btn.active {
        background: var(--accent-color) !important;
        color: white !important;
    }
    .dark-mode .file-card,
    .dark-mode .empty-state {
        background: rgba(30, 30, 36, 0.45) !important; /* Smooth glass card */
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
    }
    .dark-mode .file-info h5 {
        color: #ffffff !important;
    }
    .dark-mode .file-description {
        color: #94a3b8 !important;
    }
    .dark-mode .file-footer {
        border-top-color: rgba(255, 255, 255, 0.05) !important;
    }
    .dark-mode .action-btn {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #94a3b8 !important;
    }
    .dark-mode .modal-content {
        background: #0b1120 !important; /* Deeper Dark Slate modal */
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .dark-mode .form-control {
        background: rgba(0, 0, 0, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
    }
    .dark-mode .form-group label {
        color: #ffffff !important;
    }
    .dark-mode .modal-header, .dark-mode .modal-footer {
        border-color: rgba(255, 255, 255, 0.05) !important;
    }
"""

content = content.replace('</style>', dark_mode_style + '\n</style>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Cloud Storage styles updated successfully!")
