from celery import Celery


#创建Celery对象
#参数main 设置脚本名
app = Celery('celery_tasks')

#加载配置文件
app.config_from_object('celery_tasks.config')