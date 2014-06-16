# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Protocol, ClientFactory

from . import pokerth_pb2
from . import message
from . import lobby
from . import game


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
        log.msg('Received unhandled message {}:\n{}'.format(
            msg.__class__.__name__, msg))

    def connectionMade(self):
        log.msg('Connection established.')

    def dataReceived(self, data):
        for buffer in self._getBufferedData(data):
            msg = message.develop(message.unpack(buffer))
            hook = self.getHook(msg.__class__.__name__)
            getattr(self, hook)(msg)

    def connectionLost(self, reason):
        log.msg('Connection lost due to: {}'.format(reason))


# Set default method for all possible message types
for msg_type in pokerth_pb2.PokerTHMessage.PokerTHMessageType.keys():
    msg_name = msg_type.split("_", 1)[1]
    hook = PokerTHProtocol.getHook(msg_name)
    setattr(PokerTHProtocol, hook, PokerTHProtocol.unhandledMessageReceived)


class States(object):
    """
    Enum of all client states
    """
    INIT = 0
    LOBBY = 1
    GAME_JOINED = 2
    GAME_STARTED = 3


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
        reactor.callLater(1, self.insideLobby)

    def insideLobby(self):
        raise NotImplementedError("We are in the lobby, implement an action!")

    def sendJoinExistingGameMessage(self, gameId, autoLeave=False):
        msg = pokerth_pb2.JoinExistingGameMessage()
        msg.gameId = gameId
        msg.autoLeave = autoLeave
        self.transport.write(message.packEnvelop(msg))
        log.msg("JoinExistingGameMessage sent")

    def sendJoinNewGameMessage(self, gameInfo, password=None, autoLeave=False):
        msg = pokerth_pb2.JoinNewGameMessage()
        msg.gameInfo.MergeFrom(gameInfo.getMsg())
        if password is not None:
            msg.password = password
        msg.autoLeave = autoLeave
        self.transport.write(message.packEnvelop(msg))
        log.msg("JoinNewGameMessage sent")

    def playerListReceived(self, msg):
        log.msg("PlayerListMessage received")
        if msg.playerListNotification == msg.playerListNew:
            self.factory.lobby.addPlayer(msg.playerId)
            reply = pokerth_pb2.PlayerInfoRequestMessage()
            reply.playerId.append(msg.playerId)
            self.transport.write(message.packEnvelop(reply))
            log.msg("InfoRequestMessage sent")
        else:  # msg.playerListLeft
            self.factory.lobby.delPlayer(msg.playerId)

    def playerInfoReplyReceived(self, msg):
        log.msg("PlayerInfoReplyMessage received")
        self.factory.lobby.setPlayerInfo(msg.playerId, msg.playerInfoData)

    def gameListNewReceived(self, msg):
        log.msg("GameListNewMessage received")
        gameInfo = lobby.GameInfo()
        gameInfo.setInfo(msg.gameInfo)
        gameInfo.gameId = msg.gameId
        gameInfo.gameMode = msg.gameMode
        gameInfo.isPrivae = msg.isPrivate
        gameInfo.adminPlayerId = msg.adminPlayerId
        self.factory.lobby.addGameInfo(gameInfo)

    def gameListPlayerJoinedReceived(self, msg):
        log.msg("GameListPlayerJoinedMessage received")
        self.factory.lobby.addPlayerToGame(msg.playerId, msg.gameId)

    def gamePlayerJoinedReceived(self, msg):
        log.msg("GamePlayerJoinedMessage received")
        player = self.factory.lobby.getPlayer(msg.playerId)
        assert self.factory.game.gameId == msg.gameId
        self.factory.game.addPlayer(player)

    def joinGameAckReceived(self, msg):
        log.msg("JoinGameAckMessage received")
        self.factory.game = game.Game(msg.gameId)
        if msg.areYouGameAdmin:
            myGameInfo = self.factory.lobby.getGameInfo(msg.gameId)
            assert myGameInfo.adminPlayerId == self.factory.playerId
        myself = self.factory.lobby.getPlayer(self.factory.playerId)
        self.factory.game.addPlayer(myself)
        self.state = States.GAME_JOINED

    def gameListUpdateReceived(self, msg):
        log.msg("GameListUpdateMessage received")
        gameInfo = self.factory.lobby.getGameInfo(msg.gameId)
        gameInfo.gameMode = msg.gameMode

    def startEventReceived(self, msg):
        log.msg("StartEventMessage received")
        gameInfo = self.factory.lobby.getGameInfo(self.factory.gameId)
        gameInfo.fillWithComputerPlayers = msg.fillWithComputerPlayers
        reply = pokerth_pb2.StartEventAckMessage()
        reply.gameId = msg.gameId
        self.transport.write(message.packEnvelop(reply))
        log.msg("StartEventAckMessage sent")
        self.state = States.GAME_STARTED

    # def GameStartInitialReceived(self, msg):
    #     log.msg("GameStartInitialMessage received")
    #     game = self.factory.getGame(msg.gameId)
    # ...


class ClientProtocolFactory(ClientFactory):
    protocol = ClientProtocol

    def __init__(self, nickName):
        self.nickName = nickName
        self.playerId = None
        self.gameId = None
        self.SessionID = None
        self.game = None
        self.lobby = lobby.Lobby()

    def clientConnectionLost(self, connector, reason):
        pass
        # connector.connect()

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
