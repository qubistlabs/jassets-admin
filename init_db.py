from os import getenv

from django.contrib.auth.models import User


ADMIN_LOGIN = getenv('ADMIN_LOGIN', 'admin')
ADMIN_PASSWORD = getenv('ADMIN_PASSWORD')
ADMIN_EMAIL = getenv('ADMIN_EMAIL')

if ADMIN_LOGIN is None or ADMIN_PASSWORD is None:
    raise Exception(
        'Admin credentials not set. '
        'Please specify environment variables ADMIN_LOGIN and ADMIN_PASSWORD')

admin_exists = User.objects.filter(username=ADMIN_LOGIN).exists()

if not admin_exists:
    User.objects.create_superuser(
        username=ADMIN_LOGIN,
        password=ADMIN_PASSWORD,
        email=ADMIN_EMAIL,
    )
    print('Administrator account created')
else:
    print('User with specified username already exists')
