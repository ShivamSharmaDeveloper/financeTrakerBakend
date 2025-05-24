from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category
from .utils import get_default_categories

@receiver(post_save, sender=User)
def create_user_categories(sender, instance, created, **kwargs):
    if created:  # Only for newly created users
        # Get default categories from utils
        default_categories = get_default_categories()
        
        # Create default categories for the new user
        for category_data in default_categories:
            Category.objects.create(
                name=category_data['name'],
                description=category_data['description'],
                type=category_data['type'],
                user=instance
            ) 