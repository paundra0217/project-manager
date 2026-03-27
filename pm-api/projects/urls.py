from django.urls import path
from .views import ProjectBotView

urlpatterns = [
    path('', ProjectBotView.project_entry),
    path('<uuid:id>', ProjectBotView.project_detail),
]