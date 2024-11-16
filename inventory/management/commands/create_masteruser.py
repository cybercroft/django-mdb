from django.core.management.base import BaseCommand
from django.db import connections
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Create superuser for all databases with a given username and password.'

    def add_arguments(self, parser):
        # Add arguments for username and password
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='The username for the superuser.'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='The password for the superuser.'
        )

    def handle(self, *args, **options):
        # Get the default user model
        User = get_user_model()

        username = options['username']
        password = options['password']

        # Loop through all databases defined in the settings
        for db_alias in connections.databases:
            self.stdout.write(f"Creating superuser for {db_alias}...")

            # Check if the username already exists in the database
            if User.objects.using(db_alias).filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"Superuser with username '{username}' already exists in {db_alias}."))
                continue

            try:
                # Manually create a superuser
                user = User(username=username)
                user.set_password(password)
                user.is_superuser = True
                user.is_staff = True
                user.save(using=db_alias)  # Save the user in the specific database

                self.stdout.write(self.style.SUCCESS(f'Successfully created superuser for database: {db_alias}'))
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f'Error creating superuser for {db_alias}: {str(e)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
