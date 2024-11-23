from django.urls import path
from .views import list_all_products, workflow_progress, trigger_workflows

urlpatterns = [
    path('', list_all_products, name='list_all_products'),
    path("workflow-progress/", workflow_progress, name="workflow_progress"),
    path('trigger-workflows/', trigger_workflows, name='trigger_workflows'),
]
