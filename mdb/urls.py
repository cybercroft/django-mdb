import os
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from mdb.admin import admin_site  

urlpatterns = [
    path('admin/', admin_site.urls),  
    # path('admin/', admin.site.urls),  
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# one-time startup function after server-starts
def _startup():
    if not os.path.exists(settings.EXPORT_PATH):
        os.makedirs(settings.EXPORT_PATH)
    if not os.path.exists(settings.IMPORT_PATH):
        os.makedirs(settings.IMPORT_PATH)
    
_startup()
