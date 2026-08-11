import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / 'matoleo_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'retirement-and-expenses-system.onrender.com,localhost,127.0.0.1'
os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://retirement-and-expenses-system.onrender.com'

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()
user, created = User.objects.get_or_create(username='proddebug', defaults={'email': 'proddebug@example.com', 'is_staff': True, 'is_superuser': True})
if created:
    user.set_password('DebugPass123')
    user.save()

client = Client()
logged = client.login(username='proddebug', password='DebugPass123')
print('logged in', logged)

for path in ['/expenses/', '/reports/expenses/', '/admin-panel/budgets/']:
    try:
        response = client.get(path, HTTP_HOST='retirement-and-expenses-system.onrender.com')
        print(path, response.status_code)
        if response.status_code >= 400:
            print(response.content[:1000].decode('utf-8', 'ignore'))
    except Exception as e:
        import traceback
        traceback.print_exc()
