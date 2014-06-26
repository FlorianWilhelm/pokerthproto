# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import sys
import random

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor, task
from twisted.python import log
from twisted.internet.defer import Deferred
from twisted.test import proto_helpers

from .fixtures import pokerth_server

from pokerthproto import lobby
from pokerthproto import game
from pokerthproto import protocol
from pokerthproto import pokerth_pb2
from pokerthproto.protocol import ClientProtocol, ClientProtocolFactory
from pokerthproto.transport import unpack, develop

__author__ = 'Florian Wilhelm'
__copyright__ = 'Florian Wilhelm'

log.startLogging(sys.stdout)


def test_lobby(pokerth_server):
    class PyClientProtocol(ClientProtocol):

        def handleInsideLobby(self, lobbyInfo):
            pass

    class PyClientProtocolFactory(ClientProtocolFactory):
        protocol = PyClientProtocol

    def test_state(proto):
        assert proto.state == protocol.States.LOBBY

    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 7234)
    nickname = 'PyClient' + str(random.getrandbits(23))
    factory = PyClientProtocolFactory(nickname)
    proto = factory.buildProtocol(('localhost', 0))
    connectProtocol(endpoint, proto)
    d = Deferred()
    reactor.callLater(4, d.callback, proto)
    d.addCallback(test_state)
    return d


def test_players(pokerth_server):
    class PyClientProtocol(ClientProtocol):

        def handleInsideLobby(self, lobbyInfo):
            pass

    class PyClientProtocolFactory(ClientProtocolFactory):
        protocol = PyClientProtocol

    def test_players(factory):
        assert factory.lobby.players[0].name == nickname

    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 7234)
    nickname = 'PyClient' + str(random.getrandbits(23))
    factory = PyClientProtocolFactory(nickname)
    proto = factory.buildProtocol(('localhost', 0))
    connectProtocol(endpoint, proto)
    d = Deferred()
    reactor.callLater(4, d.callback, factory)
    d.addCallback(test_players)
    return d


def test_create_game(pokerth_server):
    class PyClientProtocol(ClientProtocol):

        def handleInsideLobby(self, lobbyInfo):
            gameInfo = lobby.GameInfo('PyClient Game')
            self.sendJoinNewGame(gameInfo)

    class PyClientProtocolFactory(ClientProtocolFactory):
        protocol = PyClientProtocol

    def test_in_game(proto):
        assert proto.state == protocol.States.GAME_JOINED

    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 7234)
    nickname = 'PyClient' + str(random.getrandbits(23))
    factory = PyClientProtocolFactory(nickname)
    proto = factory.buildProtocol(('localhost', 0))
    connectProtocol(endpoint, proto)
    d = Deferred()
    reactor.callLater(4, d.callback, proto)
    d.addCallback(test_in_game)
    return d


def test_two_players_in_lobby(pokerth_server):
    class PyClient1Protocol(ClientProtocol):

        def handleInsideLobby(self, lobbyInfo):
            try:
                gameId = self.factory.lobby.getGameInfoId('PyClient Game')
            except lobby.LobbyError:
                reactor.callLater(1, self.handleInsideLobby, lobbyInfo)
            else:
                self.sendJoinExistingGame(gameId)

    class PyClient2Protocol(ClientProtocol):

        def handleInsideLobby(self, lobbyInfo):
            gameInfo = lobby.GameInfo('PyClient Game')
            self.sendJoinNewGame(gameInfo)

    class PyClient1ProtocolFactory(ClientProtocolFactory):
        protocol = PyClient1Protocol

    class PyClient2ProtocolFactory(ClientProtocolFactory):
        protocol = PyClient2Protocol

    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 7234)
    factory1 = PyClient1ProtocolFactory('PyClient1')
    d = endpoint.connect(factory1)

    def start_2nd_client():
        factory2 = PyClient2ProtocolFactory('Pfsdlfsdfj')
        d = endpoint.connect(factory2)
        d.addCallback(lambda proto: task.deferLater(reactor, 7, test_in_game))
        return d

    def test_in_game():
        assert len(factory1.lobby.players) == 2
        assert len(factory1.game.players) == 2

    d.addCallback(lambda proto: task.deferLater(reactor, 7, start_2nd_client))
    return d


def test_enum2str():
    chatType = pokerth_pb2.ChatMessage.ChatType
    for k, v in chatType.items():
        assert k == protocol.enum2str(chatType, v)


def test_chat():
    class PyClientProtocol(ClientProtocol):

        def handleChat(self, chatType, text, lobbyInfo, gameInfo=None,
                       playerInfo=None):
            ClientProtocol.handleChat(self, chatType, text, lobbyInfo,
                                      gameInfo, playerInfo)
            if playerInfo is None:
                self.sendChatRequest("Pong")
            else:
                self.sendChatRequest("Pooong", 5, 6)

    class PyClientProtocolFactory(ClientProtocolFactory):
        protocol = PyClientProtocol

    factory = PyClientProtocolFactory('PyClient1')
    factory.game = game.Game(1, 42)
    gameInfo = lobby.GameInfo("GameName")
    gameInfo.gameId = 1
    factory.lobby.addGameInfo(gameInfo)
    factory.lobby.addPlayer(1)
    proto = factory.buildProtocol(("localhost", 0))
    transport = proto_helpers.StringTransport()
    proto.makeConnection(transport)
    msg = pokerth_pb2.ChatMessage()
    msg.chatType = msg.chatTypeLobby
    msg.chatText = "Ping"
    proto.chatReceived(msg)
    reply = develop(unpack(transport.value()))
    assert reply.chatText == "Pong"
    msg.gameId = 1
    msg.playerId = 1
    proto.chatReceived(msg)
    reply = develop(unpack(transport.value()))
    assert reply.chatText == "Pooong"
    assert reply.targetGameId == 5
    assert reply.targetPlayerId == 6


