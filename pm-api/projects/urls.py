from django.urls import path
from .views import ProjectBotView

urlpatterns = [
    path('', ProjectBotView.project_entry),
    path('<uuid:id>', ProjectBotView.project_detail),
    path('<uuid:project_id>/columns', ProjectBotView.column_entry),
    path('<uuid:project_id>/columns/reorder', ProjectBotView.reorder_column),
    path('columns/<uuid:column_id>', ProjectBotView.column_detail)
]