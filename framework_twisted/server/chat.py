# -*- coding: utf-8 -*-

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor


class Chat(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "LOGIN"

    def connectionMade(self):
        msg = "What's your name?"
        self.sendLine(msg.encode())

    def connectionLost(self, reason):
        # 断开链接时删除当前对象
        if self.name in self.users:
            del self.users[self.name]

    def lineReceived(self, line):
        if self.state == "LOGIN":
            self.handle_LOGIN(line)
        else:
            self.handle_CHAT(line)

    def handle_LOGIN(self, name):
        name = name.decode()
        if name in self.users:
            msg = "Name taken, please choose another."
            self.sendLine(msg.encode())
            return
        # 发送确认登录消息
        msg = "Welcome, %s!" % name
        self.sendLine(msg.encode())
        print('User login: %s' % name)
        # 存储在线的 Protocol 实例
        self.name = name
        self.users[name] = self
        self.state = "CHAT"

    def handle_CHAT(self, message):
        message = message.decode()
        message = "<%s> %s" % (self.name, message)
        print('Received massage: %s' % message)
        # 广播消息给除了自已以外所有 Protocol
        for name, protocol in self.users.items():
            if protocol != self:
                protocol.sendLine(message.encode())


class ChatFactory(Factory):

    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return Chat(self.users)


end_point = TCP4ServerEndpoint(reactor, 8123)
end_point.listen(ChatFactory())
reactor.run()
