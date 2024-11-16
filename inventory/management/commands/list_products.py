# inventory/management/commands/list_products.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from inventory.models import Product  # Ensure Product model is correctly imported


class Command(BaseCommand):
    help = 'List all Product instances from the specified database version or all versions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ver',
            type=str,
            default=None,
            help='Database version to list products from (e.g., "1.0.0"). If not provided, lists from all versions.'
        )

    def handle(self, *args, **options):
        version = options['ver']

        # Validate the database alias(es) to process
        if version:
            if version not in settings.DATABASES:
                raise CommandError(f"Database version '{version}' does not exist in DATABASES settings.")
            aliases = [version]
        else:
            aliases = [alias for alias in settings.DATABASES.keys() if alias != 'default']

        if not aliases:
            raise CommandError("No valid database versions found to list products.")

        # List products for each alias
        for alias in aliases:
            self.stdout.write(f"Listing Product instances from database '{alias}':")

            try:
                products = Product.objects.using(alias).all()
                if not products.exists():
                    self.stdout.write(self.style.WARNING(f"No products found in database '{alias}'."))
                    continue

                for product in products:
                    self.stdout.write(
                        f"- ID: {product.id}, Name: {product.name}, Price: {product.price}, Stock: {product.stock}"
                    )
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f"Failed to list Product instances from database '{alias}': {e}"
                ))
