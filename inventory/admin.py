# inventory/admin.py
from django.contrib import admin
from mdb.admin import admin_site
from .models import Product


@admin.register(Product, site=admin_site)  # Register Product with the custom admin site
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category',)
    ordering = ('name',)

    def get_queryset(self, request):
        # Example of dynamically querying a specific database alias
        database_alias = request.GET.get('database', 'default')  # Set the database based on the URL or other logic
        return super().get_queryset(request).using(database_alias)

    def has_add_permission(self, request):
        # Ensure superuser has permission for all databases
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Ensure superuser has permission for all databases
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Ensure superuser has permission for all databases
        return request.user.is_superuser    