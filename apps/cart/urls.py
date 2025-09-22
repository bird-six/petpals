from django.urls import path
from apps.cart import views

app_name = 'cart'
urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/<int:pet_id>/', views.add_pet_to_cart, name='add_pet_to_cart'),
    path('delete/<int:pet_id>/', views.delete_pet_to_cart, name='delete_pet_to_cart'),
    path('delete_selected/', views.delete_selected_pets, name='delete_selected_pets'),
]