# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from . import pokerth_pb2

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


class Player(object):

    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def isHuman(self):
        return self._isHuman

    @property
    def playerRights(self):
        return self._playerRights

    @property
    def avatarType(self):
        return self._avatarType

    @property
    def avatarHash(self):
        return self._avatarHash

    def setInfo(self, infoData):
        self._name = infoData.playerName
        self._isHuman = infoData.isHuman
        self._playerRights = infoData.playerRights
        self._avatarType = infoData.avatarData.avatarType
        self._avatarHash = infoData.avatarData.avatarHash

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.id == other.id
        return NotImplemented


class GameInfo(object):

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
        self._manualBlinds = []

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


class Game(object):

    def __init__(self, gameId, gameMode, gameInfo, isPrivate, adminPlayerId):
        self._gameId = gameId
        self._gameMode = gameMode
        self._isPrivate = isPrivate
        self._gameInfo = gameInfo
        self._adminPlayerId = adminPlayerId
        self._players = []

    @property
    def players(self):
        return self._players

    def add_player(self, player):
        self._players.append(player)

    def rm_player(self, player):
        self._players = [p for p in self._players if p != player]

    @property
    def gameId(self):
        return self._gameId

    @property
    def gameMode(self):
        return self._gameMode

    @property
    def isPrivate(self):
        return self._isPrivate

    @property
    def gameInfo(self):
        return self._gameInfo

    @property
    def adminPlayerId(self):
        return self._adminPlayerId

    def __eq__(self, other):
        if isinstance(other, Game):
            return self.gameId == other.gameId
        return NotImplemented
