import random

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.views import APIView
from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from verifications.serializers import RegisterSmscodeSerializer

'''

前端传递来一个 uuid 过来 我们后端生产一个图片

1. 接受image_code_id
2.生成图片和验证码
3.把验证码保存到redis
4.返回图片响应
GET ：verifications/imagecodes/(?P<image_code_id>.+)/
'''
class RegisterImageCodeView(APIView):

    def get(self,request,image_code_id):

        #创建图片和验证码
        text,image = captcha.generate_captcha()
        #通过redis 进行保存验证码
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s'%image_code_id,60,text)
        # 将图片返回
        # 注意  图片 是二进制 我们通过HttpResponse返回
        return HttpResponse(image,content_type='image/jpeg')

class RegisterSmsCodeView(APIView):
    def get(self,request,mobile):
        # 接收参数
        params = request.query_params
        #校验参数 需要验证码 用户输入 的图片验证码和redis的保存是否一致
        serializer =RegisterSmscodeSerializer(data = params)
        serializer.is_valid(raise_exception=True)

        # 生成短信
        sms_code = '%06d'%random.randint(0,999999)
        # 将短信保存在redis中
        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_'+mobile,5*60,sms_code)
        #使用云通讯发送短信
        # CCP().send_template_sms(mobile,[sms_code,5],1)
        from celery_tasks.sms.tasks import send_sms_code
        #delay 的参数和任务的参数对应
        # 必须调用delay方法
        send_sms_code.delay(mobile,sms_code)

        #返回响应
        return HttpResponse({'msg':'OK'})

