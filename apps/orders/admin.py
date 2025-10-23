from django.contrib import admin
from apps.orders.models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_number",
        "user",
        "status",
        "total_amount",
        "created_time",
        "complete_time",
    )
    list_filter = ("status", "created_time")
    ordering = ("-created_time",)
    readonly_fields = ("created_time", "pay_time")  # 将创建时间设为只读
    fieldsets = (
        ("基本信息", {
            "fields": ("order_number", "user", "status", "remark")
        }),
        ("金额信息", {
            "fields": ("total_amount", "payment_method")
        }),
        ("时间信息", {
            "fields": ("created_time", "pay_time", "ship_time", "complete_time")  # 保留created_time在详情页显示
        }),
        ("地址信息", {
            "fields": ("address",)
        }),
    )

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
