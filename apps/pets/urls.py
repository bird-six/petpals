from django.urls import path
from apps.pets import views

app_name = 'pets'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.pets, name='pets'),
]