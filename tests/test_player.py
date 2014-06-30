# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

from pokerthproto.player import Player
from pokerthproto.pokerth_pb2 import PlayerInfoReplyMessage, \
    netPlayerRightsNormal, netAvatarImagePng

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_player():
    player = Player(1)
    assert player.playerId == 1
    player.money = 100
    assert player.money == 100
    player.seat = 0
    assert player.seat == 0
    player2 = Player(1)
    assert player2 == player
    assert player.__eq__(1) == NotImplemented
    infoData = PlayerInfoReplyMessage.PlayerInfoData()
    infoData.playerName = 'Player'
    infoData.isHuman = True
    infoData.playerRights = netPlayerRightsNormal
    infoData.countryCode = 'DE'
    infoData.avatarData.avatarType = netAvatarImagePng
    infoData.avatarData.avatarHash = '123'
    player.setInfo(infoData)
    assert player.name == 'Player'
    assert player.isHuman
    assert player.playerRights == netPlayerRightsNormal
    assert player.countryCode == 'DE'
    assert player.avatarHash == '123'
    assert player.avatarType == netAvatarImagePng
