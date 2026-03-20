from django.db import models
from pmapi.models import ActiveManager, TimeStampedModel
from projects.models import ProjectBoard, BoardColumn
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.
class TaskItem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    project = models.ForeignKey(ProjectBoard, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    category = models.ForeignKey(BoardColumn, on_delete=models.CASCADE)
    updated_by = models.CharField(max_length=24, default="")
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.name
    
class TaskMembers(TimeStampedModel):
    class MemberRole(models.TextChoices):
        ASSIGNEE = 'ASG', _('Assignee')
        REVIEWER = 'REV', _('Reviewer')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    taskitem = models.ForeignKey(TaskItem, on_delete=models.CASCADE)
    user = models.CharField(max_length=24)
    role = models.CharField(max_length=3, choices=MemberRole.choices, default=MemberRole.ASSIGNEE)
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.user