from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from finance.models import Category, Transaction, Budget

class Command(BaseCommand):
    help = 'Sets up a demo user with default categories'

    def handle(self, *args, **kwargs):
        # Remove all existing users and their related data
        self.stdout.write('Removing existing users and data...')
        User.objects.all().delete()
        
        # Create demo user
        self.stdout.write('Creating demo user...')
        demo_user = User.objects.create_user(
            username='demo',
            password='demo123',
            email='demo@example.com'
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully set up demo user'))
        self.stdout.write('Username: demo')
        self.stdout.write('Password: demo123') 