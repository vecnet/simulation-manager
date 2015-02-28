from django.core.management.base import BaseCommand, CommandError

from sim_manager import auth


class Command(BaseCommand):
    args = '[action]'
    help = '\n'.join((
        'Manage the user account that is used by cluster scripts',
        '',
        'Actions:',
        '  create : create the user and write its credentials to a file for script use',
        '  delete : delete the user and its credentials file if the user exists',
        '  (none) : print whether the user exists or not',
    ))

    def handle(self, *args, **options):
        if len(args) == 0:
            self.print_user_existence()
        else:
            action = args[0]
            if action not in ('create', 'delete'):
                raise CommandError('Invalid action: "%s"' % action)
            if len(args) > 1:
                raise CommandError('Extra arguments after the action "%s": %s' % (action, ' '.join(args[1:])))
            if action == "create":
                self.create_user()
            else:
                self.delete_user()

    def print_user_existence(self):
        if auth.script_user_exists():
            status = "exists"
        else:
            status = "does not exist"
        self.stdout.write('User "%s" %s' % (auth.SCRIPT_USER, status))

    def create_user(self):
        if auth.script_user_exists():
            raise CommandError('User "%s" already exists' % auth.SCRIPT_USER)
        auth.create_script_user()
        self.stdout.write('Created the user "%s" and its credentials file' % auth.SCRIPT_USER)

    def delete_user(self):
        if auth.script_user_exists():
            auth.delete_script_user()
            self.stdout.write('Deleted the user "%s" and its credentials file' % auth.SCRIPT_USER)
        else:
            self.stdout.write('User "%s" does not exist' % auth.SCRIPT_USER)
