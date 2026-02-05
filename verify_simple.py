import os
import django
import sys
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realestate.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
username = 'testadmin'
password = 'admin123_Password'

client = Client()
client.login(username=username, password=password)

checks = [
    ('/dashboard/', 200),
    ('/buyer/dashboard/', 200),
    ('/seller/dashboard/', 200),
    ('/platform-admin/dashboard/', 200),
    ('/security/dashboard/', 200),
    ('/irt/dashboard/', 200),
]

for url, expected_status in checks:
    resp = client.get(url)
    msg = "OK" if resp.status_code == expected_status else f"FAIL({resp.status_code})"
    print(f"CHECK:{url}:{msg}")

resp = client.get('/')
content = resp.content.decode('utf-8')
if '>Home</a>' not in content:
    print("CHECK:HOME_LINKS_REMOVED:OK")
else:
    print("CHECK:HOME_LINKS_REMOVED:FAIL")
