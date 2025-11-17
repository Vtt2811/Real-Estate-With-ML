import os
import sys
from pathlib import Path
import django

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate.settings')
django.setup()

from django.contrib.auth import get_user_model

def change_admin_password(username='admin', new_password='Admin@123456'):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        print(f"✓ Password for '{username}' changed successfully to '{new_password}'")
    except User.DoesNotExist:
        print(f"✗ User '{username}' not found")

if __name__ == '__main__':
    change_admin_password()
