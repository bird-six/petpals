from django.urls import path
from apps.orders import views

app_name = 'orders'
urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/<int:pet_id>/', views.checkout, name='checkout'),
    path('create/', views.order_create, name='order_create'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('pay/<int:order_id>/', views.pay, name='pay'),
    path('pay/result/', views.alipay_return, name='success'),
    path('alipay/notify/', views.alipay_notify, name="alipay_notify"),
    path('refund/<int:order_id>/', views.refund, name='refund'),
]