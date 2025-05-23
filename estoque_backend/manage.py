#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path  # Adicione esta linha

def main():
    """Run administrative tasks."""
    # Adicione estas 3 linhas antes do setdefault:
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(str(BASE_DIR))
    sys.path.append(str(BASE_DIR / 'estoque_backend'))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'estoque_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
