from .models import ProjectBoard
from .serializers import ProjectBoardSerializer, ProjectBoardCreateSerializer, ProjectBoardEditSerializer
import traceback
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
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
            description="Edit the project data by ID",
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