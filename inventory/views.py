import json
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from celery_progress.views import get_progress
from inventory.models import Product, Task
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Q
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


def list_all_tasks(request):
    databases = set(settings.DATABASES.keys())
    databases.remove("default")
    all_tasks = {}

    for db_alias in databases:
        try:
            tasks = Task.objects.using(db_alias).all()
            all_tasks[db_alias] = tasks
        except Exception as e:
            all_tasks[db_alias] = f"Error fetching tasks: {e}"

    return render(request, 'inventory/workflow/tasks.html', {'all_tasks': all_tasks})


def calculate_total_progress(tasks):
    progress_current = 0
    progress_total = 0
    for task in tasks:
        progress_current += task.current
        progress_total += task.total
    return 100 * progress_current / progress_total if progress_total else 0


def workflow_progress(request, db_alias):
    try:
        tasks = Task.objects.using(db_alias).all()
        total_progress = calculate_total_progress(tasks)
        return JsonResponse({'progress_percent': total_progress}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def workflow_progress_all(request):
    workflows = {}
    
    databases = set(settings.DATABASES.keys())
    databases.remove("default")
    
    # Group tasks by database alias
    for db_alias in databases:
        tasks = Task.objects.using(db_alias).all().order_by('triggered_on', 'pk')
        workflows[db_alias] = {
            "tasks": tasks,
            "progress_percent": calculate_total_progress(tasks)
        }

    return render(request, "inventory/workflow/progress.html", {"workflows": workflows})


def overall_progress(request):
    databases = set(settings.DATABASES.keys())
    databases.remove("default")

    overall_current = 0
    overall_total = 0
    is_running_or_pending = False

    for db_alias in databases:
        try:
            tasks = Task.objects.using(db_alias).all()
            for task in tasks:
                overall_current += task.current
                overall_total += task.total
            if tasks.filter(Q(status=Task.Status.PENDING) | Q(status=Task.Status.RUNNING)).exists():
                is_running_or_pending = True
                
                
        except Exception:
            pass

    progress = (overall_current / overall_total * 100) if overall_total > 0 else 0
    return JsonResponse({
        "progress": round(progress, 2),
        "is_running_or_pending": is_running_or_pending,
    })


def trigger_workflows(request):
    run_all_workflows.apply_async()
    return redirect('workflow_progress_all')


def get_task_progress_pending():
    return {
        'state': "PENDING",
        'complete': False,
        'success': None,
        'progress': {'pending': True, 'current': 0, 'total': 100, 'percent': 0}
    }
    
    
def get_task_progress_success():
    return {
        'state': "SUCCESS",
        'complete': True,
        'success': True,
        'progress': {'pending': False, 'current': 100, 'total': 100, 'percent': 100}
    }


def get_task_progress_revoked():
    return {
        'state': "REVOKED",
        'complete': True,
        'success': None,
        'progress': {'pending': False, 'current': 0, 'total': 100, 'percent': 0}
    }


@never_cache
def task_progress(request, db, pk):
    try:
        task = Task.objects.using(db).get(pk=pk)
        if task.task_id:
            return get_progress(request, task_id=task.task_id)
        else:
            if task.status == Task.Status.PENDING:
                ctx = get_task_progress_pending()
            elif task.status == Task.Status.COMPLETED:
                ctx = get_task_progress_success()
            else:
                ctx = get_task_progress_revoked()
    except Task.DoesNotExist:
        ctx = get_task_progress_revoked()
    return HttpResponse(json.dumps(ctx), content_type='application/json')

