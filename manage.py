#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Tự động chạy migrate khi khởi động server
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        try:
            print("--- Tự động kiểm tra và áp dụng migrations ---")
            execute_from_command_line([sys.argv[0], 'migrate'])
            print("-----------------------------------------------")
        except Exception as e:
            print(f"Lỗi khi tự động chạy migrate: {e}")

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
