from django.conf import settings
from celery import chain, group, shared_task
from celery_progress.backend import ProgressRecorder
from .models import Task, Product


class TaskProgressRecorder(ProgressRecorder):
    def __init__(self, celery_task, db_task: Task, db_alias="default"):
        self.db_alias = db_alias
        self.db_task = db_task
        super().__init__(celery_task)
        
    def set_progress(self, current, total, description=""):
        self.db_task.current = current
        self.db_task.total = total 
        self.db_task.percent = current / total
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
    
    recorder = TaskProgressRecorder(obj, db_task)
    
    # Task logic goes here...
    for i in range(1, db_task.total+1):
        if i % 1000 == 0:
            recorder.set_progress(i, db_task.total)
            
    db_task.current = db_task.total
    db_task.status = Task.Status.COMPLETED
    db_task.save(using=db_alias)
    
    return f"{db_task.get_type_display()} completed for {db_alias}"


@shared_task(bind=True)
def import_task(self, db_alias, task_id):
    trigger_task(self, db_alias, task_id)


@shared_task(bind=True)
def update_task(self, res, db_alias, task_id):
    trigger_task(self, db_alias, task_id)


@shared_task(bind=True)
def export_task(self, res, db_alias, task_id):
    trigger_task(self, db_alias, task_id)


class WorkflowStep:
    def __init__(self, name="", tasks=None, parallel=True):
        self.name = name 
        self.tasks = tasks or []
        self.parallel = parallel
    
    @property
    def progress_total(self):
        return sum([task.total for task in self.tasks]) 
    
    @property
    def progress_current(self):
        return sum([task.current for task in self.tasks]) 
    
    @property
    def progress_percent(self):
        return self.progress_current / self.progress_total
    
    def get_celery_task(self, db_task: Task, db_alias):
        if db_task.type == Task.Type.DB_IMPORT:
            return import_task.s(db_alias, db_task.id) 
        elif db_task.type == Task.Type.DB_UPDATE:
            return update_task.s(db_alias, db_task.id)
        elif db_task.type == Task.Type.DB_EXPORT:
            return export_task.s(db_alias, db_task.id)
        else:
            raise ValueError(f"Unknown task type: {db_task.type}")

    def execute(self, db_alias):
        if not self.tasks:
            return None
        
        # Parallel execution
        if self.parallel:
            if len(self.tasks) == 1:
                return self.get_celery_task(self.tasks[0], db_alias)
            return group(self.get_celery_task(task, db_alias) for task in self.tasks)
        
        # Sequential execution
        if len(self.tasks) == 1:
            return self.get_celery_task(self.tasks[0], db_alias)
        task_chain = chain(self.get_celery_task(self.tasks[0], db_alias))
        for task in self.tasks[1:]:
            task_chain |= self.get_celery_task(task, db_alias)
        return task_chain


class Workflow:
    def __init__(self, db_alias):
        self.db_alias = db_alias
        self.steps = []

    @property
    def progress_current(self):
        return sum([step.progress_current for step in self.steps])
    
    @property
    def progress_total(self):
        return sum([step.progress_total for step in self.steps])
    
    @property
    def progress_percent(self):
        return self.progress_current / self.progress_total

    def add_step(self, step):
        self.steps.append(step)

    def run(self):
        workflow_chain = None

        for step in self.steps:
            step_execution = step.execute(self.db_alias)
            if not step_execution:
                continue
            if workflow_chain is None:
                workflow_chain = step_execution
            else:
                workflow_chain = workflow_chain | step_execution

        if workflow_chain:
            workflow_chain.apply_async()    


class ImportWorkflow(Workflow):
    
    def __init__(self, db_alias="default"):
        super().__init__(db_alias)
       
    @property
    def is_triggered(self): 
        # Check if workflow task is triggered 
        status_active = [Task.Status.PENDING, Task.Status.RUNNING]
        types_accepted = [Task.Type.DB_IMPORT, Task.Type.DB_UPDATE, Task.Type.DB_EXPORT]
        return Task.objects.using(self.db_alias).filter(status__in=status_active, type__in=types_accepted).exists()
    
    def setup(self):
        
        # 1. WorkflowStep: Import
        import_step = WorkflowStep(name="Import Step", parallel=True)
        for i in range(1, 4):
            db_task, is_created = Task.objects.using(self.db_alias).update_or_create(
                name=f"{Task.Type.DB_IMPORT}_{i}",
                type=Task.Type.DB_IMPORT,
                defaults={
                    'task_id': None,
                    'status': Task.Status.PENDING,
                    'current': 0,
                    'total': 500000
                }
            )
            import_step.tasks.append(db_task)
        self.add_step(import_step)
        
        # 2. WorkflowStep: Update
        update_step = WorkflowStep(name="Update Step", parallel=False)
        for i in range(1, 4):
            db_task, is_created = Task.objects.using(self.db_alias).update_or_create(
                name=f"{Task.Type.DB_UPDATE}_{i}",
                type=Task.Type.DB_UPDATE,
                defaults={
                    'task_id': None,
                    'status': Task.Status.PENDING,
                    'current': 0,
                    'total': 150000
                }
            )
            update_step.tasks.append(db_task)
        self.add_step(update_step)
            
        # 3. WorkflowStep: Export
        export_step = WorkflowStep(name="Export Step", parallel=True)
        for i in range(1, 4):
            db_task, is_created = Task.objects.using(self.db_alias).update_or_create(
                name=f"{Task.Type.DB_EXPORT}_{i}",
                type=Task.Type.DB_EXPORT,
                defaults={
                    'task_id': None,
                    'status': Task.Status.PENDING,
                    'current': 0,
                    'total': 50000
                }
            )
            export_step.tasks.append(db_task)
        self.add_step(export_step)        
        

@shared_task(bind=True)
def run_all_workflows(self):
    databases = [db_alias for db_alias in settings.DATABASES if db_alias != "default"]
    for db_alias in databases:
        workflow = ImportWorkflow(db_alias=db_alias)
        workflow.setup()
        workflow.run()
