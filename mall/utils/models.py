from django.db import models

class BaseModel(models.Model):
    ''' 模型类补充字段'''
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')

    class Meta:
        abstract = True  #是抽象模型类，用于继承使用数据迁移的时候不会创建BaseModel表