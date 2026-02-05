import os
import django
import sys
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realestate.settings")
django.setup()

from django.middleware.csrf import get_token

client = Client(enforce_csrf_checks=True)

# 1. GET request to login page to get the cookie
response = client.get('/signin/')
csrf_token = response.cookies['csrftoken'].value
print(f"Got CSRF token from cookie: {csrf_token}")

# 2. Extract CSRF token from the form (simulated)
# In a real browser, the {% csrf_token %} tag renders a hidden input.
# The Test Client's post method automatically handles CSRF if we don't pass it manually 
# BUT only if we use the client correctly.
# Ideally, we grab the token from the cookie and send it.

data = {
    'username': 'testadmin',
    'password': 'admin123_Password',
    'csrfmiddlewaretoken': csrf_token
}

print("Attempting login with CSRF token...")
response = client.post('/signin/', data)

if response.status_code == 302:
    print("Login SUCCESSFUL (Redirected)")
elif response.status_code == 200:
    print("Login FAILED (Stayed on page)")
    if "CSRF verification failed" in response.content.decode():
         print("CSRF ERROR DETECTED")
    else:
         print("Validation Error or other issue")
else:
    print(f"Unexpected status: {response.status_code}")
    if response.status_code == 403:
         print("403 Forbidden - Likely CSRF Failure")
         print(response.content.decode())
