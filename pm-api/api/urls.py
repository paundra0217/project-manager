from django.urls import path, include

urlpatterns = [
    # Projects
    path('guilds/<str:guild_id>/projects/', include('projects.urls')),

    # Tasks
    path('tasks/', include('tasks.urls')),
]