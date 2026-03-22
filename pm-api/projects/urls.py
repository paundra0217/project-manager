from django.urls import path
from .views import ProjectBotView

urlpatterns = [
    path('get-project-list/<str:guild_id>', ProjectBotView.get_project_list),
    path('get-project/<uuid:id>', ProjectBotView.get_project),
    path('create-project', ProjectBotView.create_project),
    path('edit-project/<uuid:id>', ProjectBotView.edit_project)
]