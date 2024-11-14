# inventory/management/commands/import_products.py
import os
import csv
from django.core.management.base import BaseCommand, CommandError
from inventory.utils import import_products 
from django.conf import settings

class Command(BaseCommand):
    help = 'Import products from a CSV file into the specified database version.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ver', 
            type=str, 
            default='default', 
            help='Database version to import data into (e.g., "1.0.0"). Defaults to "default".'
        )
        parser.add_argument(
            '--file', 
            type=str, 
            default='products.csv', 
            help='Path to the CSV file containing product data.'
        )

    def handle(self, *args, **options):
        version = options['ver']
        file_path = options['file']
        database_alias = version  # Use version string as the alias

        # Check if the specified database exists
        if database_alias not in settings.DATABASES:
            raise CommandError(f"Database alias '{database_alias}' does not exist in DATABASES settings.")

        # Check if the file exists
        if not os.path.isfile(file_path):
            raise CommandError(f"File '{file_path}' does not exist.")

        # Open the CSV file and prepare data for import
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = []

            for row in reader:
                # Prepare data for each product
                product_data = {
                    'name': row['name'],
                    'price': float(row['price']),
                    'stock': int(row['stock']),
                    'category': row.get('category', 'Unknown')  # Handle category if it exists
                }
                data.append(product_data)

            # Call the utility function to import the data
            import_products(data, version=database_alias)

            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported {len(data)} products into '{database_alias}' from '{file_path}'."
            ))