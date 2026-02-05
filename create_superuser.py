import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realestate.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'testadmin'
email = 'admin@example.com'
password = 'admin123_Password'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
