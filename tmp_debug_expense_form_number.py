import os
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root / 'matoleo_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
import django
django.setup()
from expenses.models import ExpenseRequest
qs = ExpenseRequest.objects.filter(form_number__startswith='EXP-2026-').order_by('form_number')
print('count', qs.count())
for form in qs.values_list('form_number', flat=True):
    print(form)
print('latest', qs.reverse().values_list('form_number', flat=True).first())
