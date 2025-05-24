
from django.urls import path
from . import views

urlpatterns = [
    path('server-time/', views.server_time, name='server_time'),
]
