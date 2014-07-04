# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import pytest

from pokerthproto.lobby import GameInfo, Lobby, LobbyError
from pokerthproto.transport import unpack, develop
from pokerthproto.player import Player
from pokerthproto.pokerth_pb2 import netGameCreated

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'


def test_gameInfo():
    gameinfo = GameInfo("My Game")
    gameinfo.gameId = 1
    msg_data = '080d7233080210011800280632290a0e4d79204f6e6c696e652047616d6' \
               '51001180a2001280838014000480450075814600a68b8177801'
    gameinfo_msg = develop(unpack(msg_data.decode('hex')))
    gameinfo.setInfo(gameinfo_msg.gameInfo)
    new_msg = gameinfo.getMsg()
    assert new_msg == gameinfo_msg.gameInfo
    lobby = Lobby()
    lobby.addGameInfo(gameinfo)
    other_gameinfo = lobby.getGameInfo(1)
    with pytest.raises(LobbyError):
        lobby.getGameInfo(2)
    assert gameinfo == other_gameinfo
    assert gameinfo.__eq__(object) == NotImplemented
    lobby_id = lobby.getGameInfoId("My Online Game")
    assert lobby_id == 1
    with pytest.raises(LobbyError):
        lobby.getGameInfoId("Unknown Game")
    player1 = Player(1)
    gameinfo.addPlayer(player1)
    assert len(gameinfo.players) == 1
    gameinfo.delPlayer(player1)
    assert len(gameinfo.players) == 0
    gameinfo.gameMode = netGameCreated
    assert gameinfo.gameMode == netGameCreated
    gameinfo.isPrivate = True
    assert gameinfo.isPrivate
    gameinfo.fillWithComputerPlayers = True
    assert gameinfo.fillWithComputerPlayers


def test_LobbyError():
    err = LobbyError("message")
    print(err)


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
    gameinfo = GameInfo("My Game")
    gameinfo.gameId = 42
    lobby.addGameInfo(gameinfo)
    assert lobby.gameInfos[0] is gameinfo
    with pytest.raises(LobbyError):
        lobby.addGameInfo(gameinfo)
    lobby.addPlayerToGame(1, 42)
    lobby.getGameInfo(42).players[0].playerId == 1
    lobby.delPlayerFromGame(1, 42)
    assert len(lobby.getGameInfo(42).players) == 0
