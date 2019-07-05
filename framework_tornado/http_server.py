# -*- coding: utf-8 -*-
# author: BergChen
# date: 2019/5/21

import os
import json
import cgi
import uuid
import tornado.web
import tornado.gen
import tornado.httpclient
import tornado.ioloop
import tornado.template
from datetime import datetime

"""
    tornado.options 模块可用于从命令行读取配置
    tornado.options.define  定义参数类型, 默认值和参数说明
    tornado.options.options 获取命令行传入的参数
"""

from tornado.options import define, options

define(name='port', default=8888, help='Run on this port', type=int)

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
    
    注意：RequestHandler.initialize 在每次 RequestHandler 子孙类初始化时都会被调用
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

    异常处理
    
    重写 RequestHandler.write_error 函数可自定义该路由下各种异常状态码的处理逻辑

"""


class ErrorBackHandler(tornado.web.RequestHandler):

    def get(self):
        greeting = self.get_argument('greeting', 'Hi')
        name = self.get_argument('name')
        self.write("%s, %s." % (greeting, name))

    def write_error(self, status_code, **kwargs):
        if status_code == 400:
            self.write('Error, Bad Request (argument "name" must be assigned).')
        else:
            self.write('Error, Other untreated status code %s.' % status_code)


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
    # 以网站转发为例

    @tornado.web.asynchronous
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch('http://httpbin.org/ip', callback=self.on_response)

    def on_response(self, response):
        if response.error:
            raise tornado.web.HTTPError(500)
        self.write(response.body)
        self.finish()


"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    协程化处理

    @tornado.gen.coroutine 装饰器同样可以将接入点函数由同步变为异步
    既满足了异步处理又符合同步编程风格
    （协程化处理无需使用 RequestHandler.finish）
    
    要点：
        1.使用 @tornado.gen.coroutine 装饰接入点函数
        2.使用异步对象来处理一些耗时的操作，比如使用 AsyncHTTPClient 请求
        3.调用 yield 关键字来获取异步对象的处理结果
"""


class CoroutineHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        response = yield http.fetch('http://httpbin.org/ip')
        self.write(response.body)


"""
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    身份验证 - Cookie 机制
   
   RequestHandler.get_cookie 获取指定的 Cookies
   （获取 HTTP 请求头的 Cookies）
   
   RequestHandler.set_cookie 设置指定的 Cookies
   （设置 HTTP 响应头的 Set-Cookies）
   
   RequestHandler.clear_cookie 清除指定的 Cookies
   （将 HTTP 请求头的 Cookies 指定的值清除为空白并设置在响应头的 Set-Cookies ）
   
   
   注意：RequestHandler.get_cookie 返回类型是 bytes 不是 str
"""

SESSION_ID = 0
REQUEST_COUNT = 0


class AuthCookiesHandler(tornado.web.RequestHandler):

    def get(self):
        global SESSION_ID
        global REQUEST_COUNT
        REQUEST_COUNT += 1
        if not self.get_cookie('session'):
            SESSION_ID += 1
            self.set_cookie('session', str(SESSION_ID))
            self.write('Session ID get new one.')
        elif REQUEST_COUNT % 3 == 0:
            self.clear_cookie('session')
            self.write('Session ID clear.')
        else:
            self.write('Session ID was set.')


"""

    身份验证 - 安全 Cookie 机制

    
    tornado.web.Application 的 cookie_secret 参数可以赋予 Cookies 加盐加密的效果，使 Cookies 难以被伪造
    但需要结合 RequestHandler.get_secure_cookie 和 RequestHandler.set_secure_cookie 来使用 

    要点：
        1.tornado.web.Application 对象初始化时需要 cookie_secret 参数，该参数作为 Cookies 加密的密钥
        2.读取 Cookies 时，使用 RequestHandler.get_secure_cookie 代替 RequestHandler.get_cookie
        3.写入 Cookies 时，使用 RequestHandler.set_secure_cookie 代替 RequestHandler.set_cookie

"""
COOKIES_SECRET = 'SALT'


class AuthSecretCookiesHandler(tornado.web.RequestHandler):

    def get(self):
        global SESSION_ID
        global REQUEST_COUNT
        REQUEST_COUNT += 1
        if not self.get_secure_cookie('session'):
            SESSION_ID += 1
            self.set_secure_cookie('session', str(SESSION_ID))
            self.write('Session ID get new one.')
        elif REQUEST_COUNT % 3 == 0:
            self.clear_cookie('session')
            self.write('Session ID clear.')
        else:
            self.write('Session ID was set.')


"""

    身份验证 - 用户身份认证
    
"""

# 存储已进行身份认证的用户 UUID 映射关系
# 这些 UUID 必须与 Cookies 关联, 才能够标识请求的认证状态
SESSION_MAP = dict()


# 继承 RequestHandler 并重写 get_current_user 方法
class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        # get_current_user 根据 Cookies 获取当前会话对应的用户身份
        global SESSION_MAP
        session_id = self.get_secure_cookie('session_id')
        session_id = session_id.decode()
        current_user = SESSION_MAP.get(session_id)
        return current_user


# 模拟需要用户身份认证才能访问的页面
class NeedAuthHandler(BaseHandler):

    # tornado.web.authenticated 装饰器
    # 用于检查当前 RequestHandler.current_user 是否存在, 即本次请求是否已经通过用户身份认证
    # 若通过则执行被装饰的接入点函数, 否则将重定向到 tornado.web.Application 制定的 login_url
    # （具体逻辑可参考 tornado.web.authenticated 文档注释）
    @tornado.web.authenticated
    def get(self):
        current_user = self.current_user
        user_name = tornado.web.escape.xhtml_escape(current_user)
        self.write('Hi, this is %s' % user_name)

    # 以下函数功能与使用 @tornado.web.authenticated 一样
    # def get(self):
    #     current_user = self.get_current_user()
    #     if not current_user:
    #         self.redirect("/login")
    #         return
    #     user_name = tornado.web.escape.xhtml_escape(current_user)
    #     self.write('Hi, this is %s' % user_name)


# 模拟登录页面
class LoginHandler(BaseHandler):

    # 收到 GET 请求返回用户身份验证页面
    def get(self):
        login_from = '<form action="/login" method="post">' \
                     'Name: <input type="text" name="name">' \
                     '<input type="submit" name="Sign in">' \
                     '</form>'
        html = '<html><body>%s</body></html>' % login_from
        self.write(html)

    # 收到 POST 进行用户身份认证
    # 认证成功则生成当前用户的 UUID 并保存, 还需要与 Cookies 关联, 然后再跳转到制定页面
    # 认证失败则依然跳转到 login_url
    def post(self):
        global SESSION_MAP
        name = self.get_argument('name')
        if len(name) <= 3:
            self.redirect('/login')
        else:
            session_id = str(uuid.uuid1())
            SESSION_MAP[session_id] = name
            self.set_secure_cookie('session_id', session_id)
            self.redirect('/need-auth')


"""

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    表单与模板 - 渲染与填充
    
    tornado.web.Application 的 template_path 参数指明模板所在目录
    RequestHandler.render 从模板目录读取指定模板并按传入参数进行填充
    
    tornado.template.Template 类也可以用于生成模板
    
    要点：
        1、“{{” 和 “}}” 括起来的内容可以是变量或者表达式

"""


class PoemIndexHandler(tornado.web.RequestHandler):

    def get(self):
        number = self.get_argument('number', '1')
        if int(number) == 1:
            self.render(template_name='poem-index.html',
                        route='/poem-page',
                        number=1)
        else:
            self.render(template_name='poem-index.html',
                        route='/poem-page-temp',
                        number=2)


class PoemPageHandler(tornado.web.RequestHandler):

    def post(self):
        noun1 = self.get_argument('noun1')
        noun2 = self.get_argument('noun2')
        verb = self.get_argument('verb')
        noun3 = self.get_argument('noun3')
        self.render('poem-page.html',
                    roads=noun1,
                    wood=noun2,
                    made=verb,
                    difference=noun3)


class PoemPageTempHandler(tornado.web.RequestHandler):

    def post(self):
        noun1 = self.get_argument('noun1')
        noun2 = self.get_argument('noun2')
        verb = self.get_argument('verb')
        noun3 = self.get_argument('noun3')
        html_temp = \
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Poem Maker Pro 2</title>
        </head>
        <body>
        <h1>Your poem 2</h1>
        <p>
            Two {{roads}} diverged in a {{wood}}, and I—<br>
            I took the one less travelled by,<br>
            And that has {{made}} all the {{difference}}.
        </p>
        </body>
        </html>
        """
        temp = tornado.template.Template(template_string=html_temp)
        content = temp.generate(roads=noun1,
                                wood=noun2,
                                made=verb,
                                difference=noun3)
        self.write(content)


"""

    表单与模板 - 填充表达式

"""


class ExpressionTempHandler(tornado.web.RequestHandler):

    def get(self):
        html_temp = \
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Expression</title>
        </head>
        <body>
        <p>
            {{ 1 + 2 }}<br>
            {{ ', '.join([i for i in range(10)]) }}<br>
        </p>
        </body>
        </html>
        """
        temp = tornado.template.Template(template_string=html_temp)
        content = temp.generate()
        self.write(content)


"""

    表单与模板 - 控制流语句

    语句块以 "{%" 开始 "%}" 结束
"""


class ControlFlowTempHandler(tornado.web.RequestHandler):

    def get(self):

        html_temp = \
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Control Flow</title>
        </head>
        <body>
        <p>
            <ul>
                {% for index in index_list %}
                    <li>{{ index }}</li>
                {% end %}
            </ul>
        </p>
        </body>
        </html>
        """
        temp = tornado.template.Template(template_string=html_temp)
        content = temp.generate()
        self.write(content)


"""

    表单与模板 - 模板函数

    Tornado 在所有模板中默认提供 4 个便利的函数
        escape      ：将字符串中的敏感字符（类似 &、<、>）转换为 HTML 编码
                      所有模板输出默认都会使用 escape，除非在 tornado.web.Application 的 autoescape 参数指明 None
        url_escape  ：对字符串进行 URL 编码
        json_encode ：相当于调用 json 库的 dumps 函数
        squeeze     ：将字符串中连续的多个空白字符替换成一个空格
        
    除以上 Tornado 自带函数外，也可以自己编写需要的函数
    只需要将函数名作为模板参数传递即可
"""


class FunctionTempHandler(tornado.web.RequestHandler):

    def get(self):

        html_temp = \
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Function</title>
        </head>
        <body>
            <p><a href="#">test_a</a> <br>{{ '<a href="#">test_a</a>' }}</p>
            <br>
            <p>http://127.0.0.1?q={{ url_escape('测试') }}</p>
            <br>
            <p>{{ json_encode(json_data) }}</p>
            <br>
            <p>{{ squeeze('Lots  of   Spaces    .') }}</p>
            <br>
            <p>{{ custom_func('Hi') }}</p>
        </body>
        </html>
        """

        def custom_func(text):
            return text + '!!!'

        json_data = {
            'name': 'Test',
            'age': 20
        }

        temp = tornado.template.Template(template_string=html_temp)
        content = temp.generate(custom_func=custom_func,
                                json_data=json_data)
        self.write(content)


"""

    模板扩展 - 模板继承

    Tornado 通过 extends 和 block 语句支持模板继承
    父模板中的 block 会被子模板中的同名 block 所覆盖
    
    要点：
        1、父模板中定义 block
        2、子模板使用 extends 继承父模板，并使用同名 block 重写父模板中的 block 内容
    
"""


class TempInheritHandler(tornado.web.RequestHandler):

    def get(self):
        inherit = self.get_argument('inherit', '0')
        if inherit == '0':
            self.render(template_name='inherit/block-page.html')
        else:
            self.render(template_name='inherit/block-sub-page.html')


"""

    模板扩展 - UI 模块

    UI 模块是封装模板中包含的标记、样式以及行为（HTML、CSS 以及 JS）的可复用组件
    
    
    
    tornado.web.Application 的 template_path 参数指明模板所在目录
    
    要点：
        1、定义 UIModuleJS 子类
        2、template_path 中定义模板的映射

"""


class UIModuleJS(tornado.web.UIModule):
    def render(self):
        return '<script>alert("Hi")</script>'


class UIModuleHandler(tornado.web.RequestHandler):

    def get(self):
        self.render(template_name='ui-module/js.html')


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

        # 异常处理
        ('/errorback/greet', ErrorBackHandler),

        # 异步化处理
        ('/async', AsyncHandler),
        ('/async-ssr', AsyncSSRHandler),

        # 协程化处理
        ('/coroutine', CoroutineHandler),

        # 身份验证 - Cookie 机制
        ('/auth-cookies', AuthCookiesHandler),
        # 身份验证 - 安全 Cookie 机制
        ('/auth-sec-cookies', AuthSecretCookiesHandler),
        # 身份验证 - 用户身份认证
        ('/login', LoginHandler),
        ('/need-auth', NeedAuthHandler),

        # 表单与模板 - 渲染与填充
        ('/poem-index', PoemIndexHandler),
        ('/poem-page', PoemPageHandler),
        ('/poem-page-temp', PoemPageTempHandler),
        # 表单与模板 - 填充表达式
        ('/exp-temp', ExpressionTempHandler),
        # 表单与模板 - 控制流语句
        ('/ctlflow-temp', ControlFlowTempHandler),
        # 表单与模板 - 模板函数
        ('/func-temp', FunctionTempHandler),

        # 模板扩展 - 模板继承
        ('/inherit-temp', TempInheritHandler),
        # 模板扩展 - UI 模块
        ('/ui-module-temp', UIModuleHandler),

    ]

    # 模板文件目录
    template_path = os.path.join(
        os.path.dirname(__file__),
        'templates'
    )

    ui_modules_sheet = {
        'JS_TEST': UIModuleJS,
    }

    app = tornado.web.Application(
        # handlers 指明路由以及对应的 RequestHandler 子类
        handlers=route_sheet,
        # template_path 指明模板文件所在目录
        template_path=template_path,
        # ui_modules 指明模板中 UI 模块 module 对应的 tornado.web.UIModule 子类
        ui_modules=ui_modules_sheet,
        # cookie_secret 作为 Cookies 加密的密钥
        cookie_secret=COOKIES_SECRET,
        # login_url 设置身份认证页面
        login_url='/login',
        # debug 为 True 时, 修改代码会使服务器重启
        debug=True
    )
    app.listen(port=options.port)
    print('Tornado web server listen to %d port.' % options.port)
    tornado.ioloop.IOLoop.instance().start()
