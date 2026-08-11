import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / 'matoleo_system'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'matoleo_system.settings'
os.environ['ALLOWED_HOSTS'] = 'testserver,.onrender.com,localhost,127.0.0.1'
os.environ['DJANGO_DEBUG'] = 'True'

print('START')
try:
    import django
    print('imported django')
    django.setup()
    print('django.setup complete')
    from django.test import Client
    from django.contrib.auth import get_user_model
    from core.models import Department, UserProfile
    print('imported models and client')

    client = Client()
    User = get_user_model()
    dept = Department.objects.create(name='RenderTestDeptDebug')
    print('created dept', dept.id)
    user = User.objects.create_user(username='renderuserdebug', password='pass')
    print('created user', user.id)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.department = dept
    profile.save()
    print('saved profile')
    logged_in = client.login(username='renderuserdebug', password='pass')
    print('login success', logged_in)
    for path in ['/expenses/', '/reports/expenses/', '/admin-panel/budgets/']:
        try:
            response = client.get(path, HTTP_HOST='retirement-and-expenses-system.onrender.com')
            print('PATH', path, 'STATUS', response.status_code)
            print('CONTENT', response.content[:300].decode('utf-8', 'ignore').replace('\n',' ').replace('\r',' '))
        except Exception as e:
            print('PATH', path, 'EXCEPTION', repr(e))
            import traceback
            traceback.print_exc()

    admin = User.objects.create_superuser(username='renderadmindebug', email='admin@debug.local', password='pass')
    client.login(username='renderadmindebug', password='pass')
    print('admin login success')
    for path in ['/admin-panel/budgets/', '/reports/download/expenses/', '/reports/download/retirement/']:
        try:
            params = {'date_from': '2026-08-01', 'date_to': '2026-08-31', 'format': 'excel'} if 'download' in path else {}
            response = client.get(path, params, HTTP_HOST='retirement-and-expenses-system.onrender.com')
            print('ADMIN PATH', path, 'STATUS', response.status_code)
            if response.status_code != 200:
                print('ADMIN CONTENT', response.content[:300].decode('utf-8', 'ignore').replace('\n',' ').replace('\r',' '))
        except Exception as e:
            print('ADMIN PATH', path, 'EXCEPTION', repr(e))
            import traceback
            traceback.print_exc()
except Exception as outer:
    print('OUTER EXCEPTION', repr(outer))
    import traceback
    traceback.print_exc()
print('END')
