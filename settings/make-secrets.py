# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
