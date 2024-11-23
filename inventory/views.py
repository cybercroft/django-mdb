from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from inventory.models import Product, Task
from django.conf import settings
from .tasks import run_all_workflows


def list_all_products(request):
    databases = set(settings.DATABASES.keys())
    databases.remove("default")
    all_products = {}

    for db_alias in databases:
        try:
            products = Product.objects.using(db_alias).all()
            all_products[db_alias] = products
        except Exception as e:
            all_products[db_alias] = f"Error fetching products: {e}"

    return render(request, 'inventory/products/list.html', {'all_products': all_products})


def workflow_progress(request):
    workflows = {}
    
    databases = set(settings.DATABASES.keys())
    databases.remove("default")
    
    # Group tasks by database alias
    for db_alias in databases:
        tasks = Task.objects.using(db_alias).all().order_by('status', 'created_on')
        progress_current = 0
        progress_total = 0
        for task in tasks:
            progress_current += task.current
            progress_total += task.total
            
        workflows[db_alias] = {
            "tasks": tasks,
            "progress_current": progress_current,
            "progress_total": progress_total,
            "progress_percent": 100 * progress_current / progress_total if progress_total else 0,
        }

    return render(request, "inventory/workflow/progress.html", {"workflows": workflows})


def trigger_workflows(request):
    run_all_workflows.apply_async()
    return redirect('workflow_progress')
