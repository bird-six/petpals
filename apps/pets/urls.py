from django.urls import path
from apps.pets import views

app_name = 'pets'
urlpatterns = [
    path('', views.pets, name='pets'),
    path('detail/<int:pet_id>/', views.detail, name='detail'),
]