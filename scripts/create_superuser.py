import os
import sys
from pathlib import Path
import django

# Ensure project root is on sys.path so `realestate` package can be imported
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser(username='admin', email='admin@example.com', password='AdminPass123!'):
    User = get_user_model()
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists")
        return
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created with password '{password}'")

if __name__ == '__main__':
    create_superuser()
