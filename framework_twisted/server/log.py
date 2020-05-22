# -*- coding: utf-8 -*-

import os
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

"""
Factory 类管理 Protocol 实例
以及进行一些连接事件的对应操作
"""


class LoggingProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        print('Connection Made, wait for logging...')

    def connectionLost(self, reason):
        print('Connection lost, logging done.')

    # 重写 LineReceiver.lineReceived 方法，在接受到单行数据时进行处理
    def lineReceived(self, line):
        log = line.decode()
        print('Logging: %s' % log)
        self.factory.fp.write(log + '\n')
        self.factory.fp.flush()


class LogfileFactory(Factory):

    def __init__(self, fileName):
        self.file = fileName
        self.fp = None

    # Factory.startFactory 连接监听开始之前执行
    def startFactory(self):
        self.fp = open(self.file, 'a')

    # Factory.stopFactory  连接监听结束之前执行
    def stopFactory(self):
        self.fp.close()

    # 为每个连接生成 Protocol 实例
    def buildProtocol(self, addr):
        return LoggingProtocol(self)


logfile = os.path.join(os.path.dirname(__file__), 'log.txt')
endpoint = TCP4ServerEndpoint(reactor, 8109)
endpoint.listen(LogfileFactory(logfile))
reactor.run()