import datetime
from django.db import models

from django.contrib.auth.models import User

from django.db.models.signals import pre_save
from django.dispatch import receiver

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    priority = models.IntegerField(null=False, default=0)

    def __str__(self):
        return self.title


class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    new_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(null=True, blank=True)
    time = models.TimeField(default="00:00:00")
    is_disabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Report"

@receiver(pre_save, sender=Task)
def update_task_history(instance, **kwargs):
    if instance.status == "COMPLETED":
        instance.completed = True
    else:
        instance.completed = False
    try:
        prev_status = Task.objects.get(pk=instance.id)
        if prev_status.status != instance.status:
            TaskHistory.objects.create(
                task=instance, old_status=prev_status.status, new_status=instance.status
            )
    except:
        pass