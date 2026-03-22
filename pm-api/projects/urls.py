from django.urls import path
from .views import ProjectBotView

urlpatterns = [
    path('list/<str:guild_id>', ProjectBotView.get_project_list),
    path('', ProjectBotView.create_project),
    path('<uuid:id>', ProjectBotView.project_detail),
]