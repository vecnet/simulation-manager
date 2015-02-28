# This script creates a secrets.py module in the folder where this script is
# located.  The secrets.py module is only created if it does not exist.

import sys

from django.utils.crypto import get_random_string
from path import path


def main():
    script_dir = path(__file__).abspath().dirname()
    secrets_path = script_dir / 'secrets.py'
    if secrets_path.exists():
        print 'File already exists:', secrets_path.relpath()
        return 1

    template_path = script_dir / 'secrets-template.py'
    with template_path.open('r') as f:
        source_code = f.read()

    secret_key = generate_secret_key()
    source_code = source_code.replace('{SECRET KEY PLACEHOLDER}', secret_key)
    with secrets_path.open('w') as f:
        f.write(source_code)
    print 'Created file:', secrets_path.relpath()
    return 0


def generate_secret_key():
    """
    Based on Django's startproject command:

      https://github.com/django/django/blob/1.6.7/django/core/management/commands/startproject.py
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(50, chars)
    return secret_key


if __name__ == '__main__':
    exit_status = main()
    sys.exit(exit_status)
