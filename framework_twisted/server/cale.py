# -*- coding: utf-8 -*-
# author: BergChen
# date: 2020/5/21

from twisted.protocols import basic
from twisted.internet import protocol


# 四则运算类
class Calculation(object):

    @staticmethod
    def __make_ints(*args):
        try:
            return [int(arg) for arg in args]
        except ValueError:
            raise TypeError(
                "Couldn't coerce arguments to integers: {}".format(*args))

    def add(self, a, b):
        a, b = self.__make_ints(a, b)
        return a + b

    def subtract(self, a, b):
        a, b = self.__make_ints(a, b)
        return a - b

    def multiply(self, a, b):
        a, b = self.__make_ints(a, b)
        return a * b

    def divide(self, a, b):
        a, b = self.__make_ints(a, b)
        return a // b


class CalculationProxy(object):
    def __init__(self):
        self.calc = Calculation()
        for m in ['add', 'subtract', 'multiply', 'divide']:
            setattr(self, 'remote_{}'.format(m), getattr(self.calc, m))


class RemoteCalculationProtocol(basic.LineReceiver):
    def __init__(self):
        self.proxy = CalculationProxy()

    def lineReceived(self, line):
        op, a, b = line.decode('utf-8').split()
        a = int(a)
        b = int(b)
        op = getattr(self.proxy, 'remote_{}'.format(op))
        result = op(a, b)
        self.sendLine(str(result).encode('utf-8'))


class RemoteCalculationFactory(protocol.Factory):
    protocol = RemoteCalculationProtocol


if __name__ == "__main__":
    from twisted.internet import reactor
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)
    reactor.listenTCP(0, RemoteCalculationFactory())
    reactor.run()
