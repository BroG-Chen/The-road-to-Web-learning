# -*- coding: utf-8 -*-

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

"""
更加简单的协议工厂创建

1.继承 Factory 类并重新 Factory.protocol 类属性指定工厂类使用的协议
2.使用 Factory.ForProtocol 类方法创建协议工厂实例
"""


class Echo(Protocol):

    def connectionMade(self):
        print('Connection Made, current num of ports: %d' % self.factory.numPorts)
        ip_address = self.transport.getHost()
        ret_mag = "Welcome! There are currently %d open connections.\n" % self.factory.numPorts
        ret_mag += "The port you are connecting to is %d.\n" % ip_address.port
        self.transport.write(ret_mag.encode())

    def connectionLost(self, reason):
        print('Connection lost, current num of ports: %d' % self.factory.numPorts)

    def dataReceived(self, data):
        print('Received: %s' % data)
        self.transport.write(data)


# 继承 Factory 类并重新 Factory.protocol 类属性指定工厂类使用的协议
class EchoFactory(Factory):
    protocol = Echo

    def startFactory(self):
        print('startFactory~')

    def stopFactory(self):
        print('stopFactory~')


# 使用 Factory.ForProtocol 类方法创建协议工厂实例
echo_factory = Factory.forProtocol(Echo)


endpoint = TCP4ServerEndpoint(reactor, 8007)
endpoint.listen(EchoFactory())      # EchoFactory 是类，需要初始化
endpoint_oth = TCP4ServerEndpoint(reactor, 8017)
endpoint_oth.listen(echo_factory)   # echo_factory 是实例，直接传递
endpoint_oth = TCP4ServerEndpoint(reactor, 8027)
endpoint_oth.listen(echo_factory)   # echo_factory 是实例，直接传递
reactor.run()
