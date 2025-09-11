from django.contrib import admin
from django.contrib.admin import site

from apps.pets.models import PetType, Pet, PetImage

@admin.register(PetType)
class PetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

class PetImageInline(admin.TabularInline):
    """图片Inline类，用于嵌入到主模型Admin中"""
    model = PetImage
    extra = 3  # 默认显示3个图片上传框


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('species', 'breed', 'name', 'birth_date', 'weight', 'gender', 'price')
    inlines = [PetImageInline]  # 嵌入图片上传表单


