import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root / 'matoleo_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'testserver,.onrender.com,localhost,127.0.0.1'

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Department, UserProfile

print('DEBUG', os.environ['DJANGO_DEBUG'])
print('ALLOWED_HOSTS', os.environ['ALLOWED_HOSTS'])

import uuid

try:
    client = Client()
    print('Client created')
    sys.stdout.flush()
    username = f'reprouser_{uuid.uuid4().hex[:8]}'
    print('Creating user', username)
    sys.stdout.flush()
    user = User.objects.create_user(username=username, password='pass')
    print('User created', user.username)
    sys.stdout.flush()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    print('Profile obtained', profile.pk)
    sys.stdout.flush()
    department_name = f'ReproDept_{uuid.uuid4().hex[:8]}'
    profile.department = Department.objects.create(name=department_name)
    profile.save()
    print('Department created', department_name)
    sys.stdout.flush()
    print('about to login')
    sys.stdout.flush()
    login_ok = client.login(username=username, password='pass')
    print('login', login_ok)
    sys.stdout.flush()

    paths = ['/expenses/', '/reports/expenses/', '/admin-panel/budgets/']
    for path in paths:
        try:
            print('Requesting', path)
            sys.stdout.flush()
            response = client.get(path, SERVER_NAME='retirement-and-expenses-system.onrender.com', HTTP_HOST='retirement-and-expenses-system.onrender.com')
            print('PATH:', path)
            print('STATUS:', response.status_code)
            print('CONTENT-START:', response.content[:400].decode('utf-8', 'ignore').replace('\n',' ').replace('\r',' '))
            print('-' * 80)
            sys.stdout.flush()
        except Exception as exc:
            print('REQUEST EXCEPTION FOR', path, exc)
            traceback.print_exc()
            sys.stdout.flush()
    print('DONE')
    sys.stdout.flush()
except Exception as e:
    import traceback
    print('EXCEPTION:', e)
    traceback.print_exc()
    sys.stdout.flush()
