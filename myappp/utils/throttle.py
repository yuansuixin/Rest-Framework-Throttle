# -*- coding:UTF-8 -*-


import time


# 自定义的访问频率控制
## 应该放在缓存里，存储访问的时间
# VISIT_RECORD = {
# }
#
# class VisitThrottle(BaseThrottle):
#  # 60秒内只能访问3次
#     def __init__(self):
#         self.history = None
#
#     # 是否可以继续访问
#     def allow_request(self,request,view):
#         # 获取用户ip
#         remote_addr = self.get_ident(request)
#         # print(remote_addr)
#         # 如果没有这个ip，将当前的访问时间写入对应的ip中
#         ctime = time.time()
#         if remote_addr not in VISIT_RECORD:
#             VISIT_RECORD[remote_addr] = [ctime,]
#             return True
#         history = VISIT_RECORD.get(remote_addr)
#         self.history = history
#         # 一分钟只可以访问3次
#         while history and history[-1] < ctime-60:
#             history.pop()
#         if len(history) < 3:
#             # 如果可以访问的话，将当前的访问时间记录下来
#             history.insert(0,ctime)
#             return True
#         # return True # return False表示访问频率太高，被限制
#
#     def wait(self):
#         # 还需要等待多少秒可以访问
#         ctime = time.time()
#         return 60-(ctime - self.history[-1])

from rest_framework.throttling import BaseThrottle, SimpleRateThrottle
# 对于匿名用户的控制，使用的内置的SimpleRateThrottle类
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


















