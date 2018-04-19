import time
from django.http import JsonResponse, HttpResponse

from rest_framework.views import APIView

from myappp import models
from myappp.utils.permission import SVIPPermission, MyPermission1
from myappp.utils.throttle import VisitThrottle

ORDER_DICT = {
    1:{
        'name': "媳妇",
        'age':18,
        'gender':'男',
        'content':'...'
    },
    2:{
        'name': "老狗",
        'age':19,
        'gender':'男',
        'content':'...。。'
    },
}


# 对token使用md5摘要
def md5(user):
    import hashlib
    import time
    ctime = str(time.time())
    m = hashlib.md5(bytes(user,encoding='utf-8'))
    m.update(bytes(ctime,encoding='utf-8'))
    return m.hexdigest()




class AuthView(APIView):
    """
    用于用户认证
    """
    # 没有权限控制
    authentication_classes = []
    permission_classes = []
    # 没有登陆就使用这个匿名用户的访问频率的限制，如果不写就是使用配置中设置的全局的访问控制
    throttle_classes = [VisitThrottle,]

    def post(self,request,*args,**kwargs):
        self.dispatch()
        ret= {'code':1000,'msg':None}
        try:
            # 获取到原生的那个request，拿到用户名和密码
            user = request._request.POST.get('username')
            pwd = request._request.POST.get('password')
            obj = models.UserInfo.objects.filter(username=user, password=pwd).first()
            #如果没有这个，返回错误码
            if not obj:
                ret['code'] = 1001
                ret['msg'] = "用户名或密码错误"
            # 为登录用户创建token
            token = md5(user)
            # 存在就更新，不存在就创建
            models.UserToken.objects.update_or_create(user=obj, defaults={'token': token})
            ret['token'] = token
        except Exception as e:
            ret['code'] = 1002
            ret['msg'] = '请求异常'
        return JsonResponse(ret)


class OrderView(APIView):
    """
    订单相关信息，只有svip用户有权限
    """
    # 只需要应用上这个列表就可以实现认证了
    # authentication_classes = [FirstAuthtication,Authtication]
    permission_classes = [SVIPPermission,]
    def get(self,request,*args,**kwargs):
        # request.user
        # request.auth
        # 权限的访问
        # if request.user.user_type != 3:
        #     return HttpResponse('无权访问')
        ret = {'code':1000,'msg':None,'data':None}
        try:
            ret['data'] = ORDER_DICT
        except Exception as e:
            pass
        return JsonResponse(ret)

class UserInfoView(APIView):
    """
    订单相关业务（普通用户，VIP）
    """

    # authentication_classes = [Authtication, ]
    permission_classes = [MyPermission1, ]
    def get(self,request,*args,**kwargs):
        if request.user.user_type == 3:
            return HttpResponse('无权访问')
        return HttpResponse('用户信息')























