from django.db import models

from apps.pets.models import Pet
from apps.users.models import User


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '购物车 Cart'
        verbose_name_plural = '购物车 Cart'
        ordering = ['-updated_at']

    def __str__(self):
        if self.user:
            return f"{self.user.username}的购物车"

    def get_total_price(self):
        """计算购物车总价"""
        return sum(item.get_total_price() for item in self.items.all())

    def get_item_count(self):
        """计算购物车商品总数"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='所属购物车'
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        verbose_name='宠物'
    )
    quantity = models.IntegerField(
        default=1,
        verbose_name='数量'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='添加时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '购物车项 CartItem'
        verbose_name_plural = '购物车项 CartItem'
        unique_together = ('cart', 'pet')  # 确保购物车中同一宠物只出现一次

    def __str__(self):
        return f"{self.pet.name} - {self.quantity}只"

    def get_total_price(self):
        """计算商品项总价"""
        return self.pet.price * self.quantity