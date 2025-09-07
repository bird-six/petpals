from django.urls import path
from apps.community import views

app_name = 'community'
urlpatterns = [
    path('', views.community, name='community'),
]