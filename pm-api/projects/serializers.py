from rest_framework import serializers

from .models import ProjectBoard

class ProjectBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectBoard
        fields = [
            "id", 
            "name", 
            "description", 
            "channel_id", 
            "message_id", 
            "is_archived",
            "created_at", 
            "updated_at"
            ]
        
class ProjectBoardCreateSerializer(serializers.ModelSerializer):
    user = serializers.CharField(write_only=True)

    class Meta:
        model = ProjectBoard
        fields = [
            "name",
            "description",
            "channel_id",
            "message_id",
            "user",
            ]
        extra_kwargs = {
            'name': {'required': True},
            'description': {'required': True},
            'channel_id': {'required': True},
            'message_id': {'required': True},
            'user': {'required': True},
        }
        
    def create(self, validated_data):
        user_id = validated_data.pop("user")
        validated_data["created_by"] = user_id
        validated_data["updated_by"] = user_id
        return super().create(validated_data)
    
class ProjectBoardEditSerializer(serializers.ModelSerializer):
    user = serializers.CharField(write_only=True)

    class Meta:
        model = ProjectBoard
        fields = [
            "name",
            "description",
            "channel_id",
            "message_id",
            "is_archived",
            "user"
            ]
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'channel_id': {'required': False},
            'message_id': {'required': False},
            'is_archived': {'required': False},
            'user': {'required': True},
        }
        
    def create(self, validated_data):
        validated_data["updated_by"] = validated_data.pop("user")
        return super().create(validated_data)