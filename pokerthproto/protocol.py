# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Protocol, ClientFactory

from . import pokerth_pb2
from . import message


class PokerTHProtocol(Protocol):

    @classmethod
    def getHook(cls, msg_name):
        hook = msg_name.replace('Message', 'Received')
        return hook[0].lower() + hook[1:]

    def unhandledMessageReceived(self, msg):
        log.msg('Received unhandled message:\n{}'.format(msg))

    def connectionMade(self):
        log.msg('Connection established.')

    def dataReceived(self, data):
        msg = message.develop(message.unpack(data))
        hook = self.getHook(msg.__class__.__name__)
        log.msg("Calling {}".format(hook))
        getattr(self, hook)(msg)

    def connectionLost(self, reason):
        log.msg('Connection lost due to: {}'.format(reason))


# Set default method for all possible message types
for msg_type in pokerth_pb2.PokerTHMessage.PokerTHMessageType.keys():
    msg_name = msg_type.split("_", 1)[1]
    hook = PokerTHProtocol.getHook(msg_name)
    setattr(PokerTHProtocol, hook, PokerTHProtocol.unhandledMessageReceived)


class States(object):
    INIT = 0


class ClientProtocol(PokerTHProtocol):
    state = States.INIT

    def announceReceived(self, msg):
        reply = pokerth_pb2.InitMessage()

        replyVersion = reply.requestedVersion
        msgVersion = msg.protocolVersion
        replyVersion.majorVersion = msgVersion.majorVersion
        replyVersion.minorVersion = msgVersion.minorVersion

        reply.buildId = 0  # 0 for Linux build
        reply.nickName = self.factory.nickName
        if msg.serverType == msg.serverTypeInternetNoAuth:
            reply.login = reply.unauthenticatedLogin
        else:
            raise NotImplementedError("Handle authentication!")
        assert reply.IsInitialized()
        self.transport.write(message.packEnvelop(reply))
        log.msg("InitMessage sent")


class ClientProtocolFactory(ClientFactory):
    protocol = ClientProtocol

    def __init__(self, nickName):
        self.nickName = nickName

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
