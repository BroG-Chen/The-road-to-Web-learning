# -*- coding: utf-8 -*-
# author: BergChen
# date: 2019/5/21

import json
import cgi
import tornado.web
import tornado.gen
import tornado.httpclient
import tornado.ioloop
from datetime import datetime

"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    路由解析 - 固定字符串路径
    
    比如路由规则 "/" 与 "/now"
"""


class MainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('Hello world!')


class NowHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        now_datetime = datetime.now()
        now = datetime.strftime(now_datetime, "%Y-%m-%d %H:%M:%S")
        self.write(now)


"""
    路由解析 - 参数字符串路径
    
    比如路由规则 "/number/(\d+)"
"""


class NumberHandler(tornado.web.RequestHandler):
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


class NumberDefaultHandler(tornado.web.RequestHandler):
    def get(self, number):
        if len(number) == 0:
            number = 'Default'
        self.write(number)


"""
    路由解析 - 多参数路径

    比如路由规则 "/date/(\d{4})/(\d{1,2})/(\d{1,2})"
"""


class DateHandler(tornado.web.RequestHandler):
    def get(self, year, month, day):
        self.write('%s 年 %s 月 %s 日' % (year, month, day))


"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    接入点函数 - 带参初始化 RequestHandler
    
    重写 RequestHandler.initialize 函数
    参数在 Application 定义 URL 映射时以 dict 方式给出
    （具体参考 RequestHandler.initialize 文档注释）
"""


class SomethingHandler(tornado.web.RequestHandler):

    def initialize(self, something):
        self.something = something

    def get(self):
        self.write(self.something)


"""
    接入点函数 - 请求处理前后

    RequestHandler.prepare 函数在请求处理前被调用，可用于进行初始化工作
    RequestHandler.on_finish 函数在请求处理后被调用，可用于进行资源清理工作
"""


class BeforeAndAfterHandler(tornado.web.RequestHandler):

    def prepare(self):
        print('"GET" prepare.')

    def on_finish(self):
        print('"GET" on finish.')

    def get(self):
        print('In "GET" method.')
        self.write('GET')


"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    输入捕获 - 解析参数

    RequestHandler.get_query_argument 与 RequestHandler.get_query_arguments
    只解析 URL 中的查询参数
    
    RequestHandler.get_body_argument 与 RequestHandler.get_body_arguments 
    只解析 Body 中的查询参数

    RequestHandler.get_argument 与 RequestHandler.get_arguments
    解析 URL 或者 Body 中的所有查询参数（一般情况下只使用 get_argument 或 get_arguments 即可）
    
        
"""


class InputCatchArgHandler(tornado.web.RequestHandler):

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


"""
    输入捕获 - 解析 HTTP 请求
    
    RequestHandler.request 返回 tornado.httputil.HTTPServerRequest 对象实例
    通过该对象能获取 HTTP 请求的相关信息
    
"""


class InputCatchReqHandler(tornado.web.RequestHandler):

    def get(self):
        remote_ip = self.request.remote_ip
        host = self.request.host
        path = self.request.path
        query = self.request.query
        protocol = self.request.protocol
        version = self.request.version
        uri = self.request.uri
        headers = self.request.headers
        body = self.request.body
        arguments = self.request.arguments
        files = self.request.files
        cookies = self.request.cookies
        http_req_info = dict()
        http_req_info.setdefault('remote_ip', str(remote_ip))
        http_req_info.setdefault('host', str(host))
        http_req_info.setdefault('path', str(path))
        http_req_info.setdefault('query', str(query))
        http_req_info.setdefault('protocol', str(protocol))
        http_req_info.setdefault('version', str(version))
        http_req_info.setdefault('uri', str(uri))
        http_req_info.setdefault('headers', str(headers))
        http_req_info.setdefault('body', str(body))
        http_req_info.setdefault('arguments', str(arguments))
        http_req_info.setdefault('files', str(files))
        http_req_info.setdefault('cookies', str(cookies))
        http_req_info_json = json.dumps(http_req_info, indent=True, ensure_ascii=False)
        print(type(self.request))
        print(http_req_info_json)
        html = cgi.escape(http_req_info_json)
        self.write(html)


"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    输出响应函数

    RequestHandler.set_status
    设置状态码以及状态描述
    
    RequestHandler.set_header
    set 设置请求头，名字相同时会覆盖
    RequestHandler.add_header
    add 添加请求头，名字相同时不会覆盖
    
    RequestHandler.set_cookie
    set 设置 Cookie，名字相同时会覆盖
    
    RequestHandler.write
    将给定的块作为 HTTP Body 发送给客户端
    通常输出字符串烧返回给客户端，但当给定的块是字典时
    
    RequestHandler.finish
    功能与 RequestHandler.write 作用相同
    但只是适用于 RequestHandler 的异步请求处理，同步或协程函数中无需调用 finish
    
    RequestHandler.render
    用于给定参数渲染模板
    
    RequestHandler.redirect
    页面重定向
    
    RequestHandler.clear
    清除先前已经写入的所有 Headers 和 Body
    RequestHandler.clear_header
    清除先前已经写入的某个 Headers
    RequestHandler.clear_cookie
    清除先前已经写入的某个 Cookies
    RequestHandler.clear_all_cookies
    清除先前已经写入的所有 Cookies

"""


class OutputResHandler(tornado.web.RequestHandler):

    def get(self):
        self.set_header(name='CUSTOM-HEADERS-BE-CLEAR', value='invisible')
        self.write('This sentence is not visible.</br>')
        self.clear()
        self.set_status(status_code=200, reason='Everything is all right')
        self.set_header(name='CUSTOM-HEADERS-NUMBER', value=1)
        self.add_header(name='CUSTOM-HEADERS-NUMBER', value=2)
        self.set_cookie(name='custom-cookie-1', value='c1')
        self.set_cookie(name='custom-cookie-2', value='c2')
        self.write('200 Everything is all right')


"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    异步化处理
    
    @tornado.web.asynchronous 装饰器可以将接入点函数由同步变为异步
    必须调用 RequestHandler.finish 函数通知 Tornado 请求处理已经完成，可以发送响应给客户端
"""


class AsyncHandler(tornado.web.RequestHandler):
    
    @tornado.web.asynchronous
    def get(self):
        self.write('Async')
        self.finish()


class AsyncSSRHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch('http://httpbin.org/ip', callback=self.on_response)

    def on_response(self, response):
        if response.error:
            raise tornado.web.HTTPError(500)
        self.write(response.body)
        self.finish()
        

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

        # 输入捕获 - 解析参数
        ('/input-catch-arg', InputCatchArgHandler),
        # 输入捕获 - 解析 HTTP 请求
        ('/input-catch-req', InputCatchReqHandler),

        # 输出响应函数 - 解析参数
        ('/output-res', OutputResHandler),

        # 异步化处理
        ('/async', AsyncHandler),
        ('/async-ssr', AsyncSSRHandler),

    ]
    app = tornado.web.Application(route_sheet)
    port = 8080
    app.listen(port=port)
    print('Tornado web server listen to %d port.' % port)
    tornado.ioloop.IOLoop.current().start()
