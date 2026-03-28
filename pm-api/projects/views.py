from .models import ProjectBoard, BoardColumn
from .serializers import (
    ProjectBoardSerializer, 
    ProjectBoardCreateSerializer, 
    ProjectBoardEditSerializer,
    BoardColumnSerializer,
    BoardColumnCreateSerializer,
    BoardColumnEditSerializer
    )
import traceback
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import transaction
from django.db.models import Max
from drf_spectacular.utils import extend_schema, extend_schema_view

class ProjectBotView():
    @extend_schema_view(
        get=extend_schema(
            description="Get the list of projects within a guild ID",
            responses=ProjectBoardSerializer
        ),
        post=extend_schema(
            description="Creates a new project within a guild ID",
            request=ProjectBoardCreateSerializer,
            responses=ProjectBoardSerializer
        ),
    )
    @api_view(["GET", "POST"])
    def project_entry(request, guild_id):
        match request.method:
            case 'GET':
                return ProjectBotView.get_project_list(request, guild_id)

            case 'POST':
                return ProjectBotView.create_project(request, guild_id)
            
            case _:
                return Response(
                    {"message": "Method not allowed"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )

    def get_project_list(request, guild_id):
        projects = ProjectBoard.objects.filter(guild_id=guild_id)

        return Response(
                {"projects": ProjectBoardSerializer(projects, many=True).data},
                status=status.HTTP_200_OK,
            )

    def create_project(request, guild_id):
        serializer = ProjectBoardCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        channel = serializer.validated_data["channel_id"]

        if ProjectBoard.objects.filter(guild_id=guild_id, channel_id=channel, is_deleted=False).exists():
            return Response(
                    {"message": "Channel already occupied by other project board."},
                    status=status.HTTP_409_CONFLICT,
                )

        project = serializer.save(
            guild_id=guild_id
        )

        return Response(
                ProjectBoardSerializer(project).data,
                status=status.HTTP_201_CREATED,
            )

    @extend_schema_view(
        get=extend_schema(
            description="Get the details of a project by ID",
            responses=ProjectBoardSerializer
        ),
        patch=extend_schema(
            description="Edit the project data",
            request=ProjectBoardEditSerializer,
            responses=ProjectBoardSerializer
        ),
        delete=extend_schema(
            description="Deletes the project data",
            responses=None
        )
    )
    @api_view(['GET', 'PATCH', 'DELETE'])
    def project_detail(request, guild_id, id):
        match request.method:
            case 'GET':
                return ProjectBotView.get_project(request, guild_id, id)

            case 'PATCH':
                return ProjectBotView.edit_project(request, guild_id, id)

            case 'DELETE':
                return ProjectBotView.delete_project(request, guild_id, id)
            
            case _:
                return Response(
                    {"message": "Method not allowed"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
        
    def get_project(request, guild_id, id):
        project = ProjectBoard.objects.filter(id=id, guild_id=guild_id).first()
        if not project:
            return Response(
                {"message": "Project does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        return Response(
                {"project": ProjectBoardSerializer(project).data},
                status=status.HTTP_200_OK,
            )
    
    def edit_project(request, guild_id, id):
        try:
            project = ProjectBoard.objects.get(id=id, guild_id=guild_id)
            serializer = ProjectBoardEditSerializer(
                project,
                data=request.data,
                partial=True
            )

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            channel = serializer.validated_data["channel_id"] if "channel_id" in serializer.validated_data else project.channel_id
            is_archived = serializer.validated_data["is_archived"] if "is_archived" in serializer.validated_data else project.is_archived

            if project.channel_id != channel:
                if ProjectBoard.objects.filter(guild_id=project.guild_id, channel_id=channel, is_deleted=False).exists():
                    return Response(
                        {"message": "Channel already occupied by other project board."},
                        status=status.HTTP_409_CONFLICT,
                    )
            
            if project.is_archived is True:
                if is_archived is not None and is_archived is False:
                    project = serializer.save()
                    return Response(
                        {"project": ProjectBoardSerializer(project).data},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"message": "Project is archived and cannot be modified."},
                        status=status.HTTP_409_CONFLICT,
                    )
            else:
                project = serializer.save()
                return Response(
                        {"project": ProjectBoardSerializer(project).data},
                        status=status.HTTP_200_OK,
                    )
        except ProjectBoard.DoesNotExist:
            return Response(
                    {"message": "Project does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            print(e)
            traceback.print_exc()
            return Response(
                    {"message": "Internal Server Error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
    
    def delete_project(request, guild_id, id):
        project = ProjectBoard.objects.get(id=id, guild_id=guild_id)
        project.is_deleted = True
        project.save()

        return Response(
                status=status.HTTP_204_NO_CONTENT,
            )

    @extend_schema_view(
        get=extend_schema(
            description="Get the list of columns within a project ID",
            responses=BoardColumnSerializer
        ),
        post=extend_schema(
            description="Creates a new column in a Project",
            request=BoardColumnCreateSerializer,
            responses=BoardColumnSerializer
        ),
    )
    @api_view(['GET', 'POST'])
    def column_entry(request, guild_id, project_id):
        match request.method:
            case 'GET':
                return ProjectBotView.list_columns(request, guild_id, project_id)

            case 'POST':
                return ProjectBotView.add_column(request, guild_id, project_id)
            
            case _:
                return Response(
                    {"message": "Method not allowed"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )

    def list_columns(request, guild_id, project_id):
        project = ProjectBoard.objects.filter(guild_id=guild_id, id=project_id).first()
        if project is None:
            return Response(
                    {"message": "Project not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        
        columns = BoardColumn.objects.filter(project=project)
        serialized = BoardColumnSerializer(columns, many=True).data
        return Response(
                {
                    "count": len(serialized),
                    "columns": serialized
                },
                status=status.HTTP_200_OK,
            )
    
    def add_column(request, guild_id, project_id):
        project = ProjectBoard.objects.filter(guild_id=guild_id, id=project_id).first()
        if project is None:
            return Response(
                    {"message": "Project not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        
        serializer = BoardColumnCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            last_order = (
                BoardColumn.objects
                .select_for_update()
                .filter(project=project, is_deleted=False)
                .aggregate(max_order=Max("order"))
            )["max_order"] or 0

            column = serializer.save(
                project=project,
                order=last_order + 1
            )
            
            columns = BoardColumn.objects.filter(project=project)
            serialized = BoardColumnSerializer(columns, many=True).data

            return Response(
                    {
                        "data": BoardColumnSerializer(column).data,
                        "count": len(serialized),
                        "columns": serialized
                    },
                    status=status.HTTP_201_CREATED,
                )

        
    @extend_schema_view(
        get=extend_schema(
            description="Get the details of a column by ID",
            responses=ProjectBoardSerializer
        ),
        patch=extend_schema(
            description="Edit the column data",
            request=ProjectBoardEditSerializer,
            responses=ProjectBoardSerializer
        ),
        delete=extend_schema(
            description="Deletes the column data",
            responses=None
        )
    )
    @api_view(['GET', 'PATCH', 'DELETE'])
    def column_detail(request, guild_id, column_id):
        match request.method:
            case 'GET':
                return ProjectBotView.get_column(request, guild_id, column_id)

            case 'PATCH':
                return ProjectBotView.edit_column(request, guild_id, column_id)

            case 'DELETE':
                return ProjectBotView.delete_project(request, guild_id, column_id)
            
            case _:
                return Response(
                    {"message": "Method not allowed"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )

    def get_column(request, guild_id, column_id):
        return

    def edit_column(request, guild_id, column_id):
        return
    
    def delete_project(request, guild_id, column_id):
        return
    
    @api_view(['POST'])
    def reorder_column(request, guild_id, project_id):
        return