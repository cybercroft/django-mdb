from celery import group


class WorkflowStep:
    def __init__(self, tasks=[], parallel=True):
        self.tasks = tasks
        self.parallel = parallel

    def execute(self, db_name):
        if not self.tasks:
            return None
        if self.parallel:
            if len(self.tasks) == 1:
                return self.tasks[0].s(db_name) 
            return group(task.s(db_name) for task in self.tasks)
        else:
            if len(self.tasks) == 1:
                return self.tasks[0].s(db_name) 
            task_chain = self.tasks[0].s(db_name)
            for task in self.tasks[1:]:
                task_chain = task_chain | task.s(db_name)
            return task_chain


class Workflow:
    def __init__(self, db_alias):
        self.db_alias = db_alias
        self.steps = []

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

        return workflow_chain
