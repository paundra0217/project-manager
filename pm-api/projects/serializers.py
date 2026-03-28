import re
from rest_framework import serializers
from .models import ProjectBoard, BoardColumn

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
            "created_by",
            "updated_by",
            "created_at", 
            "updated_at"
            ]
        
class ProjectBoardCreateSerializer(serializers.ModelSerializer):
    user = serializers.RegexField(
        regex=r"^\d{17,20}$",
        error_messages={
            "invalid": "User must be a valid Discord ID."
        },
        write_only=True
    )

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
    user = serializers.RegexField(
        regex=r"^\d{17,20}$",
        error_messages={
            "invalid": "User must be a valid Discord ID."
        },
        write_only=True
    )

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
    

class BoardColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardColumn
        fields = [
            "id", 
            "project", 
            "name", 
            "color", 
            "created_by",
            "updated_by",
            "created_at", 
            "updated_at"
            ]
        
class BoardColumnCreateSerializer(serializers.ModelSerializer):
    user = serializers.RegexField(
        regex=r"^\d{17,20}$",
        error_messages={
            "invalid": "User must be a valid Discord ID."
        },
        write_only=True
    )

    class Meta:
        model = BoardColumn
        fields = [
            "name", 
            "color", 
            "user"
            ]
        extra_kwargs = {
            'name': {'required': True},
            'color': {'required': True},
            'user': {'required': True},
        }

    def validate_color(self, value):
        value = value.lstrip("#")

        if not re.match(r"^[0-9a-fA-F]{6}$", value):
            raise serializers.ValidationError(
                "Color must be a valid 6-digit hex code (e.g. #A1B2C3)."
            )
        return value.upper()  # optional normalization
        
    def create(self, validated_data):
        user_id = validated_data.pop("user")
        validated_data["created_by"] = user_id
        validated_data["updated_by"] = user_id
        return super().create(validated_data)
    
class BoardColumnEditSerializer(serializers.ModelSerializer):
    user = serializers.RegexField(
        regex=r"^\d{17,20}$",
        error_messages={
            "invalid": "User must be a valid Discord ID."
        },
        write_only=True
    )

    class Meta:
        model = BoardColumn
        fields = [
            "name", 
            "color", 
            "user"
            ]
        extra_kwargs = {
            'name': {'required': True},
            'color': {'required': True},
            'user': {'required': True},
        }

    def validate_color(self, value):
        if not re.match(r"^#(?:[0-9a-fA-F]{6})$", value):
            raise serializers.ValidationError(
                "Color must be a valid 6-digit hex code (e.g. #A1B2C3)."
            )
        return value.upper()  # optional normalization
        
    def create(self, validated_data):
        user_id = validated_data.pop("user")
        validated_data["created_by"] = user_id
        validated_data["updated_by"] = user_id
        return super().create(validated_data)