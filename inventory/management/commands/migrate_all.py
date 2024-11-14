# inventory/management/commands/migrate_all.py
from django.core.management import call_command
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Run migrations on all databases defined in DATABASES"

    def handle(self, *args, **kwargs):
        databases = settings.DATABASES.keys()
        for db in databases:
            self.stdout.write(f"Applying migrations to {db}...")
            call_command('migrate', database=db)
            self.stdout.write(self.style.SUCCESS(f"Successfully migrated {db}"))
