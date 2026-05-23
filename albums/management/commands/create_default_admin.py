from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create default admin user if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        password = 'admin123'
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email='admin@example.com', password=password)
            self.stdout.write(self.style.SUCCESS(f'Created superuser {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists'))
