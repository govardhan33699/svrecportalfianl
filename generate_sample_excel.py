import pandas as pd
import os

# Create sample data
data = {
    'Roll Number': ['STU001', 'STU002'],
    'First Name': ['John', 'Jane'],
    'Last Name': ['Doe', 'Smith'],
    'Email': ['john.doe@test.com', 'jane.smith@test.com'],
    'Password': ['pass123', 'pass456'],
    'Gender': ['Male', 'Female'],
    'Address': ['Street 1, NY', 'Street 2, LA'],
    'Course': ['CSE (AI)', 'CSE (AI)'],
    'Session Start Year': [2025, 2025],
    'Session End Year': [2026, 2026]
}

df = pd.DataFrame(data)

# Create media directory if it doesn't exist
media_dir = os.path.join(os.getcwd(), 'media')
if not os.path.exists(media_dir):
    os.makedirs(media_dir)

file_path = os.path.join(media_dir, 'sample_students.xlsx')
df.to_excel(file_path, index=False)
print(f"Sample Excel created at: {file_path}")
