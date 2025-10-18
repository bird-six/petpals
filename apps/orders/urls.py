from django.urls import path
from apps.orders import views

app_name = 'orders'
urlpatterns = [
    path('', views.order, name='order'),
    path('create/', views.order_create, name='order_create'),
    path('pay/<int:order_id>/', views.pay, name='pay'),
]