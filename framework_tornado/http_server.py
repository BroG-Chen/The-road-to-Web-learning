# -*- coding: utf-8 -*-
# author: BergChen
# date: 2019/5/21

from tornado import ioloop
from tornado import web
from datetime import datetime


"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    路由解析 - 固定字符串路径
    
    比如路由规则 "/" 与 "/now"
"""


class MainHandler(web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('Hello world!')


class NowHandler(web.RequestHandler):
    def get(self, *args, **kwargs):
        now_datetime = datetime.now()
        now = datetime.strftime(now_datetime, "%Y-%m-%d %H:%M:%S")
        self.write(now)


"""
    路由解析 - 参数字符串路径
    
    比如路由规则 "/number/(\d+)"
"""


class NumberHandler(web.RequestHandler):
    def get(self, number):
        self.write(number)


"""
    路由解析 - 带默认值的参数路径
    
    注意：
        与书籍《Python高效开发实战 Django Tornado Flask Twisted》P241 所述不太一样
        但参数字符串不存在时，RequestHandler 仍然会接受到空参数字符串
        
        比如路由规则 "/number-default/(\d*)"
        当访问路径 "/number-default/string" 时，RequestHandler 接受 "string" 
        当访问路径 "/number-default/" 时，RequestHandler 接受到的却是空字符串 "" 
"""


class NumberDefaultHandler(web.RequestHandler):
    def get(self, number):
        if len(number) == 0:
            number = 'Default'
        self.write(number)


"""
    路由解析 - 多参数路径

    比如路由规则 "/date/(\d{4})/(\d{1,2})/(\d{1,2})"
"""


class DateHandler(web.RequestHandler):
    def get(self, year, month, day):
        self.write('%s 年 %s 月 %s 日' % (year, month, day))


"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    接入点函数 - 带参初始化 RequestHandler
    
    重写 RequestHandler.initialize 函数
    参数在 Application 定义 URL 映射时以 dict 方式给出
    （具体参考 RequestHandler.initialize 文档注释）
"""


class SomethingHandler(web.RequestHandler):

    def initialize(self, something):
        self.something = something

    def get(self):
        self.write(self.something)


"""
    接入点函数 - 请求处理前后

    RequestHandler.prepare 函数在请求处理前被调用，可用于进行初始化工作
    RequestHandler.on_finish 函数在请求处理后被调用，可用于进行资源清理工作
"""


class BeforeAndAfterHandler(web.RequestHandler):

    def prepare(self):
        print('"GET" prepare.')

    def on_finish(self):
        print('"GET" on finish.')

    def get(self):
        print('In "GET" method.')
        self.write('GET')


"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    输入捕获

    RequestHandler.get_query_argument 与 RequestHandler.get_query_arguments
    只解析 URL 中的查询参数
    
    RequestHandler.get_body_argument 与 RequestHandler.get_body_arguments 
    只解析 Body 中的查询参数

    RequestHandler.get_argument 与 RequestHandler.get_arguments
    解析 URL 或者 Body 中的所有查询参数（一般情况下只使用 get_argument 或 get_arguments 即可）
    
        
"""


class InputCatchHandler(web.RequestHandler):

    def get(self):
        arg = self.get_argument(name='arg')
        args = self.get_arguments(name='args')
        res_body_list = [
            'arg value: %s' % arg,
            'arg type: %s' % str(arg.__class__).strip('<').strip('>'),
            'args value: %s' % args,
            'args type: %s' % str(args.__class__).strip('<').strip('>'),
        ]
        res_body = '</br>'.join(res_body_list)
        self.write(res_body)



if __name__ == '__main__':
    # 路由解析
    route_sheet = [
        # 路由解析 - 固定字符串路径
        ('/', MainHandler),
        ('/now', NowHandler),
        # 路由解析 - 参数字符串路径
        ('/number/(\d+)', NumberHandler),
        # 路由解析 - 带默认值的参数路径
        ('/number-default/(\d*)', NumberDefaultHandler),
        # 路由解析 - 多参数路径
        ('/date/(\d{4})/(\d{1,2})/(\d{1,2})', DateHandler),

        # 接入点函数 - 带参初始化
        ('/something', SomethingHandler, {'something': 'Say something.'}),
        # 接入点函数 - 请求处理前后
        ('/before-and-after', BeforeAndAfterHandler),

        # 接入点函数 - 请求处理前后
        ('/input-catch', InputCatchHandler),
    ]
    app = web.Application(route_sheet)
    port = 80
    app.listen(port=port)
    print('Tornado web server listen to %d port.' % port)
    ioloop.IOLoop.current().start()
