# inventory/management/commands/clear_products.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from inventory.models import Product  # Ensure Product model is correctly imported


class Command(BaseCommand):
    help = 'Clear all Product instances from the specified database version or all versions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ver',
            type=str,
            default=None,
            help='Database version to clear products from (e.g., "1.0.0"). If not provided, clears from all versions.'
        )

    def handle(self, *args, **options):
        version = options['ver']

        # Ensure valid database alias(es) to process
        if version:
            if version not in settings.DATABASES:
                raise CommandError(f"Database version '{version}' does not exist in DATABASES settings.")
            aliases = [version]
        else:
            aliases = [alias for alias in settings.DATABASES.keys() if alias != 'default']

        if not aliases:
            raise CommandError("No valid database versions found to clear products.")

        # Clear products for each alias
        for alias in aliases:
            self.stdout.write(f"Clearing all Product instances from database '{alias}'...")

            try:
                count, _ = Product.objects.using(alias).all().delete()
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully cleared {count} Product instances from database '{alias}'."
                ))
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"Failed to clear Product instances from database '{alias}': {e}"
                ))
