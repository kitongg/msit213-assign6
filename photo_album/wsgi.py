import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_album.settings')

application = get_wsgi_application()

if os.environ.get('RUN_MIGRATIONS_ON_STARTUP', '1') == '1':
    call_command('migrate', interactive=False, verbosity=1)
