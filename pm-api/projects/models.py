from django.db import models
from pmapi.models import ActiveManager
import uuid

# Create your models here.
class ProjectBoard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    server_id = models.CharField(max_length=24)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.name
    
class BoardColumn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    project = models.ForeignKey(ProjectBoard, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    color = models.CharField(max_length=12)
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.name