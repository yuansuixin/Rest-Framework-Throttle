# Rest-Framework源码解析----访问频率（节流）


## 访问频率控制（节流）

#### 1.控制访问频率（自定义组件）

```
# 应该放在缓存里，存储访问的时间
VISIT_RECORD = {
}

class VisitThrottle(object):
 # 60秒内只能访问3次
    def __init__(self):
        self.history = None

    # 是否可以继续访问
    def allow_request(self,request,view):
        # 获取用户ip
        #remote_addr = self.get_ident(request)
        remote_addr = request._request.META.get('REMOTE_ADDR')
        # print(remote_addr)
        # 如果没有这个ip，将当前的访问时间写入对应的ip中
        ctime = time.time()
        if remote_addr not in VISIT_RECORD:
            VISIT_RECORD[remote_addr] = [ctime,]
            return True
        history = VISIT_RECORD.get(remote_addr)
        self.history = history
        # 一分钟只可以访问3次
        while history and history[-1] < ctime-60:
            history.pop()
        if len(history) < 3:
            # 如果可以访问的话，将当前的访问时间记录下来
            history.insert(0,ctime)
            return True
        # return True # return False表示访问频率太高，被限制

    def wait(self):
        # 还需要等待多少秒可以访问
        ctime = time.time()
        return 60-(ctime - self.history[-1])



class AuthView(APIView):
    """
    用于用户认证
    """
    # 没有权限控制
    authentication_classes = []
    permission_classes = []
    throttle_classes = [VisitThrottle,]

    def post(self,request,*args,**kwargs):

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
```
#### 2.源码
- 源码流程，和认证的源码类似，
    - 匹配到url，然后到view视图里，执行父类的as_view()方法，该方法返回一个view函数，而在view（）函数里返回的是dispatch（）方法，我们就从dispatch()方法开始
    - 先封装好request，然后执行initial()实现一系列的认证，然后是权限的判断，后面就是访问频率了check_throttles（）
    - check_throttles（）方法，是一个循环，在get_throttles()函数中有一个列表生成式，拿到对象列表，对象列表是从throttle_classes中获取到的，默认是配置文件中拿到，当然也可以自己写到视图里，循环遍历对象列表，调用对象的allow_request()方法，通过返回值判断是否被限制，如果被限制就会抛出异常

#### 3. 全局配置和局部

- 全局配置，和认证，权限相似，直接在配置文件中设置就可以

```
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES':['myappp.utils.throttle.VisitThrottle'],
}

```
- 局部设置，就是直接在视图中加上throttle_classes这个列表就可以了，上面的自定义的代码中使用了局部的


#### 4.内置的控制频率的类
- 内置的类BaseThrottle类，自己写控制频率的类的时候需要继承
- 获取用户ip的时候，源码使用的是get_ident()方法，我们自己写的时候可以直接调用父类的这个方法
- 可以全局配置
- 内置的SimpleRateThrottle，其实也是由源码中的allow_request（）发起的
- 如果单独使用访问频率限制，直接加到视图中就可以了

```
from rest_framework.throttling import BaseThrottle, SimpleRateThrottle
# 对于匿名用户的控制
class VisitThrottle(SimpleRateThrottle):
    scope = 'luffy'
    def get_cache_key(self, request, view):
        return self.get_ident(request)


# 对于登录用户的控制
class UserThrottle(SimpleRateThrottle):
    scope = 'luffyuser'
    def get_cache_key(self, request, view):
        # 获取到用户名，
        return request.user.username
```

```
REST_FRAMEWORK = {
    # 我们没有辣么多的控制，加进来一个节流的类就可以，如果全加上，容易出现错误
    # 加上对登录用户的控制
    'DEFAULT_THROTTLE_CLASSES':['myappp.utils.throttle.UserThrottle'],
    'DEFAULT_THROTTLE_RATES':{
        'luffy':'3/m',# 一分钟可以访问3次
        'luffyuser':'10/m',# 一分钟访问10次，对于登录用户
    }
}

```


###### 梳理
- 基本使用
    - 类，必须继承BaseThrottle类，必须实现：allow_request(),wait()方法
    - 类， 必须继承：SimpleRateThrottle，实现：get_cache_key，scope='luccy'(配置文件中的key)

- 全局应用和局部应用


[节流的详细解析](https://yuansuixin.github.io/archives/2018/01/ "节流的详细解析")