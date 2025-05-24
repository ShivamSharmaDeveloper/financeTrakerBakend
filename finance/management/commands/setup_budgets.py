from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from finance.models import Category, Budget
from datetime import date
from calendar import monthrange

class Command(BaseCommand):
    help = 'Set up default monthly budgets for categories'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to set up budgets for')

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options['username'])
            
            # Get current month's start and end dates
            today = timezone.now().date()
            start_date = today.replace(day=1)
            _, last_day = monthrange(today.year, today.month)
            end_date = today.replace(day=last_day)

            # Default budget amounts for expense categories
            default_budgets = {
                'Groceries': 5000,
                'Rent/Mortgage': 15000,
                'Utilities': 3000,
                'Transportation': 2000,
                'Entertainment': 2000,
                'Dining Out': 3000,
                'Shopping': 3000,
                'Healthcare': 2000,
                'Education': 2000,
                'Travel': 5000,
                'Bills': 5000,
                'Subscriptions': 1000,
                'Other Expenses': 2000,
            }

            budgets_created = 0
            budgets_updated = 0

            # Get all expense categories for the user
            categories = Category.objects.filter(user=user, type='expense')

            for category in categories:
                default_amount = default_budgets.get(category.name, 2000)  # Default 2000 for unknown categories
                
                # Try to get existing budget for this month
                budget, created = Budget.objects.get_or_create(
                    user=user,
                    category=category,
                    start_date__lte=end_date,
                    end_date__gte=start_date,
                    defaults={
                        'amount': default_amount,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                )

                if created:
                    budgets_created += 1
                else:
                    # Update existing budget if it was created with a different amount
                    if budget.amount != default_amount:
                        budget.amount = default_amount
                        budget.save()
                        budgets_updated += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {budgets_created} budgets and updated {budgets_updated} budgets for {user.username}'
                )
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with username {options["username"]} does not exist')
            ) 