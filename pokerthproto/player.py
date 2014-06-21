# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


class Player(object):
    """
    Player in poker game including all information of
    :obj:`pokerth_pb2.PlayerInfoReplyMessage.playerInfoData`
    """
    def __init__(self, playerId):
        self._playerId = playerId
        self._money = None
        self._name = None
        self._seat = None
        self._isHuman = None
        self._playerRights = None
        self._avatarType = None
        self._avatarHash = None

    @property
    def money(self):
        return self._money

    @money.setter
    def money(self, money):
        self._money = money

    @property
    def playerId(self):
        return self._playerId

    @property
    def name(self):
        return self._name

    @property
    def seat(self):
        return self._seat

    @seat.setter
    def seat(self, seat):
        self._seat = seat

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
            return self.playerId == other.playerId
        return NotImplemented
