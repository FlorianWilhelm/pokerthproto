# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import pytest

from pokerthproto.lobby import GameInfo, Lobby, LobbyError
from pokerthproto.player import Player

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_gameInfo():
    gameinfo = GameInfo("My Game")
    gameinfo.gameId = 1
    lobby = Lobby()
    lobby.addGameInfo(gameinfo)
    other_gameinfo = lobby.getGameInfo(1)
    with pytest.raises(LobbyError):
        lobby.getGameInfo(2)
    assert gameinfo == other_gameinfo
    lobby_id = lobby.getGameInfoId("My Game")
    assert lobby_id == 1
    with pytest.raises(LobbyError):
        lobby.getGameInfoId("Unknown Game")


def test_players():
    lobby = Lobby()
    assert len(lobby.players) == 0
    lobby.addPlayer(1)
    assert len(lobby.players) == 1
    lobby.addPlayer(2)
    with pytest.raises(LobbyError):
        lobby.addPlayer(2)
    lobby.delPlayer(2)
    assert len(lobby.players) == 1
    player = lobby.getPlayer(1)
    assert player.playerId == 1
    with pytest.raises(LobbyError):
        lobby.getPlayer(2)

