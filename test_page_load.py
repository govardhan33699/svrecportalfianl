import requests
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def test_admin_page():
    session = requests.Session()
    # First, get the login page to get CSRF token
    response = session.get('http://127.0.0.1:8000/')
    csrf_token = session.cookies.get('csrftoken')
    
    # Login
    login_data = {
        'email': 'testadmin@admin.com',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token
    }
    response = session.post('http://127.0.0.1:8000/doLogin/', data=login_data, headers={'Referer': 'http://127.0.0.1:8000/'})
    
    print(f"Login Status: {response.status_code}")
    print(f"Final URL: {response.url}")
    
    # Try to access admin home
    response = session.get('http://127.0.0.1:8000/admin/home/')
    print(f"Admin Home Status: {response.status_code}")
    if response.status_code == 500:
        print("Error 500 detected!")
        # Try to find the error in the response text if DEBUG=True
        if 'Traceback' in response.text:
            print("Found Traceback in response!")
            with open('error_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
    elif response.status_code == 200:
        print("Admin Home loaded successfully!")
    else:
        print(f"Received status code: {response.status_code}")

if __name__ == "__main__":
    test_admin_page()
