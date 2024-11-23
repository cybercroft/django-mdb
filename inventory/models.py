# inventory/models.py
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.CharField(max_length=255, default="")    

    def __str__(self):
        return self.name


class AbstractTask(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        FAILED = 'FAILED', 'Failed'
        REVOKED = 'REVOKED', 'Revoked'
        COMPLETED = 'COMPLETED', 'Completed'

    class Type(models.TextChoices):
        GENERIC = 'GENERIC', 'Generic'
        DB_IMPORT = 'DB_IMPORT', 'Database Import'
        DB_UPDATE = 'DB_UPDATE', 'Database Update'
        DB_EXPORT = 'DB_EXPORT', 'Database Export'
        DB_WORKFLOW = 'DB_WORKFLOW', 'Database Workflow'

    created_on = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the task was created")
    updated_on = models.DateTimeField(auto_now=True, help_text="Timestamp when the task was last updated")
    database = models.CharField(max_length=100, help_text="Alias of the database where the task is saved")
    name = models.CharField(max_length=255, help_text="Name of the task")
    task_id = models.CharField(max_length=255, null=True, blank=True)  # Celery task ID
    current = models.PositiveIntegerField(default=0, help_text="Current iteration of the task")
    total = models.PositiveIntegerField(help_text="Total iterations of the task")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current status of the task"
    )
    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        default=Type.GENERIC,
        help_text="Type of the task"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def progress_detail(self):
        return f"{self.get_type_display()}: {self.current} of {self.total}"
        
    @property
    def progress_percent(self):
        return self.current / self.total if self.total else 0


class Task(AbstractTask):
    pass
