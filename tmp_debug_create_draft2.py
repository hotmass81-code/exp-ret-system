import os
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root / 'matoleo_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
import django
import traceback

django.setup()
from django.test import Client
from django.contrib.auth.models import User
from core.models import Department, UserProfile

log_path = repo_root / 'tmp_debug_create_draft2.log'
with open(log_path, 'w', encoding='utf-8') as log:
    def write(*args):
        line = ' '.join(str(a) for a in args)
        log.write(line + '\n')
        log.flush()
        print(line)

    try:
        user, created = User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'})
        if created:
            write('created user')
        user.set_password('pass123')
        user.save()
        write('saved user', user.username)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if not profile.department:
            dept, _ = Department.objects.get_or_create(name='Test Dept')
            profile.department = dept
            profile.save()
            write('created department', dept.id)

        client = Client()
        logged_in = client.login(username='testuser', password='pass123')
        write('logged_in', logged_in)
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
        write('response status', response.status_code)
        write('response redirected', response.url if response.status_code in (301, 302) else None)
        write('response content', response.content[:200])
        write('cookies', dict(client.cookies))
    except Exception as exc:
        write('EXCEPTION', exc)
        traceback.print_exc(file=log)
        traceback.print_exc()
