import re

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    #token, jwt 身材个横的token
    # user = None,  jwt 认证成功之后的user
    # request = None ， 请求
    return {
        'token': token,
        'user_id':user.id,
        'username':user.username
    }
def get_user_by_account(username):
    try:
        #1.根据用户名确认用户输入的是手机号还是用户名
        if re.match(r'1[3-9]\d{9}',username):
            user = User.objects.get(mobile=username)

        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user=None
    return user
from django.contrib.auth.backends import ModelBackend

class UsernameMobleModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
    #     try:
    #         #1.根据用户名确认用户输入的是手机号还是用户名
    #         if re.match(r'1[3-9]\d{9}',username):
    #             user = User.objects.get(mobile=username)
    #
    #         else:
    #             user = User.objects.get(username=username)
    #     except User.DoesNotExist:
    #         user=None
        user=get_user_by_account(username)
        # 2.验证码 用户密码
        if user is not None and user.check_password(password):
            return user
        #必须返回
        return None