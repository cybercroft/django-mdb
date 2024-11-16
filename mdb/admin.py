from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.db import connections


class MultiDatabaseAdminSite(admin.AdminSite):
    site_header = 'Multi-Database Admin Panel'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('databases/', self.admin_view(self.view_all_databases)),
        ]
        return custom_urls + urls

    def view_all_databases(self, request):
        # Ensure user has permission to view databases
        if not request.user.is_superuser:
            return self.render_to_response({'error': 'You do not have permission to access these databases.'})
    
        databases = connections.databases
        all_data = {}
    
        for db_alias in databases:
            # Access each database
            with connections[db_alias].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM django_content_type")  # Example query
                count = cursor.fetchone()[0]
                all_data[db_alias] = count
    
        return self.render_to_response({'databases': all_data})

    def changelist_view(self, request, extra_context=None):
        # Add the database selection option to the admin panel view
        db_param = request.GET.get('database', 'default')
        databases = connections.databases.keys()
        extra_context = extra_context or {}
        extra_context['database_selector'] = format_html("""
            <form method="get" style="margin-bottom: 15px;">
                <label for="database">Select Database: </label>
                <select name="database" onchange="this.form.submit();">
                    {}
                </select>
            </form>
        """.format(''.join([f'<option value="{db}"{" selected" if db == db_param else ""}>{db}</option>' for db in databases])))
                
        return super().changelist_view(request, extra_context=extra_context)


# Register the custom admin site
admin_site = MultiDatabaseAdminSite()


# Register the User model with the custom admin site
@admin.register(User, site=admin_site)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser')


# Register the Group model with the custom admin site
@admin.register(Group, site=admin_site)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    