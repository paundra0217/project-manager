from rest_framework import serializers

from .models import ProjectBoard

class ProjectBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectBoard
        fields = ["id", "name", "description", "channel_id", "message_id", "created_at", "updated_at"]