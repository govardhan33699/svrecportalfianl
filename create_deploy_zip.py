import os
import zipfile

def create_zip():
    project_dir = r"c:\Users\shiva\Downloads\SVRECPORTALMAIN"
    output_zip = r"c:\Users\shiva\Downloads\SVRECPORTAL_DEPLOY_WITH_DB.zip"
    exclude = ["venv", "node_modules", ".git", ".cursor", "__pycache__"]

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude]
            
            for file in files:
                # Exclude files
                if any(ext in file for ext in [".pyc"]):
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, project_dir)
                zipf.write(full_path, rel_path)
    
    print(f"Zip created successfully at {output_zip}")

if __name__ == "__main__":
    create_zip()
