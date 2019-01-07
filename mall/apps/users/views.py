from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

"""
前端发送用户给后端  我们后端判断用户 是否注册

请求方式
GET  /user/usernames/(?P<username>\w{5,20})/count/

POST

"""
class RegisterUsernameAPIView(APIView):

    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        context={
            'count':count,
            'username':username
        }

        return Response(context)

class RegisPhoneCountAPIView(APIView):
    """
        查询手机号的个数
        GET:/user/phones/(?P<mobile>1[3456789]\d{9}/count/)

    """
    def get(self,request,mobile):
        #通过模型查询获取手机号个数
        count = User.objects.filter(mobile=mobile).count()
        context = {
            'count':count,
            'phone':mobile
        }
        return Response(context)
