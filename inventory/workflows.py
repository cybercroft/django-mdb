from celery import chain, group
from inventory.models import Task


class WorkflowTask:
    def __init__(self, task:Task, func):
        self.task = task 
        self.func = func 


class WorkflowStep:
    def __init__(self, name="", parallel=False):
        self.name = name 
        self.parallel = parallel
        self.tasks = []
    
    @property
    def progress_total(self):
        return sum([task.total for task in self.tasks]) 
    
    @property
    def progress_current(self):
        return sum([task.current for task in self.tasks]) 
    
    @property
    def progress_percent(self):
        return self.progress_current / self.progress_total

    def add_task(self, task: Task, func):
        self.tasks.append(WorkflowTask(task=task, func=func))
    
    def execute(self):
        if len(self.tasks) == 0:
            return None
        elif len(self.tasks) == 1:
            return self.tasks[0].func
        # Parallel execution
        if self.parallel:
            return group(task.func for task in self.tasks)
        # Sequential execution
        task_chain = chain(self.tasks[0].func) 
        for task in self.tasks[1:]:
            task_chain = task_chain | task.func
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
            step_execution = step.execute()
            if not step_execution:
                continue
            if workflow_chain is None:
                workflow_chain = step_execution
            else:
                workflow_chain = workflow_chain | step_execution

        if workflow_chain:
            workflow_chain.apply_async()    
