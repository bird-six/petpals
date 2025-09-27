# apps/orders/models.py
from django.db import models
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from apps.pets.models import Pet
from apps.users.models import Address
import time
import uuid

User = get_user_model()

class Order(models.Model):
    """订单主表"""
    ORDER_STATUS = (
        ("pending_payment", "待支付"),
        ("paid", "已支付"),
        ("shipped", "已发货"),
        ("completed", "已完成"),
        ("cancelled", "已取消"),
    )
    # 添加支付方式选项
    PAYMENT_METHOD = (
        ("wechat", "微信支付"),
        ("alipay", "支付宝"),
        ("cod", "货到付款"),
    )

    order_number = models.CharField(max_length=32, unique=True, verbose_name="订单编号")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="用户")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, verbose_name="收货地址")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单总金额")
    status = models.CharField(max_length=16, choices=ORDER_STATUS, default="pending_payment", verbose_name="订单状态")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")
    ship_time = models.DateTimeField(null=True, blank=True, verbose_name="发货时间")
    complete_time = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    remark = models.TextField(null=True, blank=True, verbose_name="订单备注")
    payment_method = models.CharField(max_length=16, choices=PAYMENT_METHOD, verbose_name="支付方式")
    def generate_order_number(self):
        """生成唯一订单号：时间戳+随机字符串（确保唯一性）"""
        timestamp = int(time.time() * 1000)  # 毫秒级时间戳，减少重复概率
        random_str = str(uuid.uuid4().hex[:6]).upper()  # 6位随机字符串
        return f"{timestamp}{random_str}"

    def save(self, *args, **kwargs):
        # 仅在新建订单时生成订单号
        if not self.order_number:
            # 处理并发下的唯一性冲突：如果生成的订单号已存在，重试生成
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                self.order_number = self.generate_order_number()
                try:
                    super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise  # 超过重试次数，抛出异常
        else:
            super().save(*args, **kwargs)
    class Meta:
        verbose_name = "订单表 Order"
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """订单项表（关联订单和商品）"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="订单")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name="宠物")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="购买单价")  # 记录下单时的价格
    count = models.PositiveIntegerField(default=1, verbose_name="购买数量")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="总金额")

    class Meta:
        verbose_name = "订单项表 OrderItem"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.order.order_number} - {self.pet.name}"
