from django.contrib import admin
from apps.orders.models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "total_amount",
        "created_time",
        "complete_time",
    )
    list_filter = ("status", "created_time")
    ordering = ("-created_time",)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "pet",
        "price",
        "count",
        "total_price",
    )
    ordering = ("-order__created_time",)
