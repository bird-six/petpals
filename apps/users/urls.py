from django.urls import path
from apps.users import views

app_name = 'users'
urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),
    path('addresses/', views.addresses, name='addresses'),
    path('browsing_history/', views.browsing_history, name='browsing_history'),
    path('my_favorites/', views.my_favorites, name='my_favorites'),
    path('my_posts/', views.my_posts, name='my_posts'),
    path('account_settings/', views.account_settings, name='account_settings'),
]