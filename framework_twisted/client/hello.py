# -*- coding: utf-8 -*-

from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol
from twisted.internet import reactor

"""
简单的客户端
客户端必须至少有 Protocol、Endpoint
但相比服务端，对客户端而言 Factory 不是必须的
"""


# Protocol 实现协议
class Hello(Protocol):

    def connectionMade(self):
        # 向服务端发送问好信息
        self.transport.write("Hello Twisted, This is First Client!\r\n".encode())
        self.transport.write("Bye bye ~\r\n".encode())

    def dataReceived(self, data):
        # 接收问好信息后打印
        print('Received: \n%s' % data.decode())
        # 断开连接
        self.transport.loseConnection()
        # Reactor 停止运行
        reactor.stop()


# Endpoint 实现连接端点，客户端使用 ClientEndpoint
point = TCP4ClientEndpoint(reactor, "localhost", 8041)
# 协议直接绑定端点
connectProtocol(point, Hello())
# Reactor 运行
reactor.run()
