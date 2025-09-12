import uuid
import time

from django.contrib.auth.hashers import make_password
from django.db import models

class User(models.Model):
    # 用户名（注册时不会填写，默认生成，格式为PetPals_id）
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    # 是否冻结（使用is_active表示，默认True）
    is_active = models.BooleanField(default=True, verbose_name='白名单')
    # 是否为管理员
    is_admin = models.BooleanField(default=False, verbose_name='是否管理员')
    # 账户创建时间
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    # 是否VIP
    is_vip = models.BooleanField(default=False, verbose_name='是否VIP')
    # 上次登录时间
    last_login = models.DateTimeField(auto_now=True, verbose_name='上次登录时间')
    # 生日
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')

    # 重写save方法，自动生成用户名
    def save(self, *args, **kwargs):
        if not self.username:
            # 生成唯一ID (时间戳+随机数)
            unique_id = str(int(time.time())) + str(uuid.uuid4().hex[:6])
            self.username = f'PetPals_{unique_id}'
        # 确保密码被哈希
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '用户表 User'
        verbose_name_plural = '用户表 User'

    def __str__(self):
        return self.username

