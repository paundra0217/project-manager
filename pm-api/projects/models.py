from django.db import models
from pmapi.models import ActiveManager, TimeStampedModel
import uuid

# Create your models here.
class ProjectBoard(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    guild_id = models.CharField(max_length=24)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    channel_id = models.CharField(max_length=24)
    message_id = models.CharField(max_length=24, default="")
    created_by = models.CharField(max_length=24, default="")
    updated_by = models.CharField(max_length=24, default="")
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.name
    
class BoardColumn(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    project = models.ForeignKey(ProjectBoard, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    color = models.CharField(max_length=12)
    order = models.IntegerField(default=0)
    created_by = models.CharField(max_length=24, default="")
    updated_by = models.CharField(max_length=24, default="")
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.name