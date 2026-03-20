from django.urls import path
from .views import ProjectView

urlpatterns = [
    path('get-project-list/<uuid:id>', ProjectView.get_project_list),
    path('create-project', ProjectView.create_project)
]