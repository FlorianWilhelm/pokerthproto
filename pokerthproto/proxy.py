# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint

from . import message
from . import protocol

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


class ProxyProtocol(protocol.PokerTHProtocol):

    def connectionMade(self):
        log.msg("Client connection established")
        self.point = TCP4ClientEndpoint(reactor, "localhost", 7234)
        client_factory = ClientProtocolFactory(self.sendToClient)
        self.client_proto = self.point.connect(client_factory)
        self.client_proto.addCallback(self.registerServer)

    def registerServer(self, proto):
        self.client_proto = proto

    def sendToClient(self, data):
        self.transport.write(data)

    def dataReceived(self, data):
        for buffer in self._getBufferedData(data):
            msg = message.develop(message.unpack(buffer))
            log.msg("{} from client:\n{}".format(msg.__class__.__name__, msg))
        self.client_proto.transport.write(data)


class ProxyProtocolFactory(Factory):
    protocol = ProxyProtocol


class ClientProtocol(protocol.PokerTHProtocol):

    def dataReceived(self, data):
        for buffer in self._getBufferedData(data):
            msg = message.develop(message.unpack(buffer))
            log.msg("{} from server:\n{}".format(msg.__class__.__name__, msg))
        self.factory.sendToClient(data)


class ClientProtocolFactory(Factory):
    protocol = ClientProtocol

    def __init__(self, sendToClient):
        self.sendToClient = sendToClient
