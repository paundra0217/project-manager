from rest_framework import serializers

from .models import ProjectBoard

class ProjectBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectBoard
        fields = ["id", "name", "description", "guild_id", "channel_id", "message_id", "created_at", "updated_at"]