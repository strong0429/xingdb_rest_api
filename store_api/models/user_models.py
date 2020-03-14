from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

from os import path

#用户头像上传地址及文件名
def photo_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    photo_file = '.'.join(['photo%06d'%instance.id, ext])
    file_path = path.join('users', 'head_photo')
    return path.join(file_path, photo_file)

#用户表，继承auth.models.AbstractUser
class XingUser(AbstractUser):
    mobile = models.CharField('手机号码', max_length=12,unique=True)
    wechat = models.CharField('微信', max_length=256, unique=True, null=True, blank=True)
    id_card = models.CharField('身份证', max_length=18, unique=True, null=True, blank=True)
    photo = models.ImageField('头像', upload_to=photo_upload_to, null=True, blank=True)

    class Meta:
        db_table = 'xing_user'
        ordering = ['last_login']  
    
    def __str__(self):
        return '%s %s' % (self.username, self.mobile)
