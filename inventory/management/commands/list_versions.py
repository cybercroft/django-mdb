# inventory/management/commands/list_db_versions.py
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'List all database versions available in settings.DATABASES'

    def handle(self, *args, **kwargs):
        databases = settings.DATABASES

        if not databases:
            self.stdout.write(self.style.WARNING("No databases found in settings."))
            return

        self.stdout.write(self.style.SUCCESS("Available database versions:\n"))
        for alias, config in databases.items():
            db_path = config.get('NAME', 'N/A')  # Get database file or name
            self.stdout.write(f"- {alias}: {db_path}")
