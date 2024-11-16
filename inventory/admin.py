# inventory/admin.py
from django.contrib import admin
from .models import Product


@admin.register(Product)  # Registering Product model using the decorator
class ProductAdmin(admin.ModelAdmin):
    # Define which fields to display in the admin list view
    list_display = ('name', 'price', 'stock', 'category')
    # Define which fields to make searchable in the admin
    search_fields = ('name', 'category')
    # Define filter options for the admin
    list_filter = ('category',)
    # Add additional customizations if necessary (e.g., fieldsets, ordering)
    ordering = ('name',)
