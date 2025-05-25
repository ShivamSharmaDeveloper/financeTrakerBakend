# Personal Budget Tracker - Backend

A Django REST API backend for the Personal Budget Tracker application.

## Features

- **RESTful API**: Complete API for budget tracking functionality
- **JWT Authentication**: Secure user authentication
- **Budget Management**: Create and track budgets by category
- **Transaction Handling**: Record and manage financial transactions
- **Category Management**: Predefined and custom categories
- **Data Analytics**: Monthly trends and category-wise analysis
- **SQLite Database**: Lightweight database for development

## Tech Stack

- **Django**: Web framework
- **Django REST Framework**: API development
- **Simple JWT**: JWT authentication
- **SQLite**: Database
- **CORS**: Cross-Origin Resource Sharing

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication
- `POST /api/auth/login/`: Login
- `POST /api/auth/logout/`: Logout
- `GET /api/auth/user/`: Get current user

### Categories
- `GET /api/categories/`: List categories
- `POST /api/categories/`: Create category
- `GET /api/categories/{id}/`: Get category
- `PUT /api/categories/{id}/`: Update category
- `DELETE /api/categories/{id}/`: Delete category

### Budgets
- `GET /api/budgets/`: List budgets
- `POST /api/budgets/`: Create budget
- `GET /api/budgets/{id}/`: Get budget
- `PUT /api/budgets/{id}/`: Update budget
- `GET /api/budgets/summary/`: Get budget summary

### Transactions
- `GET /api/transactions/`: List transactions
- `POST /api/transactions/`: Create transaction
- `GET /api/transactions/{id}/`: Get transaction
- `PUT /api/transactions/{id}/`: Update transaction
- `DELETE /api/transactions/{id}/`: Delete transaction
- `GET /api/transactions/monthly_trends/`: Get monthly trends

## Database Schema

### User
- id (PK)
- username
- email
- password

### Category
- id (PK)
- name
- description
- type (income/expense)
- user (FK)

### Budget
- id (PK)
- category (FK)
- amount
- start_date
- end_date
- user (FK)

### Transaction
- id (PK)
- category (FK)
- amount
- type (income/expense)
- description
- date
- user (FK)

## Development Assumptions

1. SQLite database for simplicity
2. JWT token-based authentication
3. Monthly budget cycles
4. Single currency (INR)
5. Basic CRUD operations only

## Security Features

- JWT Authentication
- Token blacklisting
- CORS configuration
- Password hashing
- User-specific data isolation

## Error Handling

- Custom exception handling
- Proper HTTP status codes
- Detailed error messages
- Input validation

## Contributing

Feel free to submit issues and enhancement requests.

## License

MIT License 