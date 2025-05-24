def get_default_categories():
    """Return a list of default categories for both income and expenses."""
    income_categories = [
        {'name': 'Salary', 'description': 'Regular employment income', 'type': 'income'},
        {'name': 'Freelance', 'description': 'Income from freelance work', 'type': 'income'},
        {'name': 'Investments', 'description': 'Income from investments', 'type': 'income'},
        {'name': 'Bonus', 'description': 'Work bonuses and rewards', 'type': 'income'},
        {'name': 'Other Income', 'description': 'Other sources of income', 'type': 'income'},
    ]

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

    return income_categories + expense_categories 