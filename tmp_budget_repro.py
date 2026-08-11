import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / 'matoleo_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.test.client import Client
from core.models import Department, UserProfile, DepartmentBudget, Contribution, BudgetTransaction
from expenses.models import ExpenseRequest
from expenses.views import expense_dashboard
from reports.views import expenses_report

User = get_user_model()

print('creating department')
department, _ = Department.objects.get_or_create(name='BudgetReproDept', defaults={'code': 'BR', 'is_active': True})
print('department', department.id)

print('creating users')
user, created = User.objects.get_or_create(username='budgetuser', defaults={'email': 'budgetuser@example.com'})
if created:
    user.set_password('DebugPass123')
    user.save()

profile, _ = UserProfile.objects.get_or_create(user=user)
profile.department = department
profile.save()

print('creating budget and contribution')
db, _ = DepartmentBudget.objects.get_or_create(department=department, defaults={'bk_amount': 1000, 'mk_enabled': True})
db.bk_amount = 1000
db.mk_enabled = True
db.save()
contrib, _ = Contribution.objects.get_or_create(department=department, name='Contribution A', defaults={'amount': 500, 'is_active': True})
contrib.amount = 500
contrib.is_active = True
contrib.save()

print('creating expense request')
expense, created = ExpenseRequest.objects.get_or_create(
    form_number='BR-001',
    defaults={
        'first_name': 'Budget',
        'last_name': 'Tester',
        'phone_number': '1234567890',
        'department': department,
        'submitted_by': user,
        'date': '2026-08-01',
        'reason': 'Budget repro',
        'total_amount': 200,
        'status': 'approved',
        'budget_choice': 'BK',
        'contribution': None,
    }
)

print('expense', expense.pk)

request = RequestFactory().get('/expenses/')
request.user = user
try:
    response = expense_dashboard(request)
    print('expense_dashboard ok', response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()

request = RequestFactory().get('/reports/expenses/')
request.user = user
try:
    response = expenses_report(request)
    print('reports ok', response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
