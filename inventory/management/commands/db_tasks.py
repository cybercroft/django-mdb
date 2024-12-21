from django.core.management.base import BaseCommand
from celery import Celery
from django.conf import settings
from inventory.models import Task


class Command(BaseCommand):
    help = "List all Celery tasks or purge specific types of tasks in the queue."

    def add_arguments(self, parser):
        parser.add_argument(
            '--purge',
            type=str,
            choices=['active', 'reserved', 'scheduled', 'all'],
            help="Purge specific types of tasks: 'active', 'reserved', 'scheduled', or 'all'."
        )
        parser.add_argument(
            '--delete',
            type=str,
            choices=['active', 'complete', 'revoked', 'all'],
            help="Purge specific types of tasks: 'active', 'completed', 'revoked', or 'all'."
        )

    def handle(self, *args, **options):
        # Initialize Celery app
        celery_app = Celery(broker=settings.CELERY_BROKER_URL)

        # Inspect current tasks
        inspector = celery_app.control.inspect()

        active_tasks = inspector.active() if inspector else None
        reserved_tasks = inspector.reserved() if inspector else None
        scheduled_tasks = inspector.scheduled() if inspector else None

        # Display tasks
        self.stdout.write("=== Celery Task Information ===")
        self.display_tasks("Active Tasks", active_tasks)
        self.display_tasks("Reserved Tasks", reserved_tasks)
        self.display_tasks("Scheduled Tasks", scheduled_tasks)

        # Purge tasks based on the option provided
        if options['purge']:
            self.purge_tasks(celery_app, options['purge'], active_tasks, reserved_tasks, scheduled_tasks)
            
        if options['delete']:
            self.stdout.write("\n=== Deleting Tasks from databases ===")
            db_aliases = [alias for alias in settings.DATABASES.keys() if alias != 'default']
            for db_alias in db_aliases:
                self.delete_tasks(options['delete'], db_alias=db_alias)

    def display_tasks(self, title, tasks):
        self.stdout.write(f"\n{title}:")
        if not tasks:
            self.stdout.write("  No tasks found.")
        else:
            for worker, task_list in tasks.items():
                self.stdout.write(f"  Worker: {worker}")
                for task in task_list:
                    self.stdout.write(f"    Task ID: {task.get('id', 'Unknown')}")
                    self.stdout.write(f"    Name: {task.get('name', 'Unknown')}")
                    self.stdout.write(f"    Args: {task.get('args', '[]')}")
                    self.stdout.write(f"    Kwargs: {task.get('kwargs', '{}')}")
                    self.stdout.write(f"    State: {task.get('state', 'Unknown')}\n")

    def purge_tasks(self, celery_app, purge_type, active_tasks, reserved_tasks, scheduled_tasks):
        try:
            if purge_type == 'active':
                self.purge_active(celery_app, active_tasks)
            elif purge_type == 'reserved':
                self.purge_reserved(celery_app)
            elif purge_type == 'scheduled':
                self.purge_scheduled(celery_app)
            elif purge_type == 'all':
                celery_app.control.purge()
                self.stdout.write("\nAll tasks have been purged from the queue.")
        except Exception as e:
            self.stderr.write(f"\nFailed to purge tasks: {e}")

    def purge_active(self, celery_app, active_tasks):
        if not active_tasks:
            self.stdout.write("\nNo active tasks to purge.")
            return

        for worker, task_list in active_tasks.items():
            for task in task_list:
                celery_app.control.revoke(task['id'], terminate=True)
                self.stdout.write(f"\nPurged active task: {task['id']}")

    def purge_reserved(self, celery_app):
        celery_app.control.purge()
        self.stdout.write("\nPurged all reserved tasks from the queue.")

    def purge_scheduled(self, celery_app):
        # Celery's `control.cancel_consumer()` or `control.discard()` may be needed
        self.stdout.write("\nScheduled tasks purging is not directly supported via control. Handle this separately.")

    def delete_tasks(self, option, db_alias):
        if option == 'active':
            active = [Task.Status.PENDING, Task.Status.RUNNING]
            count = Task.objects.using(db_alias).filter(status__in=active).delete()[0]
            self.stdout.write(f"{count} tasks have been deleted from database '{db_alias}'.")
        elif option == 'completed':
            count = Task.objects.using(db_alias).filter(status=Task.Status.COMPLETED).delete()[0]
            self.stdout.write(f"{count} tasks have been deleted from database '{db_alias}'.")
        elif option == 'revoked':
            count = Task.objects.using(db_alias).filter(status=Task.Status.REVOKED).delete()[0]
            self.stdout.write(f"{count} tasks have been deleted from database '{db_alias}'.")
        elif option == 'all':
            count = Task.objects.using(db_alias).all().delete()[0]
            self.stdout.write(f"{count} tasks have been deleted from database '{db_alias}'.")
        else:
            self.stderr.write(f"\nUnrecognized option for --delete: '{option}'")