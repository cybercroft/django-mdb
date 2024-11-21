import time
from django.conf import settings
from celery import group, shared_task
from celery_progress.backend import ProgressRecorder
from .workflows import Workflow, WorkflowStep


@shared_task(bind=True)
def import_task(self, db_name):
    progress_recorder = ProgressRecorder(self)
    total_steps = 10  # Example total steps
    for i in range(total_steps):
        print(f"Importing step {i + 1} for {db_name}")
        time.sleep(2)
        progress_recorder.set_progress(i + 1, total_steps, description=f"Step {i + 1} completed")
    return f"Import completed for {db_name}"


@shared_task(bind=True)
def update_task(self, db_name):
    progress_recorder = ProgressRecorder(self)
    total_steps = 5
    for i in range(total_steps):
        print(f"Updating step {i + 1} for {db_name}")
        time.sleep(1)
        progress_recorder.set_progress(i + 1, total_steps, description=f"Step {i + 1} completed")
    return f"Update completed for {db_name}"


@shared_task(bind=True)
def export_task(self, db_name):
    progress_recorder = ProgressRecorder(self)
    total_steps = 3
    for i in range(total_steps):
        print(f"Exporting step {i + 1} for {db_name}")
        time.sleep(2)
        progress_recorder.set_progress(i + 1, total_steps, description=f"Step {i + 1} completed")
    return f"Export completed for {db_name}"


@shared_task(bind=True)
def run_all_workflows(self):

    databases = [db_name for db_name in settings.DATABASES if db_name != "default"]
    progress_recorder = ProgressRecorder(self)
    total_workflows = len(databases)
    workflow_results = []

    for idx, db_name in enumerate(databases, start=1):
        workflow = Workflow(db_name)

        # Add steps to the workflow
        workflow.add_step(WorkflowStep([import_task, import_task], parallel=True))  # Import step
        workflow.add_step(WorkflowStep([update_task, update_task], parallel=False))  # Update step
        workflow.add_step(WorkflowStep([export_task, export_task], parallel=True))  # Export step

        # Schedule the workflow to run
        workflow_results.append(workflow.run())

        # Update progress for the current workflow
        progress_recorder.set_progress(idx, total_workflows, description=f"Workflow for {db_name} completed")

    # Run all workflows in parallel
    group(workflow_results)()
