from django.urls import path
from .views import list_all_products

urlpatterns = [
    path('', list_all_products, name='list_all_products'),
]
