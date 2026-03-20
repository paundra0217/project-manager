from django.urls import path, include

urlpatterns = [
    # Auth
    path('projects/', include('projects.urls')),

    # User Task
    path('tasks/', include('tasks.urls')),
]