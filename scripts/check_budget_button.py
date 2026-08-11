import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
try:
    # Ensure project root is on sys.path so Python can import the project package
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # Also add the package dir so apps like 'core' import as top-level modules
    package_dir = os.path.join(project_root, 'matoleo_system')
    if package_dir not in sys.path:
        sys.path.insert(0, package_dir)
    django.setup()
except Exception as e:
    print('Django setup error:', e)
    sys.exit(2)

from django.test import Client
from django.contrib.auth.models import User
from core.models import Department, UserProfile
from core.models import Treasurer
from django.conf import settings

# Create or get test department and user
dept, _ = Department.objects.get_or_create(name='AutoTestDept')
user, created = User.objects.get_or_create(username='budget_tester', defaults={'first_name':'Budget','last_name':'Tester','email':'budget@test.local'})
if created:
    user.set_password('password')
    user.save()

profile, _ = UserProfile.objects.get_or_create(user=user)
profile.department = dept
profile.save()

# Create a treasurer user for treasurer dashboard tests
treasurer_user, tcreated = User.objects.get_or_create(username='treasurer_user', defaults={'first_name':'Treasurer','last_name':'User','email':'treasurer@test.local'})
if tcreated:
    treasurer_user.set_password('password')
    treasurer_user.save()
treasurer_profile, _ = Treasurer.objects.get_or_create(user=treasurer_user)
treasurer_profile.is_active = True
treasurer_profile.save()

c = Client()
c.force_login(user)
# Ensure test host is allowed
try:
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS += ['testserver']
except Exception:
    pass

try:
    r = c.get('/expenses/')
    print('Status:', r.status_code)
    content = r.content.decode('utf-8')
    found_id = 'id="openBudgetBtn"' in content
    found_text = '>Budget<' in content
    print('Has openBudgetBtn:', found_id)
    print('Has Budget text:', found_text)
    idx = content.find('id="openBudgetBtn"')
    if idx != -1:
        start = max(0, idx-200)
        end = idx+200
        print('\n--- snippet around button ---')
        print(content[start:end])
        print('--- end snippet ---\n')
except Exception as e:
    print('Request error:', e)
    import traceback
    traceback.print_exc()

print('Done')

# Check treasurer dashboard for Manage Budgets button
c.force_login(treasurer_user)
try:
    r = c.get('/treasurer-dashboard/')
    print('Treasurer Status:', r.status_code)
    content = r.content.decode('utf-8')
    has_manage = ('/admin-panel/budgets/' in content) or ('Manage Budgets' in content)
    print('Has Manage Budgets link/text:', has_manage)
    if has_manage:
        idx = content.find('Manage Budgets')
        if idx != -1:
            start = max(0, idx-120)
            end = idx+120
            print('\n--- snippet around manage budgets ---')
            print(content[start:end])
            print('--- end snippet ---\n')
except Exception as e:
    print('Treasurer request error:', e)
    import traceback
    traceback.print_exc()
