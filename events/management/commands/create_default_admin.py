from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create default admin user (development only).'

    def handle(self, *args, **options):
        User = get_user_model()
        email = 'adminevent@gmail.event'
        username = 'adminevent'
        password = 'rootroot'

        # Avoid overwriting existing users
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser created: {email} (username: {username})'))
