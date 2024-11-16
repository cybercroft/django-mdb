import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
import psycopg2
from psycopg2 import sql


class Command(BaseCommand):
    help = "Create missing PostgreSQL databases based on Django's DATABASES setting."

    def add_arguments(self, parser):
        parser.add_argument(
            '--migrate',
            action='store_true',
            help='Apply migrations to any new database created.',
        )

    def handle(self, *args, **kwargs):
        # Get argument for migrations
        migrate = kwargs['migrate']

        # PostgreSQL connection parameters
        user = os.getenv('POSTGRES_USER', 'myuser')
        password = os.getenv('POSTGRES_PASSWORD', 'mypassword')
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')

        # Connect to the default 'postgres' database to manage databases
        self.stdout.write("Connecting to PostgreSQL...")
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.autocommit = True
            cursor = conn.cursor()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error connecting to PostgreSQL: {e}"))
            return

        # Check for and create missing databases
        for db_name, db_config in settings.DATABASES.items():
            if db_name == 'default':
                continue  # Skip the default database

            database_name = db_config['NAME']
            self.stdout.write(f"Checking database: {database_name}...")

            try:
                cursor.execute(
                    sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
                    [database_name]
                )
                if cursor.fetchone():
                    self.stdout.write(self.style.SUCCESS(f"Database {database_name} already exists."))
                else:
                    self.stdout.write(f"Creating database: {database_name}...")
                    cursor.execute(
                        sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
                    )
                    self.stdout.write(self.style.SUCCESS(f"Database {database_name} created successfully."))

                    # Apply migrations if the --migrate flag is set
                    if migrate:
                        self.stdout.write(f"Running migrations for {db_name}...")
                        try:
                            call_command('migrate', database=db_name)
                            self.stdout.write(self.style.SUCCESS(f"Migrations completed for {db_name}."))
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"Error running migrations for {db_name}: {e}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error checking/creating database {database_name}: {e}"))

        # Close connections
        cursor.close()
        conn.close()
        self.stdout.write(self.style.SUCCESS("All databases checked and created if necessary."))
