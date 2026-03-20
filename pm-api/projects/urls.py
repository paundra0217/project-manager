from django.urls import path
from .views import ProjectBotView

urlpatterns = [
    path('get-project-list/<str:guild_id>', ProjectBotView.get_project_list),
    path('create-project', ProjectBotView.create_project)
]