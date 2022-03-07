from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from .models import Task, Report
from celery.decorators import periodic_task
from celery import shared_task

@shared_task
def send_report(report):
    user = report.user
    task = Task.objects.filter(user=user, deleted=False)
    pending_tasks = task.filter(status="PENDING").count()
    completed_tasks = task.filter(status="COMPLETED").count()
    in_progress_tasks = task.filter(status="IN_PROGRESS").count()
    cancelled_tasks = task.filter(status="CANCELLED").count()
    body = f"""
        Hi {user.username},
        \n\nYou have {pending_tasks} pending tasks,
        {completed_tasks} completed tasks,
        {in_progress_tasks} in progress tasks,
        {cancelled_tasks} cancelled tasks.
        \n\n
        {user}
    """
    send_mail(
        "Daily Tasks Status Report [Task Manager]",
        body,
         "tasks@gdc.com",
        [user.email, "Syedareehaquasar@gmail.com"],
        fail_silently=False,
    )
    
    report.timestamp += timedelta(days=1)
    report.save()


@periodic_task(run_every=timedelta(seconds=10))
def report_mailer():
    currentTime = datetime.now(tz=timezone.utc)
    reports = Report.objects.filter(
        timestamp__lte = currentTime,
        is_disabled = False
    )
    for report in reports:
        send_report(report)