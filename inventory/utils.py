# inventory/utils.py
from inventory.models import Product

def import_data(data, version=None):
    database_alias = version if version else "default"
    
    for product_data in data:
        Product.objects.using(database_alias).update_or_create(
            name=product_data['name'],
            defaults={
                'price': product_data['price'],
                'stock': product_data['stock'],
            }
        )
    print(f"Data imported to '{database_alias}' successfully.")
