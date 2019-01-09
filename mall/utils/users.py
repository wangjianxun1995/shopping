def jwt_response_payload_handler(token, user=None, request=None):
    #token, jwt 身材个横的token
    # user = None,  jwt 认证成功之后的user
    # request = None ， 请求
    return {
        'token': token,
        'user_id':user.id,
        'username':user.username
    }