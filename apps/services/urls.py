from django.urls import path
from apps.services import views

app_name = 'services'
urlpatterns = [
    path('', views.services, name='services'),
]