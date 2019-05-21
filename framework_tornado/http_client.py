# -*- coding: utf-8 -*-
# author: BergChen
# date: 2019/5/20

from tornado import ioloop
from tornado import gen
from tornado.httpclient import HTTPClient
from tornado.httpclient import AsyncHTTPClient

"""
    Tornado 同步请求
"""


def sync_visit(url):
    http_client = HTTPClient()
    res = http_client.fetch(url)
    print(res.body)


if __name__ == '__main__':
    # url = 'http://httpbin.org/ip'
    # sync_visit(url=url)
    pass

"""
    Tornado 异步请求 - 基本异步请求
    
    需要指定回调函数
    
    不能直接被调用，调用后需要 IOLoop 启动才会执行
"""


def handle_res(response):
    print(response.body)


def async_visit(url, callback):
    http_client = AsyncHTTPClient()

    def handle_response(response):
        callback(response)

    http_client.fetch(url, callback=handle_response)


if __name__ == '__main__':
    # url = 'http://httpbin.org/ip'
    # async_visit(url=url, callback=handle_res)
    # io_loop = ioloop.IOLoop.current()
    # io_loop.start()
    pass

"""
    Tornado 异步请求 - 协程函数

    该方法不需要指定回调函数，代码风格与同步时类似

    
    协程函数不能直接被调用，但可以通过下面3种方式调用
    1.在其他的协程函数中通过 yield 调用
    2.在 IOLoop 启动（调用 start 函数）前，通过 run_sync 函数调用
    3.在 IOLoop 启动（调用 start 函数）时，通过 spawn_callback 函数调用
    （与直接调用后执行启动 IOLoop 效果一致）
"""


@gen.coroutine
def async_visit_by_coroutine(url):
    http_client = AsyncHTTPClient()
    res = yield http_client.fetch(url)
    print(res.body)


# 1.在其他的协程函数中通过 yield 调用
@gen.coroutine
def coroutine_func():
    url = 'http://httpbin.org/ip'
    yield async_visit_by_coroutine(url=url)


# 2.在 IOLoop 启动（调用 start 函数）前，通过 run_sync 函数调用
if __name__ == '__main__':
    # io_loop = ioloop.IOLoop.current()
    # io_loop.run_sync(func=coroutine_func)
    pass


# 3.在 IOLoop 启动（调用 start 函数）后，通过 run_sync 函数调用
if __name__ == '__main__':
    # io_loop = ioloop.IOLoop.current()
    # io_loop.spawn_callback(coroutine_func)
    # io_loop.start()
    pass

"""
    Tornado 异步请求 - 协程函数 - 等待多个异步调用
    
    Tornado 允许使用 yield 在多个异步调用中，
    只需要将这些调用以 list 或 dict 的方式传递给 yield
"""

@gen.coroutine
def async_visit_contains_more_wait_by_coroutine():
    http_client = AsyncHTTPClient()
    res_list = yield [
        http_client.fetch('http://httpbin.org/ip'),
        http_client.fetch('https://www.baidu.com'),
        http_client.fetch('https://www.163.com'),
        http_client.fetch('http://127.0.0.1/now')
    ]
    for res in res_list:
        print(res.body)


if __name__ == '__main__':
    # io_loop = ioloop.IOLoop.current()
    # io_loop.run_sync(async_visit_contains_more_wait_by_coroutine)
    pass
