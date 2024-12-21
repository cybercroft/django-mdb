import json
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from celery_progress.views import get_progress
from inventory.models import Product, Task
from inventory.utils import WorkflowProgress
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Q
from django.core.management import call_command
from .tasks import run_all_workflows


def get_active_databases():
    return [alias for alias in settings.DATABASES.keys() if alias != 'default']


def list_all_products(request):
    databases = get_active_databases()
    all_products = {}

    for db_alias in databases:
        try:
            all_products[db_alias] = Product.objects.using(db_alias).all()
        except Exception as e:
            all_products[db_alias] = f"Error fetching products: {e}"

    return render(request, 'inventory/products/list.html', {'all_products': all_products})


def list_all_tasks(request):
    databases = get_active_databases()
    all_tasks = {}

    for db_alias in databases:
        try:
            all_tasks[db_alias] = Task.objects.using(db_alias).all()
        except Exception as e:
            all_tasks[db_alias] = f"Error fetching tasks: {e}"

    return render(request, 'inventory/workflow/tasks.html', {'all_tasks': all_tasks})


def workflow_progress(request, db_alias):
    try:
        progress = WorkflowProgress()
        tasks = Task.objects.using(db_alias).all()
        progress.update(tasks=tasks)
        return JsonResponse({
            'progress_percent': round(progress.percent, 2),
            "is_complete": progress.is_complete,
            "is_active": progress.is_active,
            }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def workflow_progress_all(request):
    workflows = {}
    databases = get_active_databases()
    
    # Group tasks by database alias
    for db_alias in databases:
        progress = WorkflowProgress()
        tasks = Task.objects.using(db_alias).all().order_by("triggered_on")
        progress.update(tasks=tasks)
        
        print(f"\nWorkflow: {db_alias}")
        for db_task in tasks:
            print(f"- Task: {db_task}")
            
        workflows[db_alias] = {
            "tasks": tasks,
            "progress_percent": round(progress.percent, 2),
            "is_complete": progress.is_complete,
            "is_active": progress.is_active,
        }

    return render(request, "inventory/workflow/progress.html", {"workflows": workflows})


def overall_progress(request):
    databases = get_active_databases()
    progress = WorkflowProgress()

    for db_alias in databases:
        try:
            tasks = Task.objects.using(db_alias).all()
            progress.update(tasks=tasks)
        except Exception:
            pass

    return JsonResponse({
        "progress": round(progress.percent, 2),
        "is_complete": progress.is_complete,
        "is_active": progress.is_active,
    })


def trigger_workflows(request):
    run_all_workflows()
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


def terminate_and_cleanup(request):
    try:
        # Call the custom management command with arguments
        call_command('db_tasks', '--purge', 'all', '--delete', 'all')
        # Redirect to homepage or another page
        return redirect('/')
    except Exception as e:
        # Handle any errors
        return HttpResponse(f"Error running command: {str(e)}", status=500)