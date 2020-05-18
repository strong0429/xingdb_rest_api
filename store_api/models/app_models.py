from django.db import models

#App版本记录表
class AppVersion(models.Model):
    app_name = models.CharField('APP名称', max_length=32)
    ver_code = models.IntegerField('版本号')
    ver_txt = models.CharField('版本描述', max_length=8)
    date_pub = models.DateTimeField('发布日期', auto_now_add=True)
    detail = models.TextField('更新清单', null=True, blank=True)

    class Meta:
        db_table = 'dbs_app_version'
        #ordering = ['app_name', 'ver_code']
        unique_together = ['app_name', 'ver_code']

    def __str__(self):
        return '%s(%s)' % (self.app_name, self.ver_txt)
