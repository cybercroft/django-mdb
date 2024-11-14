# inventory/utils.py
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from inventory.models import Product


def import_products(data, version=None):
    database_alias = version if version else "default"
    
    for product_data in data:
        Product.objects.using(database_alias).update_or_create(
            name=product_data.get('name'),
            defaults={
                'price': product_data.get('price', 0),
                'stock': product_data.get('stock', 0),
                'category': product_data.get('category', 'Unknown')  # Include category if provided                
            }
        )


def get_products(version="default"):
    database_alias = version

    # Check if the specified database exists
    if database_alias not in settings.DATABASES:
        raise ObjectDoesNotExist(f"Database alias '{database_alias}' does not exist in DATABASES settings.")
    
    # Query and return all products from the specified database version
    return Product.objects.using(database_alias).all()