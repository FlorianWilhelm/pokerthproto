# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Protocol, ClientFactory

from .pokerth_pb2 import PokerTHMessage

PokerTHMessageType = PokerTHMessage.PokerTHMessageType


class PokerTHProtocol(Protocol):

    @classmethod
    def getHook(cls, msg_type):
        name = [k for k, v in PokerTHMessageType.items() if v == msg_type][0]
        hook = name.split('_')[1].replace('Message', 'Received')
        return hook[0].lower() + hook[1:]

    def unhandledMessageReceived(self, msg):
        log.msg('Received unhandled message:\n{}'.format(msg))

    def connectionMade(self):
        log.msg('Connection established.')

    def dataReceived(self, data):
        msg = PokerTHMessage()
        # Skip first 4 bytes when parsing
        msg.ParseFromString(data[4:])
        hook = self.getHook(msg.messageType)
        log.msg("Calling {}".format(hook))
        getattr(self, hook)(msg)

    def connectionLost(self, reason):
        log.msg('Connection lost due to: {}'.format(reason))


# Set default method for all possible message types
for _, msg_type in PokerTHMessageType.items():
    hook = PokerTHProtocol.getHook(msg_type)
    setattr(PokerTHProtocol, hook, PokerTHProtocol.unhandledMessageReceived)


class States(object):
    INIT = 0


class ClientProtocol(PokerTHProtocol):
    state = States.INIT

    def announceReceived(self, msg):
        msgBody = msg.announceMessage
        reply = PokerTHMessage()
        reply.messageType = reply.Type_InitMessage
        replyBody = reply.initMessage
        replyVersion = replyBody.requestedVersion
        msgVersion = msgBody.protocolVersion
        replyVersion.majorVersion = msgVersion.majorVersion
        replyVersion.minorVersion = msgVersion.minorVersion
        replyBody.buildId = 0  # 0 for Linux build
        replyBody.nickName = self.factory.nickName
        if msgBody.serverType == msgBody.serverTypeInternetNoAuth:
            replyBody.login = replyBody.unauthenticatedLogin
        else:
            raise NotImplementedError("Handle authentication!")
        assert reply.IsInitialized()
        self.transport.write(serialize(reply))
        log.msg(reply)
        log.msg(serialize(reply).encode('string-escape'))
        log.msg("InitMessage sent")


class ClientProtocolFactory(ClientFactory):
    protocol = ClientProtocol

    def __init__(self, nickName):
        self.nickName = nickName

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()


def serialize(msg):
    msg_str = msg.SerializeToString()
    # Prefix with 4 bytes of message length
    prefix = bytearray.fromhex(b'{:08x}'.format(len(msg_str)))
    return str(prefix) + msg_str
