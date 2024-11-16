# inventory/management/commands/import_products.py
import os
import csv
from django.core.management.base import BaseCommand, CommandError
from inventory.utils import import_products
from django.conf import settings


class Command(BaseCommand):
    help = 'Import products from CSV files in the IMPORT_PATH into the specified or all database versions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ver',
            type=str,
            default=None,
            help='Database version to import data into (e.g., "1.0.0"). If not specified, imports for all versions.'
        )
        parser.add_argument(
            '--file', 
            type=str, 
            default=None, 
            help='Name of the CSV file containing product data.'
        )

    def handle(self, *args, **options):
        version = options['ver']
        file_name = options['file']
        import_path = settings.IMPORT_PATH

        if not os.path.exists(import_path):
            raise CommandError(f"IMPORT_PATH '{import_path}' does not exist.")

        # Determine the subfolders to process
        if version:
            # Check if the specific version is valid
            if version not in settings.DATABASES:
                raise CommandError(f"Database version '{version}' does not exist in DATABASES settings.")
            subfolders = [os.path.join(import_path, version)]
        else:
            # Process all database versions in settings.DATABASES
            subfolders = [os.path.join(import_path, alias) for alias in settings.DATABASES.keys() if alias != 'default']

        for subfolder in subfolders:
            if not os.path.exists(subfolder) or not os.path.isdir(subfolder):
                self.stdout.write(self.style.WARNING(f"Skipping '{subfolder}' (does not exist or is not a directory)."))
                continue

            # Get all CSV files in the subfolder
            if file_name:
                if file_name in os.listdir(subfolder):
                    csv_files = [os.path.join(subfolder, file_name)] 
                else:
                    self.stdout.write(self.style.WARNING(f"File '{file_name}' not found in '{subfolder}'."))
                    continue
            else:
                csv_files = [os.path.join(subfolder, file) for file in os.listdir(subfolder) if file.endswith('.csv')]

            if not csv_files:
                self.stdout.write(self.style.WARNING(f"No CSV files found in '{subfolder}'."))
                continue

            database_alias = os.path.basename(subfolder)
            self.stdout.write(f"Processing database alias '{database_alias}' from folder '{subfolder}'.")

            for csv_file in csv_files:
                self.stdout.write(f"Importing from '{csv_file}'...")
                try:
                    self.import_csv_file(csv_file, database_alias)
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed to import from '{csv_file}': {e}"))


    def import_csv_file(self, file_path, database_alias):
        """Handles the import of a single CSV file into the specified database alias."""
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = []

            for row in reader:
                try:
                    # Prepare data for each product
                    product_data = {
                        'name': row['name'],
                        'price': float(row['price']),
                        'stock': int(row['stock']),
                        'category': row.get('category', 'Unknown')  # Handle missing category gracefully
                    }
                    data.append(product_data)
                except KeyError as e:
                    raise CommandError(f"Missing required column {e} in file '{file_path}'.")

            # Call the utility function to import the data
            import_products(data, version=database_alias)

            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported {len(data)} products into '{database_alias}' from '{file_path}'."
            ))

            