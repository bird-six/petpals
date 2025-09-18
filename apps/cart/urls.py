from django.urls import path
from apps.cart import views

app_name = 'cart'
urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/<int:pet_id>/', views.add_pet_to_cart, name='add_pet_to_cart'),
]