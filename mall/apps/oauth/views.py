from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from mall import settings
from rest_framework import status
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
        token = OAuthQQ.get_access_token(code)

        # 3.用token换openid
        openid = OAuthQQ.get_open_id(token)
        pass