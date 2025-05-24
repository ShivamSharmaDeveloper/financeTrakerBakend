from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import DatabaseError
import os
import sys

class Command(BaseCommand):
    help = 'Creates a superuser automatically.'

    def handle(self, *args, **options):
        try:
            username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
            email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
            password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')

            self.stdout.write(f'Attempting to create superuser {username}...')

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.SUCCESS(f'Superuser {username} already exists'))
                return

            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser {username}'))

        except DatabaseError as e:
            self.stdout.write(self.style.ERROR(f'Database error: {e}'))
            sys.exit(1)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {e}'))
            sys.exit(1) 