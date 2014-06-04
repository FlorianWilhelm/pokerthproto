# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

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
