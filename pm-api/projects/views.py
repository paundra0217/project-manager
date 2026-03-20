from django.shortcuts import render
from .models import ProjectBoard
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action

class ProjectView():
    @api_view(["GET"])
    def get_project(id, request):
        return
    
    @api_view(["GET"])
    def get_project_list(id, request):
        projects = ProjectBoard.objects.filter(server_id=id)
        return

    @api_view(["POST"])
    def create_project(request):
        name = request.data.get("name")
        if not name:
            return Response(
                {"message": "Name is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        description = request.data.get("description")
        if not description:
            return Response(
                {"message": "Description is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        server = request.data.get("server")
        if not server:
            return Response(
                {"message": "Server is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        channel = request.data.get("channel")
        if not channel:
            return Response(
                {"message": "Channel is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        message = request.data.get("message")
        if not message:
            return Response(
                {"message": "Message is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        project = ProjectBoard.objects.create(
            name=name, 
            description=description, 
            server_id=server, 
            channel_id=channel,
            message_id=message
            )

        return Response(
                {"id": project.id},
                status=status.HTTP_201_CREATED,
            )