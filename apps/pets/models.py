import os
from datetime import datetime

from django.db import models

# Create your models here.

def pet_image_path(instance, filename):
    # 获取文件扩展名
    ext = filename.split('.')[-1]

    # 获取当前时间，精确到秒
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")

    # 构建新的文件名：宠物类别-宠物名字-当前时间.扩展名
    new_filename = f"{instance.species}-{instance.name}-{current_time}.{ext}"

    # 返回完整路径
    return os.path.join('pets/', new_filename)

class PetType(models.Model):
    name = models.CharField(max_length=20, verbose_name='类型名称')  # 宠物类型名称
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    class Meta:
        verbose_name = "宠物类型表 PetType"
        verbose_name_plural = "宠物类型表 PetType"

class PetImage(models.Model):
    pet = models.ForeignKey('Pet', on_delete=models.CASCADE, related_name='images', verbose_name='所属宠物')
    image = models.ImageField(
        upload_to=pet_image_path,
        verbose_name='宠物图片',
        default='media/pets/default.jpg',
        null=False,
        blank=False,
    )
    is_primary = models.BooleanField(default=False, verbose_name='是否为主图')  # 标记是否为主图
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    class Meta:
        verbose_name = "宠物图片表 PetImage"
        verbose_name_plural = "宠物图片表 PetImage"

class Pet(models.Model):
    SPECIES_CHOICES = [
        ('cat', '猫咪'),
        ('dog', '狗狗'),
        ('little', '小宠'),
        ('aquatic', '水族'),
        ('bird', '鸟类'),
    ]
    species = models.CharField(
        null=False,
        blank=False,
        max_length=10,
        choices=SPECIES_CHOICES,
        verbose_name='宠物类别',
    )  # 宠物类别
    breed = models.CharField(max_length=20, verbose_name='宠物品种', null=False, blank=False)  # 宠物品种
    name = models.CharField(max_length=20, verbose_name='宠物名字', null=False, blank=False)  # 宠物名字
    birth_date = models.DateField(verbose_name="出生日期", null=False, blank=False)  # 宠物出生日期
    weight = models.FloatField(verbose_name='宠物重量(斤)')  # 宠物重量
    GENDER_CHOICES = [
        ('male', '公'),
        ('female', '母'),
    ]
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name='宠物性别',
        null=False,
        blank=False,
    )  # 宠物性别
    description = models.TextField(verbose_name='宠物描述', null=False, blank=False)  # 宠物描述
    price = models.FloatField(verbose_name='宠物价格(元)', null=False, blank=False)  # 宠物价格
    tag = models.CharField(max_length=5, verbose_name='宠物标签', null=True, blank=True)  # 宠物标签
    address = models.CharField(max_length=100, verbose_name='宠物地址', null=True, blank=True)  # 宠物地址
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    # 添加方法获取主图
    def get_primary_image(self):
        try:
            return self.images.filter(is_primary=True).first().image
        except:
            # 如果没有设置主图，则返回第一张图或默认图
            first_image = self.images.first()
            return first_image.image

    class Meta:
        verbose_name = "宠物商品表 Pet"
        verbose_name_plural = "宠物商品表 Pet"