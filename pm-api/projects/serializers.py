from rest_framework import serializers

from .models import ProjectBoard

class ProjectBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectBoard
        fields = ["id", "name", "description", "created_at", "updated_at"]