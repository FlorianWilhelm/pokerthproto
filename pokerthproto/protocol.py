# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Protocol, ClientFactory

from . import pokerth_pb2
from . import message
from . import poker


class PokerTHProtocol(Protocol):
    _buffer = ''
    _msgSize = None

    def _getBufferedData(self, data):
        self._buffer += data
        bufData = []
        while True:
            if self._msgSize is None:
                if len(self._buffer) >= 4:
                    self._msgSize = message.readSizeBytes(self._buffer[:4])
                    self._buffer = self._buffer[4:]
                else:
                    break
            if len(self._buffer) >= self._msgSize:
                bufData.append(self._buffer[:self._msgSize])
                self._buffer = self._buffer[self._msgSize:]
                self._msgSize = None
            else:
                break
        return bufData

    @classmethod
    def getHook(cls, msg_name):
        hook = msg_name.replace('Message', 'Received')
        return hook[0].lower() + hook[1:]

    def unhandledMessageReceived(self, msg):
        log.msg('Received unhandled message:\n{}'.format(msg))

    def connectionMade(self):
        log.msg('Connection established.')

    def dataReceived(self, data):
        for buffer in self._getBufferedData(data):
            msg = message.develop(message.unpack(buffer))
            hook = self.getHook(msg.__class__.__name__)
            log.msg('Calling {}'.format(hook))
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
    LOBBY = 1


class ClientProtocol(PokerTHProtocol):
    state = States.INIT

    def announceReceived(self, msg):
        log.msg("AnnounceMessage received")
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

    def initAckReceived(self, msg):
        log.msg("InitAckMessage received")
        self.factory.playerId = msg.yourPlayerId
        self.factory.sessionId = msg.yourSessionId
        self.state = States.LOBBY

    def playerListReceived(self, msg):
        log.msg("PlayerListMessage received")
        if msg.playerListNotification == msg.playerListNew:
            self.factory.addPlayer(msg.playerId)
            reply = pokerth_pb2.PlayerInfoRequestMessage()
            reply.playerId.append(msg.playerId)
            self.transport.write(message.packEnvelop(reply))
            log.msg("InfoRequestMessage sent")
        else:  # msg.playerListLeft
            self.factory.rmPlayer(msg.playerId)

    def playerInfoReplyReceived(self, msg):
        log.msg("PlayerInfoReplyMessage received")
        self.factory.setPlayerInfo(msg.playerId, msg.playerInfoData)


class ClientProtocolFactory(ClientFactory):
    protocol = ClientProtocol

    def __init__(self, nickName):
        self.nickName = nickName
        self.playerId = None
        self.SessionID = None
        self.players = []

    def addPlayer(self, playerId):
        player = poker.Player(playerId)
        if player not in self.players:
            self.players.append(player)

    def rmPlayer(self, playerId):
        self.players = [p for p in self.players if p.id != playerId]

    def getPlayer(self, playerId):
        return [p for p in self.players if p.id == playerId][0]

    def setPlayerInfo(self, playerId, infoData):
        player = self.getPlayer(playerId)
        player.setInfo(infoData)

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
