from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from mall import settings
from rest_framework import status

from oauth.models import OAuthQQUser

'''
当用户点击qq 按钮的时候会 发送一个请求
我们后端返回给他一个url（URL是根据 文档拼接出来的）

GET /oauth/qq/status/
'''
class OAuthQQURLAPIView(APIView):
    def get(self,request):

        # oauth_url = 'https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id=101474184&redirect_uri=http://www.meiduo.site:8080/oauth_callback.html&state=test'
        # 1.创建oauth实例对象
        state = 'test'
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                            client_secret=settings.QQ_CLIENT_SECRET,
                            redirect_uri=settings.QQ_REDIRECT_URI,
                            state=state)
        #获取跳转的url
        # get_qq_url方法已经封装好了qq授权地址
        oauth_url = oauth.get_qq_url()

        return Response({'auth_url':oauth_url})


'''
1.用户同意授权登录，这个时候辉返回一个code
2.我们用这个code换取token
3.有了token 我们换区openid
'''
"""
前端辉接受到 用户同意之后的 code 前端应该 将这个code 发送给后端

1.接受这个数据
2.用code换token
3.用token换openid

GET  /oauth/qq/users/?code=xxxx
"""
class OAuthQQUserAPIView(APIView):

    def get(self,request):
        # 1.接受这个数据
        params = request.query_params
        code = params.get('code')
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2.用code换token
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,)
        token = oauth.get_access_token(code)

        # 3.用token换openid
        openid = oauth.get_open_id(token)

        #openid 是此网站上唯一对应用户身份的标识，网站可将此id进行存储
        #便于用户下次登录 辨识其身份
        #获取openid 的两种情况“
        #1.用户之前绑定过
        #2. 用户之前没有绑定过
        #根据openid查询数据
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #不存在


            return Response({'access_token':openid})

        else:
            #存在 让用户登录
            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(qquser.user)
            token = jwt_encode_handler(payload)

            return Response({
                'token':token,
                'username':qquser.user.username,
                'user_id':qquser.user.id
            })


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mall import settings
#1.创建一个序列化器
# secret_key 密匙
#expires——in = None 过期时间 单位是秒
s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)

# 组织数据
data = {
    'openid':'1234567890'
}
# 3. 让序列化其对数据进行处理
token = s.dumps(data)

#4. 获取数据对数据进行解密
s.loads(token)

# 如果token 被篡改了 是可以检测到的
#如果token过期了 会报异常