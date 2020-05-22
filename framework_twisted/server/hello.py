# -*- coding: utf-8 -*-

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

"""
简单的服务端
服务端必须至少有 Protocol、Factory、Endpoint
"""


# Protocol 使用协议
class Hello(Protocol):

    def connectionMade(self):
        # 向客户端发送问好信息
        self.transport.write("Hello Twisted, This is First Server!\r\n".encode())
        self.transport.write("Bye bye ~\r\n".encode())

    def dataReceived(self, data):
        # 接收问好信息后打印
        print('Received: \n%s' % data.decode())
        # 断开连接
        self.transport.loseConnection()
        # Reactor 停止运行
        reactor.stop()


# Factory 实现协议工厂
class HelloFactory(Factory):

    def buildProtocol(self, addr):
        return Hello()


# Endpoint 实现连接端点，服务端使用 ServerEndpoint
endpoint = TCP4ServerEndpoint(reactor, 8041)
# 协议工厂绑定端点
endpoint.listen(HelloFactory())
# Reactor 运行
reactor.run()
