from django.conf import settings
from django.utils import timezone as tz
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from inventory.workflows import WorkflowStep, Workflow
from inventory.models import Task, Product


class TaskProgressRecorder(ProgressRecorder):
    def __init__(self, celery_task, db_task: Task, db_alias="default"):
        self.db_alias = db_alias
        self.db_task = db_task
        super().__init__(celery_task)
        
    def set_progress(self, current, total, description=""):
        self.db_task.current = current
        self.db_task.total = total 
        self.db_task.save(using=self.db_alias)
        detail = description if description else self.db_task.progress_detail
        return super().set_progress(current, total, detail)


def trigger_task(obj, db_alias, task_id):
    try:
        db_task = Task.objects.using(db_alias).get(id=task_id)
    except Task.DoesNotExist:
        return f"Task with id '{task_id}' not found in database '{db_alias}'."

    # Sync the Celery runtime task ID with the database
    db_task.task_id = obj.request.id 
    db_task.status = Task.Status.RUNNING
    db_task.save(using=db_alias)
    
    recorder = TaskProgressRecorder(celery_task=obj, db_task=db_task, db_alias=db_alias)
    
    # Task logic goes here...
    for i in range(1, db_task.total+1):
        if i % 1000 == 0:
            recorder.set_progress(i, db_task.total)
            
    db_task.status = Task.Status.COMPLETED
    db_task.save(using=db_alias)
    recorder.set_progress(db_task.total, db_task.total)
    
    return f"{db_task.get_type_display()} completed for {db_alias}"


@shared_task(bind=True) # First-Task in chain
def trigger_preprocess_task(self, db_alias, task_id):
    return trigger_task(self, db_alias, task_id)


@shared_task(bind=True)
def trigger_import_task(self, res, db_alias, task_id):
    return trigger_task(self, db_alias, task_id)


@shared_task(bind=True)
def trigger_update_task(self, res, db_alias, task_id):
    return trigger_task(self, db_alias, task_id)


@shared_task(bind=True)
def trigger_export_task(self, res, db_alias, task_id):
    return trigger_task(self, db_alias, task_id)


@shared_task(bind=True)
def trigger_postprocess_task(self, res, db_alias, task_id):
    return trigger_task(self, db_alias, task_id)


class ImportWorkflow(Workflow):
    
    def __init__(self, db_alias="default"):
        super().__init__(db_alias)
       
    @staticmethod
    def is_triggered(db_alias): 
        # Check if workflow task is triggered 
        status_active = [Task.Status.PENDING, Task.Status.RUNNING]
        types_accepted = [Task.Type.DB_IMPORT, Task.Type.DB_UPDATE, Task.Type.DB_EXPORT, Task.Type.DB_PROCESS]
        return Task.objects.using(db_alias).filter(status__in=status_active, type__in=types_accepted).exists()

    def create_task(self, task_name:str, task_type:Task.Type, total=1):
        db_task, is_created = Task.objects.using(self.db_alias).update_or_create(
            name=task_name,
            type=task_type,
            defaults={
                'task_id': None,
                'database': self.db_alias,
                'status': Task.Status.PENDING,
                'triggered_on': tz.now(),
                'current': 0,
                'total': total 
            }
        )
        return db_task
    
    def _setup_preprocess_step(self):
        task_type = Task.Type.DB_PROCESS
        pre_process_step = WorkflowStep(name="Pre-Process Step")
        db_task = self.create_task(task_name="Pre-Process", task_type=task_type, total=10000)
        pre_process_step.add_task(task=db_task, func=trigger_preprocess_task.s(self.db_alias, db_task.pk))
        self.add_step(pre_process_step)        

    def _setup_import_step(self):
        task_type = Task.Type.DB_IMPORT
        import_step = WorkflowStep(name="Import Step", parallel=True)
        for i in range(1, 4):
            db_task = self.create_task(task_name=f"{task_type}_{i}", task_type=task_type, total=500000)
            import_step.add_task(task=db_task, func=trigger_import_task.s(self.db_alias, db_task.pk))
        self.add_step(import_step)
        
    def _setup_update_step(self):
        task_type = Task.Type.DB_UPDATE
        update_step = WorkflowStep(name="Update Step", parallel=False)
        for i in range(1, 4):
            db_task = self.create_task(task_name=f"{task_type}_{i}", task_type=task_type, total=500000)
            update_step.add_task(task=db_task, func=trigger_update_task.s(self.db_alias, db_task.pk))
        self.add_step(update_step)
        
    def _setup_export_step(self):
        task_type = Task.Type.DB_EXPORT
        export_step = WorkflowStep(name="Export Step", parallel=True)
        for i in range(1, 4):
            db_task = self.create_task(task_name=f"{task_type}_{i}", task_type=task_type, total=200000)
            export_step.add_task(task=db_task, func=trigger_export_task.s(self.db_alias, db_task.pk))
        self.add_step(export_step)        
        
    def _setup_postprocess_step(self):
        task_type = Task.Type.DB_PROCESS
        post_process_step = WorkflowStep(name="Post-Process Step")
        db_task = self.create_task(task_name="Post-Process", task_type=task_type, total=5000)
        post_process_step.add_task(task=db_task, func=trigger_postprocess_task.s(self.db_alias, db_task.pk))
        self.add_step(post_process_step)        
    
    def setup(self):
        self._setup_preprocess_step()
        self._setup_import_step()
        self._setup_update_step()
        self._setup_export_step()
        self._setup_postprocess_step()
        

@shared_task(bind=True)
def run_workflow(self, db_alias):
    if ImportWorkflow.is_triggered(db_alias):
        return
    workflow = ImportWorkflow(db_alias=db_alias)
    workflow.setup()
    workflow.run()
    
        
@shared_task(bind=True)
def run_all_workflows(self):
    databases = [db_alias for db_alias in settings.DATABASES if db_alias != "default"]
    for db_alias in databases:
        run_workflow(db_alias) 
