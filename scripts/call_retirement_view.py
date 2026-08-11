import os, sys, django
sys.path.insert(0, r'd:\System\matumizi_system')
sys.path.insert(0, r'd:\System\matumizi_system\matoleo_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','matoleo_system.settings')
django.setup()
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from reports import views

User=get_user_model()
u=User.objects.get(username='Eric')
rf=RequestFactory()
req=rf.get('/reports/download/retirement/', {'date_from':'2026-08-01','date_to':'2026-08-31','format':'excel'})
req.user=u
fmt = req.GET.get('format','').strip().lower()
is_admin = u.is_staff or u.is_superuser
is_treasurer = hasattr(u, 'treasurer_profile')
print('fmt=', fmt)
print('is_admin=', is_admin, 'is_treasurer=', is_treasurer)

resp=views.download_retirement_report(req)
print('resp content-type:', resp.get('Content-Type'))
print('resp length:', len(resp.content))
# write out
with open('call_retirement_output.bin','wb') as f:
    f.write(resp.content)
print('Wrote call_retirement_output.bin')

import inspect
print('\n--- view source ---\n')
print(inspect.getsource(views.download_retirement_report))
print('\n--- view file ---\n')
print(views.__file__)
