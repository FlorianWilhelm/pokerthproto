# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from . import pokerth_pb2
from .player import Player

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


class GameInfo(object):
    """
    Wrapper object for :obj:`pokerth_pb2.PNetGameInfo`

    This object is needed in order to create an own game.
    """
    def __init__(self, gameName=None):
        self._gameName = gameName
        self._netGameType = pokerth_pb2.NetGameInfo.normalGame
        self._maxNumPlayers = 10
        self._raiseIntervalMode = pokerth_pb2.NetGameInfo.raiseOnHandNum
        self._raiseEveryHands = 8
        self._endRaiseMode = pokerth_pb2.NetGameInfo.doubleBlinds
        self._endRaiseSmallBlindValue = 0
        self._proposedGuiSpeed = 4
        self._delayBetweenHands = 7
        self._playerActionTimeout = 20
        self._firstSmallBlind = 10
        self._startMoney = 3000
        self._allowSpectators = True
        self._gameId = None
        self._gameMode = None
        self._isPrivate = None
        self._adminPlayerId = None
        self._manualBlinds = []
        self._players = []
        self._fillWithComputerPlayers = None

    @property
    def gameName(self):
        return self._gameName

    @property
    def netGameType(self):
        return self._netGameType

    @property
    def maxNumPlayers(self):
        return self._maxNumPlayers

    @property
    def raiseIntervalMode(self):
        return self._raiseIntervalMode

    @property
    def raiseEveryHands(self):
        return self._raiseEveryHands

    @property
    def endRaiseMode(self):
        return self._endRaiseMode

    @property
    def endRaiseSmallBlindValue(self):
        return self._endRaiseSmallBlindValue

    @property
    def proposedGuiSpeed(self):
        return self._proposedGuiSpeed

    @property
    def delayBetweenHands(self):
        return self._delayBetweenHands

    @property
    def playerActionTimeout(self):
        return self._playerActionTimeout

    @property
    def firstSmallBlind(self):
        return self._firstSmallBlind

    @property
    def startMoney(self):
        return self._startMoney

    @property
    def allowSpectators(self):
        return self._allowSpectators

    @property
    def manualBlinds(self):
        return self._manualBlinds

    def setInfo(self, gameInfo):
        self._gameName = gameInfo.gameName
        self._netGameType = gameInfo.netGameType
        self._maxNumPlayers = gameInfo.maxNumPlayers
        self._raiseIntervalMode = gameInfo.raiseIntervalMode
        self._raiseEveryHands = gameInfo.raiseEveryHands
        self._endRaiseMode = gameInfo.endRaiseMode
        self._endRaiseSmallBlindValue = gameInfo.endRaiseSmallBlindValue
        self._proposedGuiSpeed = gameInfo.proposedGuiSpeed
        self._delayBetweenHands = gameInfo.delayBetweenHands
        self._playerActionTimeout = gameInfo.playerActionTimeout
        self._firstSmallBlind = gameInfo.firstSmallBlind
        self._startMoney = gameInfo.startMoney
        self._allowSpectators = gameInfo.allowSpectators
        self._manualBlinds = gameInfo.manualBlinds

    def getMsg(self):
        msg = pokerth_pb2.NetGameInfo()
        msg.gameName = self.gameName
        msg.netGameType = self.netGameType
        msg.maxNumPlayers = self.maxNumPlayers
        msg.raiseIntervalMode = self.raiseIntervalMode
        msg.raiseEveryHands = self.raiseEveryHands
        msg.endRaiseMode = self.endRaiseMode
        msg.endRaiseSmallBlindValue = self.endRaiseSmallBlindValue
        msg.proposedGuiSpeed = self.proposedGuiSpeed
        msg.delayBetweenHands = self.delayBetweenHands
        msg.playerActionTimeout = self.playerActionTimeout
        msg.firstSmallBlind = self.firstSmallBlind
        msg.startMoney = self.startMoney
        msg.allowSpectators = self.allowSpectators
        msg.manualBlinds.extend(self.manualBlinds)
        return msg

    @property
    def gameId(self):
        return self._gameId

    @gameId.setter
    def gameId(self, id):
        self._gameId = id

    @property
    def gameMode(self):
        return self._gameMode

    @gameMode.setter
    def gameMode(self, mode):
        self._gameMode = mode

    @property
    def isPrivate(self):
        return self._isPrivate

    @isPrivate.setter
    def isPrivate(self, bool):
        self._isPrivate = bool

    @property
    def adminPlayerId(self):
        return self._adminPlayerId

    @adminPlayerId.setter
    def adminPlayerId(self, id):
        self._adminPlayerId = id

    @property
    def players(self):
        return self._players

    @property
    def fillWithComputerPlayers(self):
        return self._fillWithComputerPlayers

    @fillWithComputerPlayers.setter
    def fillWithComputerPlayers(self, bool):
        self._fillWithComputerPlayers = bool

    def __eq__(self, other):
        if isinstance(other, GameInfo):
            return self.gameId == other.gameId
        return NotImplemented


class LobbyError(Exception):

    def __unicode__(self):
        return unicode(self.message)

    def __str__(self):
        return unicode(self).encode('utf-8')


class Lobby(object):

    def __init__(self):
        self._players = []
        self._gameInfos = []

    @property
    def gameInfos(self):
        return self._gameInfos

    def addGameInfo(self, gameInfo):
        if gameInfo not in self._gameInfos:
            self._gameInfos.append(gameInfo)
        else:
            raise LobbyError("Game is already in our list of games")

    @property
    def players(self):
        return self._players

    def addPlayer(self, playerId):
        player = Player(playerId)
        if player not in self._players:
            self._players.append(player)
        else:
            raise LobbyError("Player with id {} already listed".format(
                playerId))

    def delPlayer(self, playerId):
        player = Player(playerId)
        self._players.remove(player)

    def getPlayer(self, playerId):
        players = [p for p in self._players if p.playerId == playerId]
        if len(players) == 1:
            return players[0]
        else:
            raise LobbyError("Player with id {} not listed".format(playerId))

    def getGameInfoId(self, gameName):
        ids = [g.gameId for g in self._gameInfos if g.gameName == gameName]
        if len(ids) == 1:
            return ids[0]
        else:
            raise LobbyError("No game of name {} found".format(gameName))

    def getGameInfo(self, gameId):
        gameInfos = [g for g in self._gameInfos if g.gameId == gameId]
        if len(gameInfos) == 1:
            return gameInfos[0]
        else:
            raise LobbyError("Game with id {} not listed".format(gameId))

    def setPlayerInfo(self, playerId, infoData):
        player = self.getPlayer(playerId)
        player.setInfo(infoData)

    def addPlayerToGame(self, playerId, gameId):
        game = self.getGameInfo(gameId)
        player = self.getPlayer(playerId)
        game.players.append(player)
