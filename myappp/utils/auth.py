# -*- coding:UTF-8 -*-

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from myappp import models


class FirstAuthtication(BaseAuthentication):
    """
    用户认证,返回None的情况，默认是匿名用户
    """
    def authenticate(self,request):
       pass

    def authenticate_header(self,request):
        pass



class Authtication(BaseAuthentication):
    """
    用户认证，一般都是使用一个对象认证，很少有多个认证的情况
    """
    def authenticate(self,request):
        # 获取到请求中的token
        token = request._request.GET.get('token')
        token_obj = models.UserToken.objects.filter(token=token).first()
        if not token_obj:
            raise exceptions.AuthenticationFailed('用户认证失败')
        # 在rest  framework内部会将这两个字段赋值给request，以供后续使用
        return (token_obj.user,token_obj)

    def authenticate_header(self,request):
        pass





