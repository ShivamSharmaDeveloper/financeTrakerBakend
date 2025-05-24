import os
import sys
from django.core.management import execute_from_command_line

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_tracker.settings')
    
    # Get the port from environment variable or use default
    port = int(os.environ.get('PORT', 8000))
    
    # Set up the command to run the server on 0.0.0.0 and the specified port
    sys.argv = ['manage.py', 'runserver', f'0.0.0.0:{port}']
    
    try:
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

if __name__ == '__main__':
    main() 