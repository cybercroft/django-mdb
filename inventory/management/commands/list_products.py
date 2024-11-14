# inventory/management/commands/list_products.py
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from inventory.utils import get_products


class Command(BaseCommand):
    help = 'List all products in a specified database version.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ver', 
            type=str, 
            default='default', 
            help='Database version to list products from (e.g., "1.0.0"). Defaults to "default".'
        )

    def handle(self, *args, **options):
        version = options['ver']
        
        try:
            # Get products using the utility function
            products = get_products(version)

            if not products.exists():
                self.stdout.write(self.style.WARNING(f"No products found in database '{version}'."))
                return
            
            self.stdout.write(self.style.SUCCESS(f"Products in '{version}' database:\n"))
            for product in products:
                self.stdout.write(f"- {product.name}: ${product.price} (Stock: {product.stock}, Category: {product.category})")
        
        except ObjectDoesNotExist as e:
            raise CommandError(str(e))
