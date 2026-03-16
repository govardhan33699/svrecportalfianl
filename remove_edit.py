import re
import os

filepath = 'main_app/templates/student_template/student_view_profile.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The specific HTML starting the "Update Profile Info" section
start_marker = '<div class="row mt-4">         <div class="col-md-12">             <div class="card card-dark shadow-sm">                 <div class="card-header">                     <h3 class="card-title">Update Profile Info</h3>'

start_idx = content.find(start_marker)

if start_idx != -1:
    end_idx = content.find('</section>', start_idx)
    if end_idx != -1:
        new_content = content[:start_idx] + content[end_idx:]
        
        # Now remove the custom JS section at the end
        start_js = new_content.find('{% block custom_js %}')
        if start_js != -1:
            end_js = new_content.find('{% endblock custom_js %}', start_js) + len('{% endblock custom_js %}')
            new_content = new_content[:start_js] + new_content[end_js:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully removed 'Update Profile Info' section.")
    else:
        print("End marker </section> not found after start marker.")
else:
    print("Start marker 'Update Profile Info' not found in file.")
