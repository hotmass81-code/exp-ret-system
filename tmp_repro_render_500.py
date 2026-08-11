import os
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / 'matoleo_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
os.environ['ALLOWED_HOSTS'] = 'testserver,.onrender.com,localhost,127.0.0.1'
import django
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from core.models import Department, UserProfile

client = Client()
host = 'retirement-and-expenses-system.onrender.com'
print('ALLOWED_HOSTS:', os.environ['ALLOWED_HOSTS'])
print('HTTP_HOST:', host)

# create a department and user with a unique suffix to avoid duplicates
suffix = os.urandom(4).hex()
try:
    dept = Department.objects.create(name=f'RenderTestDept_{suffix}')
except Exception:
    dept = Department.objects.filter(name=f'RenderTestDept_{suffix}').first()

user = User.objects.create_user(username=f'rendertestuser_{suffix}', password='pass')
profile, _ = UserProfile.objects.get_or_create(user=user)
profile.department = dept
profile.save()
client.login(username=f'rendertestuser_{suffix}', password='pass')

paths = ['/expenses/', '/reports/expenses/', '/admin-panel/budgets/']
for path in paths:
    response = client.get(path)
    print('PATH:', path)
    print('STATUS:', response.status_code)
    print('CONTENT-START:', response.content[:200].decode('utf-8', 'ignore').replace('\n',' ').replace('\r',' '))
    print('-' * 80)

# test as admin for budgets and reports
admin = User.objects.create_superuser(username=f'renderadmin_{suffix}', email=f'admin_{suffix}@test.local', password='pass')
client.login(username=f'renderadmin_{suffix}', password='pass')
for path in ['/admin-panel/budgets/', '/reports/expenses/']:
    response = client.get(path)
    print('ADMIN PATH:', path)
    print('STATUS:', response.status_code)
    print('CONTENT-START:', response.content[:200].decode('utf-8', 'ignore').replace('\n',' ').replace('\r',' '))
    print('-' * 80)
