from django.shortcuts import render
from .models import ProjectBoard
from .serializers import ProjectBoardSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action

class ProjectBotView():
    @api_view(["GET"])
    def get_project_list(request, guild_id):
        projects = ProjectBoard.objects.filter(server_id=guild_id)

        return Response(
                {"projects": ProjectBoardSerializer(projects, many=True).data},
                status=status.HTTP_200_OK,
            )

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
        
        user = request.data.get("user")
        if not user:
            return Response(
                {"message": "Project creator (user) is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        project = ProjectBoard.objects.create(
            name=name, 
            description=description, 
            server_id=server, 
            channel_id=channel,
            message_id=message,
            updated_by=user
            )

        return Response(
                {"id": project.id},
                status=status.HTTP_201_CREATED,
            )
    
    @api_view(['GET', 'PATCH', 'DELETE'])
    def project_detail(request, id):
        if request.method == 'GET':
            return ProjectBotView.get_project(request, id)

        elif request.method == 'PATCH':
            return ProjectBotView.edit_project(request, id)

        elif request.method == 'DELETE':
            return ProjectBotView.delete_project(request, id)
        
    def get_project(request, id):
        project = ProjectBoard.objects.filter(id=id).first()
        if not project:
            return Response(
                {"message": "Project does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        return Response(
                {"project": ProjectBoardSerializer(project).data},
                status=status.HTTP_200_OK,
            )
    
    def edit_project(request, id):
        name = request.data.get("name")
        description = request.data.get("description")
        user = request.data.get("user")
        channel = request.data.get("channel")
        message = request.data.get("message")

        project = ProjectBoard.objects.get(id=id)
        project.name = name if name else project.name
        project.description = description if description else project.description
        project.updated_by = user if user else project.user
        project.channel_id = channel if channel else project.channel_id
        project.message_id = message if message else project.message_id
        project.save()

        return Response(
                {"project": ProjectBoardSerializer(project).data},
                status=status.HTTP_200_OK,
            )
    
    def delete_project(request, id):
        project = ProjectBoard.objects.get(id=id)
        project.is_deleted = True
        project.save()

        return Response(
                status=status.HTTP_204_NO_CONTENT,
            )