from django.contrib import admin
from django.contrib.admin import site

from apps.pets.models import PetType, Pet

@admin.register(PetType)
class PetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

# @admin.register(Pet)
# class PetAdmin(admin.ModelAdmin):
#     list_display = ('name', 'birth_date', 'weight', 'gender', 'description', 'price', 'created_at', 'updated_at')

site.register(Pet)
