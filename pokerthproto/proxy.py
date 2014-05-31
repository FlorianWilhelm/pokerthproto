# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ClientEndpoint

from . import pokerth_pb2

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


class ProxyProtocol(Protocol):

    def connectionMade(self):
        self.factory.numConnections += 1
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
        msg = pokerth_pb2.PokerTHMessage()
        msg.ParseFromString(data[4:])
        log.msg("From client: {}".format(msg))
        log.msg(data.encode('string-escape'))
        self.client_proto.transport.write(data)

    def connectionLost(self, reason):
        log.msg('Client connection lost due to: {}'.format(reason))


class ProxyProtocolFactory(Factory):
    protocol = ProxyProtocol
    numConnections = 0


class ClientProtocol(Protocol):
    def connectionMade(self):
        log.msg("Connection to server established")

    def dataReceived(self, data):
        msg = pokerth_pb2.PokerTHMessage()
        msg.ParseFromString(data[4:])
        log.msg("From server: {}".format(msg))
        self.factory.sendToClient(data)

    def connectionLost(self, reason):
        log.msg('Server connection lost due to: {}'.format(reason))


class ClientProtocolFactory(Factory):
    protocol = ClientProtocol

    def __init__(self, sendToClient):
        self.sendToClient = sendToClient
