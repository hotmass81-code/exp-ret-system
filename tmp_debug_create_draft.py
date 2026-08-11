import os
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root / 'matoleo_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from core.models import Department, UserProfile

# Setup test data
user, _ = User.objects.get_or_create(username='testuser', defaults={'email':'test@example.com'})
user.set_password('pass123')
user.save()
profile, _ = UserProfile.objects.get_or_create(user=user)
if not profile.department:
    dept, _ = Department.objects.get_or_create(name='Test Dept')
    profile.department = dept
    profile.save()

client = Client()
logged_in = client.login(username='testuser', password='pass123')
print('logged_in', logged_in)
response = client.post('/expenses/new/', {
    'first_name': 'Test',
    'last_name': 'Draft',
    'phone_number': '+255123456789',
    'department': str(profile.department.id),
    'date': '2026-08-10',
    'reason': 'Draft save test',
    'item_description[]': ['Item 1'],
    'item_amount[]': ['100.00'],
    'budget_choice': 'BK',
}, HTTP_HOST='127.0.0.1')
print('status_code', response.status_code)
print('redirected', response.url if response.status_code in (301,302) else None)
print('content', response.content[:1000])
print('cookies', client.cookies)
