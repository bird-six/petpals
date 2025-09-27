from django.urls import path
from apps.users import views

app_name = 'users'
urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.user_register, name='user_register'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),
    path('addresses/', views.addresses, name='addresses'),
    path('browsing_history/', views.browsing_history, name='browsing_history'),
    path('my_favorites/', views.my_favorites, name='my_favorites'),
    path('my_posts/', views.my_posts, name='my_posts'),
    path('account_settings/', views.account_settings, name='account_settings'),

    path('addresses/provinces/', views.get_provinces, name='get_provinces'),
    path('addresses/cities/', views.get_cities, name='get_cities'),
    path('addresses/districts/', views.get_districts, name='get_districts'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('addresses/set_default/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('addresses/get/<int:address_id>/', views.get_address, name='get_address'),
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),
]