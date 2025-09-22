from django.contrib import admin
from apps.users.models import User, Address


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_vip', 'is_active', 'is_admin')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipient_name', 'phone_number', 'province', 'city', 'district', 'detail_address', 'is_default')

