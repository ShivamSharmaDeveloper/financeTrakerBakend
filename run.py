import os
import sys
from django.core.management import execute_from_command_line

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_tracker.settings')
    
    port = int(os.environ.get('PORT', '8000'))
    
    # Modify the command to use the correct port
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        sys.argv = [sys.argv[0], f'runserver', f'0.0.0.0:{port}']
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main() 