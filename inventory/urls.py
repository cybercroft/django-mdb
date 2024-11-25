from django.urls import path
import inventory.views as views


urlpatterns = [
    path('', views.list_all_products, name='list_all_products'),
    path('workflow-tasks', views.list_all_tasks, name='list_all_tasks'),
    path("workflow-progress/<str:db_alias>/", views.workflow_progress, name="workflow_progress"),
    path("workflow-progress/", views.workflow_progress_all, name="workflow_progress_all"),
    path('overall-progress/', views.overall_progress, name='overall_progress'),    
    path('trigger-workflows/', views.trigger_workflows, name='trigger_workflows'),
    path('task-progress/<str:db>/<int:pk>/', views.task_progress, name='task_progress'),
]
