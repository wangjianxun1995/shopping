import re
from rest_framework import serializers

from users.models import User
from django_redis import get_redis_connection

class RegiserUserSerializer(serializers.ModelSerializer):

    #自己定义字段就可以了
    # 用户再进行提交的时候有3个数据:校验密码,短信验证码,是否同意协议
    # 所以,我们需要定义三个字段
    password2 = serializers.CharField(label='校验密码', allow_null=False, allow_blank=False, write_only=True)
    sms_code = serializers.CharField(label='短信验证码', max_length=6, min_length=6, allow_null=False, allow_blank=False,write_only=True)
    allow = serializers.CharField(label='是否同意协议', allow_null=False, allow_blank=False, write_only=True)

    token =serializers.CharField(label='token',read_only=True)
    """
    ModelSerializer 自动生产字段的过程
    会对fields 进行便利，先去model中哦查看是否有相应的字段
    如果有则自动生产如果没有则查看当前类 是否定义
    """
    class Meta:
        model = User
        fields = ['id','token','mobile','username','password','allow','sms_code','password2']
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }
    """
    mobile: 符合手机号管则
    密码：两次密码需要一致
    短信
    """
    #单个字段
    def validate_mobile(self, value):
        if not re.match(r'1[3-9]\d{9}',value):
            raise serializers.ValidationError('手机号不符合规则')

        return value

    def validate_allow(self,value):
        if value != 'true':
            raise serializers.ValidationError('没有同意协议')
        return value
    # 多个字段
    def validate(self, attrs):
        # 两次密码必须一致
        password = attrs['password']
        password2=attrs['password2']
        if password!=password2:
            raise serializers.ValidationError('密码不一致')


        #短信
        #2.1 获取用户提交的验证码
        mobiele = attrs.get('mobile')
        sms_code = attrs['sms_code']
        #2.2 获取redis
        redis_conn = get_redis_connection('code')
        redis_code = redis_conn.get('sms_'+mobiele)
        if redis_code is None:
            raise serializers.ValidationError('验证码失效')
        # 最好删除短信
        redis_conn.delete('sms_' + mobiele)
        #2.3 比对
        if redis_code.decode()!=sms_code:
            raise serializers.ValidationError('验证码不一致')
        return attrs

    def create(self, validated_data):
        # print(validated_data)
        del validated_data['sms_code']
        del validated_data['password2']
        del validated_data['allow']

        user = User.objects.create(**validated_data)
        # print(user)
        user.set_password(validated_data['password'])
        user.save()
        """
        当用户注册成功之后，自动登录

        自动登录的功能是要求用户注册成功之后 返回数据的时候需要额外添加一个token

        1.序列话的时候添加token
        2.token 怎么生成---->入库之后生产touken
        """
        #用户入库之后生产token
        from rest_framework_jwt.settings import api_settings
        # 需要使用jwt 的两个方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 让payload（载荷）成放一些用户信息
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user

