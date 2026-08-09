import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matoleo_system.settings')
django.setup()

out_path = os.path.join(os.getcwd(), 'create_superuser_out.txt')
try:
    User = get_user_model()
    username = 'Thomas'
    email = 'thomas@example.com'
    password = 'Hot@2000'
    if User.objects.filter(username=username).exists():
        msg = f"exists:{username}"
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        msg = f"created:{username}"
except Exception as e:
    msg = 'error:' + str(e)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(msg)
print(msg)
