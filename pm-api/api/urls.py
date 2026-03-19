from django.urls import path, include

urlpatterns = [
    # Auth
    path('auth/', include('userauth.urls')),

    # User Task
    path('usertask/', include('usertask.urls')),

    # User Participant
    path('participant/', include('participant.urls')),

    # User Clicks
    path('userclicks/', include('userclicks.urls')),

    # Dashboard
    path('dashboard/', include('dashboard.urls')),
]