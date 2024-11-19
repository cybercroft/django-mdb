from django.shortcuts import render
from inventory.models import Product
from django.conf import settings


def list_all_products(request):
    databases = settings.DATABASES.keys()
    all_products = {}

    for db_alias in databases:
        try:
            products = Product.objects.using(db_alias).all()
            all_products[db_alias] = products
        except Exception as e:
            all_products[db_alias] = f"Error fetching products: {e}"

    return render(request, 'inventory/products/list.html', {'all_products': all_products})
