# inventory/utils.py
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from inventory.models import Product, Task


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


class WorkflowProgress:
    
    def __init__(self):
        self.current = 0
        self.total = 0
        self.percent = 0
        self.status = {}
   
    @property
    def is_complete(self):
        return True if len(self.status) == 1 and self.status.get(Task.Status.COMPLETED, 0) else False
    
    @property
    def is_pending(self):
        return True if self.status.get(Task.Status.PENDING, 0) else False
    
    @property
    def is_running(self):
        return True if self.status.get(Task.Status.RUNNING, 0) else False
    
    @property
    def is_active(self):
        return True if self.is_running or self.is_pending else False
    
    def reset(self):
        self.current = 0
        self.total = 0
        self.progress = 0
        self.status = {}
        
    def update(self, tasks):
        for task in tasks:
            self.total += 1
            self.current += task.current / task.total if task.total else 0
            if task.status in self.status.keys():
                self.status[task.status] += 1
            else:
                self.status[task.status] = 1
        self.percent = 100 * self.current / self.total if self.total else 0
                