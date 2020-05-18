from django.contrib.auth.models import BaseUserManager, AbstractBaseUser  #PermissionsMixin, UserManager
from django.utils import timezone
from django.db import models

import re
from os import path
from public.utils import MobileValidator, IDValidator

#自定义用户管理类：UserManager
class UserManager(BaseUserManager):
    def _create_user(self, mobile, wechat, password, **extra_fields):
        if not mobile:
            raise ValueError('注册用户必须提供手机号码')
        user = self.model(mobile = mobile, wechat = wechat, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile, wechat=None, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', False)

        if extra_fields.get('is_admin') is True:
            raise ValueError('非超级用户必须设置：is_admin=False')
        return self._create_user(mobile, wechat, password, **extra_fields)

    def create_superuser(self, mobile, wechat=None, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('创建超级用户必须设置：is_admin=True.')

        return self._create_user(mobile, wechat, password, **extra_fields)
        

#用户头像上传地址及文件名
def photo_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    photo_file = '.'.join(['photo%06d'%instance.id, ext])
    file_path = path.join('users', 'head_photo')
    return path.join(file_path, photo_file)

#用户表，继承auth.models.AbstractBaseUser
class User(AbstractBaseUser): # 暂不做权限管理, PermissionsMixin):
    id_card_validator = IDValidator()
    mobile_validator = MobileValidator()

    mobile = models.CharField(
        '手机号码', max_length=11, unique=True, validators=[mobile_validator]
    )
    autonym = models.CharField('实名', max_length=16, null=True, blank=True)
    id_card = models.CharField('身份证', max_length=18, unique=True, \
        null=True, blank=True, validators=[id_card_validator])
    nickname = models.CharField('昵称', max_length=24, null=True, blank=True)
    wechat = models.CharField('微信', max_length=256, unique=True, null=True, blank=True)
    email = models.EmailField('邮箱', null=True, blank=True)
    photo = models.ImageField('头像', upload_to=photo_upload_to, null=True, blank=True)
    date_joined = models.DateTimeField('注册日期', default=timezone.now)
    
    is_admin = models.BooleanField('管理员', default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['wechat']

    class Meta:
        db_table = 'dbs_user'

    def get_full_name(self):
        return self.autonym

    def get_short_name(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    '''
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    '''
    def __str__(self):
        return "%s %s" % (self.mobile, self.autonym)


