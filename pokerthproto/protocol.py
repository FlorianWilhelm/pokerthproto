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

    def gameListNewReceived(self, msg):
        log.msg("GameListNewMessage received")
        gameInfo = poker.GameInfo()
        gameInfo.setInfo(msg.gameInfo)
        game = poker.Game(msg.gameId, msg.gameMode, gameInfo,
                          msg.isPrivate, msg.adminPlayerId)
        if game not in self.factory.games:
            self.factory.games.append(game)

    def gameListPlayerJoinedReceived(self, msg):
        log.msg("GameListPlayerJoinedMessage received")
        game = self.factory.getGame(msg.gameId)
        player = self.factory.getPlayer(msg.playerId)
        game.add_player(player)

    def gamePlayerJoinedReceived(self, msg):
        log.msg("GamePlayerJoinedMessage received")
        game = self.factory.getGame(msg.gameId)
        player = self.factory.getPlayer(msg.playerId)
        game.add_player(player)

    def joinGameAckReceived(self, msg):
        log.msg("JoinGameAckMessage received")
        self.factory.gameId = msg.gameId
        self.state = States.GAME_JOINED

    def gameListUpdateReceived(self, msg):
        log.msg("GameListUpdateMessage received")
        game = self.factory.getGame(msg.gameId)
        game.gameMode = msg.gameMode

    def startEventReceived(self, msg):
        log.msg("StartEventMessage received")
        reply = pokerth_pb2.StartEventAckMessage()
        reply.gameId = msg.gameId
        game = self.factory.getCurrentGame()
        game.fillWithComputerPlayers = msg.fillWithComputerPlayers
        self.transport.write(message.packEnvelop(reply))
        log.msg("StartEventAckMessage sent")


class ClientProtocolFactory(ClientFactory):
    protocol = ClientProtocol

    def __init__(self, nickName):
        self.nickName = nickName
        self.playerId = None
        self.gameId = None
        self.SessionID = None
        self.players = []
        self.games = []

    def addPlayer(self, playerId):
        player = poker.Player(playerId)
        if player not in self.players:
            self.players.append(player)

    def rmPlayer(self, playerId):
        self.players = [p for p in self.players if p.id != playerId]

    def getPlayer(self, playerId):
        return [p for p in self.players if p.id == playerId][0]

    def getGameId(self, gameName):
        ids = [g.gameId for g in self.games if g.gameInfo.gameName == gameName]
        if ids:
            return ids[0]
        else:
            raise RuntimeError("No game of name {} found".format(gameName))

    def getGame(self, gameId):
        return [g for g in self.games if g.gameId == gameId][0]

    def getCurrentGame(self):
        if self.gameId is not None:
            return self.getGame(self.gameId)
        else:
            raise RuntimeError("Not in game currently")

    def setPlayerInfo(self, playerId, infoData):
        player = self.getPlayer(playerId)
        player.setInfo(infoData)

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
