from django.db import migrations
from django.contrib.auth.models import User

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('finance', 'Category')
    User = apps.get_model('auth', 'User')
    
    # Get or create a default admin user
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'email': 'admin@example.com'
        }
    )

    # Income categories
    income_categories = [
        {'name': 'Salary', 'description': 'Regular employment income', 'type': 'income'},
        {'name': 'Freelance', 'description': 'Income from freelance work', 'type': 'income'},
        {'name': 'Investments', 'description': 'Income from investments', 'type': 'income'},
        {'name': 'Bonus', 'description': 'Work bonuses and rewards', 'type': 'income'},
        {'name': 'Other Income', 'description': 'Other sources of income', 'type': 'income'},
    ]

    # Expense categories
    expense_categories = [
        {'name': 'Groceries', 'description': 'Food and household items', 'type': 'expense'},
        {'name': 'Rent/Mortgage', 'description': 'Housing expenses', 'type': 'expense'},
        {'name': 'Utilities', 'description': 'Electricity, water, gas, etc.', 'type': 'expense'},
        {'name': 'Transportation', 'description': 'Public transport, fuel, car maintenance', 'type': 'expense'},
        {'name': 'Entertainment', 'description': 'Movies, games, hobbies', 'type': 'expense'},
        {'name': 'Dining Out', 'description': 'Restaurants and takeout', 'type': 'expense'},
        {'name': 'Shopping', 'description': 'Clothing and personal items', 'type': 'expense'},
        {'name': 'Healthcare', 'description': 'Medical expenses and insurance', 'type': 'expense'},
        {'name': 'Education', 'description': 'Courses, books, training', 'type': 'expense'},
        {'name': 'Travel', 'description': 'Vacations and trips', 'type': 'expense'},
        {'name': 'Bills', 'description': 'Regular monthly bills', 'type': 'expense'},
        {'name': 'Subscriptions', 'description': 'Regular subscription services', 'type': 'expense'},
        {'name': 'Other Expenses', 'description': 'Miscellaneous expenses', 'type': 'expense'},
    ]

    # Create all categories
    for category_data in income_categories + expense_categories:
        Category.objects.get_or_create(
            name=category_data['name'],
            user=admin_user,
            defaults={
                'description': category_data['description'],
                'type': category_data['type']
            }
        )

def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('finance', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ] 