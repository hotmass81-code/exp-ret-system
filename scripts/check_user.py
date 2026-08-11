import os
import sys
import django
sys.path.insert(0, r'd:\System\matumizi_system')
sys.path.insert(0, r'd:\System\matumizi_system\matoleo_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    u = User.objects.get(username='Eric')
except Exception as e:
    print('User lookup error:', e)
    raise
print('username:', u.username)
print('is_staff:', u.is_staff)
print('is_superuser:', u.is_superuser)
print('has treasurer_profile:', hasattr(u, 'treasurer_profile'))
print('has approver_profile:', hasattr(u, 'approver_profile'))
