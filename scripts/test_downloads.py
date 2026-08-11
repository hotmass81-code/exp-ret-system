import os
import sys
sys.path.insert(0, r'd:\System\matumizi_system')
sys.path.insert(0, r'd:\System\matumizi_system\matoleo_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','matoleo_system.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
User=get_user_model()
try:
    u=User.objects.get(username='Eric')
except Exception as e:
    print('User error', e)
    raise
c=Client()
c.force_login(u)
urls=[('/reports/download/expenses/?date_from=2026-08-01&date_to=2026-08-31&format=excel','expense_test.xlsx'),
      ('/reports/download/retirement/?date_from=2026-08-01&date_to=2026-08-31&format=excel','retirement_test.xlsx')]
for url, fname in urls:
    resp=c.get(url, HTTP_HOST='127.0.0.1:8000')
    print(url, resp.status_code, resp.get('Content-Type'), len(resp.content))
    with open(fname,'wb') as f:
        f.write(resp.content)
    print('Wrote', fname)
