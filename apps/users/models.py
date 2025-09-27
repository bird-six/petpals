from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True, verbose_name='用户名')
    email = models.EmailField(max_length=100, unique=True)
    # 是否为管理员
    is_admin = models.BooleanField(default=False, verbose_name='是否管理员')
    # 是否VIP
    is_vip = models.BooleanField(default=False, verbose_name='是否VIP')
    # 生日
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')

    # 为组和权限字段添加related_name以避免冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='user_set_custom',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='user_set_custom',
        related_query_name='user',
    )

    # 重写save方法，自动生成用户名
    def save(self, *args, **kwargs):
        if not self.username:
            # 生成唯一ID (时间戳+随机数)
            import uuid
            import time
            unique_id = str(int(time.time())) + str(uuid.uuid4().hex[:6])
            self.username = f'PetPals_{unique_id}'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '用户表 User'
        verbose_name_plural = '用户表 User'

    def __str__(self):
        return self.email

class Address(models.Model):
    """用户收货地址模型"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="用户"
    )
    recipient_name = models.CharField(
        max_length=50,
        verbose_name="收件人"
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name="联系电话"
    )
    province = models.CharField(
        max_length=50,
        verbose_name="省份/直辖市"
    )
    city = models.CharField(
        max_length=50,
        verbose_name="城市"
    )
    district = models.CharField(
        max_length=50,
        verbose_name="区/县"
    )
    detail_address = models.CharField(
        max_length=200,
        verbose_name="详细地址"
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="是否默认地址"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        verbose_name = "收货地址 Address"
        verbose_name_plural = "收货地址 Address"
        ordering = ["-is_default", "-updated_at"]  # 优先显示默认地址，按更新时间排序


    def __str__(self):
        return f"{self.recipient_name}的地址：{self.province}{self.city}{self.district}{self.detail_address}"

    def save(self, *args, **kwargs):
        """重写保存方法：当设置为默认地址时，自动取消该用户其他地址的默认状态"""
        if self.is_default:
            # 过滤出该用户其他的默认地址，并设为非默认
            Address.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


