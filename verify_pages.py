import os
import django
import sys
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realestate.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Ensure user exists (re-verify)
username = 'testadmin'
password = 'admin123_Password'
if not User.objects.filter(username=username).exists():
    print(f"User {username} not found! Cannot verify.")
    sys.exit(1)

client = Client()

print("--- 1. Testing Login ---")
login_resp = client.post('/signin/', {'username': username, 'password': password})
if login_resp.status_code == 302:
    print(f"Login successful (Redirects to: {login_resp.url})")
else:
    print(f"Login FAILED. Status: {login_resp.status_code}")
    print(login_resp.content.decode('utf-8')[:500])
    sys.exit(1)

urls_to_check = [
    '/dashboard/',
    '/buyer/dashboard/',
    '/seller/dashboard/',
    '/platform-admin/dashboard/',
    '/security/dashboard/',
    '/irt/dashboard/',
]

print("\n--- 2. Testing Dashboards ---")
for url in urls_to_check:
    print(f"Checking {url}...", end=" ")
    resp = client.get(url)
    if resp.status_code == 200:
        print("OK (200)")
    elif resp.status_code == 302:
         print(f"REDIRECT (302) -> {resp.url}")
    else:
        print(f"FAILED ({resp.status_code})")

print("\n--- 3. Testing Home Page Content ---")
resp = client.get('/')
content = resp.content.decode('utf-8')
if '>Home</a>' in content and '>Buy</a>' in content and '>Sell</a>' in content:
    print("FAIL: 'Home', 'Buy', 'Sell' links still found in HTML!")
else:
    # We should be careful not to match other instances of "Home" like in the title or footer if they are simpler text
    # The links were <a href="#">Home</a>
    if '<a href="#">Home</a>' not in content:
        print("PASS: <a href=\"#\">Home</a> link NOT found.")
    else:
        print("FAIL: <a href=\"#\">Home</a> link FOUND.")

print("\n--- 4. Testing Logout ---")
logout_resp = client.get('/signout/')
if logout_resp.status_code == 302:
    print(f"Logout successful (Redirects to: {logout_resp.url})")
else:
    print(f"Logout FAILED ({logout_resp.status_code})")
