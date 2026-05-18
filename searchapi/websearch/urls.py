from django.urls import path, include
from . import views

urlpatterns = [
    
    path('search', view=views.StandardAPIView.as_view()),
]
