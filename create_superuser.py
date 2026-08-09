import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
django.setup()

User = get_user_model()
username = 'Thomas'
email = 'thomas@example.com'
password = 'Hot@2000'

if User.objects.filter(username=username).exists():
    print(f"Superuser '{username}' already exists")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created")
