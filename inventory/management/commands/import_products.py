# inventory/management/commands/import_products.py
import csv
import os
from django.core.management.base import BaseCommand, CommandError
from inventory.models import Product
from django.conf import settings

class Command(BaseCommand):
    help = 'Import products from a CSV file into the specified database version.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--version', 
            type=str, 
            default='default', 
            help='Database version to import data into (e.g., 1.0.0). Defaults to "default".'
        )
        parser.add_argument(
            '--file', 
            type=str, 
            default='products.csv', 
            help='Path to the CSV file containing product data.'
        )

    def handle(self, *args, **options):
        version = options['version']
        file_path = options['file']
        database_alias = version  # Set the version directly as the alias

        # Check if the specified database exists
        if database_alias not in settings.DATABASES:
            raise CommandError(f"Database alias '{database_alias}' does not exist in DATABASES settings.")

        # Check if the file exists
        if not os.path.isfile(file_path):
            raise CommandError(f"File '{file_path}' does not exist.")

        # Open the CSV file and import each row
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            products_created = 0

            for row in reader:
                product, created = Product.objects.using(database_alias).update_or_create(
                    name=row['name'],
                    defaults={
                        'price': float(row['price']),
                        'stock': int(row['stock']),
                    }
                )
                if created:
                    products_created += 1

            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported {products_created} products into '{database_alias}' from '{file_path}'."
            ))
